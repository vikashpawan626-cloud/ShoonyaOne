import subprocess
import os
import shutil
import time
import threading

def _run_cmd(cmd: list, timeout: int = 15) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip() or res.stderr.strip()
    except Exception as e:
        return f"Error: {e}"

def run_terminal_command(command: str) -> dict:
    """
    Termux / Linux shell command execute karta hai.
    Used for checking files, system processes, storage, network, or running scripts.
    """
    # Prevent dangerous destructive commands
    dangerous = ["rm -rf /", "mkfs", ":(){ :|:& };:"]
    if any(d in command for d in dangerous):
        return {"success": False, "error": "Destructive command blocked for safety."}
        
    try:
        res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=20)
        output = res.stdout.strip() or res.stderr.strip() or "Command completed with no output."
        return {"success": res.returncode == 0, "output": output[:2000]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def launch_app(app_name: str) -> dict:
    """
    Android apps open karta hai.
    Supports: whatsapp, youtube, chrome, settings, camera, calculator, maps, gallery, playstore, etc.
    """
    name = app_name.lower().strip()
    
    app_intents = {
        "youtube": ["am", "start", "-a", "android.intent.action.VIEW", "-d", "https://youtube.com"],
        "whatsapp": ["am", "start", "-a", "android.intent.action.VIEW", "-d", "whatsapp://"],
        "chrome": ["termux-open-url", "https://google.com"],
        "browser": ["termux-open-url", "https://google.com"],
        "settings": ["am", "start", "-a", "android.settings.SETTINGS"],
        "wifi_settings": ["am", "start", "-a", "android.settings.WIFI_SETTINGS"],
        "bluetooth_settings": ["am", "start", "-a", "android.settings.BLUETOOTH_SETTINGS"],
        "camera": ["am", "start", "-a", "android.media.action.IMAGE_CAPTURE"],
        "calculator": ["am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.APP_CALCULATOR"],
        "maps": ["am", "start", "-a", "android.intent.action.VIEW", "-d", "geo:0,0"],
        "gallery": ["am", "start", "-a", "android.intent.action.VIEW", "-t", "image/*"],
        "playstore": ["am", "start", "-a", "android.intent.action.VIEW", "-d", "market://details?id=com.google.android.gms"]
    }
    
    for key, cmd in app_intents.items():
        if key in name:
            _run_cmd(cmd)
            return {"success": True, "opened": key, "message": f"{key.capitalize()} app open kar di gayi hai."}
            
    # Default fallback: try termux-open
    if name.startswith("http://") or name.startswith("https://"):
        _run_cmd(["termux-open-url", name])
        return {"success": True, "opened": name}
        
    return {"success": False, "error": f"App '{app_name}' ka direct intent nahi mila. Name check karein."}

def manage_files(action: str, target_path: str, data: str = "") -> dict:
    """
    Phone / Termux files aur folders manage karta hai.
    Action: 'list' (directory dekhna), 'read' (file padhna), 'write' (file likhna ya save karna).
    """
    act = action.lower().strip()
    path = os.path.expanduser(target_path)
    
    try:
        if act == "list":
            if not os.path.exists(path):
                return {"success": False, "error": f"Path '{path}' nahi mila."}
            files = os.listdir(path)
            return {"success": True, "files": files[:30], "total": len(files)}
            
        elif act == "read":
            if not os.path.isfile(path):
                return {"success": False, "error": f"File '{path}' nahi mili."}
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(4000)
            return {"success": True, "content": content}
            
        elif act == "write":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
            return {"success": True, "message": f"File '{path}' successfully likh di gayi."}
            
        else:
            return {"success": False, "error": f"Unknown action '{action}'. Valid: list, read, write."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def set_timer(seconds: int, note: str = "Timer complete") -> dict:
    """Countdown timer set karta hai jo expire hone par bolta hai aur notification bhejta hai."""
    sec = max(1, min(86400, int(seconds)))
    
    def _timer_worker():
        time.sleep(sec)
        try:
            subprocess.run(["termux-notification", "--title", "ShoonyaOne Timer", "--content", note, "--priority", "high"])
            subprocess.run(["termux-vibrate", "-d", "1000"])
            from .voice import speak
            speak(f"Vikash, aapka timer poora ho gaya: {note}")
        except Exception:
            pass

    threading.Thread(target=_timer_worker, daemon=True).start()
    return {"success": True, "seconds": sec, "note": note, "message": f"{sec} seconds ka timer start ho gaya hai."}
