import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ReportWindow(QDialog):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.results = results
        self.setWindowTitle("Algorithm Analysis Report")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title Label
        title_label = QLabel("Algorithm Analysis Report")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Create Matplotlib figure and canvas for the chart
        self.figure = plt.Figure(figsize=(10, 7), dpi=100)  # Increase the width and height
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Plot the results as a bar chart
        self.plot_chart()

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def plot_chart(self):
        # Extract algorithm names, path lengths, and states explored from results
        algorithms = [result[0] for result in self.results]
        path_lengths = [result[1] if isinstance(result[1], int) else 0 for result in self.results]  # Handle non-integer values
        states_explored = [result[2] if isinstance(result[2], int) else 0 for result in self.results]  # Handle non-integer values

        ax = self.figure.add_subplot(111)
        bar_width = 0.35
        index = range(len(algorithms))

        # Create bars for Path Length and States Explored
        bar1 = ax.bar(index, path_lengths, bar_width, label='Path Lengths', color='blue')
        bar2 = ax.bar([p + bar_width for p in index], states_explored, bar_width, label='States Explored', color='orange')

        # Add value annotations on top of the bars, with increased distance
        for i, v in enumerate(path_lengths):
            ax.text(i - 0.1, v + 1, str(v), color='blue', ha='center', va='bottom', fontsize=12)

        for i, v in enumerate(states_explored):
            ax.text(i + bar_width - 0.1, v + 1, str(v), color='orange', ha='center', va='bottom', fontsize=12)

        # Set labels and title
        ax.set_xlabel('Algorithms')
        ax.set_ylabel('Values')
        ax.set_title('Comparison of Algorithms (Path Length vs States Explored)')

        ax.set_xticks([p + bar_width / 2 for p in index])
        ax.set_xticklabels(algorithms)

        ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=12)  # Move legend out of plot area

        # Adjust layout to prevent overlap
        self.figure.tight_layout(pad=2.0)
