#!/usr/bin/env python3
"""
Main script to make the AI play the Stick Hero game
"""
import sys
import os
import pygame
import time
import numpy as np

# Add the directories to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from environments.stick_hero_env import StickHeroEnv
from environments.ai_env import StickHeroAIEnv
from environments.manual_game import ManualGameInterface
from agents.dqn_agent import DQNAgent
from training.trainer import list_models
from ui.terminal_ui import (Style, print_title, print_subtitle, print_status,
                           print_metric, loading_dots, get_input, select_from_list,
                           game_status_line)

class AIGameInterface:
    """Interface to make the AI play"""

    def __init__(self, model_path, difficulty="normal"):
        print_title("🤖 AI initialization")

        # Load the AI agent
        loading_dots("Loading the model")
        self.ai_agent = DQNAgent(6, 2)
        try:
            self.ai_agent.load(model_path)
            self.ai_agent.epsilon = 0
            print_status("✅", "Model", model_path.split('/')[-1], Style.SUCCESS)
        except Exception as e:
            print_status("❌", "Error", str(e), Style.ERROR)
            raise

        # Create the environments
        loading_dots("Creating environments")
        self.visual_env = StickHeroEnv(difficulty=difficulty)
        self.ai_env = StickHeroAIEnv()
        self.clock = pygame.time.Clock()

        # Display the configuration
        diff_colors = {"easy": Style.SUCCESS, "normal": Style.WARNING, "hard": Style.ERROR}
        diff_emojis = {"easy": "🟢", "normal": "🟡", "hard": "🔴"}

        print_status(diff_emojis.get(difficulty, "🟡"), "Difficulty", difficulty.upper(), diff_colors.get(difficulty, Style.WHITE))
        print_status("🎮", "Controls", "ESC=Quit, SPACE=Pause", Style.MUTED)

    def sync_environments(self):
        """Synchronize the visual environment with the AI environment"""
        if hasattr(self.visual_env, 'platforms') and len(self.visual_env.platforms) > self.visual_env.current_platform + 1:
            current_plat = self.visual_env.platforms[self.visual_env.current_platform]
            next_plat = self.visual_env.platforms[self.visual_env.current_platform + 1]

            gap_distance = next_plat[0] - (current_plat[0] + current_plat[2])
            next_platform_width = next_plat[2]

            self.ai_env.gap_distance = gap_distance
            self.ai_env.next_platform_width = next_platform_width
            self.ai_env.stick_length = self.visual_env.stick_length
            self.ai_env.score = self.visual_env.score
            self.ai_env.game_over = self.visual_env.game_over

            self.ai_env.min_stick_for_success = gap_distance
            self.ai_env.max_stick_for_success = gap_distance + next_platform_width
            self.ai_env.perfect_stick_length = gap_distance + next_platform_width // 2

    def run_game(self, episodes=3, speed=1.0):
        """Run the game with the AI"""
        print_title(f"🎮 AI plays {episodes} games")

        all_scores = []
        episode_results = []

        for episode in range(episodes):
            print(f"\n{Style.PRIMARY}━━━ Game {episode + 1}/{episodes} ━━━{Style.RESET}")

            # Reset
            self.visual_env.reset()
            self.ai_env.reset()

            paused = False
            steps = 0
            max_steps = 10000
            total_reward = 0
            last_status_update = 0

            while not self.visual_env.game_over and steps < max_steps:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print(f"\n{Style.ERROR}Game closed{Style.RESET}")
                        self.visual_env.close()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            print(f"\n{Style.ERROR}Exit requested{Style.RESET}")
                            self.visual_env.close()
                            return
                        elif event.key == pygame.K_SPACE:
                            paused = not paused
                            status = "⏸️ PAUSE" if paused else "▶️ RESUME"
                            print(f"\n{Style.WARNING}{status}{Style.RESET}")

                if not paused:
                    # Synchronize and decide
                    self.sync_environments()
                    ai_state = self.ai_env._get_state()
                    ai_action = self.ai_agent.act(ai_state)

                    action_names = ["Grow", "Place"]
                    current_action = action_names[ai_action]

                    # Calculate the current success rate
                    current_success_rate = None
                    if episode_results:
                        current_success_rate = (sum(episode_results) / len(episode_results)) * 100

                    # Display the status
                    if steps - last_status_update >= 20:
                        game_status_line(
                            episode + 1, episodes,
                            self.visual_env.score,
                            current_action,
                            self.visual_env.stick_length,
                            self.ai_env.gap_distance,
                            self.ai_env.perfect_stick_length,
                            current_success_rate
                        )
                        last_status_update = steps

                    # Execute the action
                    if ai_action == 0:  # Grow
                        if not self.visual_env.stick_growing and not self.visual_env.stick_rotated:
                            self.visual_env.stick_growing = True
                    elif ai_action == 1:  # Place
                        if self.visual_env.stick_growing:
                            self.visual_env.stick_growing = False
                            if not self.visual_env.stick_rotated:
                                self.visual_env.stick_rotating = True
                                # Calculate the precision based on the success zone
                                stick = self.visual_env.stick_length
                                min_success = self.ai_env.min_stick_for_success
                                max_success = self.ai_env.max_stick_for_success
                                perfect = self.ai_env.perfect_stick_length

                                if min_success <= stick <= max_success:
                                    # In the success zone, calculate the proximity to the perfect point
                                    zone_width = max_success - min_success
                                    distance_from_perfect = abs(stick - perfect)
                                    precision_pct = max(0, 100 - (distance_from_perfect / (zone_width / 2) * 50))
                                else:
                                    # Outside the success zone, precision = 0
                                    precision_pct = 0

                                precision_color = Style.SUCCESS if precision_pct >= 80 else Style.WARNING if precision_pct >= 50 else Style.ERROR
                                status = "SUCCESS" if min_success <= stick <= max_success else "FAILURE"
                                status_color = Style.SUCCESS if min_success <= stick <= max_success else Style.ERROR

                                print(f"\n{Style.ACCENT}🎯 Placement! Stick: {stick:.0f} | "
                                      f"Zone: {min_success:.0f}-{max_success:.0f} | "
                                      f"Precision: {precision_color}{precision_pct:.0f}%{Style.RESET} | "
                                      f"{status_color}{status}{Style.RESET}")

                    # Update the game
                    if self.visual_env.stick_growing:
                        _, reward, _ = self.visual_env.step(1)
                    elif self.visual_env.stick_rotating or self.visual_env.stick_rotated:
                        _, reward, _ = self.visual_env.step(2)
                    else:
                        _, reward, _ = self.visual_env.step(0)

                    total_reward += reward

                # Display the game
                self.visual_env.render()
                self.clock.tick(int(60 * speed))
                steps += 1

            # Episode result
            print()

            if steps >= max_steps:
                print_status("⚠️", "Timeout", f"{max_steps} steps", Style.WARNING)

            # Save the result
            success = not self.visual_env.game_over and self.visual_env.score > 0
            episode_results.append(1 if success else 0)

            # Display the result
            result_icon = "🎉" if success else "💀"
            result_color = Style.SUCCESS if success else Style.ERROR
            result_text = "SUCCESS" if success else "FAILURE"

            print_status(result_icon, result_text, color=result_color)
            print_metric("Score", self.visual_env.score, color=Style.SUCCESS if self.visual_env.score >= 3 else Style.WHITE)
            print_metric("Reward", f"{total_reward:+.1f}", color=Style.ACCENT)

            all_scores.append(self.visual_env.score)

            # Pause between episodes
            if episode < episodes - 1:
                print(f"\n{Style.MUTED}  Next game in 2s...{Style.RESET}")
                time.sleep(2)

        # Final statistics
        print_title("📊 Final results")
        avg_score = np.mean(all_scores)
        max_score = max(all_scores) if all_scores else 0
        success_rate = (np.array(all_scores) > 0).mean() * 100 if all_scores else 0

        avg_color = Style.SUCCESS if avg_score >= 3 else Style.WARNING if avg_score >= 1 else Style.WHITE
        success_color = Style.SUCCESS if success_rate >= 60 else Style.WARNING if success_rate >= 30 else Style.ERROR

        print_metric("Games played", episodes)
        print_metric("Average score", f"{avg_score:.1f}", color=avg_color)
        print_metric("Max score", max_score, color=Style.SUCCESS if max_score >= 5 else Style.WHITE)
        print_metric("Success rate", f"{success_rate:.0f}%", color=success_color)
        print_metric("Scores", str(all_scores), color=Style.MUTED)

        print(f"\n{Style.SUCCESS}🏁 Finished! Thank you for watching the AI play{Style.RESET}")
        time.sleep(1)
        self.visual_env.close()

