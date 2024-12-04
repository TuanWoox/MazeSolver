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
        # Extract algorithm names and states explored
        algorithms = [result["Name"] for result in self.results]
        states_explored = [
            result["Explore_States"] if isinstance(result["Explore_States"], (int, float)) else 0
            for result in self.results
        ]
        path_counts = [
            result["Path_Steps_Counts"] if isinstance(result["Path_Steps_Counts"], (int, float)) else 0
            for result in self.results
        ]
        times_taken = [
            result["Time_Taken"] if isinstance(result["Time_Taken"], (int, float)) else 0
            for result in self.results
        ]
        # Define bar width
        bar_width = 0.8  # Wide bars with no space in between
        fontSize = 8.5;
        if len(states_explored) >= 5:
            fontSize = 6.5;
        # Clear the figure for a clean plot
        self.figure.clear()

        # Create the axis
        ax = self.figure.add_subplot(111)

        # Plot bars for states explored
        bars1 = ax.bar(
            range(len(algorithms)),  # Base indices for each bar
            states_explored,
            bar_width,
            color="royalblue"
        )
        

        # Add algorithm names with states explored on top of each bar
        for bar, algorithm, states in zip(bars1, algorithms, states_explored):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # Center text on the bar
                height + 1,  # Slightly above the bar
                f'{algorithm} - {states}',  # Format: "Algorithm - States"
                ha='center', va='bottom', fontsize=fontSize, color='black'
            )

        # Offset the x-coordinates for path counts
        offset_indices_path_counts = [x + 1 + len(algorithms) for x in range(len(algorithms))]

        # Plot bars for path counts
        bars2 = ax.bar(
            offset_indices_path_counts,  # Offset indices to place bars after the first set
            path_counts,
            bar_width,
            color="orange"
        )

        # Add algorithm names with path counts on top of each bar
        for bar, algorithm, paths in zip(bars2, algorithms, path_counts):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # Center text on the bar
                height + 1,  # Slightly above the bar
                f'{algorithm} - {paths}',  # Format: "Algorithm - Paths"
                ha='center', va='bottom', fontsize=fontSize, color='black'
            )

        # Offset the x-coordinates for time taken
        offset_indices_time_taken = [x + 2 + 2 * len(algorithms) for x in range(len(algorithms))]

        # Plot bars for time taken
        bars3 = ax.bar(
            offset_indices_time_taken,  # Offset indices to place bars after the second set
            times_taken,
            bar_width,
            color="green"
        )

        for bar, algorithm, time in zip(bars3, algorithms, times_taken):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # Center text on the bar
                height + 1,  # Slightly above the bar
                f'{algorithm} - {time:.1f}',  # Format: "Algorithm - Time" with 2 decimal places
                ha='center', va='bottom', fontsize=fontSize, color='black'
            )

        # Set common x-axis label under the bars
        ax.set_xlabel("Component Compared", fontsize=12, labelpad=15)

        # Remove x-ticks (since labels are on top)
        ax.set_xticks([])

        # Set y-axis label
        ax.set_ylabel("Count", fontsize=12)

        # Set plot title
        ax.set_title("Components", fontsize=14)

        # Add legend
        ax.legend(
            [bars1, bars2, bars3],
            ['States Explored (Blue)', 'Path Counts (Orange)', 'Time Taken (Green)'],
            loc='upper right',
            fontsize=10
        )

        # Adjust layout for better spacing
        self.figure.tight_layout(pad=3.0)

        # Redraw the canvas
        self.canvas.draw()




