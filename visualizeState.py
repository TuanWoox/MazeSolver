import sys
import re
import tkinter as tk
from tkinter import simpledialog
from queue import Queue
import heapq
import subprocess
import os
import startScreen

class Node:
    def __init__(self, state, parent=None, action=None, cost=0, priority=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

class Maze:
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()

        if contents.count("A") != 1 or contents.count("B") != 1:
            raise Exception("Maze must have exactly one start point and one goal")

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None
        self.num_explored = 0

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]
        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def bfs_solve(self, visualize):
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        self.explored = set()

        frontier = Queue()
        frontier.put(start)

        while not frontier.empty():
            node = frontier.get()
            self.num_explored += 1
            visualize(node.state)  # Visualize explored state

            if node.state == self.goal:
                return self.backtrack_solution(node)

            self.explored.add(node.state)
            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.put(child)

        raise Exception("no solution")

    def dfs_solve(self, visualize):
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        self.explored = set()

        frontier = []  # Using a list as a stack
        frontier.append(start)

        while frontier:
            node = frontier.pop()
            self.num_explored += 1
            visualize(node.state)  # Visualize explored state

            if node.state == self.goal:
                return self.backtrack_solution(node)

            self.explored.add(node.state)
            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.append(child)

        raise Exception("no solution")

    def greedy_solve(self, visualize):
        """Greedy Best-First Search."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        start.priority = self.heuristic(start.state)
        self.explored = set()

        frontier = []
        heapq.heappush(frontier, (start.priority, start))

        while frontier:
            _, node = heapq.heappop(frontier)
            self.num_explored += 1
            visualize(node.state)  # Visualize explored state

            if node.state == self.goal:
                return self.backtrack_solution(node)

            self.explored.add(node.state)
            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    child.priority = self.heuristic(state)
                    heapq.heappush(frontier, (child.priority, child))

        raise Exception("No solution found with Greedy Best-First Search.")

    def a_star_solve(self, visualize):
        """A* Search."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None, cost=0)
        start.priority = self.heuristic(start.state)
        self.explored = set()

        frontier = []
        heapq.heappush(frontier, (start.priority, start))

        while frontier:
            _, node = heapq.heappop(frontier)
            self.num_explored += 1
            visualize(node.state)  # Visualize explored state

            if node.state == self.goal:
                return self.backtrack_solution(node)

            self.explored.add(node.state)
            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    child = Node(state=state, parent=node, action=action, cost=node.cost + 1)
                    child.priority = child.cost + self.heuristic(state)
                    heapq.heappush(frontier, (child.priority, child))

        raise Exception("No solution found with A* Search.")

    def backtrack_solution(self, node):
        actions = []
        cells = []
        while node.parent is not None:
            actions.append(node.action)
            cells.append(node.state)
            node = node.parent
        actions.reverse()
        cells.reverse()
        self.solution = (actions, cells)
        return cells  # Return cells in the found path

    def heuristic(self, state):
        """A* heuristic that combines Manhattan distance with a bias toward open cells near the goal."""
        row, col = state
        goal_row, goal_col = self.goal

        # Calculate the basic Manhattan distance to the goal (B)
        base_distance = abs(row - goal_row) + abs(col - goal_col)

        # Initialize the minimum distance to an adjacent empty cell near the goal (B)
        min_distance_to_empty = float('inf')

        # Check the neighboring cells of the goal (B)
        for r_offset, c_offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor_row = goal_row + r_offset
            neighbor_col = goal_col + c_offset

            # Ensure the neighbor is within bounds
            if 0 <= neighbor_row < self.height and 0 <= neighbor_col < self.width:
                # Check if the neighbor is an empty cell
                if not self.walls[neighbor_row][neighbor_col]:
                    # Calculate the distance from the current state to this empty cell
                    distance_to_empty = abs(row - neighbor_row) + abs(col - neighbor_col)
                    min_distance_to_empty = min(min_distance_to_empty, distance_to_empty)

        # If we found an empty neighboring cell, prioritize paths leading to it
        if min_distance_to_empty < float('inf'):
            return base_distance + min_distance_to_empty  # Encourage moving towards nearby empty cells

        return base_distance  # Fallback to the base Manhattan distance
    
