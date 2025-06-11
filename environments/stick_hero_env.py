import pygame
import sys
import random
import numpy as np

class StickHeroEnv:
    def __init__(self, width=800, height=600, difficulty="normal"):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Stick Hero")

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)

        # Difficulty configuration
        self.difficulty = difficulty
        self._set_difficulty_params()

        # Fixed parameters
        self.platform_height = 20
        self.stick_width = 8
        self.hero_size = 30
        self.stick_speed = 5
        self.hero_speed = 6
        self.fall_speed = 12
        self.stick_angle = 0
        self.stick_rotating = False
        self.falling = False
        self.fall_y = 0

        # Camera system
        self.camera_x = 0
        self.camera_speed = 5
        self.camera_target_x = 0

        # Replay button
        self.replay_button = pygame.Rect(self.width//2 - 50, self.height//2 + 20, 100, 40)

        # Game state
        self.reset()

    def _set_difficulty_params(self):
        """Configure the parameters according to the difficulty"""
        if self.difficulty == "facile":
            # Easy mode: wider platforms, smaller gaps
            self.platform_width_min = 60  # Wider platforms
            self.platform_width_max = 120
            self.base_gap_min = 100  # Smaller gaps
            self.base_gap_max = 200
            self.difficulty_progression = 0.02  # Slower progression
            print("🟢 EASY mode: Wider platforms (60-120px), Smaller gaps (100-200px)")

        elif self.difficulty == "normal":
            # Normal mode: balanced
            self.platform_width_min = 40
            self.platform_width_max = 90
            self.base_gap_min = 120
            self.base_gap_max = 250
            self.difficulty_progression = 0.035  # Moderate progression
            print("🟡 NORMAL mode: Medium platforms (40-90px), Moderate gaps (120-250px)")

        elif self.difficulty == "hard":
            # Hard mode: very hard
            self.platform_width_min = 30
            self.platform_width_max = 80
            self.base_gap_min = 150
            self.base_gap_max = 300
            self.difficulty_progression = 0.05
            print("🔴 HARD mode: Small platforms (30-80px), Large gaps (150-300px)")

        else:  # default = normal
            self.difficulty = "normal"
            self._set_difficulty_params()
            return

    def reset(self):
        self.platforms = []
        self.current_platform = 0
        self.stick_length = 0
        self.stick_growing = False
        self.stick_rotated = False
        self.stick_angle = 0
        self.stick_rotating = False
        self.falling = False
        self.fall_y = 0
        self.score = 0
        self.game_over = False
        self.camera_x = 0
        self.camera_target_x = 0

        # Create the initial platforms
        self._generate_initial_platforms()
        self.hero_x = self.platforms[0][0] + self.platforms[0][2] - self.hero_size // 2
        self.hero_y = self.platforms[0][1] - self.hero_size

    def _generate_initial_platforms(self):
        """Generate the initial platforms with difficulty adapted"""
        self.platforms = []
        x = 50
        y = self.height - 100

        # First platform (bigger to start)
        if self.difficulty == "facile":
            width = random.randint(100, 140)
        else:
            width = random.randint(60, 100)
        self.platforms.append((x, y, width, "démarrage"))

        # Generate the first platforms with reduced difficulty
        original_score = self.score
        self.score = 0

        for i in range(4):
            # The first two are a bit easier
            if i < 2:
                self.score = -2  # Negative difficulty = easier
            else:
                self.score = i - 2  # Gradual progression
            self._add_new_platform()

        self.score = original_score  # Restore the original score

    def _add_new_platform(self):
        """Add a new platform at the end with progressive difficulty"""
        if not self.platforms:
            return

        last_platform = self.platforms[-1]
        last_x = last_platform[0] + last_platform[2]

        # Calculate the progressive difficulty based on the score
        difficulty_multiplier = 1 + (self.score * self.difficulty_progression)

        # Calculate the gap with progressive difficulty
        gap_min = int(self.base_gap_min * difficulty_multiplier)
        gap_max = int(self.base_gap_max * difficulty_multiplier)

        # Add extreme variability sometimes (very distant platforms)
        if random.random() < 0.15:  # 15% chance of having an extreme gap
            gap_max = int(gap_max * 1.5)

        # Ensure gap_max is always >= gap_min before calling randint
        effective_gap_max = max(gap_min, min(gap_max, 500))
        gap = random.randint(gap_min, effective_gap_max)

        # Calculate the width with progressive reduction
        width_reduction = min(0.3, self.score * 0.02)  # Max reduction of 30%
        min_width = max(25, int(self.platform_width_min * (1 - width_reduction)))
        max_width = max(min_width + 10, int(self.platform_width_max * (1 - width_reduction)))

        # Special platform types based on the score
        platform_type = random.random()

        if self.score > 3 and platform_type < 0.15:  # 15% - Ultra-small platforms
            min_width = max(15, min_width - 20)
            max_width = max(min_width + 3, 35)
            width = random.randint(min_width, max_width)
        elif self.score > 7 and platform_type < 0.25:  # 10% - Tiny platforms
            width = random.randint(12, 25)
        elif platform_type < 0.4:  # 15% - Small platforms
            min_width = max(20, min_width - 15)
            max_width = max(min_width + 5, max_width - 20)
            # Ensure max_width is always >= min_width
            max_width = max(max_width, min_width)
            width = random.randint(min_width, max_width)
        else:  # 60% - Normal platforms
            # Ensure max_width is always >= min_width
            max_width = max(max_width, min_width)
            width = random.randint(min_width, max_width)

        y = self.height - 100

        # Add the platform with a type for the rendering
        platform_size_category = "normale"
        if width <= 20:
            platform_size_category = "tiny"
        elif width <= 35:
            platform_size_category = "ultra-small"
        elif width <= 50:
            platform_size_category = "small"

        self.platforms.append((last_x + gap, y, width, platform_size_category))

        # Debug info to see the progression
        if self.score > 0 and self.score % 5 == 0:
            print(f"📈 Score {self.score}: Gap={gap}, Width={width}, Difficulty={difficulty_multiplier:.2f}")

    def _update_camera(self):
        """Update the camera position to keep the hero visible and the platforms visible"""
        if self.current_platform < len(self.platforms):
            # Desired hero position on the screen (1/4 of the width from the left)
            desired_hero_screen_x = self.width // 4

            # Calculate the target camera position based on the hero position
            target_x = self.hero_x - desired_hero_screen_x

            # Ensure the next platform is completely visible
            if self.current_platform + 1 < len(self.platforms):
                next_platform = self.platforms[self.current_platform + 1]
                next_platform_end = next_platform[0] + next_platform[2]

                # The next platform must be visible with a margin
                min_camera_for_visibility = next_platform_end - self.width + 100

                # Use the minimum to ensure visibility
                target_x = max(target_x, min_camera_for_visibility)

            # Never go negative
            self.camera_target_x = max(0, target_x)

            # Smooth camera animation
            if abs(self.camera_x - self.camera_target_x) > 1:
                self.camera_x += (self.camera_target_x - self.camera_x) * 0.1

    def step(self, action):
        reward = 0
        done = False
        if self.game_over:
            return self._get_state(), reward, True

        # Stick growth management
        if action == 1 and not self.stick_growing and not self.stick_rotated:
            self.stick_growing = True
        elif action == 2 and self.stick_growing:
            self.stick_growing = False
            self.stick_rotating = True

        if self.stick_growing:
            self.stick_length += self.stick_speed

        # Stick rotation animation
        if self.stick_rotating:
            self.stick_angle += 8
            if self.stick_angle >= 90:
                self.stick_angle = 90
                self.stick_rotated = True
                self.stick_rotating = False

        # Hero movement on the stick
        if self.stick_rotated and not self.falling:
            self.hero_x += self.hero_speed
            stick_tip_x = self._stick_tip_x()
            next_plat = self.platforms[self.current_platform + 1]

            if self.hero_x >= stick_tip_x:
                plat_x, plat_y, plat_width = next_plat[0], next_plat[1], next_plat[2]
                if plat_x <= stick_tip_x <= plat_x + plat_width:
                    self.current_platform += 1
                    self.score += 1
                    self._prepare_next_round()
                    reward = 1
                else:
                    self.falling = True

        # Fall animation
        if self.falling:
            self.hero_y += self.fall_speed
            if self.hero_y > self.height:
                self.game_over = True
                done = True
                reward = -10

        # Update the camera
        self._update_camera()

        return self._get_state(), reward, done

    def _prepare_next_round(self):
        # Reposition the hero
        current_plat = self.platforms[self.current_platform]
        self.hero_x = current_plat[0] + current_plat[2] - self.hero_size // 2
        self.hero_y = current_plat[1] - self.hero_size

        # Reset the stick
        self.stick_length = 0
        self.stick_angle = 0
        self.stick_rotated = False
        self.stick_growing = False
        self.stick_rotating = False
        self.falling = False
        self.fall_y = 0

        # Generate new platforms if necessary (more in advance)
        while len(self.platforms) - self.current_platform < 5:
            self._add_new_platform()

    def _stick_base(self):
        plat_x, plat_y, plat_width = self.platforms[self.current_platform][0], self.platforms[self.current_platform][1], self.platforms[self.current_platform][2]
        return plat_x + plat_width, plat_y

    def _stick_tip_x(self):
        base_x, base_y = self._stick_base()
        if self.stick_angle < 90:
            return base_x
        else:
            return base_x + self.stick_length

    def _get_state(self):
        current_platform = self.platforms[self.current_platform]
        next_platform = self.platforms[self.current_platform + 1] if self.current_platform + 1 < len(self.platforms) else None

        state = {
            'hero_x': self.hero_x,
            'hero_y': self.hero_y,
            'stick_length': self.stick_length,
            'stick_angle': self.stick_angle,
            'current_platform_x': current_platform[0],
            'next_platform_x': next_platform[0] if next_platform else None,
            'gap': next_platform[0] - (current_platform[0] + current_platform[2]) if next_platform else None
        }
        return state

    def render(self):
        self.screen.fill(self.WHITE)

        # Draw the platforms (with camera offset)
        for i, platform in enumerate(self.platforms):
            x, y, width = platform[0], platform[1], platform[2]
            screen_x = x - self.camera_x
            if -width <= screen_x <= self.width:  # Only draw the visible platforms
                pygame.draw.rect(self.screen, self.BLACK,
                               (screen_x, y, width, self.platform_height))

                # Add a perfect zone visible only on the next platform
                if i == self.current_platform + 1 and width > 15:  # Next platform and wide enough
                    perfect_zone_width = min(15, width // 3)  # Perfect zone = 1/3 of the width or 15px max
                    perfect_zone_x = screen_x + width // 2 - perfect_zone_width // 2
                    perfect_zone_y = y - 3  # Slightly above

                    # Small green line to indicate the perfect zone
                    pygame.draw.rect(self.screen, self.GREEN,
                                   (perfect_zone_x, perfect_zone_y, perfect_zone_width, 3))

        # Draw the stick
        base_x, base_y = self._stick_base()
        screen_base_x = base_x - self.camera_x
        if self.stick_length > 0:
            if not self.stick_rotated and not self.stick_rotating:
                pygame.draw.rect(self.screen, self.BLUE,
                    (screen_base_x - self.stick_width // 2, base_y - self.stick_length,
                     self.stick_width, self.stick_length))
            else:
                angle_rad = np.radians(self.stick_angle)
                end_x = screen_base_x + self.stick_length * np.sin(angle_rad)
                end_y = base_y - self.stick_length * np.cos(angle_rad)
                pygame.draw.line(self.screen, self.BLUE,
                               (screen_base_x, base_y), (end_x, end_y), self.stick_width)

        # Draw the hero
        screen_hero_x = self.hero_x - self.camera_x
        pygame.draw.rect(self.screen, self.RED,
            (screen_hero_x - self.hero_size // 2, self.hero_y,
             self.hero_size, self.hero_size))

        # Display the score and the difficulty
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)

        score_text = font.render(f'Score: {self.score}', True, self.BLACK)
        self.screen.blit(score_text, (10, 10))

        # Display the difficulty level
        difficulty_level = 1 + (self.score * self.difficulty_progression)
        diff_text = small_font.render(f'Difficulty: {difficulty_level:.1f}x ({self.difficulty.upper()})', True, self.BLACK)
        self.screen.blit(diff_text, (10, 50))

        # Display the next platform info (top right)
        if self.current_platform + 1 < len(self.platforms) and not self.game_over:
            current_plat = self.platforms[self.current_platform]
            next_plat = self.platforms[self.current_platform + 1]
            gap = next_plat[0] - (current_plat[0] + current_plat[2])
            width = next_plat[2]

            info_text = small_font.render(f'Gap: {gap} | Width: {width}', True, (120, 120, 120))
            text_rect = info_text.get_rect()
            text_rect.topright = (self.width - 10, 10)
            self.screen.blit(info_text, text_rect)

        if self.game_over:
            over_text = font.render('Game Over', True, self.RED)
            self.screen.blit(over_text, (self.width // 2 - 80, self.height // 2 - 20))

            pygame.draw.rect(self.screen, self.GREEN, self.replay_button)
            replay_text = font.render('Replay', True, self.BLACK)
            text_rect = replay_text.get_rect(center=self.replay_button.center)
            self.screen.blit(replay_text, text_rect)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.game_over and self.replay_button.collidepoint(pos):
            self.reset()
            return True
        return False

    def close(self):
        pygame.quit()
        sys.exit()