import os
import random

def generate_complex_maze(width, height, start, goal):
    # Initialize maze with walls
    maze = [['#' for _ in range(2 * width + 1)] for _ in range(2 * height + 1)]
    
    # Function to add passages with more connections near the start
    def add_passages(x, y):
        stack = [(x, y)]
        visited = set()
        
        while stack:
            x, y = stack[-1]
            visited.add((x, y))
            maze[2 * y + 1][2 * x + 1] = ' '

            # Find unvisited neighbors
            neighbours = []
            for nx, ny in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if 0 <= nx < width and 0 <= ny < height:
                    if maze[2 * ny + 1][2 * nx + 1] == '#':
                        neighbours.append((nx, ny))
            
            if neighbours:
                # Choose a random unvisited neighbour and add it to the stack
                nx, ny = random.choice(neighbours)
                stack.append((nx, ny))
                
                # Remove wall between cells
                maze[y + ny + 1][x + nx + 1] = ' '
            else:
                stack.pop()

    # Start adding passages from the start position
    start_x, start_y = start
    add_passages(start_x, start_y)

    # Add extra paths for connectivity near the start area
    for _ in range(int(width * height * 0.8)):  # Increase density near the start
        rand_x, rand_y = random.randint(0, width // 3), random.randint(0, height // 3)
        maze[2 * rand_y + 1][2 * rand_x + 1] = ' '

    # Add random passages throughout for better interconnectivity
    for _ in range(int(width * height * 1.5)):
        rand_x, rand_y = random.randint(1, width - 1), random.randint(1, height - 1)
        maze[2 * rand_y + 1][2 * rand_x + 1] = ' '

    # Mark the start and goal positions
    maze[1][1] = 'A'  # Start point 'A'
    goal_x, goal_y = goal
    maze[2 * goal_y + 1][2 * goal_x + 1] = 'B'  # Goal point 'B'
    
    return maze

def save_maze_to_file(maze, file_path):
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory) and directory != '':
        os.makedirs(directory)
    
    with open(file_path, "w") as file:
        for row in maze:
            file.write(''.join(row) + '\n')

# Maze dimensions and start/goal positions
maze_width, maze_height = 27, 14
maze_start, maze_goal = (0, 0), (maze_width - 1, maze_height - 1)

# Generate and save the maze
maze = generate_complex_maze(maze_width, maze_height, maze_start, maze_goal)
maze_path = "maze.txt"
save_maze_to_file(maze, maze_path)

print(f"Maze saved to {maze_path}")
