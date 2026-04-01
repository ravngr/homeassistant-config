#!/usr/bin/env python3

import os
import os.path
import sys
from ssl import CERT_REQUIRED

from ldap3 import Server, Connection, Tls, ALL
from ldap3.core.exceptions import LDAPException
from ldap3.utils.conv import escape_bytes, escape_filter_chars


_LDAP_DEFAULT_TIMEOUT = 2


def stderr_print(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)


def get_user(ldap_connection: Connection, ldap_base_dn: str, ldap_base_filter: str, ldap_username_attr: str,
        ldap_name_attr: str, username: str) -> tuple[str, str, list[str]] | None:
    ldap_search = ldap_connection.search(
        ldap_base_dn,
        ldap_base_filter,
        attributes=[
            ldap_name_attr,
            'memberOf'
        ]
    )

    if len(ldap_connection.entries) == 1:
        # Extract user DN and displayName from search results
        return \
            ldap_connection.entries[0].entry_dn, \
            getattr(ldap_connection.entries[0], ldap_name_attr).value, \
            ldap_connection.entries[0].memberOf.values,
    elif len(ldap_search.entries) > 1:
        stderr_print(f"LDAP filter returned ")

    return None


if __name__ == '__main__':
    # Load .env if available
    from dotenv import load_dotenv

    load_dotenv()

    try:
        ldap_uri = os.environ['LDAP_URI']
        ldap_base_dn = os.environ['LDAP_BASE_DN']
        ldap_bind_dn = os.environ['LDAP_BIND_DN']
        ldap_bind_password = os.environ['LDAP_BIND_PASSWORD']
    except KeyError as exc:
        stderr_print(f"Requirement LDAP environment variable {exc!r} is not defined")
        sys.exit(1)

    try:
        ldap_timeout = os.getenv('LDAP_TIMEOUT', _LDAP_DEFAULT_TIMEOUT)
    except ValueError:
        ldap_timeout = _LDAP_DEFAULT_TIMEOUT

    ldap_admin_group = os.getenv('LDAP_ADMIN_GROUP')
    ldap_local_group = os.getenv('LDAP_LOCAL_GROUP')
    ldap_base_filter = os.getenv('LDAP_BASE_FILTER', 'objectClass=inetOrgPerson')
    ldap_username_attr = os.getenv('LDAP_USERNAME_ATTR', 'uid')
    ldap_name_attr = os.getenv('LDAP_NAME_ATTR', 'displayName')

    ldap_tls_client_key_path = os.getenv('LDAP_TLS_CLIENT_KEY_PATH')
    ldap_tls_client_cert_path = os.getenv('LDAP_TLS_CLIENT_CERT_PATH')
    ldap_tls_ca_path = os.getenv('LDAP_TLS_CA_PATH')

    ldap_tls = None

    if ldap_tls_client_key_path or ldap_tls_client_cert_path or ldap_tls_ca_path:
        ldap_tls = Tls(
            local_private_key_file=ldap_tls_client_key_path,
            local_certificate_file=ldap_tls_client_cert_path,
            validate=CERT_REQUIRED,
            ca_certs_file=ldap_tls_ca_path
        )

    try:
        username = escape_filter_chars(os.environ['username'])
        password = os.environ['password']
    except KeyError as exc:
        stderr_print(f"Requirement environment variable {exc!r} is not defined")
        sys.exit(1)

    # LDAP filter
    user_filter = f"{ldap_username_attr}={username.lower()}"
    ldap_filter = f"(&({ldap_base_filter})({user_filter}))"

    # Setup LDAP connection
    ldap_server = Server(
        ldap_uri,
        tls=ldap_tls,
        connect_timeout=ldap_timeout
    )

    try:
        with Connection(
            ldap_server,
            ldap_bind_dn,
            ldap_bind_password,
            auto_bind=True,
            read_only=True,
            raise_exceptions=True
        ) as ldap_connection:
            user = get_user(
                ldap_connection,
                ldap_base_dn,
                ldap_filter,
                ldap_username_attr,
                ldap_name_attr,
                username
            )
    except LDAPException as exc:
        stderr_print(f"Error during LDAP connection: {exc!s}")
        sys.exit(1)

    if user is None:
        stderr_print(f"LDAP entry matching filter {ldap_filter!r} not found")
        sys.exit(1)

    user_dn, user_name, user_groups = user
    user_admin = False
    user_local = False

    if ldap_admin_group and ldap_admin_group in user_groups:
        user_admin = True

    if ldap_local_group and ldap_local_group in user_groups:
        user_local = True

    stderr_print(f"Matched user {user_dn!r}, admin={user_admin}, local={user_local}")

    # Validate password by connecting
    try:
        with Connection(
                ldap_server,
                user_dn,
                password,
                auto_bind=True,
                raise_exceptions=True
            ) as ldap_connection:
                pass
    except LDAPException as exc:
        stderr_print(f"Authentication of user {user_dn!r} failed")
        sys.exit(1)

    print(
        f"name = {user_name}\n" \
        f"group = {'system-admin' if user_admin else 'system-users'}\n" \
        f"local_only = {'true' if user_local else 'false'}\n"
    )

    sys.exit(0)
