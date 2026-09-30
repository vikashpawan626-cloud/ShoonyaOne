import subprocess
import re
import shutil

def speak(text: str, rate: float = 1.1) -> bool:
    """Termux TTS ke zariye voice me output bolta hai."""
    try:
        clean_txt = re.sub(r'[*_#`]', '', text)
        cmd = ["termux-tts-speak", "-r", str(rate), clean_txt]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def listen_speech() -> str:
    """Termux Speech-to-text popup open karta hai aur user ki aawaz sun kar text return karta hai."""
    try:
        cmd = ["termux-speech-to-text"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        text = result.stdout.strip()
        return text
    except Exception as e:
        return ""
