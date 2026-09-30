#!/usr/bin/env python3
"""
ShoonyaOne - Autonomous Agent AI for Android
Entry point for interactive CLI, voice mode, and one-shot commands.
"""

import sys
import os

from shoonya.ui import print_banner, Colors, print_agent_response, print_error
from shoonya.agent import ShoonyaAgent
from shoonya.tools.voice import speak, listen_speech

def run_interactive(agent: ShoonyaAgent):
    print_banner()
    speak("ShoonyaOne agent online. All systems ready.")

    while True:
        try:
            prompt_str = f"{Colors.GREEN}ShoonyaOne > {Colors.RESET}"
            user_input = input(prompt_str).strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "band karo", "alvida"]:
                farewell = "Alvida Vikash. ShoonyaOne shutting down."
                print(f"{Colors.YELLOW}{farewell}{Colors.RESET}")
                speak(farewell)
                break

            # Voice command trigger
            if user_input.lower() in ["voice", "speak", "bolke", "mic"]:
                print(f"{Colors.CYAN}Listening... Kahiye Vikash...{Colors.RESET}")
                spoken_text = listen_speech()
                if spoken_text:
                    print(f"{Colors.GREEN}Aapne kaha:{Colors.RESET} {spoken_text}")
                    agent.process(spoken_text)
                else:
                    print(f"{Colors.YELLOW}Koi aawaz detect nahi hui.{Colors.RESET}")
                continue

            # Process natural language task through autonomous agent loop
            agent.process(user_input)

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.YELLOW}ShoonyaOne stopped. Goodbye!{Colors.RESET}")
            break
        except Exception as e:
            print_error(f"Unexpected error: {e}")

def main():
    agent = ShoonyaAgent()

    # If arguments are passed, execute as one-shot command
    # e.g.: python3 main.py "battery status batao aur torch on karo"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--voice":
            print(f"{Colors.CYAN}Voice input mode active...{Colors.RESET}")
            spoken_text = listen_speech()
            if spoken_text:
                print(f"{Colors.GREEN}Command:{Colors.RESET} {spoken_text}")
                agent.process(spoken_text)
            else:
                print(f"{Colors.YELLOW}Koi voice input nahi mila.{Colors.RESET}")
        else:
            query = " ".join(sys.argv[1:])
            print(f"{Colors.CYAN}Executing task:{Colors.RESET} {query}")
            agent.process(query)
    else:
        run_interactive(agent)

if __name__ == "__main__":
    main()
