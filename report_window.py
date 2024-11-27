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
        self.figure = plt.Figure(figsize=(12, 7), dpi=100)  # Increased figure width for better spacing
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Plot the results as a bar chart
        self.plot_chart()

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def plot_chart(self):
        # Extract algorithm names, path lengths, states explored, and time taken from results
        algorithms = [result["Name"] for result in self.results]
        path_lengths = [
            result["Path_Steps_Counts"] if isinstance(result["Path_Steps_Counts"], (int, float)) else 0
            for result in self.results
        ]
        states_explored = [
            result["Explore_States"] if isinstance(result["Explore_States"], (int, float)) else 0
            for result in self.results
        ]
        times_taken = [
            result["Time_Taken"] if isinstance(result["Time_Taken"], (int, float)) else 0
            for result in self.results
        ]

        # Clear the figure for a clean plot
        self.figure.clear()

        # Create the bar chart
        ax = self.figure.add_subplot(111)
        bar_width = 0.25  # Bar width for better spacing between bars
        index = range(len(algorithms))

        # Create bars for Path Length, States Explored, and Time Taken
        bar1 = ax.bar(index, path_lengths, bar_width, label="Path Lengths", color="royalblue")
        bar2 = ax.bar(
            [p + bar_width for p in index],
            states_explored,
            bar_width,
            label="States Explored",
            color="darkorange",
        )
        bar3 = ax.bar(
            [p + 2 * bar_width for p in index],
            times_taken,
            bar_width,
            label="Time Taken (s)",
            color="seagreen",
        )

        # Add value annotations on top of the bars
        for i, v in enumerate(path_lengths):
            if v != 0:
                ax.text(i, v + 0.5, str(v), color="black", ha="center", fontsize=12)

        for i, v in enumerate(states_explored):
            if v != 0:
                ax.text(i + bar_width, v + 0.5, str(v), color="black", ha="center", fontsize=12)

        for i, v in enumerate(times_taken):
            if v != 0:
                ax.text(i + 2 * bar_width, v + 0.5, f"{v:.4f}", color="black", ha="center", fontsize=12)

        # Set labels and title
        ax.set_xlabel("Algorithms", fontsize=14)
        ax.set_ylabel("Values", fontsize=14)
        ax.set_title("Comparison of Algorithms (Path Length, States Explored, Time Taken)", fontsize=16)

        # Set x-ticks and labels
        ax.set_xticks([p + bar_width for p in index])  # Center the x-ticks
        ax.set_xticklabels(algorithms, fontsize=12)

        # Add grid and adjust aesthetics
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend(loc="upper left", fontsize=12)
        self.figure.tight_layout(pad=3.0)  # Adjust layout to avoid overlap

        # Redraw the canvas
        self.canvas.draw()
