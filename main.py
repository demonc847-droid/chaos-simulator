"""Main entry point for Chaos Simulator.

This file starts Pygame, creates the window, runs the main loop, and asks the
other modules to update and draw their parts of the simulation.
"""

import pygame

from agent import spawn_agents
from chaos import ChaosEngine
from combat import CombatEngine
from food import spawn_food, update_food
from settings import (
    ARENA_RECT,
    BACKGROUND_COLOR,
    BOUNDARY_COLOR,
    BOUNDARY_SHADOW_COLOR,
    BOUNDARY_WIDTH,
    BOUNDARY_RADIUS,
    FPS,
    GAME_TITLE,
    GRID_COLOR,
    PLAYABLE_RECT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOW_AGENT_LABELS,
    UI_UPDATE_INTERVAL,
)
from ui1 import create_debug_window
from ui2 import create_agent_monitor


def update(agents, foods, arena_rect, chaos, combat, dt):
    """Update everything in the game world once per frame."""
    chaos.update(dt)
    combat.update(agents, dt, foods, arena_rect)

    if combat.food_respawn_needed:
        foods.extend(spawn_food(arena_rect))
        combat.food_respawn_needed = False

    # Each agent asks the AI for movement, then handles its own wall collisions.
    for agent in agents:
        agent.update(arena_rect, foods, chaos)

    # Food handles detecting when agents collect it and respawning afterward.
    if combat.can_eat_food():
        update_food(agents, foods, arena_rect, chaos)


def handle_events(chaos):
    """Handle Pygame input and return False when the game should quit."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            chaos.trigger_manual_rule_change()

    return True


def draw(screen, background, agents, foods, agent_label_font):
    """Draw one full frame to the window."""

    # The background grid and boundary do not change, so they are drawn once
    # into a surface and copied here each frame.
    screen.blit(background, (0, 0))

    # Draw food before agents so agents stay visually on top when overlapping.
    for food in foods:
        food.draw(screen)

    # Draw every agent after the arena and food so the circles appear on top.
    for agent in agents:
        label_font = agent_label_font if SHOW_AGENT_LABELS else None
        agent.draw(screen, label_font)

    # Show everything we just drew on the actual window.
    pygame.display.flip()


def draw_background_grid(screen):
    """Draw a subtle grid so movement is easier to see."""
    spacing = 40
    for x in range(0, SCREEN_WIDTH, spacing):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, spacing):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


def create_background():
    """Create the static background surface used every frame."""
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    background.fill(BACKGROUND_COLOR)
    draw_background_grid(background)

    pygame.draw.rect(
        background,
        BOUNDARY_SHADOW_COLOR,
        pygame.Rect(ARENA_RECT).inflate(-2, -2),
        BOUNDARY_WIDTH + 4,
        border_radius=BOUNDARY_RADIUS,
    )
    pygame.draw.rect(
        background,
        BOUNDARY_COLOR,
        ARENA_RECT,
        BOUNDARY_WIDTH,
        border_radius=BOUNDARY_RADIUS,
    )
    return background


def update_external_ui(debug_ui, agent_ui, clock, agents, foods, chaos, combat, timer, dt):
    """Refresh slower Tkinter UI windows without dragging down Pygame FPS."""
    timer += dt
    if timer < UI_UPDATE_INTERVAL:
        return timer

    debug_ui.update(clock, agents, foods, chaos, combat)
    agent_ui.update(agents, combat)
    return 0


def main():
    """Set up Pygame and run the game until the player closes the window."""

    # Pygame must be initialized before using its display, events, or clock.
    pygame.init()

    # Create the main game window and set the title bar text.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    background = create_background()

    # The clock controls the loop speed so the game does not run too fast.
    clock = pygame.time.Clock()
    agent_label_font = pygame.font.Font(None, 20)

    # Convert the playable area from settings.py into a Pygame Rect object.
    # This is the space inside the red boundary where agents and food can be.
    arena_rect = pygame.Rect(PLAYABLE_RECT)

    # Create the starting agents before the loop begins.
    agents = spawn_agents(arena_rect)
    foods = spawn_food(arena_rect)
    chaos = ChaosEngine()
    combat = CombatEngine()
    debug_ui = create_debug_window(chaos.trigger_manual_rule_change)
    agent_ui = create_agent_monitor(debug_ui.root)
    ui_timer = UI_UPDATE_INTERVAL

    # The main loop keeps running until a quit event is received.
    running = True
    while running:
        # Handle window events. Press C to trigger a manual chaos rule.
        running = handle_events(chaos)

        # Wait just enough to keep the game near the target FPS.
        dt = clock.tick(FPS) / 1000

        # Update game objects, then draw the new frame.
        update(agents, foods, arena_rect, chaos, combat, dt)
        draw(screen, background, agents, foods, agent_label_font)
        ui_timer = update_external_ui(
            debug_ui,
            agent_ui,
            clock,
            agents,
            foods,
            chaos,
            combat,
            ui_timer,
            dt,
        )

    # Cleanly shut down Pygame after leaving the loop.
    agent_ui.close()
    debug_ui.close()
    pygame.quit()


# This makes the game start only when this file is run directly.
if __name__ == "__main__":
    main()
