import sqlite3
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QTableView
from PySide6.QtCore import QSize
from PySide6.QtSql import QSqlDatabase, QSqlTableModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Koneksi ke database SQLite
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("quiz_app.db")
        if not self.db.open():
            print("Error: Tidak dapat membuka database")
            sys.exit(1)

        # Membuat model tabel untuk menampilkan data
        self.model = QSqlTableModel()
        self.model.setTable("users")
        self.model.select()

        # Menyiapkan antarmuka pengguna
        self.setWindowTitle("Quiz App - User Management")
        self.setMinimumSize(QSize(1024, 600))

        container = QWidget()
        layout = QVBoxLayout()

        # Input pencarian
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari user berdasarkan nama...")
        self.search_input.textChanged.connect(self.update_filter)
        layout.addWidget(self.search_input)

        # Tabel untuk menampilkan data
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        layout.addWidget(self.table_view)

        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_filter(self, s):
        # Memperbaiki format string filter
        filter_str = f'Name LIKE "%{s}%"'
        self.model.setFilter(filter_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
