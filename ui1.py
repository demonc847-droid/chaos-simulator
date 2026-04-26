"""Separate debug window for high-level simulation information.

This UI lives outside the Pygame window so it does not cover the arena.
"""

try:
    import tkinter as tk
except ImportError:
    tk = None


class DebugWindow:
    """Shows FPS, counts, chaos rule, and timing in a separate window."""

    def __init__(self, on_manual_chaos=None):
        self.closed = False
        self.root = None
        self.labels = {}
        self.on_manual_chaos = on_manual_chaos

        if tk is None:
            self.closed = True
            return

        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.closed = True
            return

        self.root.title("Chaos Simulator - Debug")
        self.root.geometry("320x260+840+80")
        self.root.configure(bg="#12161e")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        title = tk.Label(
            self.root,
            text="Simulation Debug",
            bg="#12161e",
            fg="#ebeef5",
            font=("Arial", 15, "bold"),
        )
        title.pack(anchor="w", padx=14, pady=(14, 8))

        for key in ("fps", "agents", "food", "chaos", "next_rule", "effect"):
            label = tk.Label(
                self.root,
                bg="#12161e",
                fg="#aab2be",
                font=("Arial", 11),
                anchor="w",
                justify="left",
            )
            label.pack(fill="x", padx=14, pady=3)
            self.labels[key] = label

        button = tk.Button(
            self.root,
            text="Trigger Chaos Now",
            command=self.trigger_manual_chaos,
            bg="#ffc457",
            fg="#10151b",
            activebackground="#ffd88a",
            activeforeground="#10151b",
            relief="flat",
            font=("Arial", 10, "bold"),
        )
        button.pack(fill="x", padx=14, pady=(12, 14))

    def trigger_manual_chaos(self):
        """Run the manual chaos callback if one was provided."""
        if self.on_manual_chaos is not None:
            self.on_manual_chaos()

    def update(self, clock, agents, foods, chaos):
        """Refresh the debug text and keep the window responsive."""
        if self.closed:
            return

        self.labels["fps"].config(text=f"FPS: {clock.get_fps():.0f}")
        self.labels["agents"].config(text=f"Agent count: {len(agents)}")
        self.labels["food"].config(text=f"Food count: {len(foods)}")
        self.labels["chaos"].config(text=f"Current chaos rule: {chaos.rule_name}")
        self.labels["next_rule"].config(
            text=f"Time until next rule: {max(0, int(chaos.time_until_next_rule))}s"
        )
        self.labels["effect"].config(text=f"Effect: {chaos.rule_description}")
        self.pump()

    def pump(self):
        """Process window events without taking over the main game loop."""
        if self.closed:
            return

        try:
            self.root.update_idletasks()
            self.root.update()
        except tk.TclError:
            self.closed = True

    def close(self):
        """Close this UI window without closing the simulator."""
        self.closed = True
        if self.root is not None:
            try:
                self.root.destroy()
            except tk.TclError:
                pass


def create_debug_window(on_manual_chaos=None):
    """Create the debug window, or a disabled object if Tk is unavailable."""
    return DebugWindow(on_manual_chaos)
