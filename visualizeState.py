import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QComboBox, QDialog, QGraphicsScene, 
    QGraphicsView, QGraphicsRectItem, QLineEdit, QMessageBox, QListWidget, QGraphicsEllipseItem,
    QGraphicsPixmapItem
)

from PyQt5.QtCore import Qt, QTimer,QSize
from PyQt5.QtGui import QColor, QBrush, QPen, QPixmap, QMovie
from MapSelectorDialog import MapSelectorDialog  # Import the separate class
from algorithms import Maze  # Assuming Maze class is implemented separately
from editMap import EditMaze
from report_window import ReportWindow  # Import the ReportWindow class
class MazeApp(QMainWindow):
    def __init__(self, maze):
        super().__init__()
        self.maze = maze
        self.cell_size = 30  # Size of each cell in pixels
        self.zoom_factor = 0.8
        self.setWindowTitle("Maze Solver")
        self.setGeometry(100, 100, 900, 700)
        self.showMaximized()  # Auto-maximize screen on startup
        self.init_ui()
        self.draw_maze()
        self.player_position = self.maze.start  # Initialize player's position at start
        self.step_count = 0  # Initialize step count to 0
        # Background setup
        

    def init_ui(self):
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Title Label
        self.title_label = QLabel("Maze Solver", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.main_layout.addWidget(self.title_label)

        # Maze Canvas (GraphicsView)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: #ecf0f1;")
        self.main_layout.addWidget(self.view, stretch=1)
        
        self.zoom_layout = QHBoxLayout()
        self.main_layout.addLayout(self.zoom_layout)

        self.add_button(self.zoom_layout, "Zoom In", self.zoom_in)
        self.add_button(self.zoom_layout, "Zoom Out", self.zoom_out)
        
        # Status Label
        self.status_label = QLabel("Welcome to Maze Solver", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #000000;")
        self.main_layout.addWidget(self.status_label)

        # Control Buttons and Dropdown
        self.controls_layout = QHBoxLayout()  # Make this an instance attribute
        self.main_layout.addLayout(self.controls_layout)

        self.setup_original_buttons()

    def add_button(self, layout, text, function):
        """Helper function to add buttons to a layout."""
        button = QPushButton(text)
        button.setStyleSheet(self.button_style())
        button.clicked.connect(function)
        layout.addWidget(button)

    def button_style(self):
        """Returns a shared button style with hover effects."""
        return """
            QPushButton {
                font-size: 14px;
                color: #ffffff;
                background-color: #3498db;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;  /* Darker blue */
            }
            QPushButton:pressed {
                background-color: #1e5799;  /* Even darker blue */
            }
        """
    def draw_maze(self):
        """Draws the maze, stretches the background image/GIF, and centers it."""
        self.scene.clear()  # Clear the scene to redraw

        # Load and stretch the background (supports GIF and images)
        bg_path = "image.gif"  # Path to the background file
        scene_width = self.maze.width  * self.cell_size 
        scene_height = self.maze.height * self.cell_size

        if bg_path.endswith(".gif"):
            # Handle animated GIF background
            bg_movie = QMovie(bg_path)
            if bg_movie.isValid():
                bg_movie.setScaledSize(QSize(scene_width, scene_height))  # Stretch GIF to scene size
                bg_label = QLabel()
                bg_label.setMovie(bg_movie)
                bg_proxy = self.scene.addWidget(bg_label)
                bg_proxy.setZValue(-1)  # Send background behind other elements
                bg_movie.start()
            else:
                print("Error: GIF background could not be loaded. Using fallback color.")
                self.scene.setBackgroundBrush(QBrush(QColor("#bdc3c7")))
        else:
            # Handle static image background
            bg_pixmap = QPixmap(bg_path)
            if not bg_pixmap.isNull():
                bg_pixmap = bg_pixmap.scaled(scene_width, scene_height, Qt.IgnoreAspectRatio)
                bg_item = QGraphicsPixmapItem(bg_pixmap)
                bg_item.setZValue(-1)
                self.scene.addItem(bg_item)
            else:
                print("Error: Background image could not be loaded. Using fallback color.")
                self.scene.setBackgroundBrush(QBrush(QColor("#bdc3c7")))

        # Calculate offsets to center the maze in the scene
        x_offset = 0  # No additional columns; maze starts at the leftmost point
        y_offset = 0  # Centering logic can be added here if needed

        # Draw the maze itself
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                x = x_offset + col * self.cell_size
                y = y_offset + row * self.cell_size

                # Draw walls (supports static images only)
                wall_path = "wall.png"  # Path to wall file
                if self.maze.walls[row][col]:
                    wall_pixmap = QPixmap(wall_path).scaled(
                        self.cell_size, self.cell_size, Qt.IgnoreAspectRatio
                    )
                    if not wall_pixmap.isNull():
                        wall_item = QGraphicsPixmapItem(wall_pixmap)
                        wall_item.setPos(x, y)
                        self.scene.addItem(wall_item)
                else:
                    # Draw floor (for empty spaces)
                    floor_path = "floor.png"
                    floor_pixmap = QPixmap(floor_path).scaled(
                        self.cell_size, self.cell_size, Qt.IgnoreAspectRatio
                    )
                    if not floor_pixmap.isNull():
                        floor_item = QGraphicsPixmapItem(floor_pixmap)
                        floor_item.setPos(x, y)
                        self.scene.addItem(floor_item)

                # Add prince (start) and princess (goal) icons
                if (row, col) == self.maze.start:
                    self.add_icon(x, y, "prince.png")  # Draw prince at start
                elif (row, col) == self.maze.goal:
                    self.add_icon(x, y, "princess.png")  # Draw princess at goal

    def add_icon(self, x, y, icon_path):
        """Helper function to add icons (prince or princess) to the maze."""
        icon_pixmap = QPixmap(icon_path).scaled(
            self.cell_size * 0.8, self.cell_size * 0.8, Qt.IgnoreAspectRatio
        )
        if not icon_pixmap.isNull():
            icon_item = QGraphicsPixmapItem(icon_pixmap)
            icon_item.setPos(x + self.cell_size * 0.1, y + self.cell_size * 0.1)
            self.scene.addItem(icon_item)


    def zoom_in(self):
            """Zooms in the maze visualization."""
            if self.zoom_factor < 2.0:  # Limit zooming in
                self.zoom_factor *= 1.2
                self.view.scale(1.2, 1.2)

    def zoom_out(self):
            """Zooms out the maze visualization."""
            if self.zoom_factor > 0.5:  # Limit zooming out
                self.zoom_factor *= 0.8
                self.view.scale(0.8, 0.8)


    def apply_algorithm(self):
        """Apply the selected solving algorithm."""
        algorithm = self.algorithm_dropdown.currentText()
        if algorithm == "Solve BFS":
            self.scene.clear()        
            self.solve_maze(self.maze.bfs_solve, "BFS")
        elif algorithm == "Solve DFS":
            self.scene.clear()
            self.solve_maze(self.maze.dfs_solve, "DFS")
        elif algorithm == "Solve A*":
            self.scene.clear()
            self.solve_maze(self.maze.a_star_solve, "A*")
        elif algorithm == "Solve Greedy":
            self.scene.clear()
            self.solve_maze(self.maze.greedy_solve, "Greedy")
        elif algorithm == "Solve Hill Climbing":
            self.scene.clear()
            self.solve_maze(self.maze.hill_climb_solve, "Hill Climbing")
        elif algorithm == "Solve Beam Search":
            self.scene.clear()
            self.solve_maze(self.maze.beam_search_solve, "Beam Search")

    def solve_maze(self, solve_method, method_name):
        """Solve the maze using the specified method and update the UI."""
        # Clear previous visualization
        self.status_label.setText(f"Solving with {method_name}...")
        QApplication.processEvents()
        self.draw_maze()

        try:
            # Solve the maze with visualization callback
            path = solve_method(self.visualize)
            
            # If a path is found, draw it
            if path:
                self.draw_path(path)
                
                # Get exploration statistics
                num_explored = self.maze.num_explored
                steps_to_goal = len(path)
                
                # Update status with solving details
                self.status_label.setText(
                    f"{method_name} complete! Explored States: {num_explored}, Steps to Goal: {steps_to_goal}"
                )
            else:
                # Handle case where no path is found
                self.status_label.setText(f"No path found with {method_name}")
        
        except Exception as e:
            # Handle any errors during solving
            self.status_label.setText(f"Error solving maze: {str(e)}")
        
        # Ensure start and end points are visible
        self.draw_start_end_points()

    def clear_cells(self):
        """Clears the solution path from the maze visualization."""
        for cell in self.solution_path:  # Assuming you have a `solution_path` list
            row, col = cell
            x = col * self.cell_size
            y = row * self.cell_size

            # Find the rectangle corresponding to the cell and remove it
            for item in self.scene.items():
                if isinstance(item, QGraphicsRectItem):
                    rect = item.rect()
                    if rect.x() == x and rect.y() == y:
                        self.scene.removeItem(item)
                        break

        # Redraw the start and goal points to ensure visibility
        self.draw_start_end_points()


    def draw_start_end_points(self):
        """Redraws the start and end points with prince and princess icons."""
        # Clear previous start and goal points
        start_row, start_col = self.maze.start
        x_start = start_col * self.cell_size
        y_start = start_row * self.cell_size

        # Draw prince icon at start
        prince_pixmap = QPixmap("prince.png").scaled(
            self.cell_size * 0.8, self.cell_size * 0.8, Qt.KeepAspectRatio
        )
        prince_item = QGraphicsPixmapItem(prince_pixmap)
        prince_item.setPos(x_start + self.cell_size * 0.1, y_start + self.cell_size * 0.1)
        self.scene.addItem(prince_item)

        # Draw princess icon at goal
        goal_row, goal_col = self.maze.goal
        x_goal = goal_col * self.cell_size
        y_goal = goal_row * self.cell_size
        princess_pixmap = QPixmap("princess.png").scaled(
            self.cell_size * 0.8, self.cell_size * 0.8, Qt.KeepAspectRatio
        )
        princess_item = QGraphicsPixmapItem(princess_pixmap)
        princess_item.setPos(x_goal + self.cell_size * 0.1, y_goal + self.cell_size * 0.1)
        self.scene.addItem(princess_item)

    def visualize(self, state, algorithm=None, value=None):
        """Visually indicates a visited cell during maze solving and records it."""
        row, col = state
        x = col * self.cell_size
        y = row * self.cell_size

        # Avoid overwriting start, goal, and wall points
        if state != self.maze.start and state != self.maze.goal and not self.maze.walls[row][col]:
            # Create a rectangle for the visited cell, with different colors for each algorithm
            rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
            
            if algorithm == 'Greedy':
                # Yellow color for greedy (based on heuristic)
                rect.setBrush(QBrush(QColor("#FFC300")))  # Yellow
            elif algorithm == 'A*':
                # Blue color for A* (based on cost + heuristic)
                rect.setBrush(QBrush(QColor("#2196F3")))  # Blue
            elif algorithm == 'DFS':
                # Green color for DFS
                rect.setBrush(QBrush(QColor("#4CAF50")))  # Green
            elif algorithm == 'HillClimbing':
                # Red color for Hill Climbing
                rect.setBrush(QBrush(QColor("#F44336")))  # Red
            elif algorithm == 'BeamSearch':
                # Purple color for Beam Search
                rect.setBrush(QBrush(QColor("#9C27B0")))  # Purple
            elif algorithm == 'DFS_Restart':
                # Cyan color for DFS with restarts
                rect.setBrush(QBrush(QColor("#00BCD4")))  # Cyan
            else:
                # Default color for other cases
                rect.setBrush(QBrush(QColor("#FFEB3B")))  # Light yellow for default

            rect.setPen(QPen(Qt.NoPen))
            self.scene.addItem(rect)

        # Redraw start and goal points to ensure they are visible
        self.draw_start_end_points()
        
        
        QApplication.processEvents()
        QTimer.singleShot(10, lambda: None)  # Small delay for visualization


    def draw_path(self, path):
        """Draws the shortest path found to the goal state."""
        if not path:
            self.status_label.setText("No path found!")
            return
        # Draw the path
        for row, col in path:
            # Skip start and goal points as they are already drawn
            if (row, col) != self.maze.start and (row, col) != self.maze.goal:
                x = col * self.cell_size
                y = row * self.cell_size

                # Create a blue rectangle for the path cell
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(QColor("#3498DB")))  # Blue color for path
                rect.setPen(QPen(Qt.NoPen))
                self.scene.addItem(rect)

        # Ensure start and goal points are always visible
        self.draw_start_end_points()
        QApplication.processEvents()

        self.status_label.setText("Path drawn successfully!")

    def load_map(self):
        """Opens a dialog to select a map file and loads the selected map."""
        save_dir = "./save"  # Define the directory where maps are stored
        dialog = MapSelectorDialog(save_dir, self)
        
        # Show the dialog and check if a map was selected
        if dialog.exec_() == QDialog.Accepted:
            selected_map = dialog.selected_map
            self.maze = Maze(selected_map)  # Load the selected maze
            self.draw_maze()  # Refresh the maze display
            self.status_label.setText(f"Loaded map from '{selected_map}'")
        else:
            self.status_label.setText("Map loading canceled.")

    def edit_maze(self):
        print(self.maze);
        """Open the EditMaze window for editing."""
        if not os.path.exists(self.maze.filename):
            QMessageBox.critical(self, "Error", f"Map file '{self.maze}' not found!")
            return
        
        # Function to reload the map
        def reload_map():
            self.maze = Maze(self.maze.filename) 
            self.draw_maze()  

        self.edit_window = EditMaze(self.maze.filename, reload_map)
        self.edit_window.show()


    def setup_original_buttons(self):
        self.algorithm_dropdown = QComboBox()
        self.algorithm_dropdown.addItems([
            "Select Algorithm", "Solve BFS", "Solve DFS",
            "Solve A*", "Solve Greedy", "Solve Hill Climbing", "Solve Beam Search"
        ])
        self.algorithm_dropdown.setStyleSheet("font-size: 14px; padding: 5px;")
        self.controls_layout.addWidget(self.algorithm_dropdown)
        """Restores the original control buttons."""
        self.add_button(self.controls_layout, "Apply Algorithm", self.apply_algorithm)
        self.add_button(self.controls_layout, "Generate Maze", self.generate_maze)
        self.add_button(self.controls_layout, "Save Map", self.save_map)
        self.add_button(self.controls_layout, "Play Mode", self.start_play_mode)
        self.add_button(self.controls_layout, "Load Map", self.load_map)
        self.add_button(self.controls_layout, "Edit", self.edit_maze)
        self.add_button(self.controls_layout, "Analyze", self.analyze_algorithms)
        self.add_button(self.controls_layout, "Exit", self.close)

    from report_window import ReportWindow  # Import the ReportWindow class
    
    def analyze_algorithms(self):
        """Compares all algorithms and generates a detailed report."""
        self.status_label.setText("Analyzing algorithms...")
        QApplication.processEvents()

        # List to store results
        results = []

        # Define algorithms to test
        algorithms = [
            (self.maze.bfs_solve, "BFS"),
            (self.maze.dfs_solve, "DFS"),
            (self.maze.a_star_solve, "A*"),
            (self.maze.greedy_solve, "Greedy"),
            (self.maze.hill_climb_solve, "Hill Climbing"),
            (self.maze.beam_search_solve, "Beam Search"),
        ]

        # Analyze each algorithm
        for solve_method, name in algorithms:
            try:
                # Reset the maze state before solving
                self.maze.reset_state()

                # Solve the maze without visualization
                path = solve_method(lambda x: None)

                # Calculate path length and states explored
                steps_to_goal = len(path) if path else "N/A"
                num_explored = self.maze.num_explored

                # Append results
                results.append((name, steps_to_goal, num_explored))
            
            except Exception as e:
                # Append error details to results
                results.append((name, "Error", str(e)))

        # Update status label for analysis completion
        self.status_label.setText("Analysis complete! Opening report...")
        QApplication.processEvents()

        # Open the Report Window
        self.report_window = ReportWindow(results, self)
        self.report_window.exec_()


    def generate_maze(self):
        # Call randomMaze.py to generate a new maze
        subprocess.run(["python", "randomMaze.py"])
        self.maze = Maze("maze.txt")  # Reload the maze
        self.draw_maze()  # Refresh the maze display
        self.status_label.setText("New maze generated!")
    def save_map(self):
        """Saves the current maze to a predefined directory and filename."""
        import os

        # Define the save directory
        save_dir = "./save"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)  # Create the directory if it doesn't exist

        # Generate a default filename based on existing files
        existing_files = [f for f in os.listdir(save_dir) if f.startswith("map") and f.endswith(".txt")]
        next_file_number = len(existing_files) + 1
        filename = f"map{next_file_number}.txt"

        # Full path for the file
        file_path = os.path.join(save_dir, filename)

        # Prepare the maze content
        map_content = []
        for i in range(self.maze.height):
            line = "".join(
                "A" if (i, j) == self.maze.start else
                "B" if (i, j) == self.maze.goal else
                " " if not self.maze.walls[i][j] else "#"
                for j in range(self.maze.width)
            )
            map_content.append(line)

        # Save the content to the file
        try:
            with open(file_path, "w") as f:
                f.write("\n".join(map_content))
            self.status_label.setText(f"Map saved as '{file_path}'")
        except Exception as e:
            self.status_label.setText(f"Error saving map: {str(e)}")

    def start_play_mode(self):
        """Activates play mode for manual navigation."""
        self.status_label.setText("Play Mode: Navigate using arrow keys!")
        
        # Initial player position at the start point
        self.player_position = self.maze.start
        self.step_count = 0  # Reset step counter
        self.draw_maze()  # Draw the maze
        self.draw_player()  # Draw the player in the start position

        # Set key event handling for play mode
        self.view.setFocus()  # Focus on the view to capture key events
        self.view.keyPressEvent = self.handle_key_event

    def handle_key_event(self, event):
        """Handles key events for manual movement of the player in play mode."""
        if event.key() == Qt.Key_Up:
            self.move_player(-1, 0)  # Move up (row - 1)
        elif event.key() == Qt.Key_Down:
            self.move_player(1, 0)  # Move down (row + 1)
        elif event.key() == Qt.Key_Left:
            self.move_player(0, -1)  # Move left (col - 1)
        elif event.key() == Qt.Key_Right:
            self.move_player(0, 1)  # Move right (col + 1)

    def move_player(self, row_offset, col_offset):
        """Moves the player within the maze, updates the step count, and redraws the maze."""
        new_row = self.player_position[0] + row_offset
        new_col = self.player_position[1] + col_offset
        
        # Ensure the player doesn't move out of bounds or into a wall
        if 0 <= new_row < self.maze.height and 0 <= new_col < self.maze.width:
            if not self.maze.walls[new_row][new_col]:  # Check if it's not a wall
                self.player_position = (new_row, new_col)
                self.step_count += 1  # Increment step count
                self.draw_maze()  # Redraw the maze
                self.draw_player()  # Redraw the player at the new position

                # Check if the player has reached the goal
                if self.player_position == self.maze.goal:
                    self.status_label.setText(f"Goal reached! Steps: {self.step_count}")
                    self.show_goal_reached_message()  # Show message and reset the game

    def draw_player(self):
        """Draws the player at the current position using prince.png."""
        # Get the current player position
        row, col = self.player_position
        x = col * self.cell_size
        y = row * self.cell_size

        # Remove any previous player drawing
        self.clear_player()

        # Load prince.png and scale it to fit the cell size
        prince_pixmap = QPixmap("prince.png").scaled(
            self.cell_size * 0.8, self.cell_size * 0.8, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Create a QGraphicsPixmapItem for the player
        self.player_item = QGraphicsPixmapItem(prince_pixmap)
        self.player_item.setPos(x + self.cell_size * 0.1, y + self.cell_size * 0.1)

        # Add the player item to the scene
        self.scene.addItem(self.player_item)


    def clear_player(self):
        """Clears any previous player drawings from the scene."""
        for item in self.scene.items():
            if isinstance(item, QGraphicsEllipseItem):  # Check if item is a player
                self.scene.removeItem(item)

    def show_goal_reached_message(self):
        """Shows a message and resets the player to the start position."""
        # Show a dialog with congratulations and step count
        self.show_congratulations_dialog()

        # Wait a bit before resetting the game
        QTimer.singleShot(1000, self.reset_to_start)  # Reset after 1 second

    def show_congratulations_dialog(self):
        """Displays a dialog with the congratulations message and step count."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Congratulations!")
        msg.setText("Congratulations! You've reached the goal.")
        msg.setInformativeText(f"You took {self.step_count} steps to complete the maze.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def reset_to_start(self):
        """Resets the player to the start position after reaching the goal."""
        self.status_label.setText("Play Mode: Navigate using arrow keys!")
        self.player_position = self.maze.start  # Reset to start
        self.step_count = 0  # Reset the step counter
        self.draw_maze()  # Redraw the maze
        self.draw_player()  # Redraw the player at the start position


if __name__ == "__main__":
    app = QApplication(sys.argv)
    maze = Maze("maze.txt")  # Replace with actual maze loading logic
    window = MazeApp(maze)
    window.show()
    sys.exit(app.exec_())