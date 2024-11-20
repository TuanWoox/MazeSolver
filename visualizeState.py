import sys
import re
import tkinter as tk
from tkinter import simpledialog
from queue import Queue
import heapq
import subprocess
import os
import startScreen
from algorithms import Maze

class MazeApp(tk.Tk):
    def __init__(self, maze):
        super().__init__()
        self.attributes("-fullscreen", True) 
        self.maze = maze
        self.cell_size = 20  # Can be adjusted if needed
        self.title("Maze Solver")
        
        # Calculate window dimensions for a 15-inch screen (approx 1440px width)
        window_width = min(self.maze.width * self.cell_size + 40, 1440)
        window_height = self.maze.height * self.cell_size + 200
        self.configure(bg="#2c3e50")  # Set background color to match StartScreen

        # Center the window on the screen with calculated dimensions
        self.center_window(window_width, window_height)

        # Canvas and UI setup
        self.canvas = tk.Canvas(self, width=self.maze.width * self.cell_size, height=self.maze.height * self.cell_size, bg="#2c3e50", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=6, pady=(20, 10), padx=10)

        self.status_label = tk.Label(self, text="Welcome to Maze Solver", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#2c3e50")
        self.status_label.grid(row=1, column=0, columnspan=6, pady=(5, 10))

        # Button style for a modern look
        button_style = {
            "font": ("Arial", 12, "bold"),
            "fg": "#2c3e50",
            "bg": "#ecf0f1",
            "activebackground": "#1abc9c",  # A fresh green color for active state
            "activeforeground": "#2c3e50",
            "width": 18,
            "height": 2,
            "borderwidth": 0,
            "relief": "raised",
            "highlightthickness": 0,
            "cursor": "hand2",  # Makes it visually clear it's clickable
        }

        # Dropdown menu for solving algorithms
        self.selected_algorithm = tk.StringVar(value="Select Algorithm")
        algorithms = [
            "Solve BFS",
            "Solve DFS",
            "Solve A*",
            "Solve Greedy",
            "Solve Hill Climbing",
            "Solve Beam Search",
        ]
        self.algorithm_dropdown = tk.OptionMenu(self, self.selected_algorithm, *algorithms)
        self.algorithm_dropdown.config(
            font=("Arial", 12),
            fg="#2c3e50",
            bg="#ecf0f1",
            activebackground="#bdc3c7",
            activeforeground="#2c3e50",
            width=20,
            relief="flat",
        )
        # Place the dropdown in the first column
        self.algorithm_dropdown.grid(row=2, column=0, padx=(5, 5), pady=10)

        # Apply button for the selected algorithm
        self.apply_button = tk.Button(
            self,
            text="Apply",
            command=self.apply_algorithm,
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#3498db",  # A beautiful blue for the Apply button
            activebackground="#2980b9",
            activeforeground="#ecf0f1",
            width=15,
            height=2,
            relief="raised",
            borderwidth=0,
            cursor="hand2",  # Makes it visually clear it's clickable
        )
        # Place the "Apply" button in the second column, next to the dropdown
        self.apply_button.grid(row=2, column=1, padx=(5, 10), pady=10)

        tk.Button(self, text="Generate Maze", command=self.generate_maze, **button_style).grid(row=2, column=3, padx=5, pady=5)
        tk.Button(self, text="Play Mode", command=self.start_play_mode, **button_style).grid(row=2, column=4, padx=5, pady=5)
        # Save Map button
        tk.Button(self, text="Save Map", command=self.save_map, **button_style).grid(
            row=4, column=3, padx=(5, 10), pady=10
        )

        # Exit to Start Screen button
        tk.Button(self, text="Exit to Start Screen", command=self.exit_to_start_screen, **button_style).grid(
            row=4, column=4, padx=(10, 5), pady=10
        )
        


        # Draw the initial maze layout
        self.draw_maze()
    def center_window(self, width, height):
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the position to center the window
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)

        # Set the position of the window
        self.geometry(f'{width}x{height}+{position_right}+{position_top}')
    def apply_algorithm(self):
        """Applies the selected solving algorithm."""
        algorithm = self.selected_algorithm.get()
        if algorithm == "Solve BFS":
            self.solve_maze_bfs()
        elif algorithm == "Solve DFS":
            self.solve_maze_dfs()
        elif algorithm == "Solve A*":
            self.solve_maze_a_star()
        elif algorithm == "Solve Greedy":
            self.solve_maze_greedy()
        elif algorithm == "Solve Hill Climbing":
            self.solve_maze_hill_climb()
        elif algorithm == "Solve Beam Search":
            self.solve_maze_beam_search()
        else:
            self.status_label.config(text="Please select a valid algorithm!")
        
    def generate_maze(self):
        # Call randomMaze.py to generate a new maze
        subprocess.run(["python", "randomMaze.py"])
        self.maze = Maze("maze.txt")  # Reload the maze
        self.draw_maze()  # Refresh the maze display
        self.status_label.config(text="New maze generated!")

    def draw_maze(self):
        """
        Draw the maze on the canvas with walls, empty spaces, start, and goal.
        """
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Check what to draw
                if self.maze.walls[row][col]:  # Wall
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="white")
                elif (row, col) == self.maze.start:  # Start (A)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="white")
                elif (row, col) == self.maze.goal:  # Goal (B)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="white")
                else:  # Empty space
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="white")
        

    def visualize(self, state):
        row, col = state
        x1, y1 = col * self.cell_size, row * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="yellow", outline="yellow")
        self.update()
        self.after(10)

    def draw_path(self, path):
        for cell in path:
            row, col = cell
            x1, y1 = col * self.cell_size, row * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="blue")
            self.update()
            self.after(10)

    def clear_cells(self):
        """
        Clears all non-wall cells and redraws the start (red) and goal (green) cells.
        """
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                if not self.maze.walls[row][col]:
                    x1, y1 = col * self.cell_size, row * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="white")

        # Redraw the start (red) and goal (green) cells
        self.draw_special_cells()

        self.update()

    def draw_special_cells(self):
        """
        Redraws the start and goal cells with their respective colors.
        """
        start_row, start_col = self.maze.start
        goal_row, goal_col = self.maze.goal

        # Draw start cell (red)
        x1, y1 = start_col * self.cell_size, start_row * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="white")

        # Draw goal cell (green)
        x1, y1 = goal_col * self.cell_size, goal_row * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="white")

    def solve_maze_bfs(self):
        self.clear_cells()
        self.solve_maze(self.maze.bfs_solve, "BFS")

    def solve_maze_dfs(self):
        self.clear_cells()
        self.solve_maze(self.maze.dfs_solve, "DFS")

    def solve_maze_a_star(self):
        self.clear_cells()
        self.solve_maze(self.maze.a_star_solve, "A*")

    def solve_maze_greedy(self):
        self.clear_cells()
        self.solve_maze(self.maze.greedy_solve, "Greedy")
    def solve_maze_hill_climb(self):
        self.clear_cells()
        self.solve_maze(self.maze.hill_climb_solve, "Hill Climbing")

    def solve_maze_beam_search(self):
        self.clear_cells()
        self.solve_maze(lambda visualize: self.maze.beam_search_solve(visualize, beam_width=2), "Beam Search")

    def solve_maze(self, solve_method, method_name):
        self.status_label.config(text=f"Solving with {method_name}...")
        self.update()
        try:
            explored_path = solve_method(self.visualize)
            self.draw_path(explored_path)
            num_explored = self.maze.num_explored
            steps_to_goal = len(explored_path)
            self.status_label.config(text=f"Solving with {method_name}, Explored States: {num_explored}, Steps to Goal: {steps_to_goal}")
        except Exception as e:
            self.status_label.config(text=str(e))

    def save_map(self):
        # Ensure the './save' directory exists
        save_dir = "./save"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Prompt for filename
        filename = simpledialog.askstring("Save Map", "Enter filename (leave blank for default):")

        # Use default naming convention if no filename is provided
        if not filename:
            # Count existing map files in the save directory to set the next default filename
            existing_maps = [f for f in os.listdir(save_dir) if f.startswith("map") and f.endswith(".txt")]
            next_map_number = len(existing_maps) + 1
            filename = f"map{next_map_number}.txt"
        else:
            # Replace disallowed characters and ensure ".txt" extension
            filename = re.sub(r'[<>:"/\\|?*]', '', filename).strip()  # Remove disallowed characters
            if not filename.endswith(".txt"):
                filename += ".txt"

        # Create map file content
        map_content = []
        for i in range(self.maze.height):
            line = "".join(
                "A" if (i, j) == self.maze.start else
                "B" if (i, j) == self.maze.goal else
                " " if not self.maze.walls[i][j] else "#"
                for j in range(self.maze.width)
            )
            map_content.append(line)

        # Define the full path for the save file
        file_path = os.path.join(save_dir, filename)

        # Save the content to a file
        with open(file_path, "w") as f:
            f.write("\n".join(map_content))

        # Update the status label to confirm the save
        self.status_label.config(text=f"Map saved as '{file_path}'")


    def start_play_mode(self):
        """Activate play mode and allow user to navigate the maze."""
        self.clear_cells()  # Clear maze and reset

        # Set play mode to active
        self.play_mode_active = True

        # Set the player's starting position to the start of the maze
        self.player_position = self.maze.start

        # Reset steps taken
        self.steps_taken = 0  # Reset step counter

        # Display a status message to the user
        self.status_label.config(text=f"Play Mode: Use arrow keys to navigate! Steps: {self.steps_taken}")

        # Bind arrow keys for movement
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)
        self.bind("<Left>", self.move_left)
        self.bind("<Right>", self.move_right)

        # Update the maze display to highlight the player's starting position
        self.update_player_position()

    def move_up(self, event=None):
        """Move player up."""
        self.move_player((-1, 0))

    def move_down(self, event=None):
        """Move player down."""
        self.move_player((1, 0))

    def move_left(self, event=None):
        """Move player left."""
        self.move_player((0, -1))

    def move_right(self, event=None):
        """Move player right."""
        self.move_player((0, 1))

    def move_player(self, direction):
        """Move the player in the specified direction."""
        if not self.play_mode_active:
            return

        row, col = self.player_position
        d_row, d_col = direction
        new_position = (row + d_row, col + d_col)

        # Check if the new position is within bounds and not a wall
        if (
            0 <= new_position[0] < self.maze.height
            and 0 <= new_position[1] < self.maze.width
            and not self.maze.walls[new_position[0]][new_position[1]]
        ):
            self.player_position = new_position
            self.update_player_position()

            # Increment step count and update status label
            self.steps_taken += 1
            self.status_label.config(text=f"Play Mode: Use arrow keys to navigate! Steps: {self.steps_taken}")

            # Check if player reached the goal
            if new_position == self.maze.goal:
                self.status_label.config(text=f"Congratulations! You reached the goal! Total Steps: {self.steps_taken}")
                self.play_mode_active = False
                self.unbind("<Up>")
                self.unbind("<Down>")
                self.unbind("<Left>")
                self.unbind("<Right>")

    def update_player_position(self):
        """Update the player's position on the canvas."""
        self.canvas.delete("player")
        row, col = self.player_position
        x1, y1 = col * self.cell_size, row * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        self.canvas.create_oval(x1, y1, x2, y2, fill="green", tag="player")
    
    
    def exit_to_start_screen(self):
        self.destroy()
        bg_image_path = "background.gif"
        start_screen = startScreen.StartScreen(bg_image_path)  # Reopen the start screen
        start_screen.mainloop()

if __name__ == "__main__":
    print("Initializing Maze...")
    maze_file = "maze.txt"  # Replace with the path to your maze file
    maze = Maze(maze_file)
    app = MazeApp(maze)
    app.mainloop()
