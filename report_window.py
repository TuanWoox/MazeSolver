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

        # Define unique colors for each algorithm
        colors = {
            "DFS": "royalblue",
            "BFS": "darkorange",
            "A*": "seagreen",
            "Greedy": "mediumpurple",
            "Beam Search": "gold",
            "Climbing HIll": "crimson"
        }
        bar_colors = [colors.get(algo, "gray") for algo in algorithms]  # Default to gray if not found

        # Clear the figure for a clean plot
        self.figure.clear()

        # Create subplots
        ax1 = self.figure.add_subplot(311)  # 3 rows, 1 column, plot 1
        ax2 = self.figure.add_subplot(312)  # 3 rows, 1 column, plot 2
        ax3 = self.figure.add_subplot(313)  # 3 rows, 1 column, plot 3

        # Bar width
        bar_width = 0.35
        index = range(len(algorithms))

        # Plot States Explored
        ax1.bar(index, states_explored, bar_width, color=bar_colors)
        ax1.set_title("States Explored Comparison", fontsize=14)
        ax1.set_xticks(index)
        ax1.set_xticklabels(algorithms, fontsize=10)
        ax1.set_ylabel("States Explored", fontsize=12)
        ax1.grid(True, linestyle="--", alpha=0.7)

        # Plot Path Lengths
        ax2.bar(index, path_lengths, bar_width, color=bar_colors)
        ax2.set_title("Path Lengths Comparison", fontsize=14)
        ax2.set_xticks(index)
        ax2.set_xticklabels(algorithms, fontsize=10)
        ax2.set_ylabel("Path Lengths", fontsize=12)
        ax2.grid(True, linestyle="--", alpha=0.7)

        # Plot Time Taken
        ax3.bar(index, times_taken, bar_width, color=bar_colors)
        ax3.set_title("Time Taken Comparison", fontsize=14)
        ax3.set_xticks(index)
        ax3.set_xticklabels(algorithms, fontsize=10)
        ax3.set_ylabel("Time (s)", fontsize=12)
        ax3.grid(True, linestyle="--", alpha=0.7)

        # Adjust layout to prevent overlap
        self.figure.tight_layout(pad=3.0)

        # Redraw the canvas
        self.canvas.draw()



