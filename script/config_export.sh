#!/bin/bash

## Globals/imports
SCRIPT_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export SCRIPT_PATH

REPO_PATH=$(readlink -f "${SCRIPT_PATH}/..")
export REPO_PATH

. "${REPO_PATH}/deps/bashplate/bashplate.sh"


## Arguments
# Check for required arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <export path>"
    exit 1
fi

config_path="${REPO_PATH}/config"
export_path="$1"
shift 1


## Check secrets
# pragma: allowlist nextline secret
secrets_name="secrets.yaml"

if [ ! -e "${config_path}/secrets.yaml" ]; then
    if [ -n "${CI:-}" ]; then
        print_warn "Running in CI mode, using secrets.ci.yaml"
        # pragma: allowlist nextline secret
        secrets_name="secrets.ci.yaml"
    else
        print_critical "Missing secrets.yaml"
        exit 1
    fi
fi


## Export configuration
# Copy files but do not overwrite (preserve UI defined entities)
for file in "automations.yaml" "scenes.yaml" "scripts.yaml"; do
    if [ ! -e "${export_path}/${file}" ]; then
        print_warn "Using default $(print_style "${file}" ${TERM_STYLE_BOLD})"
        cp "${config_path}/${file}" "${export_path}/${file}"
    fi
done

# Cleanup old packages and SSH configs
print_info "Removing old files"
rm -Rf "${export_path}/packages"
rm -f "${export_path}/ssh/config*"

# Copy configuration core files
print_info "Copying $(print_style "configuration.yaml" ${TERM_STYLE_BOLD})"
cp "${config_path}/configuration.yaml" "${export_path}/configuration.yaml"
print_info "Copying $(print_style "${secrets_name}" ${TERM_STYLE_BOLD})"
cp "${config_path}/${secrets_name}" "${export_path}/secrets.yaml"

# Copy directories
find "${config_path}" -maxdepth 1 -type d -print0 | while read -rd $'\0' dir; do
    print_info "Copying directory $(print_style "${dir}" ${TERM_STYLE_BOLD})"
    cp -R "$dir" "${export_path}"
done

# Cleanup non-CI files in CI mode
if [ -n "${CI:-}" ]; then
    print_warn "Remove non-CI files"
    grep -Rl "ci::remove" "${export_path}" | xargs rm -f
fi

# Fix permissions on SSH files
print_info "Fixing SSH file permissions"
find "${export_path}/ssh" -type d -exec chmod 700 {} +
find "${export_path}/ssh" -type f -exec chmod 600 {} +
