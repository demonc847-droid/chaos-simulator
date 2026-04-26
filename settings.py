"""Settings for Chaos Simulator.

This file is the project's control panel. Values here are imported by the
other files, so changing a number or color here changes the whole simulation
without needing to hunt through the game code.
"""

# Text shown in the window title bar.
GAME_TITLE = "Chaos Simulator"

# The size of the Pygame window, measured in pixels.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Frames per second. A higher number tries to update/draw the game more often.
FPS = 60

# External Tkinter UI windows are slower than Pygame drawing, so refresh them
# only a few times per second instead of once every frame.
UI_UPDATE_INTERVAL = 0.25

# RGB color values. Each color is written as (red, green, blue), from 0 to 255.
BACKGROUND_COLOR = (18, 20, 26)
GRID_COLOR = (28, 32, 40)
BOUNDARY_COLOR = (220, 40, 40)
BOUNDARY_SHADOW_COLOR = (85, 16, 20)

# How rounded the corners of the arena border should be.
BOUNDARY_RADIUS = 10

# The arena is the playable rectangle inside the window.
# A margin of 0 means the arena touches the window edges.
ARENA_MARGIN = 0
BOUNDARY_WIDTH = 10

# Pygame rectangles use (left, top, width, height).
ARENA_RECT = (
    ARENA_MARGIN,
    ARENA_MARGIN,
    SCREEN_WIDTH - ARENA_MARGIN * 2,
    SCREEN_HEIGHT - ARENA_MARGIN * 2,
)

# The red border is drawn inside ARENA_RECT. The playable area starts after
# that border, so agents and food stay in the space inside the red walls.
PLAYABLE_RECT = (
    ARENA_MARGIN + BOUNDARY_WIDTH,
    ARENA_MARGIN + BOUNDARY_WIDTH,
    SCREEN_WIDTH - ARENA_MARGIN * 2 - BOUNDARY_WIDTH * 2,
    SCREEN_HEIGHT - ARENA_MARGIN * 2 - BOUNDARY_WIDTH * 2,
)

# The game will create a random number of agents within this range.
MIN_AGENTS = 2
MAX_AGENTS = 2

# Agent drawing and movement settings.
AGENT_RADIUS = 8
AGENT_MIN_SPEED = 1.15
AGENT_MAX_SPEED = 2.65
AGENT_TURN_SMOOTHING = 0.18

# Simple survival/AI settings.
# Agents below this energy level start looking for food on purpose.
LOW_ENERGY_THRESHOLD = 55

# Agents above this energy level wander instead of urgently chasing food.
HIGH_ENERGY_THRESHOLD = 78

# How far an agent can "notice" food when it is hungry.
FOOD_DETECTION_RADIUS = 280

# These small costs make agents slowly become hungry over time.
ENERGY_DRAIN_PER_FRAME = 0.018
HEALTH_DRAIN_WHEN_STARVING = 0.025

# Combat settings.
# Agents will only check for possible fights every few seconds, so combat does
# not happen constantly every frame.
FIGHT_ROLL_INTERVAL = 3

# Chance that a nearby 1v1 fight starts when the fight roll happens.
FIGHT_CHANCE = 0.35

# After fighting, an agent waits this long before it can start another fight.
FIGHT_COOLDOWN = 10

# During an active fight, damage is applied on this timer instead of every
# frame, which keeps combat readable and easier to balance.
DAMAGE_INTERVAL = 0.5

# How fast paired agents move toward each other before they start trading hits.
COMBAT_APPROACH_SPEED = 180

# How long an agent should visually flash after being hit.
HIT_FLASH_DURATION = 0.2

# How long a defeated agent stays gray before respawning somewhere else.
RESPAWN_DELAY = 3

# The smallest amount of health a successful hit can remove.
MIN_DAMAGE = 1

# Chaos rule timing and UI.
# A new chaos rule appears after a random delay between these two values.
CHAOS_MIN_SECONDS = 30
CHAOS_MAX_SECONDS = 60

# How long the rule-change message stays visible on screen.
CHAOS_MESSAGE_SECONDS = 4

# Colors used for the visual cue when a chaos rule changes.
CHAOS_TEXT_COLOR = (255, 245, 180)
CHAOS_PANEL_COLOR = (36, 30, 22)
CHAOS_BORDER_COLOR = (255, 196, 87)

# Debug/UI colors.
UI_TEXT_COLOR = (235, 238, 245)
UI_MUTED_TEXT_COLOR = (170, 178, 190)
UI_PANEL_COLOR = (18, 22, 30)
UI_PANEL_BORDER_COLOR = (72, 84, 100)
HEALTH_BAR_COLOR = (78, 201, 111)
ENERGY_BAR_COLOR = (88, 166, 255)
BAR_BACKGROUND_COLOR = (45, 49, 58)

# Agent ID labels are drawn above each agent in the main Pygame window.
AGENT_LABEL_TEXT_COLOR = (245, 247, 250)
AGENT_LABEL_BACKGROUND_COLOR = (12, 14, 18)
AGENT_OUTLINE_COLOR = (8, 10, 14)
SHOW_AGENT_LABELS = True

# Starting survival stats for every new agent.
AGENT_START_HEALTH = 100
AGENT_START_ENERGY = 100

# Agents pick one of these colors when they spawn.
AGENT_COLORS = (
    (88, 166, 255),
    (126, 231, 135),
    (255, 196, 87),
    (255, 123, 114),
    (210, 168, 255),
    (57, 211, 215),
)

# Food settings. Food is drawn as squares so it is visually different from the
# circular agents.
FOOD_COUNT = 18
FOOD_SIZE = 11
FOOD_COLOR = (88, 220, 128)
FOOD_OUTLINE_COLOR = (24, 92, 54)
FOOD_HEALTH_VALUE = 4
FOOD_ENERGY_VALUE = 18
MAX_AGENT_HEALTH = 100
MAX_AGENT_ENERGY = 100
