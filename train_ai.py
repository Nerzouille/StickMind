#!/usr/bin/env python3
"""
Main script to train the AI Stick Hero
"""
import sys
import os

# Add the directories to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from training.trainer import train_agent, test_agent, list_models
from ui.terminal_ui import Style, print_title, print_subtitle, print_status, get_input, select_from_list

def main():
    """Main menu to train the AI"""
    print_title("🎮 Stick Hero IA - Training")

    print(f"\n  {Style.PRIMARY}1.{Style.RESET} Train a new agent")
    print(f"  {Style.PRIMARY}2.{Style.RESET} Test an existing agent")

    choice = get_input("Choix")
    if choice is None:
        return

    if choice == "1":
        episodes = get_input("Number of episodes", default=1000, input_type=int)
        if episodes is not None:
            train_agent(episodes)

    elif choice == "2":
        models = list_models()
        if not models:
            print_status("❌", "No model found", color=Style.ERROR)
            print_status("💡", "Train an agent first", color=Style.WARNING)
            return

        model_idx = select_from_list(models, "Model", show_details=True)
        if model_idx is not None:
            test_agent(models[model_idx]['name'])

    else:
        print_status("❌", "Invalid choice", color=Style.ERROR)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Style.WARNING}Program interrupted{Style.RESET}")
    except Exception as e:
        print_status("❌", f"Error: {e}", color=Style.ERROR)