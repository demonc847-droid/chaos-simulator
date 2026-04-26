"""Simple survival AI for Chaos Simulator.

This module decides where agents want to move. It does not draw anything and
it does not directly move agents; it only returns a velocity direction that the
Agent class can use.
"""

import random

import pygame

from settings import (
    AGENT_MAX_SPEED,
    AGENT_MIN_SPEED,
    AGENT_TURN_SMOOTHING,
    FOOD_DETECTION_RADIUS,
    HIGH_ENERGY_THRESHOLD,
    LOW_ENERGY_THRESHOLD,
)


def choose_velocity(agent, foods, arena_rect, chaos):
    """Choose the best velocity for one agent this frame."""

    desired_direction = pygame.Vector2()

    # Hungry agents search for nearby food. Well-fed agents keep wandering so
    # the arena still feels alive instead of every bot moving in a straight line.
    nearest_food = find_nearest_food(agent, foods)
    if should_seek_food(agent, nearest_food):
        desired_direction += direction_to(agent.position, nearest_food.rect.center) * 1.4
    else:
        desired_direction += wander_direction(agent)

    # Some chaos rules make agent decisions noisier, so add extra random drift.
    if chaos.random_movement > 0:
        desired_direction += random_unit_vector() * chaos.random_movement

    # Only push away from walls when the agent is actually touching one. This
    # lets agents reach the red boundary instead of turning away too early.
    desired_direction += boundary_escape_direction(agent, arena_rect) * 1.4

    # If all steering cancelled out, keep moving in the current direction.
    if desired_direction.length_squared() == 0:
        desired_direction = agent.velocity.copy()

    target_velocity = velocity_from_direction(desired_direction, agent, chaos)
    return smooth_velocity(agent.velocity, target_velocity)


def find_nearest_food(agent, foods):
    """Return the closest food square to an agent, or None when no food exists."""
    if not foods:
        return None

    return min(
        foods,
        key=lambda food: agent.position.distance_squared_to(food.rect.center),
    )


def should_seek_food(agent, food):
    """Return True when an agent is hungry and food is close enough to chase."""
    if food is None or agent.energy > LOW_ENERGY_THRESHOLD:
        return False

    distance_to_food = agent.position.distance_to(food.rect.center)
    return distance_to_food <= FOOD_DETECTION_RADIUS


def direction_to(start, target):
    """Return a normalized direction vector from start to target."""
    direction = pygame.Vector2(target) - pygame.Vector2(start)
    if direction.length_squared() == 0:
        return pygame.Vector2()

    return direction.normalize()


def wander_direction(agent):
    """Return a smooth random direction for agents that are not hungry."""

    # Store wander state on the agent so it can keep the same general direction
    # for a short time instead of jittering randomly every frame.
    if not hasattr(agent, "wander_timer"):
        agent.wander_timer = 0
        agent.wander_vector = random_unit_vector()

    if agent.wander_timer <= 0:
        agent.wander_timer = random.randint(30, 90)
        agent.wander_vector = random_unit_vector()

    agent.wander_timer -= 1
    return agent.wander_vector


def boundary_escape_direction(agent, arena_rect):
    """Return a direction that pushes an agent off a wall it is touching."""
    push = pygame.Vector2()

    if agent.position.x - agent.radius <= arena_rect.left:
        push.x += 1
    if agent.position.x + agent.radius >= arena_rect.right:
        push.x -= 1
    if agent.position.y - agent.radius <= arena_rect.top:
        push.y += 1
    if agent.position.y + agent.radius >= arena_rect.bottom:
        push.y -= 1

    if push.length_squared() == 0:
        return push

    return push.normalize()


def velocity_from_direction(direction, agent, chaos):
    """Convert a desired direction into a velocity vector."""
    if direction.length_squared() == 0:
        return pygame.Vector2()

    direction = direction.normalize()

    # Hungry agents move faster, because finding food is urgent.
    if agent.energy <= LOW_ENERGY_THRESHOLD:
        speed = AGENT_MAX_SPEED
    elif agent.energy >= HIGH_ENERGY_THRESHOLD:
        speed = AGENT_MIN_SPEED
    else:
        speed = (AGENT_MIN_SPEED + AGENT_MAX_SPEED) / 2

    return direction * speed * chaos.speed_multiplier * chaos.friction


def smooth_velocity(current_velocity, target_velocity):
    """Blend toward the new velocity so movement feels less jittery."""
    if current_velocity.length_squared() == 0:
        return target_velocity

    smoothed = current_velocity.lerp(target_velocity, AGENT_TURN_SMOOTHING)
    if smoothed.length_squared() == 0:
        return target_velocity

    return smoothed


def random_unit_vector():
    """Create a random direction vector with a length of 1."""
    angle = random.uniform(0, 360)
    return pygame.Vector2(1, 0).rotate(angle)
