import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QGridLayout, QMessageBox
)
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QTimer
import os

class DrawCustomMap(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Draw Your Map")
        self.setMinimumSize(1000, 800)  # Adjust minimum size for responsiveness

        # Main layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)  # Add margins for spacing
        self.layout.setSpacing(20)

        # Instructions label
        self.instructions = QLabel("Click and drag to toggle walls. Use 'Set Start' and 'Set Goal' to mark points.")
        self.instructions.setAlignment(Qt.AlignCenter)
        self.instructions.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        self.layout.addWidget(self.instructions)

        # Canvas for grid
        self.canvas = CustomCanvas(self)
        self.layout.addWidget(self.canvas, stretch=1)

        # Button panel
        self.button_layout = QGridLayout()
        self.button_layout.setSpacing(15)
        self.layout.addLayout(self.button_layout)

        self.add_button("Add Walls", lambda: self.canvas.set_mode("add"), 0, 0)
        self.add_button("Remove Walls", lambda: self.canvas.set_mode("remove"), 0, 1)
        self.add_button("Set Start", lambda: self.canvas.set_mode("start"), 0, 2)
        self.add_button("Set Goal", lambda: self.canvas.set_mode("goal"), 0, 3)
        self.add_button("Clear Map", self.canvas.clear_map, 0, 4)
        self.add_button("Save Map", self.canvas.save_map, 1, 0, object_name="save_map_button")
        self.add_button("Exit", self.close, 1, 4)   

    def add_button(self, text, command, row, col,object_name=None):
        button = QPushButton(text)
        if object_name:
            button.setObjectName(object_name)  # Assign the object name
        button.setStyleSheet(
            """
            QPushButton {
                font-size: 16px; 
                color: black; 
                background: #ecf0f1; 
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: #bdc3c7;
            }
            QPushButton:pressed {
                background: #95a5a6;
            }
            """
        )
        button.clicked.connect(command)
        self.button_layout.addWidget(button, row, col)


class CustomCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = None  # Track the current mode: 'add', 'remove', 'start', 'goal'
        self.grid_size = 20  # Initial size for cells
        self.rows = 27
        self.cols = 55
        self.cell_states = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.start_pos = None
        self.goal_pos = None
        self.dragging = False
        self.setMouseTracking(True)

        # Initialize border cells
        self.create_border()

        # Initialize resize timer
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.resize_grid)  # Connect to resize grid method

    def create_border(self):
        """Create a border around the grid that cannot be modified."""
        # Set first and last row to walls
        for col in range(self.cols):
            self.cell_states[0][col] = '#'
            self.cell_states[self.rows - 1][col] = '#'
        
        # Set first and last column to walls
        for row in range(self.rows):
            self.cell_states[row][0] = '#'
            self.cell_states[row][self.cols - 1] = '#'

    def set_mode(self, mode):
        """Set the current mode for interaction."""
        self.current_mode = mode

    def mousePressEvent(self, event):
        self.dragging = True
        self.handle_cell(event.x(), event.y())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.handle_cell(event.x(), event.y())

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def handle_cell(self, x, y):
        """Handle cell updates based on the current mode."""
        col, row = x // self.grid_size, y // self.grid_size
        if 0 <= col < self.cols and 0 <= row < self.rows:
            # Prevent modification of border cells
            if row == 0 or row == self.rows - 1 or col == 0 or col == self.cols - 1:
                return

            if self.current_mode == "start":  # Set Start
                if self.start_pos:
                    old_col, old_row = self.start_pos
                    self.cell_states[old_row][old_col] = ' '
                self.cell_states[row][col] = 'A'
                self.start_pos = (col, row)
            elif self.current_mode == "goal":  # Set Goal
                if self.goal_pos:
                    old_col, old_row = self.goal_pos
                    self.cell_states[old_row][old_col] = ' '
                self.cell_states[row][col] = 'B'
                self.goal_pos = (col, row)
            elif self.current_mode == "add":  # Add Walls
                self.cell_states[row][col] = '#'
            elif self.current_mode == "remove":  # Remove Walls
                self.cell_states[row][col] = ' '
            self.update()  # Redraw canvas

    def resizeEvent(self, event):
        """Handle resizing of the canvas."""
        self.resize_timer.start(100)  # Debounce resizing to avoid performance issues

    def resize_grid(self):
        """Resize the grid dynamically based on the canvas size."""
        available_width = self.width()
        available_height = self.height()
        self.grid_size = min(available_width // self.cols, available_height // self.rows)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 1))
        for y in range(self.rows):
            for x in range(self.cols):
                rect = QRect(x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size)
                if self.cell_states[y][x] == '#':
                    painter.fillRect(rect, QColor("black"))
                elif self.cell_states[y][x] == 'A':
                    painter.fillRect(rect, QColor("green"))
                elif self.cell_states[y][x] == 'B':
                    painter.fillRect(rect, QColor("red"))
                painter.drawRect(rect)

    def set_start(self):
        self.current_marker = 'A'

    def set_goal(self):
        self.current_marker = 'B'

    def clear_map(self):
        """Clear the map but keep the border intact."""
        self.cell_states = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.create_border()  # Recreate the border
        self.start_pos = None
        self.goal_pos = None
        self.update()

    def save_map(self):
        """Save the custom map to a directory './save'."""
        if self.start_pos is None or self.goal_pos is None:
            QMessageBox.critical(self, "Error", "Please set both the start and goal positions.")
            return
        try:
            save_dir = "./save"
            os.makedirs(save_dir, exist_ok=True)  # Create the directory if it doesn't exist
            file_path = os.path.join(save_dir, "custom_maze.txt")
            with open(file_path, "w") as f:
                for row in self.cell_states:
                    f.write("".join(row) + "\n")
            QMessageBox.information(self, "Success", f"Your custom map has been saved to {file_path}!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save the map: {str(e)}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawCustomMap()
    window.show()
    sys.exit(app.exec_())