def main():
    """Main menu for Stick Hero game"""
    print_title("🎮 Stick Hero - Game")
    print_subtitle("Choose your playing mode")

    # Mode selection
    modes = ["🤖 Watch AI play", "🎮 Play manually"]
    mode_idx = select_from_list(modes, "Mode")
    if mode_idx is None:
        return

    print_subtitle("Configuration")

    # Difficulty choice
    difficulties = ["🟢 Easy", "🟡 Normal", "🔴 Hard"]
    diff_idx = select_from_list(difficulties, "Difficulty")
    if diff_idx is None:
        diff_idx = 1  # Normal by default

    difficulty_map = {0: "easy", 1: "normal", 2: "hard"}
    difficulty = difficulty_map[diff_idx]

    if mode_idx == 0:  # AI mode
        # Search for models
        models = list_models()
        if not models:
            print_status("❌", "No model found", color=Style.ERROR)
            print_status("💡", "Train an agent with train_ai.py", color=Style.WARNING)
            return

        model_idx = select_from_list(models, "Model", show_details=True)
        if model_idx is None:
            return

        episodes = get_input("Games", default=3, input_type=int) or 3
        speed = get_input("Speed", default=1.0, input_type=float) or 1.0

        loading_dots("Preparing AI game")

        try:
            ai_interface = AIGameInterface(models[model_idx]['name'], difficulty)
            ai_interface.run_game(episodes, speed)
        except Exception as e:
            print_status("❌", f"Error: {e}", color=Style.ERROR)

    elif mode_idx == 1:  # Manual mode
        loading_dots("Preparing manual game")

        try:
            manual_interface = ManualGameInterface(difficulty)
            manual_interface.run_game()
        except Exception as e:
            print_status("❌", f"Error: {e}", color=Style.ERROR)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Style.WARNING}Operation cancelled{Style.RESET}")
    except Exception as e:
        print_status("❌", f"Error: {e}", color=Style.ERROR)