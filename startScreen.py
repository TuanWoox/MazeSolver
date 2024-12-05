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
    QDialog,
)

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt

from MapSelectorDialog import MapSelectorDialog  # Import the separate class
import visualizeState
from drawCustomMap import DrawCustomMap




class MazeSolverApp(QMainWindow):
    def __init__(self, bg_image_path):
        super().__init__()
        self.setWindowTitle("Maze Solver")
        self.setFixedSize(1200, 800)

        # Sound effects and music setup
        self.hover_sound = QMediaPlayer()
        self.hover_sound.setMedia(QMediaContent(QUrl.fromLocalFile("hover1.mp3")))  # Replace with your hover sound file

        self.click_sound = QMediaPlayer()
        self.click_sound.setMedia(QMediaContent(QUrl.fromLocalFile("click.mp3")))  # Replace with your click sound file

        # Background music setup
        self.background_music = QMediaPlayer()
        self.background_music.setMedia(QMediaContent(QUrl.fromLocalFile("background_music.mp3")))  # Replace with your music file path
        self.background_music.setVolume(50)
        self.background_music.play()

        # Connect the stateChanged signal to restart music when it finishes
        self.background_music.stateChanged.connect(self.loop_background_music)

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
        
    def loop_background_music(self, state):
        if state == QMediaPlayer.StoppedState:  # If the music stops
            self.background_music.play()        # Replay the music

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
        button.setFixedSize(600, 60)

        # Connect button events to sound effects
        button.enterEvent = lambda event: self.hover_sound.play()
        button.clicked.connect(lambda: self.play_click_sound(command))

        self.overlay_layout.addWidget(button)

    def play_click_sound(self, command):
        self.click_sound.play()
        command()

    def play_with_random_map(self):
        self.close()
        maze_file = "maze.txt"
        if os.path.exists(maze_file):
            maze = visualizeState.Maze(maze_file)
            self.maze_app = visualizeState.MazeApp(maze)
            self.maze_app.show()
        else:
            QMessageBox.critical(self, "Error", "Random maze file not found!")

    def draw_custom_map(self):
        if hasattr(self, 'custom_map_window') and self.custom_map_window.isVisible():
            self.custom_map_window.activateWindow()
        else:
            self.custom_map_window = DrawCustomMap()
            self.custom_map_window.show()

    def open_map_selector(self):
        save_dir = "./save"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        dialog = MapSelectorDialog(save_dir, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_map = dialog.selected_map
            self.load_selected_map(selected_map)

    def load_selected_map(self, file_path):
        if os.path.exists(file_path):
            maze = visualizeState.Maze(file_path)
            self.maze_app = visualizeState.MazeApp(maze)
            self.maze_app.show()
        else:
            QMessageBox.critical(self, "Error", "Map file not found!")



if __name__ == "__main__":
    bg_image_path = "background.gif"  # Replace with your GIF or image path
    app = QApplication(sys.argv)
    window = MazeSolverApp(bg_image_path)
    window.show()
    sys.exit(app.exec_())
