import aiohttp
import asyncio
from typing import Optional


# Reference: https://www.voipinfo.net/docs/cisco/CUIP_BK_P82B3B16_00_phones-services-application-development-notes.pdf


_CISCO_TIMEOUT = aiohttp.ClientTimeout(total=5.0)
_XML_SCHEMA_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


async def _cisco_phone_command_send(session: aiohttp.Session, target: str, xml: str):
    url = f"http://{target}/CGI/Execute"
    payload = {'XML': xml}
    log.debug(f"Cisco IP phone command to {url} with payload {payload!r}")

    try:
        async with session.post(url, data=payload) as resp:
            resp_str = await resp.text()
            log.debug(f"Response ({resp.status}): {resp}")
    except aiohttp.ClientError as exc:
        log.error(f"Error sending command to {url} (error: {exc!s})")


async def _cisco_phone_command(target_csv: str, xml: str, username: Optional[str] = None, password: Optional[str] = None):
    auth = aiohttp.BasicAuth(
        username or 'username',
        password or 'password'
    )

    async with aiohttp.ClientSession(auth=auth, raise_for_status=True, timeout=_CISCO_TIMEOUT) as session:
        await asyncio.gather(
            *[
                _cisco_phone_command_send(
                    session,
                    target.strip(),
                    xml
                )
                for target
                in target_csv.split(',')
            ]
        )

    await session.close()


@service
def cisco_phone_background(target: str, icon_url: str, image_url: str):
    """yaml
name: Set background image on a Cisco IP phone
description: Uses CGI execute to clear any active application or popup.
fields:
  target:
    description: Comma-seperated list of target IP phone hostname or IP address.
    example: 'phone-hostname'
    required: true
    selector:
      text: {}
  icon_url:
    description: Icon URL.
    selector:
      text:
        type: url
  image_url:
    description: Image URL.
    selector:
      text:
        type: url
    """
    log.info(f"Setting background {image_url} on {target}")

    _cisco_phone_command(
        target,
        _XML_SCHEMA_HEADER + (
            "<setBackground><background>"
            f"<icon>{icon_url}</icon>"
            f"<image>{image_url}</image>"
            "</background></setBackground>"
        )
    )


@service
def cisco_phone_clear(target: str, priority: int = 0):
    """yaml
name: Clear popup or application from a Cisco IP phone
description: Uses CGI execute to clear any active application or popup.
fields:
  target:
    description: Comma-seperated list of target IP phone hostname or IP address.
    example: 'phone-hostname'
    required: true
    selector:
      text: {}
  priority:
    description: Execution priority.
    advanced: true
    selector:
      select:
        mode: dropdown
        options:
          - label: Immediate
            value: 0
          - label: When idle
            value: 1
          - label: If idle
            value: 2
    """
    log.info(f"Clearing {target}")

    _cisco_phone_command(
        target,
        _XML_SCHEMA_HEADER + (
            "<CiscoIPPhoneExecute>"
            f"<ExecuteItem URL=\"Init:Services\" Priority=\"{priority}\" />"
            "</CiscoIPPhoneExecute>"
        )
    )


@service
def cisco_phone_dial(target: str, number: str, mute: bool = False, priority: int = 0):
    """yaml
name: Dial number from a Cisco IP phone
description: Uses CGI execute to dial a number from a phone.
fields:
  target:
    description: Comma-seperated list of target IP phone hostname or IP address.
    example: 'phone-hostname'
    required: true
    selector:
      text: {}
  number:
    description: Number to dial.
    example: '123'
    required: true
    selector:
      text:
        type: tel
  priority:
    description: Execution priority.
    advanced: true
    selector:
      select:
        mode: dropdown
        options:
          - label: Immediate
            value: 0
          - label: When idle
            value: 1
          - label: If idle
            value: 2
    """
    log.info(f"Dialing {number} on {target}")

    _cisco_phone_command(
        target,
        _XML_SCHEMA_HEADER + (
            "<CiscoIPPhoneExecute>"
            f"<ExecuteItem URL=\"Dial:{number}:0::0\" Priority=\"{priority}\" />"
            "</CiscoIPPhoneExecute>"
        )
    )


