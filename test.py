from PyQt5.QtGui import QColor, QBrush, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem
from PyQt5.QtCore import Qt

def draw_maze(self):
    """Draws the maze with styled walls and custom start/goal graphics."""
    self.scene.clear()
    for row in range(self.maze.height):
        for col in range(self.maze.width):
            x = col * self.cell_size
            y = row * self.cell_size

            # Style walls with 3D effect
            if self.maze.walls[row][col]:  # Wall
                color = QColor("#b0c4de")  # Light steel blue
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(color))
                rect.setPen(QPen(QColor("#4682b4"), 2))  # Steel blue border
                self.scene.addItem(rect)
            else:
                # Draw empty space
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(QColor("#ecf0f1")))  # Light gray
                rect.setPen(QPen(Qt.NoPen))
                self.scene.addItem(rect)

            # Add prince (start) and princess (goal) icons
            if (row, col) == self.maze.start:
                prince_pixmap = QPixmap("prince.png").scaled(
                    self.cell_size, self.cell_size, Qt.KeepAspectRatio
                )
                prince_item = QGraphicsPixmapItem(prince_pixmap)
                prince_item.setPos(x, y)
                self.scene.addItem(prince_item)

            elif (row, col) == self.maze.goal:
                princess_pixmap = QPixmap("princess.png").scaled(
                    self.cell_size, self.cell_size, Qt.KeepAspectRatio
                )
                princess_item = QGraphicsPixmapItem(princess_pixmap)
                princess_item.setPos(x, y)
                self.scene.addItem(princess_item)
