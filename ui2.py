"""Separate agent monitor window.

This UI focuses on agent health and energy so the main Pygame window can stay
clear for watching the simulation.
"""

try:
    import tkinter as tk
except ImportError:
    tk = None

from settings import MAX_AGENT_ENERGY, MAX_AGENT_HEALTH


class AgentMonitorWindow:
    """Shows the top-energy agent and compact stats for every agent."""

    def __init__(self, master=None):
        self.closed = False
        self.window = None
        self.agent_rows = {}

        if tk is None:
            self.closed = True
            return

        try:
            self.window = tk.Toplevel(master) if master is not None else tk.Tk()
        except tk.TclError:
            self.closed = True
            return

        self.window.title("Chaos Simulator - Agents")
        self.window.geometry("380x420+840+370")
        self.window.configure(bg="#10151b")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        title = tk.Label(
            self.window,
            text="Agent Monitor",
            bg="#10151b",
            fg="#ebeef5",
            font=("Arial", 15, "bold"),
        )
        title.pack(anchor="w", padx=14, pady=(14, 6))

        self.top_agent_label = tk.Label(
            self.window,
            bg="#10151b",
            fg="#ffc457",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.top_agent_label.pack(fill="x", padx=14, pady=(0, 10))

        self.list_frame = tk.Frame(self.window, bg="#10151b")
        self.list_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def update(self, agents):
        """Refresh agent leaderboard and status bars."""
        if self.closed:
            return

        try:
            top_agent = max(agents, key=lambda agent: agent.energy, default=None)
            if top_agent is None:
                self.top_agent_label.config(text="Top energy: none")
            else:
                self.top_agent_label.config(
                    text=(
                        f"Top energy: {top_agent.name} "
                        f"({top_agent.energy:.0f} energy, {top_agent.health:.0f} health)"
                    )
                )

            sorted_agents = sorted(agents, key=lambda agent: agent.energy, reverse=True)
            active_names = {agent.name for agent in sorted_agents}

            for name in list(self.agent_rows):
                if name not in active_names:
                    self.agent_rows[name]["frame"].destroy()
                    del self.agent_rows[name]

            for index, agent in enumerate(sorted_agents):
                row = self.agent_rows.get(agent.name)
                if row is None:
                    row = self.create_agent_row(agent)
                    self.agent_rows[agent.name] = row

                row["frame"].grid(row=index, column=0, sticky="ew", pady=3)
                row["name"].config(text=agent.name)
                row["health"].config(width=bar_width(agent.health, MAX_AGENT_HEALTH))
                row["energy"].config(width=bar_width(agent.energy, MAX_AGENT_ENERGY))
                row["stats"].config(
                    text=f"H {agent.health:5.1f}  E {agent.energy:5.1f}"
                )

            self.pump()
        except tk.TclError:
            self.closed = True

    def create_agent_row(self, agent):
        """Build one row for an agent."""
        frame = tk.Frame(self.list_frame, bg="#18202a", padx=8, pady=6)
        frame.columnconfigure(1, weight=1)

        name_label = tk.Label(
            frame,
            text=agent.name,
            bg="#18202a",
            fg="#ebeef5",
            width=9,
            anchor="w",
            font=("Arial", 10, "bold"),
        )
        name_label.grid(row=0, column=0, rowspan=2, sticky="w")

        health_bar = tk.Label(frame, bg="#4ec96f", height=1)
        health_bar.grid(row=0, column=1, sticky="w", padx=(8, 0), pady=1)

        energy_bar = tk.Label(frame, bg="#58a6ff", height=1)
        energy_bar.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=1)

        stats_label = tk.Label(
            frame,
            bg="#18202a",
            fg="#aab2be",
            font=("Arial", 9),
            anchor="e",
        )
        stats_label.grid(row=0, column=2, rowspan=2, padx=(8, 0), sticky="e")

        return {
            "frame": frame,
            "name": name_label,
            "health": health_bar,
            "energy": energy_bar,
            "stats": stats_label,
        }

    def close(self):
        """Close this UI window without closing the simulator."""
        self.closed = True
        if self.window is not None:
            try:
                self.window.destroy()
            except tk.TclError:
                pass

    def pump(self):
        """Process this window's events."""
        if self.closed:
            return

        self.window.update_idletasks()
        self.window.update()


def bar_width(value, maximum):
    """Convert a stat value into a Tk label width."""
    percent = max(0, min(1, value / maximum))
    return max(1, int(percent * 24))


def create_agent_monitor(master=None):
    """Create the agent monitor window."""
    return AgentMonitorWindow(master)
