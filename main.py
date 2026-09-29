import os
import sys
import json
import logging
import subprocess
from colorama import init, Fore, Style
import google.generativeai as genai
from duckduckgo_search import DDGS

# Colorama aur Logging setup
init(autoreset=True)
logging.basicConfig(
    filename="shoonyaone.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print(Fore.RED + "Error: GEMINI_API_KEY environment variable set nahi hai.")
    print(Fore.YELLOW + "Pehle command chalayein: export GEMINI_API_KEY='aapki_api_key'")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Hardware / Termux API Tools ---

def run_termux_command(cmd_list):
    """Termux-API commands ko safely run karta hai."""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_battery_status():
    """Battery details check karta hai."""
    out = run_termux_command(["termux-battery-status"])
    try:
        data = json.loads(out)
        return f"Battery: {data.get('percentage')}% ({data.get('status')})"
    except Exception:
        return "Battery details retrieve nahi ho payi."

def toggle_torch(state: bool):
    """Torch/Flashlight ON ya OFF karta hai."""
    arg = "on" if state else "off"
    run_termux_command(["termux-torch", arg])
    return f"Torch {arg.upper()} ho gaya."

def search_web(query: str):
    """DuckDuckGo se live web search karta hai."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                return summary
            return "Koi relevant information nahi mili."
    except Exception as e:
        return f"Search error: {e}"

# --- Main Assistant Loop ---

def shoonya_loop():
    print(Fore.CYAN + Style.BRIGHT + "=" * 45)
    print(Fore.GREEN + Style.BRIGHT + "       🚀 ShoonyaOne AI Assistant Active       ")
    print(Fore.CYAN + Style.BRIGHT + "=" * 45)
    print(Fore.YELLOW + "Type 'exit' ya 'quit' band karne ke liye.\n")

    chat = model.start_chat(history=[])

    system_instruction = (
        "You are ShoonyaOne, an advanced autonomous personal assistant running on Android/Termux. "
        "You have access to terminal commands, web search, and hardware tools. "
        "Keep responses direct, helpful, and concise."
    )

    while True:
        try:
            user_input = input(Fore.BLUE + Style.BRIGHT + "ShoonyaOne > " + Fore.WHITE).strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print(Fore.YELLOW + "ShoonyaOne shutting down. Goodbye!")
                break

            # Local hardware commands
            if "battery" in user_input.lower():
                status = get_battery_status()
                print(Fore.MAGENTA + f"⚡ {status}")
                continue

            elif "torch on" in user_input.lower():
                print(Fore.YELLOW + toggle_torch(True))
                continue

            elif "torch off" in user_input.lower():
                print(Fore.YELLOW + toggle_torch(False))
                continue

            elif user_input.lower().startswith("search "):
                q = user_input[7:]
                print(Fore.CYAN + f"Searching web for: {q}...")
                results = search_web(q)
                print(Fore.LIGHTWHITE_EX + results)
                continue

            # General AI Chat Response
            response = chat.send_message(f"{system_instruction}\nUser: {user_input}")
            print(Fore.GREEN + f"\nShoonyaOne: {response.text}\n")
            logging.info(f"User: {user_input} | Response: {response.text}")

        except KeyboardInterrupt:
            print("\n" + Fore.YELLOW + "Interrupted. Exiting...")
            break
        except Exception as err:
            print(Fore.RED + f"Error: {err}")
            logging.error(f"Error: {err}")

if __name__ == "__main__":
    shoonya_loop()
