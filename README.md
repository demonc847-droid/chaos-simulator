# Chaos Simulator

A small Python/Pygame survival simulation where simple agents move around an arena, search for food, manage energy, and try to stay alive.

## File Structure

```text
chaos_simulator/
├── main.py      # Starts Pygame, runs the main loop, updates and draws objects
├── settings.py  # Project constants like screen size, FPS, colors, AI values
├── agent.py     # Agent class, random spawning, movement, drawing, survival stats
├── food.py      # Food class, random spawning, collision detection, respawning
├── ai.py        # Agent decision-making: seek food, wander, avoid walls
├── chaos.py     # Random rule-changing system
├── ui1.py       # Separate debug window with FPS, counts, and chaos info
├── ui2.py       # Separate agent monitor window with health and energy stats
└── utils.py     # Small helper functions
```

## Getting Started

Run the project with:

```bash
venv/bin/python main.py
```

If you do not have the virtual environment yet, create it and install Pygame:

```bash
python3 -m venv venv
venv/bin/python -m pip install pygame
```

## Project Idea

The goal is to build a simulation where agents survive by collecting food while the rules of the world randomly change over time. The `chaos.py` module controls events such as speed changes, food energy changes, friction changes, and more random movement.

## Current Features

- Opens an `800x600` Pygame window.
- Draws a simple arena with red boundaries and a subtle background grid.
- Spawns agents randomly inside the arena.
- Gives each agent a position, velocity, health, energy, color, and name.
- Draws agents as moving circles with ID numbers above them.
- Spawns food randomly inside the arena.
- Draws food as square shapes so it is easy to tell apart from agents.
- Detects when agents touch food.
- Restores agent health and energy when food is eaten.
- Respawns food after it is collected.
- Uses simple AI so agents wander when full, seek nearby food when hungry, and bounce away from walls.
- Changes a chaos rule automatically every `30-60` seconds.
- Supports manual chaos with the `C` key or the debug window button.
- Opens two separate UI windows so stats do not cover the main simulation.
- Throttles external UI updates for better FPS with larger agent counts.

## Controls

```text
C      Trigger a chaos rule immediately
Close  Quit the main Pygame window
```

## Performance Notes

The external debug windows update a few times per second instead of every frame. You can tune this in `settings.py` with:

```python
UI_UPDATE_INTERVAL = 0.25
```

If you run many agents and want more FPS, you can disable agent number labels:

```python
SHOW_AGENT_LABELS = False
```

## Next Steps

- Add death, reproduction, or scoring.
- Tune AI values in `settings.py`.
- Add save/load or graph history for agent performance.
