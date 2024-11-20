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
    def hill_climb_solve(self, visualize):
        """Hill Climbing Search."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        self.explored = set()

        current_node = start
        while True:
            self.num_explored += 1
            visualize(current_node.state)

            if current_node.state == self.goal:
                return self.backtrack_solution(current_node)

            self.explored.add(current_node.state)

            # Get all neighbors and sort by heuristic value (ascending)
            neighbors = [
                Node(state=state, parent=current_node, action=action)
                for action, state in self.neighbors(current_node.state)
                if state not in self.explored
            ]
            for neighbor in neighbors:
                neighbor.priority = self.heuristic(neighbor.state)

            if not neighbors:
                raise Exception("No solution found with Hill Climbing (stuck in local minima).")

            # Choose the neighbor with the best heuristic (smallest value)
            best_neighbor = min(neighbors, key=lambda x: x.priority)

            # If no improvement, stop (local minimum reached)
            if self.heuristic(current_node.state) <= best_neighbor.priority:
                raise Exception("No solution found with Hill Climbing (local minima).")

            current_node = best_neighbor
    def beam_search_solve(self, visualize, beam_width=2):
        """Beam Search."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        self.explored = set()

        frontier = [(self.heuristic(start.state), start)]  # Priority queue of (heuristic, node)

        while frontier:
            self.num_explored += len(frontier)

            # Sort frontier by heuristic and keep only the best `beam_width` nodes
            frontier.sort(key=lambda x: x[0])
            frontier = frontier[:beam_width]

            next_frontier = []
            for _, node in frontier:
                visualize(node.state)

                if node.state == self.goal:
                    return self.backtrack_solution(node)

                self.explored.add(node.state)
                for action, state in self.neighbors(node.state):
                    if state not in self.explored:
                        child = Node(state=state, parent=node, action=action)
                        child.priority = self.heuristic(state)
                        next_frontier.append((child.priority, child))

            frontier = next_frontier

        raise Exception("No solution found with Beam Search.")


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

        # Buttons in a single row for generation and solving
        tk.Button(self, text="Generate Maze", command=self.generate_maze, **button_style).grid(
            row=2, column=0, padx=5, pady=5
        )
        tk.Button(self, text="Play Mode", command=self.start_play_mode, **button_style).grid(
            row=2, column=1, padx=5, pady=5
        )
        tk.Button(self, text="Solve BFS", command=self.solve_maze_bfs, **button_style).grid(
            row=2, column=2, padx=5, pady=5
        )
        tk.Button(self, text="Solve DFS", command=self.solve_maze_dfs, **button_style).grid(
            row=2, column=3, padx=5, pady=5
        )
        tk.Button(self, text="Solve  A*", command=self.solve_maze_a_star, **button_style).grid(
            row=2, column=4, padx=5, pady=5
        )
        tk.Button(self, text="Solve Greedy", command=self.solve_maze_greedy, **button_style).grid(
            row=2, column=5, padx=5, pady=5
        )

        # Additional solving algorithms and utility buttons in the next row
        tk.Button(self, text="Solve Hill Climbing", command=self.solve_maze_hill_climb, **button_style).grid(
            row=3, column=0, padx=5, pady=5
        )
        tk.Button(self, text="Solve Beam Search", command=self.solve_maze_beam_search, **button_style).grid(
            row=3, column=1, padx=5, pady=5
        )
        tk.Button(self, text="Save Map", command=self.save_map, **button_style).grid(
            row=3, column=4, padx=5, pady=5
        )
        tk.Button(self, text="Exit to Start Screen", command=self.exit_to_start_screen, **button_style).grid(
            row=3, column=5, padx=5, pady=5
        )



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
        start_screen = startScreen.StartScreen()  # Reopen the start screen
        start_screen.mainloop()



if __name__ == "__main__":
    print("Initializing Maze...")
    maze_file = "maze.txt"  # Replace with the path to your maze file
    maze = Maze(maze_file)
    app = MazeApp(maze)
    app.mainloop()