class MazeApp(tk.Tk):
    def __init__(self, maze):
        super().__init__()
        self.maze = maze
        self.cell_size = 20  # Can be adjusted if needed
        self.title("Maze Solver")
        
        # Calculate window dimensions based on maze size
        window_width = max(self.maze.width * self.cell_size + 40, 600)
        window_height = self.maze.height * self.cell_size + 150
        self.configure(bg="#2c3e50")  # Set background color to match StartScreen

        # Center the window on the screen with calculated dimensions
        self.center_window(window_width, window_height)

        # Canvas and UI setup
        self.canvas = tk.Canvas(self, width=self.maze.width * self.cell_size, height=self.maze.height * self.cell_size, bg="#2c3e50", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=6, pady=(20, 10), padx=10)

        self.status_label = tk.Label(self, text="", font=("Helvetica", 12), fg="#ecf0f1", bg="#2c3e50")
        self.status_label.grid(row=1, column=0, columnspan=6, pady=(5, 10))

        # Button layout remains unchanged
        button_style = {
            "font": ("Helvetica", 12),
            "fg": "#2c3e50",
            "bg": "#ecf0f1",
            "activebackground": "#bdc3c7",
            "activeforeground": "#2c3e50",
            "width": 15,
            "height": 1,
            "borderwidth": 0,
            "relief": "raised",
        }

        # Buttons in a single row
        tk.Button(self, text="Generate Maze", command=self.generate_maze, **button_style).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(self, text="Play Mode", command=self.start_play_mode, **button_style).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self, text="Solve with BFS", command=self.solve_maze_bfs, **button_style).grid(row=2, column=2, padx=5, pady=5)
        tk.Button(self, text="Solve with DFS", command=self.solve_maze_dfs, **button_style).grid(row=2, column=3, padx=5, pady=5)
        tk.Button(self, text="Solve with A*", command=self.solve_maze_a_star, **button_style).grid(row=2, column=4, padx=5, pady=5)
        tk.Button(self, text="Solve with Greedy", command=self.solve_maze_greedy, **button_style).grid(row=2, column=5, padx=5, pady=5)
        
        # Exit button in a separate row
        tk.Button(self, text="Save Map", command=self.save_map, **button_style).grid(row=3, column=0, columnspan=3, pady=(10, 20))
        tk.Button(self, text="Exit to Start Screen", command=self.exit_to_start_screen, **button_style).grid(row=3, column=3, columnspan=3, pady=(10, 20))

        # Draw the initial maze layout
        self.draw_maze()
    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width // 2) - (width // 2)
        y_position = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x_position}+{y_position}")
    def generate_maze(self):
        # Call randomMaze.py to generate a new maze
        subprocess.run(["python", "randomMaze.py"])
        self.maze = Maze("maze.txt")  # Reload the maze
        self.draw_maze()  # Refresh the maze display
        self.status_label.config(text="New maze generated!")

    def draw_maze(self):
        self.canvas.delete("all")
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                x1, y1 = col * self.cell_size, row * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                color = "black" if self.maze.walls[row][col] else "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

        # Start and goal positions
        start_x, start_y = self.maze.start
        goal_x, goal_y = self.maze.goal
        self.canvas.create_oval(start_x * self.cell_size, start_y * self.cell_size,
                                (start_x + 1) * self.cell_size, (start_y + 1) * self.cell_size, fill="green")
        self.canvas.create_oval(goal_x * self.cell_size, goal_y * self.cell_size,
                                (goal_x + 1) * self.cell_size, (goal_y + 1) * self.cell_size, fill="red")

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
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                if not self.maze.walls[row][col]:
                    x1, y1 = col * self.cell_size, row * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="white")
        self.update()

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
        # Implement play mode logic if needed
        pass

    def exit_to_start_screen(self):
        self.destroy()
        start_screen = startScreen.StartScreen()  # Reopen the start screen
        start_screen.mainloop()



if __name__ == "__main__":
    print("Initializing Maze...")
    maze_file = "maze.txt"  # Replace with the path to your maze file
    maze = Maze(maze_file)
    app = MazeApp(maze)
    app.mainloop()
