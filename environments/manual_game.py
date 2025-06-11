"""
Manual game interface for Stick Hero
"""
import sys
import os
import pygame

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environments.stick_hero_env import StickHeroEnv
from ui.terminal_ui import Style, print_title, print_status, print_metric, loading_dots

class ManualGameInterface:
    """Interface for manual play"""

    def __init__(self, difficulty="normal"):
        print_title("🎮 Manual Game")

        # Create the environment
        loading_dots("Creating environment")
        self.env = StickHeroEnv(difficulty=difficulty)
        self.clock = pygame.time.Clock()

        # Display configuration
        diff_colors = {"easy": Style.SUCCESS, "normal": Style.WARNING, "hard": Style.ERROR}
        diff_emojis = {"easy": "🟢", "normal": "🟡", "hard": "🔴"}

        print_status(diff_emojis.get(difficulty, "🟡"), "Difficulty", difficulty.upper(), diff_colors.get(difficulty, Style.WHITE))
        print_status("🎮", "Controls", "HOLD MOUSE/SPACE=Grow stick, RELEASE=Place", Style.MUTED)
        print_status("⚠️", "Important", "ESC=Quit, Click Replay button after game over", Style.MUTED)

    def run_game(self):
        """Run manual game"""
        print_title("🎮 Play manually!")
        print(f"\n{Style.PRIMARY}━━━ Good luck! ━━━{Style.RESET}")

        stick_growing = False
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if not self.env.game_over and not self.env.stick_rotated:
                            stick_growing = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        stick_growing = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.env.game_over:
                            # Check replay button
                            if self.env.handle_click(event.pos):
                                print(f"\n{Style.SUCCESS}🔄 New game started!{Style.RESET}")
                        else:
                            if not self.env.stick_rotated:
                                stick_growing = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click release
                        stick_growing = False

            # Update game based on manual input
            if not self.env.game_over:
                if stick_growing and not self.env.stick_rotated:
                    self.env.step(1)  # Grow stick
                elif not stick_growing and self.env.stick_growing:
                    self.env.step(2)  # Place stick
                else:
                    self.env.step(0)  # No action

            # Render game
            self.env.render()
            self.clock.tick(60)

        print(f"\n{Style.SUCCESS}🏁 Thanks for playing!{Style.RESET}")
        print_metric("Final Score", self.env.score, color=Style.SUCCESS if self.env.score >= 5 else Style.WHITE)

        self.env.close()