"""
Terminal UI for Stick Hero AI
"""
import time
import os

class Style:
    """Minimalist and modern style"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Palette
    PRIMARY = '\033[94m'      # Modern blue
    SUCCESS = '\033[92m'      # Green success
    WARNING = '\033[93m'      # Yellow warning
    ERROR = '\033[91m'        # Rouge erreur
    ACCENT = '\033[96m'       # Cyan accent
    MUTED = '\033[90m'        # Gris muted
    WHITE = '\033[97m'        # Blanc clean

def print_title(title):
    """Main title"""
    print(f"\n{Style.PRIMARY}▌{Style.RESET} {Style.BOLD}{title}{Style.RESET}")

def print_subtitle(subtitle):
    """Discrete subtitle"""
    print(f"{Style.MUTED}  {subtitle}{Style.RESET}")

def print_status(icon, message, value="", color=Style.WHITE):
    """Minimalist status line"""
    if value:
        print(f"  {icon} {message}: {color}{value}{Style.RESET}")
    else:
        print(f"  {icon} {color}{message}{Style.RESET}")

def print_metric(label, value, unit="", color=Style.WHITE):
    """Simple and clean metric"""
    print(f"  {label}: {color}{value}{unit}{Style.RESET}")

def loading_dots(message, duration=1):
    """Discrete dots animation"""
    print(f"\n  {message}", end='', flush=True)
    for _ in range(int(duration * 4)):
        print(".", end='', flush=True)
        time.sleep(0.25)
    print(f" {Style.SUCCESS}✓{Style.RESET}")

def progress_line(current, total, label="", width=40):
    """Minimalist progress bar"""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)

    if percent < 0.3:
        color = Style.ERROR
    elif percent < 0.7:
        color = Style.WARNING
    else:
        color = Style.SUCCESS

    status = f"\r  {label} {color}[{bar}]{Style.RESET} {percent*100:5.1f}%"
    print(status, end='', flush=True)

def select_from_list(items, prompt="Choix", show_details=False):
    """Selection in a list with proper display"""
    if not items:
        print_status("❌", "No element available", color=Style.ERROR)
        return None

    print_subtitle(f"{prompt}s available")

    for i, item in enumerate(items):
        if show_details and isinstance(item, dict):
            print(f"  {Style.PRIMARY}{i+1}.{Style.RESET} {item['name']}")
            if 'details' in item:
                print(f"     {Style.MUTED}{item['details']}{Style.RESET}")
        else:
            print(f"  {Style.PRIMARY}{i+1}.{Style.RESET} {item}")

    try:
        choice = int(input(f"\n  {prompt}: ")) - 1
        if 0 <= choice < len(items):
            return choice
        else:
            print_status("❌", "Invalid choice", color=Style.ERROR)
            return None
    except (ValueError, KeyboardInterrupt):
        print_status("❌", "Operation cancelled", color=Style.WARNING)
        return None

def get_input(prompt, default=None, input_type=str):
    """Input with default value"""
    if default is not None:
        full_prompt = f"  {prompt} (default {default}): "
    else:
        full_prompt = f"  {prompt}: "

    try:
        value = input(full_prompt) or default
        if value is None:
            return None
        return input_type(value)
    except ValueError:
        print_status("❌", "Invalid value", color=Style.ERROR)
        return None
    except KeyboardInterrupt:
        print_status("❌", "Operation cancelled", color=Style.WARNING)
        return None

def game_status_line(episode, total, score, action, stick, gap, perfect_zone, current_success_rate=None):
    """Minimalist status line with relevant information"""
    action_color = Style.SUCCESS if action == "Grow" else Style.ACCENT
    score_color = Style.SUCCESS if score >= 3 else Style.WARNING if score >= 1 else Style.WHITE

    # Calculate the precision if we have a placement
    precision_info = ""
    if action == "Place" and perfect_zone > 0:
        # Estimate a success zone around the gap (gap + width/2)
        min_success = gap
        max_success = gap + gap * 0.5  # Approximate success zone
        if min_success <= stick <= max_success:
            zone_width = max_success - min_success
            distance_from_perfect = abs(stick - perfect_zone)
            precision_pct = max(0, 100 - (distance_from_perfect / (zone_width / 2) * 50))
        else:
            precision_pct = 0
        precision_color = Style.SUCCESS if precision_pct >= 80 else Style.WARNING if precision_pct >= 50 else Style.ERROR
        precision_info = f"| Precision: {precision_color}{precision_pct:.0f}%{Style.RESET} "
    elif current_success_rate is not None:
        rate_color = Style.SUCCESS if current_success_rate >= 60 else Style.WARNING if current_success_rate >= 30 else Style.ERROR
        precision_info = f"| Success: {rate_color}{current_success_rate:.0f}%{Style.RESET} "

    print(f"\r  Episode {episode}/{total} | "
          f"Score: {score_color}{score:2d}{Style.RESET} | "
          f"Action: {action_color}{action:<7}{Style.RESET} | "
          f"Stick: {stick:3.0f} | Gap: {gap} {precision_info}",
          end='', flush=True)