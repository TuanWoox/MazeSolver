import tkinter as tk
from tkinter import messagebox
import subprocess
import visualizeState
import os

class StartScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maze Solver Game")
        self.geometry("500x500")
        self.configure(bg="#2c3e50")
        
        # Center the window on the screen
        self.center_window(500, 500)

        banner = tk.Label(self, text="Maze Solver Game", font=("Helvetica", 28, "bold"), fg="#ecf0f1", bg="#2c3e50")
        banner.pack(pady=30)

        # Member info display
        member_info = [
            "Bach Duc Canh - 22110012",
            "Nguyen Tien Toan - 22110078",
            "Ly Dang Trieu - 22110080",
            "Nguyen Tuan Vu - 22110091",
        ]
        info_frame = tk.Frame(self, bg="#2c3e50")
        info_frame.pack(pady=10)
        
        for member in member_info:
            label = tk.Label(info_frame, text=member, font=("Helvetica", 14), fg="#bdc3c7", bg="#2c3e50")
            label.pack(anchor="w", padx=20)

        # Button configurations
        button_style = {
            "font": ("Helvetica", 14),
            "fg": "#2c3e50",
            "bg": "#ecf0f1",
            "activebackground": "#bdc3c7",
            "activeforeground": "#2c3e50",
            "width": 20,
            "height": 2,
            "borderwidth": 0,
            "relief": "raised",
        }

        random_map_button = tk.Button(self, text="Play with Random Map", command=self.play_with_random_map, **button_style)
        random_map_button.pack(pady=10)

        load_map_button = tk.Button(self, text="Play with Loaded Map", command=self.open_map_selector, **button_style)
        load_map_button.pack(pady=10)

        exit_button = tk.Button(self, text="Exit Game", command=self.destroy, **button_style)
        exit_button.pack(pady=10)

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width // 2) - (width // 2)
        y_position = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x_position}+{y_position}")

    def play_with_random_map(self):
        subprocess.run(["python", "randomMaze.py"])
        self.destroy()
        maze_file = "maze.txt"
        maze = visualizeState.Maze(maze_file)
        app = visualizeState.MazeApp(maze)
        app.mainloop()

    def open_map_selector(self):
        map_selector = tk.Toplevel(self)  # Initialize map_selector here
        map_selector.title("Select a Map")
        
        # Set window dimensions and center it on the screen
        window_width, window_height = 300, 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        map_selector.geometry(f"{window_width}x{window_height}+{x}+{y}")
        map_selector.configure(bg="#34495e")

        # Display maps in the './save' directory
        label = tk.Label(map_selector, text="Available Maps:", font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#34495e")
        label.pack(pady=10)

        # List available map files from './save'
        save_dir = "./save"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)  # Ensure the './save' directory exists

        for file in os.listdir(save_dir):
            if file.endswith(".txt"):
                map_name = file.replace(".txt", "")
                button = tk.Button(map_selector, text=map_name, font=("Helvetica", 14), fg="#2c3e50", bg="#ecf0f1",
                                command=lambda f=file: self.load_selected_map(os.path.join(save_dir, f), map_selector))
                button.pack(pady=5)

    def load_selected_map(self, filename, map_selector_window):
        map_selector_window.destroy()
        self.destroy()
        maze = visualizeState.Maze(filename)
        app = visualizeState.MazeApp(maze)
        app.mainloop()

if __name__ == "__main__":
    start_screen = StartScreen()
    start_screen.mainloop()