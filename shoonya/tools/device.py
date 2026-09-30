import subprocess
import json
import re

def _run_cmd(cmd: list) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_battery_status() -> dict:
    """Phone ki current battery percentage, charging status, health aur temperature return karta hai."""
    out = _run_cmd(["termux-battery-status"])
    try:
        data = json.loads(out)
        return {
            "percentage": data.get("percentage"),
            "status": data.get("status"),
            "health": data.get("health"),
            "temperature": data.get("temperature"),
            "plugged": data.get("plugged"),
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": f"Battery status parse error: {e}"}

def set_torch(state: bool) -> dict:
    """Torch (Flashlight) ko turn ON (True) ya OFF (False) karta hai."""
    arg = "on" if state else "off"
    _run_cmd(["termux-torch", arg])
    return {"success": True, "action": f"Torch turned {arg.upper()}"}

def set_brightness(level: int) -> dict:
    """Screen ki brightness set karta hai (0 se 255 ke beech)."""
    val = max(0, min(255, int(level)))
    _run_cmd(["termux-brightness", str(val)])
    return {"success": True, "brightness_level": val, "message": f"Brightness set to {val}"}

def set_volume(stream: str, volume: int) -> dict:
    """
    Phone ki specific audio volume stream set karta hai.
    Valid streams: 'music', 'call', 'ring', 'system', 'alarm', 'notification'
    """
    valid_streams = ["music", "call", "ring", "system", "alarm", "notification"]
    stream_clean = stream.lower().strip()
    if stream_clean not in valid_streams:
        stream_clean = "music"
    
    vol = max(0, int(volume))
    _run_cmd(["termux-volume", stream_clean, str(vol)])
    return {"success": True, "stream": stream_clean, "volume": vol}

def get_volume_info() -> list:
    """Phone ki audio streams aur unke current volume levels return karta hai."""
    out = _run_cmd(["termux-volume"])
    try:
        return json.loads(out)
    except Exception:
        return []

def vibrate_phone(duration_ms: int = 500) -> dict:
    """Phone ko vibrate karta hai."""
    ms = max(50, min(5000, int(duration_ms)))
    _run_cmd(["termux-vibrate", "-d", str(ms)])
    return {"success": True, "duration_ms": ms}

def show_toast(message: str) -> dict:
    """Screen par popup toast notification show karta hai."""
    _run_cmd(["termux-toast", "-s", message])
    return {"success": True, "toast": message}

def send_notification(title: str, content: str, priority: str = "high") -> dict:
    """Android status bar me system notification send karta hai."""
    cmd = ["termux-notification", "--title", title, "--content", content, "--priority", priority]
    _run_cmd(cmd)
    return {"success": True, "notification_title": title}

def read_notifications() -> list:
    """Recent system notifications read karta hai."""
    out = _run_cmd(["termux-notification-list"])
    try:
        data = json.loads(out)
        notifications = []
        for n in data[:10]:
            notifications.append({
                "packageName": n.get("packageName", ""),
                "title": n.get("title", ""),
                "content": n.get("content", ""),
                "when": n.get("when", "")
            })
        return notifications
    except Exception as e:
        return [{"error": str(e)}]

def get_clipboard() -> str:
    """Clipboard ka current copied text return karta hai."""
    return _run_cmd(["termux-clipboard-get"])

def set_clipboard(text: str) -> dict:
    """Clipboard me text copy karta hai."""
    try:
        proc = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=text, timeout=5)
        return {"success": True, "copied": text[:50] + ("..." if len(text) > 50 else "")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_wifi_info() -> dict:
    """Current connected WiFi network details return karta hai."""
    out = _run_cmd(["termux-wifi-connectioninfo"])
    try:
        return json.loads(out)
    except Exception:
        return {"status": "Unable to fetch WiFi info"}
