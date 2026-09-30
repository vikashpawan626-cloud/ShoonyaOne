import subprocess
import json
import re
import difflib

def _run_cmd(cmd: list) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_contacts() -> list:
    """Phone ke contacts list fetch karta hai."""
    out = _run_cmd(["termux-contact-list"])
    try:
        return json.loads(out)
    except Exception:
        return []

def search_contacts(query: str) -> list:
    """Contacts me naam ya number search karta hai."""
    contacts = get_contacts()
    q = query.lower().strip()
    matches = []
    
    for c in contacts:
        name = c.get("name", "")
        num = c.get("number", "")
        if q in name.lower() or q in num:
            matches.append({"name": name, "number": num})
            
    if not matches:
        # Fuzzy match
        names = [c.get("name", "") for c in contacts if c.get("name")]
        close = difflib.get_close_matches(q, [n.lower() for n in names], n=3, cutoff=0.5)
        for matched_name in close:
            for c in contacts:
                if c.get("name", "").lower() == matched_name:
                    matches.append({"name": c.get("name"), "number": c.get("number")})
                    
    return matches[:5]

def find_number(target: str) -> tuple:
    """Naam ya number me se valid call number aur display name nikalta hai."""
    clean_digits = re.sub(r"[^\d+]", "", target)
    if len(clean_digits) >= 10:
        return clean_digits, target
    
    matches = search_contacts(target)
    if matches:
        first = matches[0]
        raw_num = first.get("number", "")
        clean_num = re.sub(r"[^\d+]", "", raw_num)
        return clean_num, first.get("name", target)
        
    return None, None

def make_phone_call(target: str) -> dict:
    """Direct phone call initiate karta hai."""
    number, name = find_number(target)
    if not number:
        return {"success": False, "error": f"Contact ya number '{target}' nahi mila"}
    
    _run_cmd(["termux-telephony-call", number])
    return {"success": True, "action": f"Calling {name} ({number})", "number": number, "name": name}

def send_sms(target: str, message: str) -> dict:
    """Kisi number ya contact ko SMS send karta hai."""
    number, name = find_number(target)
    if not number:
        return {"success": False, "error": f"Valid phone number ya contact '{target}' nahi mila"}
    
    cmd = ["termux-sms-send", "-n", number, message]
    _run_cmd(cmd)
    return {"success": True, "action": f"SMS sent to {name} ({number})", "message": message}

def read_sms_inbox(limit: int = 5) -> list:
    """Recent inbox SMS read karta hai."""
    out = _run_cmd(["termux-sms-inbox", "-l", str(limit)])
    try:
        data = json.loads(out)
        result = []
        for sms in data:
            result.append({
                "from": sms.get("sender", sms.get("number")),
                "body": sms.get("body", ""),
                "received": sms.get("received", "")
            })
        return result
    except Exception as e:
        return [{"error": f"SMS read error: {e}"}]

def get_call_logs(limit: int = 5) -> list:
    """Recent phone call logs (incoming, outgoing, missed) check karta hai."""
    out = _run_cmd(["termux-call-log", "-l", str(limit)])
    try:
        data = json.loads(out)
        logs = []
        for call in data:
            logs.append({
                "name": call.get("name", "Unknown"),
                "phone_number": call.get("phone_number", ""),
                "type": call.get("type", ""),
                "date": call.get("date", ""),
                "duration": call.get("duration", "")
            })
        return logs
    except Exception as e:
        return [{"error": f"Call log error: {e}"}]
