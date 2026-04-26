# Chaos Simulator

**Chaos Simulator** is a small Python/Pygame survival sandbox where simple agents move through an arena, search for food, manage energy, and react to unpredictable rule changes.

It is currently a **V1 prototype**: playable, readable, and built to be easy to expand.

## Highlights

- Survival agents with health, energy, velocity, colors, and ID labels.
- Square food pickups that restore health and energy.
- Simple AI: agents wander, hunt food when hungry, and bounce away from walls.
- Chaos rules that change the simulation every `30-60` seconds.
- Manual chaos trigger with the `C` key or the debug UI button.
- Separate debug windows so stats do not cover the main simulation.
- FPS-friendly UI refresh throttling for larger agent counts.

## Demo Behavior

When you run the project, three windows open:

- **Main Pygame window**: the arena, agents, food, and movement.
- **Debug window**: FPS, agent count, food count, current chaos rule, and next rule timer.
- **Agent monitor**: top-energy agent plus health and energy stats for each agent.

## Installation

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

Run the simulator:

```bash
venv/bin/python main.py
```

## Controls

```text
C      Trigger a chaos rule immediately
Close  Quit the main Pygame window
```

## Project Structure

```text
chaos_simulator/
├── main.py           # Starts Pygame and runs the main loop
├── settings.py       # Project tuning: FPS, colors, AI values, chaos timing
├── agent.py          # Agent class, movement, drawing, survival stats
├── food.py           # Food spawning, drawing, collision, respawning
├── ai.py             # Agent decision-making
├── chaos.py          # Random rule-changing system
├── ui1.py            # Separate debug window
├── ui2.py            # Separate agent monitor window
├── utils.py          # Small helper functions
├── requirements.txt  # Python dependencies
└── README.md
```

## Chaos Rules

The chaos engine can apply rules such as:

- Agent speed increases.
- Agent speed decreases.
- Food gives more energy.
- Food gives less energy.
- Friction changes.
- Random movement increases.

The goal is for the simulation to feel unpredictable while still being understandable.

## Performance Tuning

The external Tkinter UI windows are intentionally throttled so they do not drag down Pygame FPS:

```python
UI_UPDATE_INTERVAL = 0.25
```

If you run many agents and want even more FPS, disable labels above agents:

```python
SHOW_AGENT_LABELS = False
```

You can also tune agent and food counts in `settings.py`:

```python
MIN_AGENTS = 20
MAX_AGENTS = 20
FOOD_COUNT = 18
```

## Current V1 Features

- `800x600` arena with red boundaries and a subtle background grid.
- Agents spawn randomly inside the playable area.
- Food spawns only inside the reachable arena space.
- Agents gain health and energy after eating food.
- Food respawns after collection.
- Agents bounce cleanly off the red boundary.
- Stuck prevention helps agents recover from bad movement states.
- Two external UI windows keep the main arena readable.

## Next Ideas

- Add death, reproduction, or scoring.
- Add graph history for agent performance.
- Add save/load support for simulation settings.
- Add more chaos rules and visual effects.
