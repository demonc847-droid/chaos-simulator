"""Agent logic for Chaos Simulator.

An agent is one moving circle in the arena. This file owns how agents are
created, what information they store, how they move, and how they are drawn.
"""

import random

import pygame

from ai import choose_velocity
from settings import (
    AGENT_COLORS,
    AGENT_MAX_SPEED,
    AGENT_MIN_SPEED,
    AGENT_OUTLINE_COLOR,
    AGENT_RADIUS,
    AGENT_START_ENERGY,
    AGENT_START_HEALTH,
    ENERGY_DRAIN_PER_FRAME,
    HEALTH_DRAIN_WHEN_STARVING,
    MAX_AGENT_ENERGY,
    MAX_AGENT_HEALTH,
    MAX_AGENTS,
    MIN_AGENTS,
    PLAYABLE_RECT,
    AGENT_LABEL_BACKGROUND_COLOR,
    AGENT_LABEL_TEXT_COLOR,
    FPS,
    HIT_FLASH_DURATION,
    MIN_DAMAGE,
)


class Agent:
    """A single simulated creature moving around the arena."""

    def __init__(self, agent_id, name, position, velocity, color):
        self.agent_id = agent_id

        # Name/ID makes it easier to track agents later in debug UI or logs.
        self.name = name

        # Vector2 stores x/y values and makes movement math easy.
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)

        # Health and energy are survival stats. Energy slowly drains over time,
        # and food can restore both values.
        self.health = AGENT_START_HEALTH
        self.energy = AGENT_START_ENERGY

        # Combat stats. Attack is the agent's raw damage power, while defense
        # blocks part of incoming damage. The fight state fields will be used
        # by the combat system when agents start 1v1 battles.
        self.attack = random.randint(6, 12)
        self.defense = random.randint(1, 4)
        self.is_alive = True
        self.is_fighting = False
        self.opponent = None
        self.hit_flash_timer = 0
        self.kills = 0

        # Each agent has its own color and circle size.
        self.color = color
        self.radius = AGENT_RADIUS
        self.last_position = self.position.copy()
        self.stuck_frames = 0
        self.label_surface = None
        self.label_background_size = None

    def redirect_wander_after_bounce(self):
        """Point wandering away from the wall after a boundary collision."""
        if self.velocity.length_squared() == 0:
            return

        self.wander_vector = self.velocity.normalize().rotate(random.uniform(-18, 18))
        self.wander_timer = 45

    def update(self, arena_rect, foods, chaos):
        """Ask the AI for a decision, then move inside the arena."""
        self.update_hit_flash()

        # Dead agents stay in the arena as visible bodies, but they no longer
        # spend energy, make AI decisions, or move around.
        if not self.is_alive:
            self.velocity.update(0, 0)
            return

        # During combat events, the CombatEngine handles this agent. Pausing
        # normal AI movement keeps 1v1 fights readable.
        if self.is_fighting:
            self.velocity.update(0, 0)
            return

        # The AI chooses a velocity based on hunger, nearby food, and walls.
        self.velocity = choose_velocity(self, foods, arena_rect, chaos)

        # Survival pressure: moving around costs a little energy each frame.
        self.energy = max(0, self.energy - ENERGY_DRAIN_PER_FRAME)
        if self.energy == 0:
            self.health = max(0, self.health - HEALTH_DRAIN_WHEN_STARVING)
            self.mark_dead_if_needed()

        self.last_position = self.position.copy()

        # Add velocity to position once per frame. This is what makes it move.
        self.position += self.velocity

        self.keep_inside_arena(arena_rect)
        self.prevent_stuck()

    def keep_inside_arena(self, arena_rect):
        """Bounce cleanly when the agent touches the arena boundary."""
        bounced = False

        if self.position.x - self.radius <= arena_rect.left:
            self.position.x = arena_rect.left + self.radius
            self.velocity.x = abs(self.velocity.x)
            bounced = True
        elif self.position.x + self.radius >= arena_rect.right:
            self.position.x = arena_rect.right - self.radius
            self.velocity.x = -abs(self.velocity.x)
            bounced = True

        if self.position.y - self.radius <= arena_rect.top:
            self.position.y = arena_rect.top + self.radius
            self.velocity.y = abs(self.velocity.y)
            bounced = True
        elif self.position.y + self.radius >= arena_rect.bottom:
            self.position.y = arena_rect.bottom - self.radius
            self.velocity.y = -abs(self.velocity.y)
            bounced = True

        if bounced:
            self.redirect_wander_after_bounce()

    def prevent_stuck(self):
        """Give an agent a new direction if it barely moves for several frames."""
        if self.position.distance_squared_to(self.last_position) < 0.01:
            self.stuck_frames += 1
        else:
            self.stuck_frames = 0

        if self.stuck_frames > 20:
            angle = random.uniform(0, 360)
            self.velocity = pygame.Vector2(AGENT_MIN_SPEED, 0).rotate(angle)
            self.wander_vector = self.velocity.normalize()
            self.wander_timer = 60
            self.stuck_frames = 0

    def draw(self, screen, font=None):
        """Draw the agent as a colored circle."""
        draw_color = self.get_draw_color()

        pygame.draw.circle(screen, AGENT_OUTLINE_COLOR, self.position, self.radius + 2)
        pygame.draw.circle(screen, draw_color, self.position, self.radius)

        if font is not None:
            self.draw_id_label(screen, font)

    def get_draw_color(self):
        """Return the current visible color for normal, hit, or dead agents."""
        if not self.is_alive:
            return (74, 78, 88)

        # Flicker between red and the normal color while the hit timer is
        # active, making damage easier to notice during fast fights.
        if self.hit_flash_timer > 0 and int(self.hit_flash_timer * FPS) % 2 == 0:
            return (255, 55, 55)

        return self.color

    def draw_id_label(self, screen, font):
        """Draw the agent's number above the circle."""
        if self.label_surface is None:
            label = str(self.agent_id)
            self.label_surface = font.render(label, True, AGENT_LABEL_TEXT_COLOR)
            self.label_background_size = self.label_surface.get_rect().inflate(8, 4).size

        label_rect = self.label_surface.get_rect()
        label_rect.centerx = int(self.position.x)
        label_rect.bottom = int(self.position.y - self.radius - 4)

        background_rect = pygame.Rect((0, 0), self.label_background_size)
        background_rect.center = label_rect.center
        pygame.draw.rect(
            screen,
            AGENT_LABEL_BACKGROUND_COLOR,
            background_rect,
            border_radius=4,
        )
        screen.blit(self.label_surface, label_rect)

    def eat(self, health_amount, energy_amount):
        """Restore health and energy after collecting food."""
        if not self.is_alive:
            return

        self.health = min(MAX_AGENT_HEALTH, self.health + health_amount)
        self.energy = min(MAX_AGENT_ENERGY, self.energy + energy_amount)

    def take_damage(self, amount):
        """Reduce health, flash red, and die if health reaches zero."""
        if not self.is_alive:
            return 0

        damage = max(MIN_DAMAGE, amount - self.defense)
        self.health = max(0, self.health - damage)
        self.hit_flash_timer = HIT_FLASH_DURATION
        self.mark_dead_if_needed()

        return damage

    def update_hit_flash(self):
        """Count down the short red flash shown after taking damage."""
        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0, self.hit_flash_timer - 1 / FPS)

    def mark_dead_if_needed(self):
        """Switch the agent into its dead state when health is empty."""
        if self.health > 0 or not self.is_alive:
            return

        self.is_alive = False
        self.is_fighting = False
        self.opponent = None
        self.velocity.update(0, 0)

    def respawn(self, arena_rect):
        """Bring a defeated agent back at a fresh random arena position."""
        x = random.randint(arena_rect.left + self.radius, arena_rect.right - self.radius)
        y = random.randint(arena_rect.top + self.radius, arena_rect.bottom - self.radius)
        angle = random.uniform(0, 360)

        self.position.update(x, y)
        self.last_position = self.position.copy()
        self.velocity = pygame.Vector2(AGENT_MIN_SPEED, 0).rotate(angle)
        self.health = AGENT_START_HEALTH
        self.energy = AGENT_START_ENERGY
        self.is_alive = True
        self.is_fighting = False
        self.opponent = None
        self.hit_flash_timer = 0
        self.stuck_frames = 0


