import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

DATA_FILE = Path(__file__).with_name("goal_tracker.json")

DEFAULT_GOALS = [
    {"name": "Goal 1 (Name)", "color": "#FF0000", "history": [True]*5 + [False]*2 + [True]*2 + [True]*3 + [False]*19},
    {"name": "Goal 2 (Name)", "color": "#FBFF00", "history": [True]*11 + [False]*20},
    {"name": "Goal 3 (Name)", "color": "#2200FF", "history": [True]*6 + [False]*25},
    {"name": "Goal 4 (Name)", "color": "#00FF0D", "history": [True]*1 + [False]*30},
]

MONTHS = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
]

COLORS = ["#7A92C5", "#70C1B3", "#81C784", "#FFB74D", "#BA68C8", "#F06292"]

THEMES = {
    "Light": {
        "bg": "#FFFFFF", "fg": "#2C3E50", "card_bg": "#FAFAFA",
        "graph_bg": "#000000", "graph_grid": "#333333",
        "up_color": "#2ECC71", "down_color": "#E74C3C", "flat_color": "#BDC3C7",
        "watermark": "#EBEBEB"
    },
    "Dark": {
        "bg": "#121212", "fg": "#E0E0E0", "card_bg": "#1E1E1E",
        "graph_bg": "#050505", "graph_grid": "#222222",
        "up_color": "#00E676", "down_color": "#FF5252", "flat_color": "#B0BEC5",
        "watermark": "#1F1F1F"
    }
}

class DigitalGoalTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Daily Goal Tracker Pro")
        self.geometry("1150x960")
        
        self.is_dark_mode = False
        self.user_name_var = tk.StringVar(value="User Name")
        self.selected_month_var = tk.StringVar(value="January")
        self.selected_map_var = tk.StringVar(value="Progress Map (Line Trend)")
        
        self.goals = self.load_goals()
        self.build_ui()

    def get_theme(self):
        return THEMES["Dark"] if self.is_dark_mode else THEMES["Light"]

    def calculate_stats(self):
        if not self.goals:
            return 0.0, 0
        
        total_possible = len(self.goals) * 31
        total_completed = sum(sum(goal["history"]) for goal in self.goals)
        accuracy = (total_completed / total_possible) * 100 if total_possible > 0 else 0.0
        
        # Calculate Consistency Streak (consecutive days with at least 1 goal completed)
        current_streak = 0
        max_streak = 0
        for day_idx in range(31):
            day_done = any(goal["history"][day_idx] for goal in self.goals)
            if day_done:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
                
        return accuracy, max_streak

    def build_ui(self):
        theme = self.get_theme()
        self.configure(bg=theme["bg"])

        # Top Control Bar
        top_bar = tk.Frame(self, bg=theme["bg"])
        top_bar.pack(fill="x", padx=20, pady=(15, 2))

        title_label = tk.Label(
            top_bar, text="Daily Goal Tracker", font=("Dancing Script", 26, "bold"),
            bg=theme["bg"], fg=theme["fg"]
        )
        title_label.pack(side="left")

        toggle_btn_text = "☀️*Light Mode" if not self.is_dark_mode else "🌙*Dark Mode"
        toggle_btn_bg = "#333333" if self.is_dark_mode else "#E0E0E0"
        toggle_btn_fg = "#FFFFFF" if self.is_dark_mode else "#000000"

        dark_mode_btn = tk.Button(
            top_bar, text=toggle_btn_text, font=("Arial", 10, "bold"),
            bg=toggle_btn_bg, fg=toggle_btn_fg, relief="flat", padx=10, pady=3,
            cursor="hand2", command=self.toggle_dark_mode
        )
        dark_mode_btn.pack(side="right")

        # User Info, Month, and Stats Cards
        meta_frame = tk.Frame(self, bg=theme["bg"])
        meta_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(meta_frame, text="_NAME_:", font=("Arial", 10, "bold"), bg=theme["bg"], fg=theme["fg"]).pack(side="left", padx=(0, 5))
        ttk.Entry(meta_frame, textvariable=self.user_name_var, width=15).pack(side="left", padx=(0, 15))

        tk.Label(meta_frame, text="_MONTH_:", font=("Arial", 10, "bold"), bg=theme["bg"], fg=theme["fg"]).pack(side="left", padx=(0, 5))
        ttk.Combobox(meta_frame, textvariable=self.selected_month_var, values=MONTHS, state="readonly", width=10).pack(side="left", padx=(0, 20))

        # Stats Displays
        accuracy, streak = self.calculate_stats()
        
        stats_frame = tk.Frame(meta_frame, bg=theme["bg"])
        stats_frame.pack(side="right")

        acc_label = tk.Label(
            stats_frame, text=f"🎯 Accuracy: {accuracy:.1f}%", font=("Arial", 10, "bold"),
            bg="#2ECC71" if accuracy >= 50 else "#E74C3C", fg="white", padx=8, pady=3
        )
        acc_label.pack(side="left", padx=5)

        streak_label = tk.Label(
            stats_frame, text=f"🔥 Consistency: {streak} Days", font=("Arial", 10, "bold"),
            bg="#3498DB", fg="white", padx=8, pady=3
        )
        streak_label.pack(side="left", padx=5)

        divider = tk.Frame(self, bg="#D3D3D3", height=1)
        divider.pack(fill="x", padx=20, pady=(8, 8))

        # Main Table Container Frame
        table_container = tk.Frame(self, bg=theme["bg"])
        table_container.pack(padx=20, pady=2, fill="both", expand=True)

        self.watermark_label = tk.Label(
            table_container, text="Life is imp", font=("Arial", 50, "bold"),
            bg=theme["bg"], fg=theme["watermark"]
        )
        self.watermark_label.place(relx=0.5, rely=0.5, anchor="center")

        self.table_frame = tk.Frame(table_container, bg="", highlightbackground="#CEE3B6", highlightthickness=1)
        self.table_frame.pack(fill="both", expand=True)

        # Add Goal Controls Frame
        add_frame = tk.Frame(self, bg=theme["bg"])
        add_frame.pack(pady=5)

        tk.Label(add_frame, text="_NEW MISSION_:", font=("Arial", 10, "bold"), bg=theme["bg"], fg=theme["fg"]).pack(side="left", padx=5)
        self.goal_entry = ttk.Entry(add_frame, width=25)
        self.goal_entry.pack(side="left", padx=5)
        self.goal_entry.bind("<Return>", lambda e: self.add_goal())

        ttk.Button(add_frame, text="+ Add New Goal", command=self.add_goal).pack(side="left", padx=5)

        # Map Selector Controls
        map_select_frame = tk.Frame(self, bg=theme["bg"])
        map_select_frame.pack(fill="x", padx=20, pady=(5, 0))

        tk.Label(map_select_frame, text="Select Analytics View:", font=("Arial", 10, "bold"), bg=theme["bg"], fg=theme["fg"]).pack(side="left", padx=5)
        map_combo = ttk.Combobox(
            map_select_frame, textvariable=self.selected_map_var, 
            values=["Progress Map (Line Trend)", "Goal Accuracy (Bar Chart)"], 
            state="readonly", width=25
        )
        map_combo.pack(side="left", padx=5)
        map_combo.bind("<<ComboboxSelected>>", lambda e: self.draw_selected_map())

        # Bottom Analytics Map Container
        self.graph_box = tk.LabelFrame(
            self, text=" Analytics Dashboard ",
            font=("Arial", 10, "bold"), bg=theme["graph_bg"], fg="#FFFFFF", padx=10, pady=5
        )
        self.graph_box.pack(fill="x", padx=20, pady=(5, 10))

        self.canvas = tk.Canvas(self.graph_box, bg=theme["graph_bg"], height=200, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.render_grid()

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()

    def render_grid(self):
        theme = self.get_theme()
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.table_frame, text="Goals", font=("Arial", 10, "bold"),
            bg=theme["card_bg"], fg=theme["fg"], width=18, relief="groove", pady=6
        ).grid(row=0, column=0, sticky="nsew")

        for day in range(1, 32):
            tk.Label(
                self.table_frame, text=str(day), font=("Arial", 8, "bold"),
                bg=theme["card_bg"], fg=theme["fg"], width=2, relief="groove", pady=6
            ).grid(row=0, column=day, sticky="nsew")

        for g_idx, goal in enumerate(self.goals):
            tk.Label(
                self.table_frame, text=goal["name"], font=("Arial", 9),
                bg=theme["bg"], fg=theme["fg"], anchor="w", padx=8, relief="groove"
            ).grid(row=g_idx+1, column=0, sticky="nsew")

            for day_idx in range(31):
                is_done = goal["history"][day_idx]
                bg_color = goal["color"] if is_done else theme["card_bg"]
                text_symbol = "✓" if is_done else ""
                fg_color = "white" if is_done else "#A0A0A0"

                btn = tk.Button(
                    self.table_frame, text=text_symbol, font=("Arial", 8, "bold"),
                    bg=bg_color, fg=fg_color, activebackground=goal["color"],
                    relief="flat", bd=1, highlightthickness=1, highlightbackground="#CCCCCC",
                    command=lambda g=g_idx, d=day_idx: self.toggle_day(g, d)
                )
                btn.grid(row=g_idx+1, column=day_idx+1, padx=1, pady=1, ipady=3, sticky="nsew")

        self.draw_selected_map()

    def draw_selected_map(self):
        map_type = self.selected_map_var.get()
        if map_type == "Goal Accuracy (Bar Chart)":
            self.draw_bar_chart()
        else:
            self.draw_progress_map()

    def draw_progress_map(self):
        self.canvas.delete("all")
        theme = self.get_theme()
        
        daily_counts = [0] * 31
        for goal in self.goals:
            for day_idx in range(31):
                if goal["history"][day_idx]:
                    daily_counts[day_idx] += 1

        width = self.canvas.winfo_width() or 1000
        height = 180
        padding_x = 30
        padding_y = 20

        max_goals = len(self.goals) if len(self.goals) > 0 else 1
        x_step = (width - 2 * padding_x) / 30

        for i in range(31):
            x = padding_x + (i * x_step)
            self.canvas.create_line(x, padding_y, x, height - padding_y, fill=theme["graph_grid"], width=1, stipple="gray25")

        points = []
        for i, count in enumerate(daily_counts):
            x = padding_x + (i * x_step)
            y = (height - padding_y) - ((count / max_goals) * (height - 2 * padding_y))
            points.append((x, y, count))

        base_y = height - padding_y
        polygon_coords = [points[0][0], base_y]
        for x, y, _ in points:
            polygon_coords.extend([x, y])
        polygon_coords.extend([points[-1][0], base_y])

        self.canvas.create_polygon(polygon_coords, fill=theme["graph_grid"], outline="", stipple="gray50")

        for i in range(len(points)):
            x, y, count = points[i]
            color = theme["flat_color"] if i == 0 else (
                theme["up_color"] if count > points[i-1][2] else (
                    theme["down_color"] if count < points[i-1][2] else theme["flat_color"]
                )
            )

            if i > 0:
                self.canvas.create_line(points[i-1][0], points[i-1][1], x, y, fill=color, width=2)

            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="#111111", width=1)

    def draw_bar_chart(self):
        self.canvas.delete("all")
        theme = self.get_theme()

        if not self.goals:
            return

        width = self.canvas.winfo_width() or 1000
        height = 180
        padding_x = 40
        padding_y = 25

        num_goals = len(self.goals)
        bar_width = min(40, (width - 2 * padding_x) / (num_goals * 1.5))
        gap = bar_width * 0.5

        for g_idx, goal in enumerate(self.goals):
            completed = sum(goal["history"])
            accuracy = (completed / 31) * 100

            x0 = padding_x + g_idx * (bar_width + gap)
            x1 = x0 + bar_width
            
            y_max = height - padding_y
            bar_h = (accuracy / 100) * (height - 2 * padding_y)
            y0 = y_max - bar_h

            self.canvas.create_rectangle(x0, y0, x1, y_max, fill=goal["color"], outline="#120606")
            self.canvas.create_text(x0 + bar_width/2, y0 - 10, text=f"{accuracy:.0f}%", fill=theme["fg"], font=("Arial", 8, "bold"))
            self.canvas.create_text(x0 + bar_width/2, y_max + 12, text=goal["name"][:8], fill=theme["fg"], font=("Arial", 8))

    def toggle_day(self, goal_idx, day_idx):
        self.goals[goal_idx]["history"][day_idx] = not self.goals[goal_idx]["history"][day_idx]
        self.save_goals()
        # Refresh UI including Stats
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()

    def add_goal(self):
        name = self.goal_entry.get().strip()
        if not name:
            messagebox.showwarning("अपूर्ण माहिती", "कृपया ध्येयाचे नाव टाका.")
            return

        color = COLORS[len(self.goals) % len(COLORS)]
        self.goals.append({"name": name, "color": color, "history": [False] * 31})
        self.save_goals()
        
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()

    def load_goals(self):
        if not DATA_FILE.exists():
            DATA_FILE.write_text(json.dumps(DEFAULT_GOALS, ensure_ascii=False, indent=2), encoding="utf-8")
            return DEFAULT_GOALS
        try:
            content = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return content if isinstance(content, list) else DEFAULT_GOALS
        except (FileNotFoundError, json.JSONDecodeError):
            return DEFAULT_GOALS

    def save_goals(self):
        DATA_FILE.write_text(json.dumps(self.goals, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    app = DigitalGoalTracker()
    app.bind("<Configure>", lambda e: app.draw_selected_map())
    app.mainloop()