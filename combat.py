"""Combat state machine for Chaos Simulator.

This file owns the high-level battle rules. The agent file stores individual
combat stats, while this engine decides when the whole simulation is in normal
survival mode, active 1v1 fight mode, or post-fight cooldown mode.
"""

import random

from settings import (
    COMBAT_APPROACH_SPEED,
    DAMAGE_INTERVAL,
    FIGHT_CHANCE,
    FIGHT_COOLDOWN,
    FIGHT_ROLL_INTERVAL,
    RESPAWN_DELAY,
)

CONTACT_TOLERANCE = 1.0


class CombatEngine:
    """Track combat mode, fight timing, active pairs, and dead agents."""

    NORMAL = "NORMAL"
    FIGHTING = "FIGHTING"
    COOLDOWN = "COOLDOWN"

    def __init__(self):
        # NORMAL means agents move, food exists, and fight rolls can happen.
        self.mode = self.NORMAL

        # Counts down until the next fight dice roll while in NORMAL mode.
        self.fight_roll_timer = FIGHT_ROLL_INTERVAL

        # Counts down after a fight ends. No new fight rolls happen here.
        self.cooldown_timer = 0

        # List of active 1v1 pairs. Each item is a tuple: (agent_a, agent_b).
        self.active_pairs = []

        # Each active pair has its own damage timer so all fights can progress
        # independently during the same fight event.
        self.damage_timers = {}

        # If the living agent count is odd, one agent sits out the fight event.
        self.bye_agents = []

        # Defeated agents stay gray for a short time before respawning.
        self.respawn_timers = {}

        # Tracks how many agents are dead, which helps UI/debug later.
        self.dead_count = 0

        # Main.py watches this flag and respawns food after a fight event ends.
        self.food_respawn_needed = False

    def update(self, agents, dt, foods=None, arena_rect=None):
        """Advance the combat mode timers by one frame."""
        self.update_respawns(dt, arena_rect)
        self.dead_count = self.count_dead_agents(agents)

        if self.mode == self.NORMAL:
            self.update_normal_mode(agents, dt, foods, arena_rect)
        elif self.mode == self.FIGHTING:
            self.update_fighting_mode(dt, arena_rect)
        elif self.mode == self.COOLDOWN:
            self.update_cooldown_mode(dt)

    def update_normal_mode(self, agents, dt, foods=None, arena_rect=None):
        """Roll for a possible fight every few seconds."""
        self.fight_roll_timer -= dt
        if self.fight_roll_timer > 0:
            return

        self.fight_roll_timer = FIGHT_ROLL_INTERVAL
        living_agents = self.get_living_agents(agents)

        if len(living_agents) < 2:
            return

        if self.roll_fight_dice():
            self.start_fighting(living_agents, foods, arena_rect)

    def roll_fight_dice(self):
        """Return True when the random fight roll starts a fight event."""
        return random.random() <= FIGHT_CHANCE

    def update_fighting_mode(self, dt, arena_rect=None):
        """Apply timed damage to every active 1v1 pair."""
        finished_pairs = []

        for pair in self.active_pairs:
            agent_a, agent_b = pair

            if not agent_a.is_alive or not agent_b.is_alive:
                self.award_kill_if_possible(agent_a, agent_b)
                finished_pairs.append(pair)
                continue

            if not self.are_agents_touching(agent_a, agent_b):
                self.move_pair_closer(agent_a, agent_b, dt, arena_rect)
                self.damage_timers[pair] = DAMAGE_INTERVAL
                continue

            self.damage_timers[pair] -= dt
            if self.damage_timers[pair] > 0:
                continue

            self.damage_timers[pair] = DAMAGE_INTERVAL
            self.exchange_damage(agent_a, agent_b)

            if not agent_a.is_alive or not agent_b.is_alive:
                self.award_kill_if_possible(agent_a, agent_b)
                finished_pairs.append(pair)

        for pair in finished_pairs:
            self.finish_pair(pair)

        if not self.active_pairs:
            self.start_cooldown(arena_rect)

    def update_cooldown_mode(self, dt):
        """Wait out the cooldown before fight rolls become possible again."""
        self.cooldown_timer -= dt
        if self.cooldown_timer <= 0:
            self.start_normal()

    def start_fighting(self, living_agents, foods=None, arena_rect=None):
        """Switch into FIGHTING mode, clear food, and create 1v1 pairs."""
        self.mode = self.FIGHTING
        self.food_respawn_needed = False
        self.clear_food(foods)
        self.active_pairs, self.bye_agents = self.create_pairs(living_agents)
        self.damage_timers = {}

        for agent_a, agent_b in self.active_pairs:
            agent_a.is_fighting = True
            agent_a.opponent = agent_b
            agent_b.is_fighting = True
            agent_b.opponent = agent_a
            self.damage_timers[(agent_a, agent_b)] = DAMAGE_INTERVAL

        if not self.active_pairs:
            self.start_cooldown()

    def start_cooldown(self, arena_rect=None):
        """Switch into COOLDOWN mode after fights end."""
        self.clear_fight_state()
        self.mode = self.COOLDOWN
        self.cooldown_timer = FIGHT_COOLDOWN
        self.food_respawn_needed = True

    def start_normal(self):
        """Return to normal survival mode."""
        self.clear_fight_state()
        self.mode = self.NORMAL
        self.fight_roll_timer = FIGHT_ROLL_INTERVAL
        self.cooldown_timer = 0
        self.food_respawn_needed = False

    def end_fighting(self):
        """Public helper for future combat logic to finish a fight round."""
        if self.mode == self.FIGHTING:
            self.start_cooldown()

    def clear_fight_state(self):
        """Remove opponent links from agents that were fighting."""
        for agent_a, agent_b in self.active_pairs:
            agent_a.is_fighting = False
            agent_a.opponent = None
            agent_b.is_fighting = False
            agent_b.opponent = None

        self.active_pairs = []
        self.damage_timers = {}
        self.bye_agents = []

    def exchange_damage(self, agent_a, agent_b):
        """Let both agents hit each other during the same damage tick."""
        agent_a.take_damage(agent_b.attack)
        agent_b.take_damage(agent_a.attack)

    def award_kill_if_possible(self, agent_a, agent_b):
        """Give a kill to the surviving agent when only one agent dies."""
        if agent_a.is_alive and not agent_b.is_alive:
            agent_a.kills += 1
            self.track_defeated_agent(agent_b)
        elif agent_b.is_alive and not agent_a.is_alive:
            agent_b.kills += 1
            self.track_defeated_agent(agent_a)
        elif not agent_a.is_alive and not agent_b.is_alive:
            self.track_defeated_agent(agent_a)
            self.track_defeated_agent(agent_b)

    def track_defeated_agent(self, agent):
        """Remember a dead agent so it can respawn after the fight event."""
        if agent not in self.respawn_timers:
            self.respawn_timers[agent] = RESPAWN_DELAY

    def finish_pair(self, pair):
        """Remove a completed pair from active combat."""
        if pair not in self.active_pairs:
            return

        agent_a, agent_b = pair
        agent_a.is_fighting = False
        agent_a.opponent = None
        agent_b.is_fighting = False
        agent_b.opponent = None
        self.active_pairs.remove(pair)
        self.damage_timers.pop(pair, None)

    def are_agents_touching(self, agent_a, agent_b):
        """Return True when two fighting agents are close enough to hit."""
        touch_distance = agent_a.radius + agent_b.radius + CONTACT_TOLERANCE
        return agent_a.position.distance_squared_to(agent_b.position) <= touch_distance**2

    def move_pair_closer(self, agent_a, agent_b, dt, arena_rect=None):
        """Move paired agents toward each other until their circles touch."""
        direction = agent_b.position - agent_a.position
        current_distance = direction.length()
        touch_distance = agent_a.radius + agent_b.radius

        if current_distance <= touch_distance:
            return

        if current_distance == 0:
            direction.update(1, 0)
        else:
            direction /= current_distance

        max_step = COMBAT_APPROACH_SPEED * dt
        gap = current_distance - touch_distance
        step = min(max_step, gap / 2)

        # Once the agents are very close, close the final tiny gap exactly.
        # This prevents pairs from looking like they touched while the math is
        # still barely outside the damage range.
        if gap <= CONTACT_TOLERANCE:
            step = gap / 2

        position_a = agent_a.position + direction * step
        position_b = agent_b.position - direction * step

        if arena_rect is not None:
            position_a, position_b = self.keep_pair_inside_arena(
                position_a,
                position_b,
                agent_a.radius,
                arena_rect,
            )

        agent_a.position.update(position_a.x, position_a.y)
        agent_b.position.update(position_b.x, position_b.y)
        agent_a.last_position = agent_a.position.copy()
        agent_b.last_position = agent_b.position.copy()
        agent_a.velocity.update(0, 0)
        agent_b.velocity.update(0, 0)

    def keep_pair_inside_arena(self, position_a, position_b, radius, arena_rect):
        """Shift a touching pair if it would appear outside the arena."""
        min_x = min(position_a.x, position_b.x)
        max_x = max(position_a.x, position_b.x)
        min_y = min(position_a.y, position_b.y)
        max_y = max(position_a.y, position_b.y)
        shift_x = 0
        shift_y = 0

        if min_x - radius < arena_rect.left:
            shift_x = arena_rect.left - (min_x - radius)
        elif max_x + radius > arena_rect.right:
            shift_x = arena_rect.right - (max_x + radius)

        if min_y - radius < arena_rect.top:
            shift_y = arena_rect.top - (min_y - radius)
        elif max_y + radius > arena_rect.bottom:
            shift_y = arena_rect.bottom - (max_y + radius)

        offset = position_a.__class__(shift_x, shift_y)
        return position_a + offset, position_b + offset

    def update_respawns(self, dt, arena_rect):
        """Respawn defeated agents after they stay gray for a few seconds."""
        if arena_rect is None:
            return

        ready_to_respawn = []
        for agent, timer in self.respawn_timers.items():
            self.respawn_timers[agent] = timer - dt
            if self.respawn_timers[agent] <= 0:
                ready_to_respawn.append(agent)

        for agent in ready_to_respawn:
            agent.respawn(arena_rect)
            self.respawn_timers.pop(agent, None)

    def clear_food(self, foods):
        """Remove all food from the arena when a fight event starts."""
        if foods is not None:
            foods.clear()

    def should_show_food(self):
        """Return True when food should exist in the arena."""
        return self.mode != self.FIGHTING

    def can_eat_food(self):
        """Return True when agents are allowed to collect food."""
        return self.mode != self.FIGHTING

    def get_time_until_next_roll(self):
        """Return the timer most useful for debug UI."""
        if self.mode == self.COOLDOWN:
            return self.cooldown_timer

        if self.mode == self.NORMAL:
            return self.fight_roll_timer

        return 0

    def create_pairs(self, living_agents):
        """Shuffle living agents into 1v1 pairs and return any bye agent."""
        shuffled_agents = living_agents[:]
        random.shuffle(shuffled_agents)

        pairs = []
        for index in range(0, len(shuffled_agents) - 1, 2):
            pairs.append((shuffled_agents[index], shuffled_agents[index + 1]))

        bye_agents = []
        if len(shuffled_agents) % 2 == 1:
            bye_agents.append(shuffled_agents[-1])

        return pairs, bye_agents

    def get_living_agents(self, agents):
        """Return agents that are still alive and available to fight."""
        return [
            agent
            for agent in agents
            if agent.is_alive and not agent.is_fighting
        ]

    def count_dead_agents(self, agents):
        """Count dead agents for future UI and debugging."""
        return sum(1 for agent in agents if not agent.is_alive)
