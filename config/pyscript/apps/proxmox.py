import aiohttp
from typing import Any, Optional


_PROXMOX_TIMEOUT = aiohttp.ClientTimeout(total=5.0)


async def _proxmox_api_request(path: str, data: Optional[dict[str, Any]] = None):
    data = data or {}

    url = f"http{'s' if pyscript.app_config.get('api_tls', False) else ''}://" \
          f"{pyscript.app_config.get('api_host')}/api2/json/{path}"

    headers = {
        'Authorization': f"PVEAPIToken={pyscript.app_config.get('api_token')}"
    }

    async with aiohttp.ClientSession(headers=headers, raise_for_status=True, timeout=_PROXMOX_TIMEOUT) as session:
        try:
            async with session.post(url, json=data) as resp:
                log.debug(f"Response ({resp.status}): {resp.json()!r}")
        except aiohttp.ClientError as exc:
            log.error(f"Error sending command to {url} (json: {data!r}, error: {exc!s})")

    await session.close()


@service
def proxmox_status_action(node: str, target_type: str, target_id: int, action: str):
    """yaml
name: Request Proxmox to change power state of a container or VM
description: Request the restart of a specified service on the OPNSense router.
fields:
  node:
    description: Node name
    example: 'pve'
    required: true
    selector:
      text: {}
  target_type:
    description: Target type
    selector:
      select:
        options:
          - label: LXC
            value: lxc
          - label: VM
            value: vm
  target_id:
    description: LXC/VM ID
    example: 101
    required: true
    selector:
      number:
        min: 0
        max: 100000
        mode: box
  action:
    description: VM action to request
    selector:
      select:
        options:
          - label: Reboot
            value: reboot
          - label: Reset
            value: reset
          - label: Resume
            value: resume
          - label: Shutdown
            value: shutdown
          - label: Start
            value: start
          - label: Stop
            value: stop
          - label: Suspend
            value: suspend
    """
    if target_type == 'lxc':
        target_type_str = 'lxc'
    elif target_type == 'vm':
        target_type_str = 'qemu'
    else:
        raise ValueError(f"Unexpected target type {target_type!r}")

    log.info(f"Requesting {action} for {target_id}@{node}")

    _proxmox_api_request(
        f"{node}/{target_type_str}/{target_id}/status/{action}"
    )
