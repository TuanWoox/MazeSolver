import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import visualizeState  # Assuming this handles the maze visualization
import random
from drawCustomMap import DrawCustomMap

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

        draw_map_button = tk.Button(self, text="Draw Custom Map", command=self.draw_custom_map, **button_style)
        draw_map_button.pack(pady=10)

        exit_button = tk.Button(self, text="Exit Game", command=self.destroy, **button_style)
        exit_button.pack(pady=10)

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width // 2) - (width // 2)
        y_position = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x_position}+{y_position}")

    def draw_custom_map(self):
        DrawCustomMap(self)  # Create an instance of DrawCustomMap and pass the main window

    def play_with_random_map(self):
        self.destroy();
        
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

        label = tk.Label(map_selector, text="Available Maps:", font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#34495e")
        label.pack(pady=10)

        save_dir = "./save"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for file in os.listdir(save_dir):
            if file.endswith(".txt"):
                map_name = file.replace(".txt", "")
                button = tk.Button(map_selector, text=map_name, font=("Helvetica", 14), fg="#2c3e50", bg="#ecf0f1",
                                command=lambda f=file: self.load_selected_map(os.path.join(save_dir, f), map_selector))
                button.pack(pady=5)

    def load_selected_map(self, filename, map_selector_window):
        # Close the map selector window
        map_selector_window.destroy()

        # Initialize the maze with the selected file
        maze = visualizeState.Maze(filename)

        # Open the maze visualization in a new window
        app = visualizeState.MazeApp(maze)

        # Start the Tkinter main loop for the maze visualization
        app.mainloop()



if __name__ == "__main__":
    app = StartScreen()
    app.mainloop()
