import os
import sys
import json
import logging
import datetime
import traceback
from .config import GEMINI_API_KEY, DEFAULT_MODEL, FALLBACK_MODELS, LOG_FILE, HISTORY_FILE, USER_NAME
from .ui import Colors, print_thought, print_action, print_verification, print_agent_response, print_error
from .prompts import SYSTEM_INSTRUCTION
from .tools import TOOL_MAP, ALL_TOOLS
from .tools.voice import speak
from .tools.device import get_battery_status, set_torch, set_brightness, set_volume
from .tools.comms import make_phone_call

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ShoonyaAgent:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.client = None
        self.model = DEFAULT_MODEL
        self.chat_session = None
        self._init_gemini()

    def _init_gemini(self):
        """Initializes Google GenAI client and chat session."""
        if not self.api_key:
            logging.warning("GEMINI_API_KEY is not set.")
            return

        try:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=self.api_key)
            self._create_chat_session(self.model)
        except ImportError:
            logging.warning("google-genai package not found. Agent in local mode.")
        except Exception as e:
            logging.error(f"Failed to init Gemini client: {e}")

    def _create_chat_session(self, model_name: str):
        """Creates a stateful chat session with full Automatic Function Calling."""
        from google.genai import types
        try:
            self.chat_session = self.client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3,
                    tools=ALL_TOOLS
                )
            )
            self.model = model_name
            logging.info(f"Chat session started with model '{model_name}' and {len(ALL_TOOLS)} tools.")
            return True
        except Exception as e:
            logging.error(f"Failed to create chat session with {model_name}: {e}")
            return False

    def log_history(self, user_msg: str, agent_msg: str):
        """Chat history txt file me append karta hai."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {USER_NAME}: {user_msg}\n")
                f.write(f"[{timestamp}] ShoonyaOne: {agent_msg}\n")
        except Exception as e:
            logging.error(f"Failed to write chat history: {e}")

    def _fast_local_route(self, text: str):
        """
        Urgent / direct single-step hardware commands bina LLM latency ke execute karta hai.
        Zero quota usage aur instant response.
        """
        low = text.lower().strip()

        # 1. Battery check
        if low in ["battery", "battery status", "battery percent", "charge kitna hai", "battery kitni hai"]:
            print_thought("Fast Route: Checking device battery metrics.")
            print_action("termux-battery-status")
            res = get_battery_status()
            if res.get("success"):
                pct = res.get("percentage")
                stat = res.get("status")
                temp = res.get("temperature")
                print_verification(True, f"Battery: {pct}% | Status: {stat} | Temp: {temp}°C")
                return f"Battery {pct} percent hai ({stat}). Health bilkul sahi hai."
            return "Battery status retrieve nahi ho paya."

        # 2. Torch control
        if low in ["torch on", "flashlight on", "torch chalu karo", "light on"]:
            print_thought("Fast Route: Turning on flashlight.")
            print_action("termux-torch on")
            set_torch(True)
            print_verification(True, "Torch is now ON")
            return "Torch on kar di hai, Vikash."

        if low in ["torch off", "flashlight off", "torch band karo", "light off"]:
            print_thought("Fast Route: Turning off flashlight.")
            print_action("termux-torch off")
            set_torch(False)
            print_verification(True, "Torch is now OFF")
            return "Torch off kar di hai."

        # 3. Direct call
        if low.startswith("call "):
            target = text[5:].strip()
            print_thought(f"Fast Route: Resolving call for '{target}'.")
            print_action(f"termux-telephony-call -> {target}")
            res = make_phone_call(target)
            if res.get("success"):
                print_verification(True, f"Calling {res.get('name')} ({res.get('number')})")
                return f"{res.get('name')} ko call lagaya ja raha hai."
            else:
                print_verification(False, res.get("error", "Call failed"))
                return res.get("error", f"{target} contact list me nahi mila.")

        return None

    def _chat_with_fallback(self, user_prompt: str) -> str:
        """Sends user message to Gemini chat session with automatic fallback on failure."""
        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        last_error = ""

        for model_name in models_to_try:
            if not self.chat_session or self.model != model_name:
                ok = self._create_chat_session(model_name)
                if not ok:
                    continue

            try:
                print_thought(f"Analyzing intent with {model_name}...")
                response = self.chat_session.send_message(user_prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                err_msg = str(e)
                last_error = err_msg
                logging.warning(f"Model {model_name} error: {err_msg}")
                self.chat_session = None  # Reset session on failure

        # If all models exhausted
        if "429" in last_error:
            return "API quota limit reach ho gayi hai Vikash. Local device tools normal kaam kar rahe hain."
        if "503" in last_error:
            return "Server par temporary demand high hai. Kripya 1 minute baad try karein."
        return f"Process karne me dikkat aayi: {last_error[:70]}"

    def process(self, user_input: str) -> str:
        """Main processing entry point."""
        text = user_input.strip()
        if not text:
            return ""

        # Step 1: Fast Local Route for single-word hardware actions
        fast_res = self._fast_local_route(text)
        if fast_res is not None:
            print_agent_response(fast_res)
            speak(fast_res)
            self.log_history(text, fast_res)
            return fast_res

        # Step 2: Autonomous AI Agent Loop
        if self.client:
            ans = self._chat_with_fallback(text)
        else:
            ans = "Gemini AI connect nahi hai, lekin local hardware commands active hain."

        print_agent_response(ans)
        speak(ans)
        self.log_history(text, ans)
        return ans
