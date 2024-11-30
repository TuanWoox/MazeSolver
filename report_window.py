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
        states_explored = [
            result["Explore_States"] if isinstance(result["Explore_States"], (int, float)) else 0
            for result in self.results
        ]
        path_lengths = [
            result["Path_Steps_Counts"] if isinstance(result["Path_Steps_Counts"], (int, float)) else 0
            for result in self.results
        ]
        times_taken = [
            result["Time_Taken"] if isinstance(result["Time_Taken"], (int, float)) else 0
            for result in self.results
        ]

        # Define bar width and positions for grouped bars
        bar_width = 0.2  # Width of each bar
        indices = range(len(algorithms))  # Base x positions for the bars
        offset = bar_width * 1.2  # Offset between metrics within each group

        # Clear the figure for a clean plot
        self.figure.clear()

        # Create the axis
        ax = self.figure.add_subplot(111)

        # Colors for each metric
        colors = ["royalblue", "darkorange", "seagreen"]

        # Plot grouped bars for each metric
        bars1 = ax.bar(
            [i - offset for i in indices],  # Shift left for States Explored
            states_explored,
            bar_width,
            label="States Explored",
            color=colors[0]
        )
        bars2 = ax.bar(
            indices,  # Centered for Path Steps
            path_lengths,
            bar_width,
            label="Path Steps",
            color=colors[1]
        )
        bars3 = ax.bar(
            [i + offset for i in indices],  # Shift right for Time Taken
            times_taken,
            bar_width,
            label="Time Taken (s)",
            color=colors[2]
        )

        # Annotate each bar with its value
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{height:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

        # Set x-ticks and labels for algorithms (each algorithm should have its own tick)
        ax.set_xticks([i for i in indices])  # Positions for algorithm names
        ax.set_xticklabels(algorithms, fontsize=10)

        # Set the plot title and axis labels
        ax.set_title("Algorithm Analysis Comparison", fontsize=14)
        ax.set_ylabel("Metrics", fontsize=12)
        ax.set_xlabel("Algorithms", fontsize=12)

        # Add the legend
        ax.legend()

        # Adjust layout for better spacing
        self.figure.tight_layout(pad=3.0)

        # Redraw the canvas
        self.canvas.draw()




