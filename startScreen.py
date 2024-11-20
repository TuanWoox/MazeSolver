import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt
import tkinter as tk
from tkinter import Tk, Toplevel, Label, Button
from tkinter import messagebox
import visualizeState  # Assuming this handles maze visualization
from drawCustomMap import DrawCustomMap  # Assuming this is the custom map module


class MazeSolverApp(QMainWindow):
    def __init__(self, bg_image_path):
        super().__init__()
        self.setWindowTitle("Maze Solver")
        self.setFixedSize(1200, 800)  # Set window size

        # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)

        # Background setup
        self.background_label = QLabel(self.central_widget)
        if bg_image_path.endswith(".gif"):
            self.movie = QMovie(bg_image_path)
            self.background_label.setMovie(self.movie)
            self.movie.start()
        else:
            pixmap = QPixmap(bg_image_path)
            self.background_label.setPixmap(pixmap)

        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1200, 800)

        # Overlay widgets
        self.overlay_widget = QWidget(self.central_widget)
        self.overlay_layout = QVBoxLayout(self.overlay_widget)
        self.overlay_layout.setAlignment(Qt.AlignCenter)
        self.overlay_layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        self.title_label = QLabel("Maze Solver", self.overlay_widget)
        self.title_label.setStyleSheet(
            "font-size: 60px; font-weight: bold; color: white; background: transparent;"
        )
        self.title_label.setAlignment(Qt.AlignCenter)
        self.overlay_layout.addWidget(self.title_label)

        # Team members label
        self.team_label = QLabel(
            "Team Members:\nNguyễn Tiến Toàn - 22110078\nBạch Đức Cảnh - 22110012\n"
            "Nguyễn Tuấn Vũ - 22110091\nLý Đăng Triều - 22110080",
            self.overlay_widget,
        )
        self.team_label.setStyleSheet(
            "font-size: 20px; color: white; background: transparent;"
        )
        self.team_label.setAlignment(Qt.AlignCenter)
        self.overlay_layout.addWidget(self.team_label)

        # Add buttons
        self.add_button("Play with Random Map", self.play_with_random_map)
        self.add_button("Play with Loaded Map", self.open_map_selector)
        self.add_button("Draw Custom Map", self.draw_custom_map)
        self.add_button("Exit Game", self.close)

        # Add overlay layout to main layout
        self.layout.addWidget(self.overlay_widget)

    def add_button(self, text, command):
        button = QPushButton(text, self.overlay_widget)
        button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px; 
                color: black; 
                background: rgba(255, 255, 255, 0.8); 
                border: 2px solid black;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background: rgba(200, 200, 200, 0.9);
            }
            QPushButton:pressed {
                background: rgba(150, 150, 150, 0.9);
            }
            """
        )
        button.setFixedSize(300, 60)
        button.clicked.connect(command)
        self.overlay_layout.addWidget(button)

    def play_with_random_map(self):
        # Run the maze visualization
        maze_file = "maze.txt"  # Example random maze file
        if os.path.exists(maze_file):
            maze = visualizeState.Maze(maze_file)
            visualizeState.MazeApp(maze).mainloop()
        else:
            QMessageBox.critical(self, "Error", "Random maze file not found!")

    def draw_custom_map(self):
        # Initialize a hidden root Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        # Launch the custom map drawing tool with `root` as the master
        DrawCustomMap(root)


    def open_map_selector(self):
        # Initialize a hidden root Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        # Save directory for maps
        save_dir = "./save"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Create a Toplevel window for map selection
        map_selector = tk.Toplevel(root)
        map_selector.title("Select a Map")
        map_selector.geometry("300x400")
        map_selector.configure(bg="#34495e")

        # Add a label for available maps
        tk.Label(
            map_selector,
            text="Available Maps:",
            font=("Helvetica", 16, "bold"),
            fg="#ecf0f1",
            bg="#34495e",
        ).pack(pady=10)

        # Dynamically create buttons for each map file
        for file in os.listdir(save_dir):
            if file.endswith(".txt"):
                tk.Button(
                    map_selector,
                    text=file.replace(".txt", ""),
                    font=("Helvetica", 14),
                    fg="#2c3e50",
                    bg="#ecf0f1",
                    command=lambda f=file: self.load_selected_map(
                        os.path.join(save_dir, f), map_selector, root
                    ),
                ).pack(pady=5)

        # Make the map selector modal
        map_selector.transient(root)  # Set parent window
        map_selector.grab_set()       # Block interaction with other windows
        map_selector.wait_window()    # Wait until the map selector is closed



    def load_selected_map(self, file_path, map_selector, root):
        # Close the map selector and root windows
        map_selector.destroy()
        root.destroy()

        if os.path.exists(file_path):
            # Initialize the maze visualization
            maze = visualizeState.Maze(file_path)
            visualizeState.MazeApp(maze).mainloop()
        else:
            QMessageBox.critical(self, "Error", "Map file not found!")

if __name__ == "__main__":
    bg_image_path = "background.gif"  # Replace with your GIF or image path
    app = QApplication(sys.argv)
    window = MazeSolverApp(bg_image_path)
    window.show()
    sys.exit(app.exec_())
