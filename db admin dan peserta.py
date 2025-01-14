import sqlite3
import sys
#import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QTableView, QPushButton, QMessageBox
from PySide6.QtCore import QSize
from PySide6.QtSql import QSqlDatabase, QSqlTableModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Koneksi ke database SQLite
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        #db_path = os.path.join(os.path.dirname(__file__), "quiz_app.db")
        #self.db.setDatabaseName(db_path)
        self.db.setDatabaseName("quizapp.db")
        if not self.db.open():
            print("Error: Tidak dapat membuka database")
            sys.exit(1)

        # Membuat model tabel untuk menampilkan data
        self.model = QSqlTableModel()
        self.model.setTable("users")
        self.model.select()

        # Menyiapkan antarmuka pengguna
        self.setWindowTitle("Quiz App - User Management")
        self.setMinimumSize(QSize(800, 600))

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
        
        # Tombol Hapus User
        self.delete_button = QPushButton("Hapus User")
        self.delete_button.clicked.connect(self.delete_user)
        layout.addWidget(self.delete_button)

        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_filter(self, s):
        # Memperbaiki format string filter
        filter_str = f'Name LIKE "%{s}%"'
        self.model.setFilter(filter_str)

    def delete_user(self):
        # Mendapatkan baris yang dipilih
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang ingin dihapus.")
            return

        # Konfirmasi penghapusan
        reply = QMessageBox.question(
            self, "Konfirmasi", "Apakah Anda yakin ingin menghapus user ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        # Hapus pengguna berdasarkan baris yang dipilih
        for index in selected_rows:
            record_id = self.model.record(index.row()).value("id")  # Asumsikan ada kolom 'id'
            query = self.db.exec(f"DELETE FROM users WHERE id = {record_id}")
            if not query.isActive():
                QMessageBox.critical(self, "Error", "Gagal menghapus user.")
                return

        # Perbarui model
        self.model.select()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()