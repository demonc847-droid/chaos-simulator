"""Food logic for Chaos Simulator.

Food appears as small squares inside the arena. When an agent touches a food
square, the agent gains health and energy, then that food respawns somewhere
else in the arena.
"""

import random

import pygame

from settings import (
    FOOD_COLOR,
    FOOD_COUNT,
    FOOD_ENERGY_VALUE,
    FOOD_HEALTH_VALUE,
    FOOD_OUTLINE_COLOR,
    FOOD_SIZE,
    PLAYABLE_RECT,
)


class Food:
    """A single collectible food square."""

    def __init__(self, position):
        # Food uses a Rect because squares/rectangles are easy to draw and
        # collide with in Pygame.
        self.rect = pygame.Rect(0, 0, FOOD_SIZE, FOOD_SIZE)
        self.rect.center = position
        self.color = FOOD_COLOR

    def respawn(self, arena_rect):
        """Move this food square to a new random spot inside the arena."""
        self.rect.center = random_food_position(arena_rect)

    def touches_agent(self, agent):
        """Return True when an agent's circle touches this food square."""

        # Find the nearest point on the square to the center of the agent.
        nearest_x = max(self.rect.left, min(agent.position.x, self.rect.right))
        nearest_y = max(self.rect.top, min(agent.position.y, self.rect.bottom))

        # If that nearest point is within the agent radius, the circle and
        # square are touching.
        distance_x = agent.position.x - nearest_x
        distance_y = agent.position.y - nearest_y
        return distance_x**2 + distance_y**2 <= agent.radius**2

    def feed(self, agent, chaos):
        """Increase an agent's health and energy without going past the max."""
        energy_amount = FOOD_ENERGY_VALUE * chaos.food_energy_multiplier
        agent.eat(FOOD_HEALTH_VALUE, energy_amount)

    def draw(self, screen):
        """Draw the food as a square."""
        pygame.draw.rect(screen, FOOD_OUTLINE_COLOR, self.rect.inflate(4, 4), border_radius=3)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=2)


def random_food_position(arena_rect):
    """Pick a random point where a whole food square fits inside the arena."""
    half_size = FOOD_SIZE // 2
    x = random.randint(arena_rect.left + half_size, arena_rect.right - half_size)
    y = random.randint(arena_rect.top + half_size, arena_rect.bottom - half_size)
    return x, y


def create_random_food(arena_rect):
    """Create one food square at a random arena position."""
    return Food(random_food_position(arena_rect))


def spawn_food(arena_rect=pygame.Rect(PLAYABLE_RECT)):
    """Create the starting group of food squares."""
    return [create_random_food(arena_rect) for _ in range(FOOD_COUNT)]


def update_food(agents, foods, arena_rect, chaos):
    """Handle food collection and respawning."""
    for agent in agents:
        for food in foods:
            if food.touches_agent(agent):
                food.feed(agent, chaos)
                food.respawn(arena_rect)
