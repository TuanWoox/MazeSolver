import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from drawCustomMap import DrawCustomMap  # Assuming the DrawCustomMap is in the same directory
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QGridLayout, QMessageBox



class EditMaze(DrawCustomMap):
    def __init__(self, map_path, reload_callback):
        """
        Initialize the edit maze window.
        :param map_path: Path to the map file to be edited.
        :param reload_callback: A function to call after saving the map.
        """
        super().__init__()
        self.map_path = map_path
        self.reload_callback = reload_callback
        self.load_map()
        save_button = self.findChild(QPushButton, "save_map_button")
        print(save_button);
        if save_button:
            save_button.clicked.disconnect()  # Disconnect from the parent class method
            save_button.clicked.connect(self.save_map)  # Connect to the overridden method

    def load_map(self):
        if not os.path.exists(self.map_path):
            QMessageBox.critical(self, "Error", f"Map file '{self.map_path}' not found!")
            return

        with open(self.map_path, "r") as file:
            lines = file.readlines()

        # Ensure the map fits into the grid size
        self.canvas.rows = len(lines)
        self.canvas.cols = max(len(line.strip()) for line in lines)
        self.canvas.cell_states = [[' ' for _ in range(self.canvas.cols)] for _ in range(self.canvas.rows)]

        for row_idx, line in enumerate(lines):
            for col_idx, char in enumerate(line.strip()):
                if char == 'A':
                    self.canvas.start_pos = (col_idx, row_idx)
                elif char == 'B':
                    self.canvas.goal_pos = (col_idx, row_idx)
                self.canvas.cell_states[row_idx][col_idx] = char
        self.canvas.update()

    def save_map(self):
        if self.canvas.start_pos is None or self.canvas.goal_pos is None:
            QMessageBox.critical(self, "Error", "Please set both the start and goal positions.")
            return
        try:
            # Save the map to the file
            with open(self.map_path, "w") as file:
                for row in self.canvas.cell_states:
                    file.write("".join(row) + "\n")

            QMessageBox.information(self, "Success", f"Your map has been saved to '{self.map_path}'!")
            self.close()

            # Trigger the reload callback
            self.reload_callback()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save the map: {str(e)}")


if __name__ == "__main__":
    def dummy_reload():
        print("Reload triggered!")  # Replace with your actual reload function in the main app.

    app = QApplication(sys.argv)
    edit_window = EditMaze("./maze.txt", dummy_reload)
    edit_window.show()
    sys.exit(app.exec_())
