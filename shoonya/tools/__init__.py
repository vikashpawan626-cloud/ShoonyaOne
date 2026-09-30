"""
ShoonyaOne Tools Registry
Collects and instruments all device, comms, web, voice, system, and adb functions.
"""

import functools
import json
from ..ui import print_thought, print_action, print_verification

from .device import (
    get_battery_status,
    set_torch,
    set_brightness,
    set_volume,
    get_volume_info,
    vibrate_phone,
    show_toast,
    send_notification,
    read_notifications,
    get_clipboard,
    set_clipboard,
    get_wifi_info
)

from .comms import (
    get_contacts,
    search_contacts,
    make_phone_call,
    send_sms,
    read_sms_inbox,
    get_call_logs
)

from .web import search_web
from .voice import speak, listen_speech
from .system import (
    run_terminal_command,
    launch_app,
    manage_files,
    set_timer
)
from .adb import (
    check_adb_connection,
    tap_screen,
    swipe_screen,
    type_text,
    press_key,
    take_screenshot,
    open_app
)

# Raw list of all 29 tools
RAW_TOOLS = [
    get_battery_status,
    set_torch,
    set_brightness,
    set_volume,
    get_volume_info,
    vibrate_phone,
    show_toast,
    send_notification,
    read_notifications,
    get_clipboard,
    set_clipboard,
    get_wifi_info,
    search_contacts,
    make_phone_call,
    send_sms,
    read_sms_inbox,
    get_call_logs,
    search_web,
    run_terminal_command,
    launch_app,
    manage_files,
    set_timer,
    check_adb_connection,
    tap_screen,
    swipe_screen,
    type_text,
    press_key,
    take_screenshot,
    open_app
]

def _instrument(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        name = fn.__name__
        arg_summary = ""
        if kwargs:
            arg_summary = json.dumps(kwargs, ensure_ascii=False)
        elif args:
            arg_summary = str(args)
            
        print_thought(f"Planning step: Execute '{name}'")
        print_action(f"{name}()", f"Parameters: {arg_summary}" if arg_summary else "")
        
        try:
            res = fn(*args, **kwargs)
            status_ok = True
            if isinstance(res, dict) and res.get("success") is False:
                status_ok = False
            elif isinstance(res, list) and res and isinstance(res[0], dict) and "error" in res[0]:
                status_ok = False
                
            summary = str(res)
            if len(summary) > 120:
                summary = summary[:120] + "..."
            print_verification(status_ok, f"Output verified: {summary}")
            return res
        except Exception as e:
            print_verification(False, f"Error during execution: {e}")
            return {"error": str(e), "success": False}
            
    return wrapper

ALL_TOOLS = [_instrument(f) for f in RAW_TOOLS]
TOOL_MAP = {f.__name__: f for f in ALL_TOOLS}
