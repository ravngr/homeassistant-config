import aiohttp
import json
from datetime import datetime
from typing import Any, Optional


@service
def ntfy_publish(topic: str, message: Optional[str] = None, title: Optional[str] = None,
                 tags: Optional[list[str]] = None, priority: Optional[int] = None,
                 actions: Optional[list[dict[str, Any]]] = None, click: Optional[str] = None,
                 attach: Optional[str] = None, markdown: Optional[bool] = None, icon: Optional[str] = None,
                 filename: Optional[str] = None, delay: Optional[datetime] = None, email: Optional[str] = None,
                 call: Optional[str] = None, host_url: Optional[str] = None, host_token: Optional[str] = None):
    """yaml
name: Publish message on ntfy
description: Publish a message to a ntfy server with various message attributes.
fields:
  topic:
    description: Target topic name
    example: 'topic'
    required: true
    selector:
      text: {}
  message:
    description: Message body
    selector:
      text:
        multiline: true
  tags:
    description: List of tags (may map to emoji)
    example: 'incoming_envelope,hammer_and_wrench'
    selector:
      text:
        multiple: true
        type: text
  priority:
    description: Message priority
    default: Default
    selector:
      select:
        options:
          - label: Min
            value: 1
          - label: Low
            value: 2
          - label: Default
            value: 3
          - label: High
            value: 4
          - label: Max
            value: 5
  actions:
    description: Custom user action buttons for notifications
    selector:
      text:
        multiple: true
        type: text
  click:
    description: URL to open when notification is clicked
    example: https://etoast.net
    selector:
      text:
        type: url
  attach:
    description: URL for attachment to notification
    selector:
      text:
        type: url
  markdown:
    description: If true message will be interpreted with markdown
    default: true
    selector:
      boolean: {}
  icon:
    description: URL for notification icon
    example: https://etoast.net/favicon.ico
    selector:
      text:
        type: url
  filename:
    description: File name of the attachment
    selector:
      text:
        type: text
  delay:
    description: Delay delivery until specified date and time
    selector:
      datetime: {}
  email:
    description: Target email address for notifications
    selector:
      text:
        type: email
  call:
    description: Target phone number for voice calls
    selector:
      text:
        type: tel
  host_url:
    description: Override publication URL
    example: https://ntfy.sh
    selector:
      text:
        type: url
  host_token:
    description: Override authorization token
    example: tk_...
    selector:
      text:
        type: text
    """
    host_url = host_url or pyscript.app_config.get('url')
    host_token = host_token or pyscript.app_config.get('token')
    host_timeout = aiohttp.ClientTimeout(total=pyscript.app_config.get('timeout'))

    headers = {
        'Authorization': f"Bearer {host_token}"
    }

    # Parse priority
    try:
        priority_value = int(priority) if priority is not None else None
    except ValueError:
        priority_value = None

    # Parse actions
    if actions is not None:
        actions_value = []

        for action in actions:
            actions_value.append(json.loads(action))
    else:
        actions_value = None

    # Parse markdown
    if markdown is not None:
        markdown_value = bool(markdown)
    else:
        markdown_value = None

    # Parse delay
    if isinstance(delay, datetime):
        delay_value = int(delay.timestamp())
    else:
        delay_value = None

    payload = {
        'topic': topic,
        'message': message,
        'title': title,
        'tags': tags,
        'priority': priority_value,
        'actions': actions_value,
        'click': click,
        'attach': attach,
        'markdown': markdown_value,
        'icon': icon,
        'filename': filename,
        'delay': delay_value,
        'email': email,
        'call': call
    }

    # Only include non-none fields
    payload_filtered = {k: v for k, v in payload.items() if v is not None}

    log.info(f"Sensing ntfy notification to {host_url} with payload {payload_filtered!r}")

    async with aiohttp.ClientSession(raise_for_status=True, timeout=host_timeout) as session:
        try:
            async with session.post(host_url, json=payload_filtered, headers=headers) as resp:
                log.debug(f"Response ({resp.status}): {resp.json()!r}")
        except aiohttp.ClientError as exc:
            log.error(f"Error sending command to {host_url} (json: {payload!r}, error: {exc!s})")

    await session.close()
