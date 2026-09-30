from colorama import init, Fore, Style

init(autoreset=True)

class Colors:
    CYAN = Fore.CYAN + Style.BRIGHT
    GREEN = Fore.GREEN + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    RED = Fore.RED + Style.BRIGHT
    MAGENTA = Fore.MAGENTA + Style.BRIGHT
    WHITE = Fore.WHITE + Style.BRIGHT
    DIM = Style.DIM
    RESET = Style.RESET_ALL

def print_banner():
    width = 50
    print(Colors.CYAN + "═" * width)
    print(Colors.GREEN + "       🚀 SHOONYAONE AUTONOMOUS AGENT AI")
    print(Colors.MAGENTA + "      Think • Plan • Execute • Verify Loop")
    print(Colors.DIM + "          Motorola Edge 40 Neo (Android 15)")
    print(Colors.CYAN + "═" * width)
    print(Colors.YELLOW + "  Tips:")
    print("  • Type commands naturally in Hindi / Hinglish / English")
    print("  • Type 'voice' for Speech-to-Text input")
    print("  • Type 'exit' ya 'quit' band karne ke liye")
    print(Colors.CYAN + "═" * width + "\n")

def print_thought(step: str, detail: str = ""):
    print(f"{Colors.BLUE}[THINK]{Colors.RESET} {step}")
    if detail:
        print(f"       {Colors.DIM}{detail}{Colors.RESET}")

def print_action(action: str, detail: str = ""):
    print(f"{Colors.YELLOW}[EXECUTE]{Colors.RESET} {action}")
    if detail:
        print(f"         {Colors.DIM}{detail}{Colors.RESET}")

def print_verification(status: bool, msg: str):
    icon = "✓" if status else "✗"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}[VERIFY {icon}]{Colors.RESET} {msg}")

def print_agent_response(text: str):
    print(f"\n{Colors.CYAN}ShoonyaOne:{Colors.RESET} {text}\n")

def print_error(msg: str):
    print(f"{Colors.RED}[ERROR] {msg}{Colors.RESET}")
