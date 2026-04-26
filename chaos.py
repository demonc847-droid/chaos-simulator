"""Random rule-changing system for Chaos Simulator.

The chaos engine makes the simulation less predictable by changing one rule
every 30-60 seconds. It keeps the rule effects small and named clearly so the
player can understand what changed.
"""

import random

import pygame

from settings import (
    CHAOS_BORDER_COLOR,
    CHAOS_MAX_SECONDS,
    CHAOS_MESSAGE_SECONDS,
    CHAOS_MIN_SECONDS,
    CHAOS_PANEL_COLOR,
    CHAOS_TEXT_COLOR,
)


class ChaosEngine:
    """Stores the current chaos rule and chooses a new one over time."""

    def __init__(self):
        self.speed_multiplier = 1.0
        self.food_energy_multiplier = 1.0
        self.friction = 1.0
        self.random_movement = 0.0
        self.rule_name = "Normal simulation"
        self.rule_description = "No chaos rule is active yet."
        self.message_timer = 0.0
        self.time_until_next_rule = self.random_rule_delay()

    def random_rule_delay(self):
        """Return a random delay before the next rule change."""
        return random.uniform(CHAOS_MIN_SECONDS, CHAOS_MAX_SECONDS)

    def reset_effects(self):
        """Clear the old rule before applying a new one."""
        self.speed_multiplier = 1.0
        self.food_energy_multiplier = 1.0
        self.friction = 1.0
        self.random_movement = 0.0

    def update(self, dt):
        """Count down and change a rule when the timer reaches zero."""
        self.time_until_next_rule -= dt
        self.message_timer = max(0.0, self.message_timer - dt)

        if self.time_until_next_rule <= 0:
            self.change_rule()
            self.time_until_next_rule = self.random_rule_delay()

    def trigger_manual_rule_change(self):
        """Change the current rule immediately and restart the timer."""
        self.change_rule()
        self.time_until_next_rule = self.random_rule_delay()

    def change_rule(self):
        """Pick and apply one new chaos rule."""
        rules = (
            self.agent_speed_increases,
            self.agent_speed_decreases,
            self.food_gives_more_energy,
            self.food_gives_less_energy,
            self.friction_increases,
            self.friction_decreases,
            self.random_movement_increases,
        )

        self.reset_effects()
        random.choice(rules)()
        self.message_timer = CHAOS_MESSAGE_SECONDS

    def agent_speed_increases(self):
        self.speed_multiplier = 1.35
        self.rule_name = "Speed Surge"
        self.rule_description = "Agents move faster."

    def agent_speed_decreases(self):
        self.speed_multiplier = 0.78
        self.rule_name = "Heavy Legs"
        self.rule_description = "Agents move slower."

    def food_gives_more_energy(self):
        self.food_energy_multiplier = 1.55
        self.rule_name = "Rich Food"
        self.rule_description = "Food restores more energy."

    def food_gives_less_energy(self):
        self.food_energy_multiplier = 0.65
        self.rule_name = "Weak Food"
        self.rule_description = "Food restores less energy."

    def friction_increases(self):
        self.friction = 0.85
        self.rule_name = "Sticky Floor"
        self.rule_description = "Movement loses speed to friction."

    def friction_decreases(self):
        self.friction = 1.18
        self.rule_name = "Slippery Floor"
        self.rule_description = "Movement slides farther."

    def random_movement_increases(self):
        self.random_movement = 0.55
        self.rule_name = "Restless Minds"
        self.rule_description = "Agents wander more unpredictably."

    def draw(self, screen, font):
        """Show a temporary visual cue when the current rule changes."""
        if self.message_timer <= 0:
            return

        title = f"Chaos Rule: {self.rule_name}"
        detail = self.rule_description
        title_surface = font.render(title, True, CHAOS_TEXT_COLOR)
        detail_surface = font.render(detail, True, CHAOS_TEXT_COLOR)

        panel_width = max(title_surface.get_width(), detail_surface.get_width()) + 32
        panel_height = 68
        panel = pygame.Rect(0, 0, panel_width, panel_height)
        panel.midtop = (screen.get_width() // 2, 16)

        pygame.draw.rect(screen, CHAOS_PANEL_COLOR, panel, border_radius=8)
        pygame.draw.rect(screen, CHAOS_BORDER_COLOR, panel, 2, border_radius=8)
        screen.blit(title_surface, (panel.x + 16, panel.y + 12))
        screen.blit(detail_surface, (panel.x + 16, panel.y + 38))
