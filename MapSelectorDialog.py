import os
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QDialog,
    QScrollArea,
)


class MapSelectorDialog(QDialog):
    def __init__(self, save_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a Map")
        self.setFixedSize(400, 600)

        # Main layout
        layout = QVBoxLayout(self)

        # Instructions label
        label = QLabel("Available Maps:")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        # Scrollable area for map buttons
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Generate map buttons dynamically
        self.save_dir = save_dir
        for file in os.listdir(self.save_dir):
            if file.endswith(".txt"):
                map_button = QPushButton(file.replace(".txt", ""))
                map_button.setStyleSheet(
                    """
                    QPushButton {
                        font-size: 16px; 
                        background-color: #e0e0e0; 
                        border: 1px solid #b0b0b0;
                        border-radius: 5px;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                    }
                    """
                )
                map_button.clicked.connect(lambda _, f=file: self.load_map(f))
                scroll_layout.addWidget(map_button)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(
            "font-size: 16px; background-color: #ff6666; color: white; border-radius: 5px; padding: 10px;"
        )
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

    def load_map(self, file_name):
        file_path = os.path.join(self.save_dir, file_name)
        if os.path.exists(file_path):
            self.selected_map = file_path
            self.accept()  # Close dialog and return success
        else:
            QMessageBox.critical(self, "Error", f"Map file '{file_name}' not found!")