def create_random_agent(agent_id, arena_rect):
    """Create one agent at a random position with a random velocity."""

    # Keep the spawn point at least one radius away from the walls so the whole
    # circle starts inside the arena.
    x = random.randint(arena_rect.left + AGENT_RADIUS, arena_rect.right - AGENT_RADIUS)
    y = random.randint(arena_rect.top + AGENT_RADIUS, arena_rect.bottom - AGENT_RADIUS)

    # Pick a random direction. The speed is normalized below so diagonal agents
    # do not accidentally move faster than straight-line agents.
    velocity = pygame.Vector2(
        random.uniform(-AGENT_MAX_SPEED, AGENT_MAX_SPEED),
        random.uniform(-AGENT_MAX_SPEED, AGENT_MAX_SPEED),
    )

    # A velocity of (0, 0) would mean the agent never moves, so give it a small
    # push if random generation lands exactly there.
    if velocity.length_squared() == 0:
        velocity.x = AGENT_MIN_SPEED
    else:
        velocity.scale_to_length(random.uniform(AGENT_MIN_SPEED, AGENT_MAX_SPEED))

    return Agent(
        agent_id=agent_id,
        name=f"Agent {agent_id}",
        position=(x, y),
        velocity=velocity,
        color=random.choice(AGENT_COLORS),
    )


def spawn_agents(arena_rect=pygame.Rect(PLAYABLE_RECT)):
    """Create a random group of agents inside the arena."""

    # The number changes each time the game starts, within the settings range.
    agent_count = random.randint(MIN_AGENTS, MAX_AGENTS)
    return [create_random_agent(index + 1, arena_rect) for index in range(agent_count)]
