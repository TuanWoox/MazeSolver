import sys
import tkinter as tk
from queue import Queue
import heapq
import subprocess

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
        self.cell_size = 25
        self.title("Maze Solver")
        self.canvas = tk.Canvas(self, width=self.maze.width * self.cell_size, height=self.maze.height * self.cell_size)
        self.canvas.pack()
        self.status_label = tk.Label(self, text="")
        self.status_label.pack()

        # Frame for buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side="top")

        # Button to generate a new maze
        self.generate_maze_button = tk.Button(self.button_frame, text="Generate Maze", command=self.generate_maze)
        self.generate_maze_button.pack(side="left")

        # Play mode button
        self.play_button = tk.Button(self.button_frame, text="Play Mode", command=self.start_play_mode)
        self.play_button.pack(side="left")

        # Buttons for different solve modes
        self.solve_bfs_button = tk.Button(self.button_frame, text="Solve with BFS", command=self.solve_maze_bfs)
        self.solve_bfs_button.pack(side="left")

        self.solve_dfs_button = tk.Button(self.button_frame, text="Solve with DFS", command=self.solve_maze_dfs)
        self.solve_dfs_button.pack(side="left")

        self.solve_a_star_button = tk.Button(self.button_frame, text="Solve with A*", command=self.solve_maze_a_star)
        self.solve_a_star_button.pack(side="left")

        self.solve_greedy_button = tk.Button(self.button_frame, text="Solve with Greedy", command=self.solve_maze_greedy)
        self.solve_greedy_button.pack(side="left")

        self.draw_maze()

    def generate_maze(self):
        # Call randomMaze.py to generate a new maze
        subprocess.run(["python", "randomMaze.py"])  # Adjust if you're using a different command to run your script
        self.maze = Maze("maze.txt")  # Reload the maze
        self.draw_maze()  # Refresh the maze display
        self.status_label.config(text="New maze generated!")

    def draw_maze(self):
        # (Unchanged) Your existing draw_maze implementation
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                if self.maze.walls[row][col]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")

        start_x, start_y = self.maze.start
        goal_x, goal_y = self.maze.goal

        self.canvas.create_oval(start_x * self.cell_size, start_y * self.cell_size,
                                (start_x + 1) * self.cell_size, (start_y + 1) * self.cell_size, fill="green")
        self.canvas.create_oval(goal_x * self.cell_size, goal_y * self.cell_size,
                                (goal_x + 1) * self.cell_size, (goal_y + 1) * self.cell_size, fill="red")

    def visualize(self, state):
        row, col = state
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="yellow")  # Color explored cells
        self.update()
        self.after(10)  # Pause for a moment to visualize

    def draw_path(self, path):
        for cell in path:
            row, col = cell
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue")  # Color path cells
            self.update()
            self.after(10)  # Pause for a moment to visualize

    def clear_cells(self):
        # Clear all non-wall cells to white
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                if not self.maze.walls[row][col]:  # Check if the cell is not a wall
                    x1 = col * self.cell_size
                    y1 = row * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")  # Clear cell
        self.update()

    def solve_maze_bfs(self):
        self.clear_cells()  # Clear all cells to white before solving
        self.solve_maze(self.maze.bfs_solve, "BFS")

    def solve_maze_dfs(self):
        self.clear_cells()  # Clear all cells to white before solving
        self.solve_maze(self.maze.dfs_solve, "DFS")

    def solve_maze_a_star(self):
        self.clear_cells()  # Clear all cells to white before solving
        self.solve_maze(self.maze.a_star_solve, "A*")

    def solve_maze_greedy(self):
        self.clear_cells()  # Clear all cells to white before solving
        self.solve_maze(self.maze.greedy_solve, "Greedy")

    def solve_maze(self, solve_method, method_name):
        self.status_label.config(text=f"Solving with {method_name}...")
        self.update()
        try:
            # First, explore the maze
            explored_path = solve_method(self.visualize)
            # Now, draw the path found
            self.draw_path(explored_path)
            # Assuming the maze object has these attributes
            num_explored = self.maze.num_explored  # Number of explored states
            steps_to_goal = len(explored_path)  # Assuming this gives the path length
            self.status_label.config(text=f"Solving with {method_name}, Explored States: {num_explored}, Steps to Goal: {steps_to_goal}")
        except Exception as e:
            self.status_label.config(text=str(e))

    def start_play_mode(self):
        # Implement the play mode logic
        pass

if __name__ == "__main__":
    maze_file = "maze.txt"  # Replace with the path to your maze file
    maze = Maze(maze_file)
    app = MazeApp(maze)
    app.mainloop()