import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QMessageBox
)


class LoadGameScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Load Game")
        self.resize(400, 300)

        # Layout chính
        self.layout = QVBoxLayout(self)

        # Danh sách các map
        self.map_list = QListWidget(self)
        self.layout.addWidget(self.map_list)

        # Nút xác nhận
        self.load_button = QPushButton("Load Map", self)
        self.load_button.clicked.connect(self.load_selected_map)
        self.layout.addWidget(self.load_button)

        # Load danh sách map từ thư mục
        self.load_map_files()

    def load_map_files(self):
        """Tìm và hiển thị danh sách các tệp bản đồ từ thư mục."""
        map_folder = "save"  # Đặt thư mục chứa file bản đồ
        if not os.path.exists(map_folder):
            os.makedirs(map_folder)  # Tạo thư mục nếu chưa tồn tại

        # Lấy danh sách file trong thư mục
        files = [f for f in os.listdir(map_folder) if f.endswith(".txt")]
        if files:
            self.map_list.addItems(files)
        else:
            self.map_list.addItem("Không có bản đồ nào!")  # Thông báo khi trống
            self.map_list.setDisabled(True)
            self.load_button.setDisabled(True)

    def load_selected_map(self):
        """Load map được chọn."""
        selected_item = self.map_list.currentItem()
        if selected_item:
            map_name = selected_item.text()
            QMessageBox.information(self, "Load Map", f"Đang load bản đồ: {map_name}")
            # Gọi hàm load bản đồ từ file
            self.load_map(map_name)
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bản đồ!")

    def load_map(self, map_name):
        """Xử lý logic load bản đồ từ file."""
        map_path = os.path.join("save", map_name)
        if os.path.exists(map_path):
            # Thực hiện các bước xử lý file map
            print(f"Loading map from: {map_path}")
            # Ví dụ: Đọc nội dung file
            with open(map_path, "r") as f:
                content = f.read()
                print(content)
        else:
            QMessageBox.critical(self, "Lỗi", f"Không tìm thấy file: {map_name}")


# Khởi chạy ứng dụng
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = LoadGameScreen()
    window.show()
    sys.exit(app.exec_())