@service
def cisco_phone_display(target: str, state: Optional[bool] = None, interval: int = False, priority: int = 0):
    """yaml
name: Control display on a Cisco IP phone
description: Uses CGI execute to control phone display.
fields:
  target:
    description: Comma-seperated list of target IP phone hostname or IP address.
    example: 'phone-hostname'
    required: true
    selector:
      text: {}
  state:
    description: Display state.
    required: true
    selector:
      select:
        mode: dropdown
        options:
          - Default
          - 'On'
          - 'Off'
  interval:
    description: Duration to maintain state in minutes, indefinite if not specified.
    selector:
      number:
        min: 1
        max: 1440
        unit_of_measurement: min
  priority:
    description: Execution priority.
    advanced: true
    selector:
      select:
        mode: dropdown
        options:
          - label: Immediate
            value: 0
          - label: When idle
            value: 1
          - label: If idle
            value: 2
    """
    log.info(f"Setting display {state} (interval: {interval}) on {target}")

    _cisco_phone_command(
        target,
        _XML_SCHEMA_HEADER + (
            "<CiscoIPPhoneExecute>"
            f"<ExecuteItem URL=\"Display:{state}:{interval or 0}\" Priority=\"{priority}\" />"
            "</CiscoIPPhoneExecute>"
        )
    )


@service
def cisco_phone_image(target: str, url: str, title: Optional[str] = None, prompt: Optional[str] = None, location_x: int = 0, location_y: int = 0, window_mode: str = '', priority: int = 0) -> None:
    """yaml
name: Display image on Cisco IP phone
description: Uses CGI execute to display an image on a phone.
fields:
  target:
    description: Comma-seperated list of target IP phone hostname or IP address.
    required: true
    selector:
      text: {}
  url:
    description: Image URL.
    required: true
    selector:
      text:
        type: url
  title:
    description: Message title
    selector:
      text: {}
  prompt:
    description: Message prompt
    selector:
      text: {}
  location_x:
    description: Image X position.
    selector:
      number:
        min: 0
        max: 279
        unit_of_measure: px
  location_y:
    description: Image Y position.
    selector:
      number:
        min: 0
        max: 167
        unit_of_measure: px
  window_mode:
    description: Image window mode.
    selector:
      select:
        mode: dropdown
        options:
          - label: Default
            value: ''
          - label: Normal
            value: Normal
          - label: Wide
            value: Wide
  priority:
    description: Execution priority.
    advanced: true
    selector:
      select:
        mode: dropdown
        options:
          - label: Immediate
            value: 0
          - label: When idle
            value: 1
          - label: If idle
            value: 2
    """
    log.info(f"Display image {url} on {target}")

    body = []

    if title:
        body.append(f"<Title>{title}</Title>")

    if prompt:
        body.append(f"<Prompt>{prompt}</Prompt>")

    body.extend([
        f"<LocationX>{location_x}</LocationX>",
        f"<LocationY>{location_y}</LocationY>",
        f"<URL>{url}</URL>"
    ])

    if len(window_mode) > 0:
        window_mode_str = f" WindowMode=\"{window_mode}\""
    else:
        window_mode_str = ''

    _cisco_phone_command(
        target,

        _XML_SCHEMA_HEADER + (
            f"<CiscoIPPhoneImageFile{window_mode_str}>" +
            ''.join(body) +
            "</CiscoIPPhoneImageFile>"
        )
    )


@pyscript_compile
def _mirror_image(filename: str, data: bytes) -> str:
    try:
        with open(filename, 'wb') as cache_file:
            cache_file.write(data)
    except Exception as exc:
        return None, exc


@service
def cisco_phone_image_auto(target: str, src_url: str, title: Optional[str] = None, prompt: Optional[str] = None, location_x: int = 0, location_y: int = 0, window_mode: str = '', priority: int = 0) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(src_url) as response:
            response.raise_for_status()
            data = response.read()


