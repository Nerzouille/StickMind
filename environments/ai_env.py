"""
AI environment for Stick Hero - Simplified interface for fast training
"""
import numpy as np
import random

class StickHeroAIEnv:
    """Stick Hero environment"""

    def __init__(self):
        # Simplified parameters for fast training
        self.gap_min = 30
        self.gap_max = 80
        self.platform_width_min = 15
        self.platform_width_max = 40
        self.stick_grow_speed = 4
        self.max_stick_length = 150

        # Put the game in a reset state
        self.reset()

    def reset(self):
        """Reset the environment"""
        self.score = 0
        self.game_over = False
        self.stick_length = 0
        self.steps_taken = 0

        # Generate a simple level
        self.gap_distance = random.randint(self.gap_min, self.gap_max)
        self.next_platform_width = random.randint(self.platform_width_min, self.platform_width_max)

        # Calculate the success zones
        self.min_stick_for_success = self.gap_distance
        self.max_stick_for_success = self.gap_distance + self.next_platform_width
        self.perfect_stick_length = self.gap_distance + self.next_platform_width // 2

        return self._get_state()

    def step(self, action):
        """
        Simplified actions:
        0: Grow the stick
        1: Place the stick now
        """
        reward = 0
        self.steps_taken += 1

        if self.game_over:
            return self._get_state(), 0, True

        if action == 0:  # Grow the stick
            old_length = self.stick_length
            self.stick_length = min(self.stick_length + self.stick_grow_speed, self.max_stick_length)

            # Immediate rewards to guide the learning
            if self.min_stick_for_success <= self.stick_length <= self.max_stick_for_success:
                # Perfect zone !
                distance_to_perfect = abs(self.stick_length - self.perfect_stick_length)
                if distance_to_perfect <= 3:
                    reward = 5.0  # Very close to perfect
                else:
                    reward = 2.0  # In the success zone
            elif self.stick_length < self.min_stick_for_success:
                # Still too short but progressing
                reward = 0.5
            else:
                # Begins to be too long
                reward = -1.0

            # Strong penalty if really too long
            if self.stick_length >= self.max_stick_length:
                reward = -10.0

        elif action == 1:  # Place the stick
            if self.min_stick_for_success <= self.stick_length <= self.max_stick_for_success:
                # SUCCESS !
                distance_to_perfect = abs(self.stick_length - self.perfect_stick_length)

                if distance_to_perfect <= 2:
                    reward = 100  # Perfect shot !
                elif distance_to_perfect <= 5:
                    reward = 50   # Very good
                else:
                    reward = 25   # Good

                self.score += 1
                # New level
                self._generate_next_level()

            else:
                # FAILURE
                if self.stick_length < self.min_stick_for_success:
                    # Too short
                    shortage = self.min_stick_for_success - self.stick_length
                    reward = -30 - shortage  # The shorter, the more penalized
                else:
                    # Too long
                    overshoot = self.stick_length - self.max_stick_for_success
                    reward = -20 - overshoot * 0.5  # Less penalized than too short

                self.game_over = True

        # Timeout if too many steps (force to place)
        if self.steps_taken >= 30:
            reward = -50
            self.game_over = True

        return self._get_state(), reward, self.game_over

    def _generate_next_level(self):
        """Generate a new level after success"""
        self.stick_length = 0
        self.steps_taken = 0

        # Progressive difficulty very gentle
        difficulty = min(self.score, 10)
        gap_range = self.gap_max - self.gap_min
        self.gap_distance = self.gap_min + random.randint(0, gap_range + difficulty * 2)
        self.gap_distance = min(self.gap_distance, self.gap_max + 20)  # Max limit

        self.next_platform_width = random.randint(self.platform_width_min, self.platform_width_max)

        # Recalculate the success zones
        self.min_stick_for_success = self.gap_distance
        self.max_stick_for_success = self.gap_distance + self.next_platform_width
        self.perfect_stick_length = self.gap_distance + self.next_platform_width // 2

    def _get_state(self):
        """Ultra-simple state for the AI"""
        state = np.array([
            self.gap_distance / 100.0, # Distance to cross
            self.next_platform_width / 50.0, # Target platform width
            self.stick_length / 100.0, # Current stick length
            (self.stick_length - self.min_stick_for_success) / 50.0, # Distance to minimum required (negative if reached)
            (self.max_stick_for_success - self.stick_length) / 50.0, # Distance to maximum allowed (negative if exceeded)
            self.score / 10.0, # Current score
        ], dtype=np.float32)

        return state

    def get_state_size(self):
        return 6  # Simplified state

    def get_action_size(self):
        return 2  # Only grow or place