import aiohttp
from typing import Any


_OPNSENSE_TIMEOUT = aiohttp.ClientTimeout(total=5.0)


async def _opnsense_api_request(path: str, **kwargs: Any):
    url = f"http{'s' if pyscript.app_config.get('api_tls', False) else ''}://" \
          f"{pyscript.app_config.get('api_host')}/api/{path}"

    auth = aiohttp.BasicAuth(
        pyscript.app_config.get('api_key'),
        pyscript.app_config.get('api_secret')
    )

    async with aiohttp.ClientSession(auth=auth, raise_for_status=True, timeout=_OPNSENSE_TIMEOUT) as session:
        try:
            async with session.post(url, data=kwargs) as resp:
                log.debug(f"Response ({resp.status}): {await resp.text()}")
        except aiohttp.ClientError as exc:
            log.error(f"Error sending command to {url} (error: {exc!s})")

    await session.close()


@service
def opnsense_wol(interface: str, mac: str):
    """yaml
name: Send WOL packet from OPNSense
description: Send a Wake-On-LAN (WOL) packet to the specified MAC address on the specified interface via OPNSense.
fields:
  interface:
    description: Source interface name
    example: 'eth0'
    required: true
    selector:
      text: {}
  mac:
    description: Target MAC address
    example: '00:00:00:00:00:00'
    selector:
      text: {}
    required: true
    """
    log.info(f"Sending wake-on-LAN to {mac} via {interface}")

    _opnsense_api_request(
        'wol/wol/set',
        {
            'interface': interface,
            'mac': mac
        }
    )