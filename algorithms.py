
from queue import Queue
import heapq

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
        self.filename = filename;
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