@service
def cisco_phone_key(target: str, key: str, priority: int = 0):
    """yaml
name: Press key on Cisco IP phone
description: Uses CGI execute to press a key on a phone.
fields:
  target:
    description: Comma-seperated list of target IP phone hostname or IP address.
    example: 'phone-hostname'
    required: true
    selector:
      text: {}
  key:
    description: Key to press.
    required: true
    selector:
      select:
        mode: dropdown
        options:
          - label: Applications
            value: Applications
          - label: Headset
            value: Headset
          - label: Messages
            value: Messages
          - label: Mute
            value: Mute
          - label: Release
            value: Release
          - label: Speaker Phone
            value: Speaker
          - label: Volume Down
            value: VolDwn
          - label: Volume Up
            value: VolUp
          - label: Line 1
            value: Line1
          - label: Line 2
            value: Line2
          - label: Navigate Back
            value: NavBack
          - label: Navigate Down
            value: NavDwn
          - label: Navigate Left
            value: NavLeft
          - label: Navigate Right
            value: NavRight
          - label: Navigate Up
            value: NavUp
          - label: Navigate Select
            value: NavSelect
          - label: Keypad 0
            value: KeyPad0
          - label: Keypad 1
            value: KeyPad1
          - label: Keypad 2
            value: KeyPad2
          - label: Keypad 3
            value: KeyPad3
          - label: Keypad 4
            value: KeyPad4
          - label: Keypad 5
            value: KeyPad5
          - label: Keypad 6
            value: KeyPad6
          - label: Keypad 7
            value: KeyPad7
          - label: Keypad 8
            value: KeyPad8
          - label: Keypad 9
            value: KeyPad9
          - label: 'Keypad #'
            value: KeyPadPound
          - label: 'Keypad *'
            value: KeyPadStar
  priority:
    description: Execution priority.
    advanced: true
    selector:
      select:
        mode: dropdown
        options:
          - label: Immediate
            value: 0
          - label: When idle
            value: 1
          - label: If idle
            value: 2
    """
    log.info(f"Pressing {key} on {target}")

    _cisco_phone_command(
        target,
        _XML_SCHEMA_HEADER + (
            "<CiscoIPPhoneExecute>"
            f"<ExecuteItem URL=\"Key:{key}\" Priority=\"{priority}\" />"
            "</CiscoIPPhoneExecute>"
        )
    )


@service
def cisco_phone_play(target: str, filename: str, priority: int = 0):
    """yaml
name: Play raw sound on Cisco IP phone
description: Uses CGI execute to play a raw formatted file on a phone.
fields:
  target:
    description: Comma-seperated list of target IP phone hostname or IP address.
    required: true
    selector:
      text: {}
  filename:
    description: File to play, must be accessible via TFTP from phone.
    example: filename.raw
    required: true
    selector:
      text:
  priority:
    description: Execution priority.
    advanced: true
    selector:
      select:
        mode: dropdown
        options:
          - label: Immediate
            value: 0
          - label: When idle
            value: 1
          - label: If idle
            value: 2
    """
    log.info(f"Play {filename} on {target}")

    _cisco_phone_command(
        target,
        _XML_SCHEMA_HEADER + (
            "<CiscoIPPhoneExecute>"
            f"<ExecuteItem URL=\"Play:{filename}\" Priority=\"{priority}\" />"
            "</CiscoIPPhoneExecute>"
        )
    )


@service
def cisco_phone_text(target: str, text: str, title: Optional[str] = None, prompt: Optional[str] = None, priority: int = 0) -> None:
    """yaml
name: Display text message on Cisco IP phone
description: Uses CGI execute to display a message on a phone.
fields:
  target:
    description: Comma-seperated list of target IP phone hostname or IP address.
    required: true
    selector:
      text: {}
  text:
    description: Text body.
    required: true
    selector:
      text:
        multiline: true
  title:
    description: Message title
    selector:
      text: {}
  prompt:
    description: Message prompt
    selector:
      text: {}
  priority:
    description: Execution priority.
    advanced: true
    selector:
      select:
        mode: dropdown
        options:
          - label: Immediate
            value: 0
          - label: When idle
            value: 1
          - label: If idle
            value: 2
    """
    log.info(f"Display {text!r} on {target}")

    body = []

    if title:
        body.append(f"<Title>{title}</Title>")

    if prompt:
        body.append(f"<Prompt>{prompt}</Prompt>")

    body.append(f"<Text>{text}</Text>")

    _cisco_phone_command(
        target,
        _XML_SCHEMA_HEADER + (
            "<CiscoIPPhoneText>" +
            ''.join(body) +
            "</CiscoIPPhoneText>"
        )
    )
