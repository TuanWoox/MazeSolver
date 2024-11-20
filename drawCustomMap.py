import tkinter as tk
import os
from tkinter import messagebox

class DrawCustomMap:
    def __init__(self, master):
        self.master = master
        self.draw_window = tk.Toplevel(self.master)
        self.draw_window.title("Draw Your Map")

        # Set canvas size based on 27x14 grid and grid size (20px per cell)
        canvas_width, canvas_height = 55 * 20, 27 * 20
        self.canvas = tk.Canvas(self.draw_window, width=canvas_width, height=canvas_height, bg="#ecf0f1")
        self.canvas.pack()

        # Grid properties
        self.grid_size = 20  # 20px per grid cell
        self.grid = {}

        # Draw grid on the canvas for a 27x14 maze
        for y in range(0, canvas_height, self.grid_size):
            for x in range(0, canvas_width, self.grid_size):
                rect = self.canvas.create_rectangle(x, y, x + self.grid_size, y + self.grid_size, outline="black", fill="white")
                self.grid[rect] = ' '  # Initialize grid cells as empty

        # Buttons to mark start and goal
        self.current_marker = None
        start_button = tk.Button(self.draw_window, text="Set Start", command=self.set_start)
        start_button.pack(pady=5)

        goal_button = tk.Button(self.draw_window, text="Set Goal", command=self.set_goal)
        goal_button.pack(pady=5)

        # Save button
        save_button = tk.Button(self.draw_window, text="Save Map", command=self.save_custom_map)
        save_button.pack(pady=10)

        # Bind mouse click event to toggle wall, space, start, and goal
        self.canvas.bind("<Button-1>", self.toggle_cell)

    def set_start(self):
        # Toggle the start marker state
        if self.current_marker == 'A':
            self.remove_marker('A')  # Remove the start marker if it's already set
            self.current_marker = None  # Reset the mode to placing walls
        else:
            self.remove_marker('A')  # Ensure only one start marker is set at a time
            self.current_marker = 'A'  # Set the current marker to 'A' (start)

    def set_goal(self):
        # Toggle the goal marker state
        if self.current_marker == 'B':
            self.remove_marker('B')  # Remove the goal marker if it's already set
            self.current_marker = None  # Reset the mode to placing walls
        else:
            self.remove_marker('B')  # Ensure only one goal marker is set at a time
            self.current_marker = 'B'  # Set the current marker to 'B' (goal)

    def remove_marker(self, marker):
        # Remove the marker from the grid (if it exists)
        for rect, cell in self.grid.items():
            if cell == marker:
                self.canvas.itemconfig(rect, fill="white")
                self.grid[rect] = ' '  # Reset the cell to empty

    def toggle_cell(self, event):
        x, y = event.x, event.y
        # Find which cell was clicked
        rect_id = self.canvas.find_closest(x, y)[0]
        rect_coords = self.canvas.coords(rect_id)

        # Toggle between wall ('#'), space (' '), start ('A') and goal ('B')
        if self.current_marker is not None:
            if self.grid[rect_id] == ' ' or self.grid[rect_id] == '#':  # If the cell is empty or a wall
                if self.current_marker == 'A':  # If the current marker is 'A' (start)
                    self.canvas.itemconfig(rect_id, fill="green")
                elif self.current_marker == 'B':  # If the current marker is 'B' (goal)
                    self.canvas.itemconfig(rect_id, fill="red")
                self.grid[rect_id] = self.current_marker
                self.current_marker = None  # Reset the marker after placing start/goal
        else:
            # If no marker is set, toggle between wall ('#') and space (' ')
            if self.grid[rect_id] == ' ':
                self.canvas.itemconfig(rect_id, fill="black")  # Wall color
                self.grid[rect_id] = '#'
            elif self.grid[rect_id] == '#':
                self.canvas.itemconfig(rect_id, fill="white")  # Empty space
                self.grid[rect_id] = ' '

    def save_custom_map(self):
        # Calculate the number of columns and rows based on the canvas size and grid size
        width = self.canvas.winfo_width() // self.grid_size
        height = self.canvas.winfo_height() // self.grid_size

        # Initialize the maze with walls
        maze = [['#' for _ in range(width)] for _ in range(height)]

        start = None
        goal = None

        for rect, cell in self.grid.items():
            rect_coords = self.canvas.coords(rect)
            # Calculate the grid cell (x, y) from the rectangle coordinates
            x = int(rect_coords[0] // self.grid_size)
            y = int(rect_coords[1] // self.grid_size)

            # Ensure the coordinates are within bounds
            if 0 <= x < width and 0 <= y < height:
                if cell == 'A':
                    start = (x, y)
                elif cell == 'B':
                    goal = (x, y)
                maze[y][x] = cell

        # Ensure both start and goal are set
        if start and goal:
            # Save the maze to a file
            save_dir = './save'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            file_path = os.path.join(save_dir, "custom_maze.txt")
            with open(file_path, "w") as f:
                for row in maze:
                    f.write(''.join(row) + '\n')

            messagebox.showinfo("Maze Saved", "Your custom maze has been saved!")
            self.draw_window.destroy()  # Close the drawing window
        else:
            messagebox.showerror("Error", "Please set both the start and goal positions.")
