import subprocess
import shutil
import os

def is_adb_available() -> bool:
    """Checks if adb binary is available in PATH or Termux."""
    return shutil.which("adb") is not None

def run_adb_command(args: list) -> dict:
    """Runs an ADB shell command and captures output."""
    if not is_adb_available():
        return {
            "success": False,
            "error": "ADB package not installed. Termux me 'pkg install android-tools' chalayein."
        }
    try:
        cmd = ["adb"] + args
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0:
            return {"success": True, "output": res.stdout.strip()}
        else:
            return {"success": False, "error": res.stderr.strip() or res.stdout.strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_adb_connection() -> dict:
    """Checks if a device is connected via ADB (e.g. Wireless Debugging)."""
    res = run_adb_command(["devices"])
    if not res.get("success"):
        return res
    
    out = res.get("output", "")
    lines = [line.strip() for line in out.splitlines() if line.strip() and not line.startswith("List of devices")]
    
    connected = [line for line in lines if "\tdevice" in line or " device" in line]
    if connected:
        return {"connected": True, "devices": connected, "message": f"Connected to {len(connected)} device(s)"}
    else:
        return {
            "connected": False,
            "message": "Koi device ADB se connected nahi hai.",
            "setup_help": (
                "Wireless Debugging setup karne ke liye:\n"
                "1. Phone Settings -> Developer Options -> 'Wireless debugging' ON karein\n"
                "2. 'Pair device with pairing code' par tap karein\n"
                "3. Termux me command chalayein: adb pair localhost:<PAIR_PORT> <PAIR_CODE>\n"
                "4. Phir connect karein: adb connect localhost:<CONNECT_PORT>"
            )
        }

def tap_screen(x: int, y: int) -> dict:
    """Screen par specific (x, y) coordinates par tap karta hai."""
    res = run_adb_command(["shell", "input", "tap", str(x), str(y)])
    return res

def swipe_screen(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> dict:
    """Screen par swipe / scroll karta hai."""
    res = run_adb_command(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
    return res

def type_text(text: str) -> dict:
    """Active input field me text type karta hai."""
    # Replace spaces with %s for adb input
    safe_text = text.replace(" ", "%s")
    res = run_adb_command(["shell", "input", "text", safe_text])
    return res

def press_key(key: str) -> dict:
    """
    Android hardware key event trigger karta hai.
    Valid keys: HOME, BACK, APP_SWITCH (Recent Apps), POWER, VOLUME_UP, VOLUME_DOWN
    """
    key_map = {
        "home": "KEYCODE_HOME",
        "back": "KEYCODE_BACK",
        "recents": "KEYCODE_APP_SWITCH",
        "recent": "KEYCODE_APP_SWITCH",
        "power": "KEYCODE_POWER",
        "enter": "KEYCODE_ENTER"
    }
    target_key = key_map.get(key.lower(), key.upper())
    if not target_key.startswith("KEYCODE_"):
        target_key = "KEYCODE_" + target_key
        
    res = run_adb_command(["shell", "input", "keyevent", target_key])
    return res

def take_screenshot(save_path: str = "/sdcard/shoonya_screen.png") -> dict:
    """Screen ka live screenshot capture karta hai."""
    res = run_adb_command(["shell", "screencap", "-p", save_path])
    if res.get("success"):
        return {"success": True, "path": save_path, "message": f"Screenshot saved at {save_path}"}
    return res

def open_app(package_or_uri: str) -> dict:
    """Android Intent ke zariye app ya URL open karta hai."""
    if package_or_uri.startswith("http://") or package_or_uri.startswith("https://"):
        cmd = ["termux-open-url", package_or_uri]
        subprocess.run(cmd)
        return {"success": True, "opened": package_or_uri}
    else:
        # Try adb monkey or am start
        res = run_adb_command(["shell", "monkey", "-p", package_or_uri, "-c", "android.intent.category.LAUNCHER", "1"])
        return res
