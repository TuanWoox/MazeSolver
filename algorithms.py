
from queue import Queue
import heapq
import random
import time

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
    def reset_state(self):
        """Resets maze state for a new solving attempt."""
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
        """Solve the maze using the Breadth-First Search algorithm."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)

        # Use a set to track explored states
        self.explored = set()

        # Initialize the frontier with the starting node
        frontier = Queue()
        frontier.put(start)
        
        # Use a set to track nodes in the frontier to avoid re-adding them
        frontier_states = set()
        frontier_states.add(start.state)

        # Start timing
        start_time = time.time()

        while not frontier.empty():
            # Get the next node from the frontier
            node = frontier.get()
            frontier_states.remove(node.state)
            self.num_explored += 1

            # Visualize the explored state
            visualize(node.state)

            # If this node contains the goal state, reconstruct the solution
            if node.state == self.goal:
                end_time = time.time()  # End timing
                elapsed_time = end_time - start_time  # Calculate elapsed time
                return elapsed_time, self.backtrack_solution(node)

            # Mark the state as explored
            self.explored.add(node.state)

            # Add neighbors to the frontier
            for action, state in self.neighbors(node.state):
                if state not in self.explored and state not in frontier_states:
                    child = Node(state=state, parent=node, action=action)
                    frontier.put(child)
                    frontier_states.add(state)

        raise Exception("no solution")


    def dfs_solve(self, visualize):
        """Improved DFS with intelligent restarts, randomization, and backtracking."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)

        # Set to track explored states
        self.explored = set()

        # Initialize the frontier as a stack
        frontier = [start]

        # Track visited nodes to prevent redundant restarts
        visited_once = set()
        start_time = time.time()

        while frontier:
            # Pop the last node from the stack
            node = frontier.pop()
            self.num_explored += 1

            # Visualize the current state
            visualize(node.state)

            if node.state == self.goal:
                end_time = time.time()  # Record end time when solution is found
                elapsed_time = end_time - start_time  # Calculate time taken
                return elapsed_time, self.backtrack_solution(node)  # Return solution and time taken

            # Mark the current state as explored
            self.explored.add(node.state)

            # Get neighbors and shuffle them for randomization
            neighbors = list(self.neighbors(node.state))
            random.shuffle(neighbors)  # Randomly shuffle the neighbors

            # Add neighbors to the frontier
            neighbors_added = False
            for action, state in neighbors:
                if state not in self.explored and state not in visited_once:
                    child = Node(state=state, parent=node, action=action)
                    frontier.append(child)
                    neighbors_added = True
                    visited_once.add(state)  # Mark neighbor as visited at least once

            # If no neighbors were added, backtrack intelligently or reset
            if not neighbors_added:
                # If the frontier is empty, check if reset is necessary
                if not frontier:
                    unvisited = [state for state in visited_once if state not in self.explored]
                    if unvisited:
                        # Restart from the nearest unexplored node to the start
                        closest_unvisited = min(unvisited, key=lambda s: self.heuristic(s))
                        frontier.append(Node(state=closest_unvisited, parent=None, action=None))
                    else:
                        # Restart completely if no unvisited nodes are found
                        frontier.append(start)

        raise Exception("No solution found using DFS.")





    def greedy_solve(self, visualize):
        """Greedy Best-First Search optimized for speed and memory."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        start.priority = self.heuristic(start.state)

        # Use sets to track explored and frontier states
        self.explored = set()
        frontier = []
        frontier_set = set()

        heapq.heappush(frontier, (start.priority, start))
        frontier_set.add(start.state)
        start_time = time.time()
        while frontier:
            _, node = heapq.heappop(frontier)
            frontier_set.remove(node.state)
            self.num_explored += 1

            # Visualize greedy state based only on heuristic value
            visualize(node.state, algorithm='Greedy', value=node.priority)

            if node.state == self.goal:
                end_time = time.time()  # Record end time when solution is found
                elapsed_time = end_time - start_time  # Calculate time taken
                return elapsed_time, self.backtrack_solution(node)  # Return solution and time taken

            self.explored.add(node.state)

            # Process neighbors
            for action, state in self.neighbors(node.state):
                if state not in self.explored and state not in frontier_set:
                    child = Node(state=state, parent=node, action=action)
                    child.priority = self.heuristic(state)  # Only heuristic used in greedy
                    heapq.heappush(frontier, (child.priority, child))
                    frontier_set.add(state)

        raise Exception("No solution found with Greedy Best-First Search.")

    def a_star_solve(self, visualize):
        """A* Search."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None, cost=0)
        start.priority = self.heuristic(start.state)  # f(n) = g(n) + h(n)

        # Set of explored states to avoid revisiting
        self.explored = set()

        # Frontier initialized with the start node, prioritized by the heuristic
        frontier = []
        heapq.heappush(frontier, (start.priority, start))
        start_time = time.time()
        while frontier:
            _, node = heapq.heappop(frontier)  # Get the node with the lowest f(n)
            self.num_explored += 1

            # Visualize the current state
            visualize(node.state)

            if node.state == self.goal:
                end_time = time.time()  # Record end time when solution is found
                elapsed_time = end_time - start_time  # Calculate time taken
                return elapsed_time, self.backtrack_solution(node)  # Return solution and time taken


            # Mark the current node as explored
            self.explored.add(node.state)

            # Check all neighbors and add to the frontier
            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    # Calculate the cost to reach this state (g(n) = parent_cost + 1)
                    new_cost = node.cost + 1
                    child = Node(state=state, parent=node, action=action, cost=new_cost)
                    
                    # f(n) = g(n) + h(n), where g(n) = cost to reach node, h(n) = heuristic to goal
                    child.priority = new_cost + self.heuristic(state)

                    # Add the child to the frontier (priority queue)
                    heapq.heappush(frontier, (child.priority, child))

        raise Exception("No solution found with A* Search.")

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

    def hill_climb_solve(self, visualize, max_restarts=5):
        """Hill Climbing Search with Random Restarts."""
        self.num_explored = 0
        start_time = time.time()
        def climb(start_node):
            """Performs a single hill climbing iteration."""
            current_node = start_node
            while True:
                self.num_explored += 1
                visualize(current_node.state)

                if current_node.state == self.goal:
                    end_time = time.time()  # Record end time when solution is found
                    elapsed_time = end_time - start_time  # Calculate time taken
                    return elapsed_time, self.backtrack_solution(current_node)


                self.explored.add(current_node.state)

                # Get neighbors and sort by heuristic value
                neighbors = [
                    Node(state=state, parent=current_node, action=action)
                    for action, state in self.neighbors(current_node.state)
                    if state not in self.explored
                ]
                for neighbor in neighbors:
                    neighbor.priority = self.heuristic(neighbor.state)

                if not neighbors:
                    return None  # Stuck at a dead end

                # Choose the neighbor with the best heuristic (smallest value)
                best_neighbor = min(neighbors, key=lambda x: x.priority)

                # Stop if no improvement
                if self.heuristic(current_node.state) <= best_neighbor.priority:
                    return None

                current_node = best_neighbor

        for _ in range(max_restarts):
            start = Node(state=self.start, parent=None, action=None)
            self.explored = set()
            solution = climb(start)
            if solution:
                return solution

        raise Exception("No solution found with Hill Climbing (after random restarts).")

      
    def beam_search_solve(self, visualize, beam_width=2, max_steps=100):
        """Beam Search with Memory Optimization and Diversity."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)

        # Initialize frontier with the start node
        frontier = [(self.heuristic(start.state), start)]  # List of (priority, node)
        self.explored = set()

        steps = 0
        start_time=time.time()
        while frontier and steps < max_steps:
            steps += 1
            self.num_explored += len(frontier)

            # Visualize all nodes in the current frontier
            for _, node in frontier:
                visualize(node.state)

                if node.state == self.goal:
                    end_time = time.time()  # Record end time when solution is found
                    elapsed_time = end_time - start_time  # Calculate time taken
                    return elapsed_time, self.backtrack_solution(node)  # Return solution and time taken    

                self.explored.add(node.state)

            # Expand frontier and collect all children
            next_frontier = []
            for _, node in frontier:
                for action, state in self.neighbors(node.state):
                    if state not in self.explored:
                        child = Node(state=state, parent=node, action=action)
                        child.priority = self.heuristic(state)
                        next_frontier.append((child.priority, child))

            # Keep the best `beam_width` nodes by heuristic value
            next_frontier.sort(key=lambda x: x[0])
            frontier = next_frontier[:beam_width]

        raise Exception("No solution found with Beam Search.")
