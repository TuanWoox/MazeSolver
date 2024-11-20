import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import visualizeState  # Assuming this handles the maze visualization
from drawCustomMap import DrawCustomMap


class StartScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maze Solver Game")
        self.geometry("500x650")
        self.configure(bg="#2c3e50")

        # Center the window on the screen
        self.center_window(500, 650)

        # Display team members
        self.create_team_section()

        # Game title banner
        banner = tk.Label(
            self,
            text="Maze Solver Game",
            font=("Helvetica", 28, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50",
            pady=10,
        )
        banner.pack(pady=20)

        # Button configurations
        button_style = {
            "font": ("Helvetica", 14),
            "fg": "#2c3e50",
            "bg": "#ecf0f1",
            "activebackground": "#dcdde1",
            "activeforeground": "#2c3e50",
            "width": 20,
            "height": 2,
            "borderwidth": 0,
            "relief": "raised",
        }

        # Add buttons with hover effects
        self.create_hover_button("Play with Random Map", self.play_with_random_map, button_style)
        self.create_hover_button("Play with Loaded Map", self.open_map_selector, button_style)
        self.create_hover_button("Draw Custom Map", self.draw_custom_map, button_style)
        self.create_hover_button("Exit Game", self.destroy, button_style)

    def create_team_section(self):
        """Creates a neatly styled team member section at the top."""
        team_frame = tk.Frame(self, bg="#34495e", padx=10, pady=10)
        team_frame.pack(fill=tk.X, pady=(10, 0))

        team_label = tk.Label(
            team_frame,
            text="Team Members:",
            font=("Helvetica", 16, "bold"),
            fg="#ecf0f1",
            bg="#34495e",
        )
        team_label.pack(anchor="w", padx=10)

        team_members = [
            "Nguyễn Tiến Toàn - 22110078",
            "Bạch Đức Cảnh - 22110012",
            "Nguyễn Tuấn Vũ - 22110091",
            "Lý Đăng Triều - 22110080",
        ]
        for member in team_members:
            member_label = tk.Label(
                team_frame,
                text=member,
                font=("Helvetica", 14),
                fg="#ecf0f1",
                bg="#34495e",
                anchor="w",
            )
            member_label.pack(fill=tk.X, padx=20, pady=2)

    def create_hover_button(self, text, command, button_style):
        """Creates a button with hover effects."""
        button = tk.Button(self, text=text, command=command, **button_style)
        button.pack(pady=10)

        # Add hover effects
        button.bind("<Enter>", lambda e: button.configure(bg="#dcdde1"))
        button.bind("<Leave>", lambda e: button.configure(bg="#ecf0f1"))

    def center_window(self, width, height):
        """Centers the window on the screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width // 2) - (width // 2)
        y_position = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x_position}+{y_position}")

    def draw_custom_map(self):
        DrawCustomMap(self)  # Create an instance of DrawCustomMap and pass the main window

    def play_with_random_map(self):
        self.destroy()

        # Running randomMaze.py to generate a random maze
        subprocess.run(["python", "randomMaze.py"])
        maze_file = "maze.txt"

        if os.path.exists(maze_file):
            # Visualize the generated maze
            maze = visualizeState.Maze(maze_file)
            app = visualizeState.MazeApp(maze)
            app.mainloop()
        else:
            messagebox.showerror("Error", "Failed to generate random maze!")

    def open_map_selector(self):
        map_selector = tk.Toplevel(self)
        map_selector.title("Select a Map")

        window_width, window_height = 300, 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        map_selector.geometry(f"{window_width}x{window_height}+{x}+{y}")
        map_selector.configure(bg="#34495e")

        label = tk.Label(
            map_selector,
            text="Available Maps:",
            font=("Helvetica", 16, "bold"),
            fg="#ecf0f1",
            bg="#34495e",
        )
        label.pack(pady=10)

        save_dir = "./save"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for file in os.listdir(save_dir):
            if file.endswith(".txt"):
                map_name = file.replace(".txt", "")
                button = tk.Button(
                    map_selector,
                    text=map_name,
                    font=("Helvetica", 14),
                    fg="#2c3e50",
                    bg="#ecf0f1",
                    command=lambda f=file: self.load_selected_map(
                        os.path.join(save_dir, f), map_selector, self
                    ),
                )
                button.pack(pady=5)

    def load_selected_map(self, filename, map_selector_window, startScreen):
        # Close the map selector window
        map_selector_window.destroy()
        startScreen.destroy()

        # Initialize the maze with the selected file
        maze = visualizeState.Maze(filename)

        # Open the maze visualization in a new window
        app = visualizeState.MazeApp(maze)

        # Start the Tkinter main loop for the maze visualization
        app.mainloop()


if __name__ == "__main__":
    app = StartScreen()
    app.mainloop()
