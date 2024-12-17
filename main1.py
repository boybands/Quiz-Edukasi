import sys
from PySide6.QtCore import QTimer, QTime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget,
    QLabel, QLineEdit, QDialog, QFormLayout, QMessageBox
)
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from datetime import datetime

# Database initialization
def initialize_database():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("quiz_app.db")

    if not db.open():
        print("Failed to connect to database.")
        sys.exit(1)

    query = QSqlQuery()

    query.exec("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    print("Database initialized.")

# Login Dialog
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(300, 200)

        layout = QFormLayout()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addRow("Email:", self.email_input)
        layout.addRow("Password:", self.password_input)

        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")

        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.handle_register)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        query = QSqlQuery()
        query.prepare("SELECT password FROM users WHERE email = :email")
        query.bindValue(":email", email)
        query.exec()

        if query.next():
            db_password = query.value(0)
            if password == db_password:
                QMessageBox.information(self, "Success", "Login Berhasil!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Password salah!")
        else:
            QMessageBox.warning(self, "Error", "Email tidak ditemukan! Silakan daftar terlebih dahulu.")

    def handle_register(self):
        register_dialog = RegisterDialog()
        if register_dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "Success", "Registrasi berhasil! Silakan login.")

# Register Dialog
class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.setFixedSize(300, 250)

        layout = QFormLayout()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addRow("Name:", self.name_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Password:", self.password_input)

        self.register_button = QPushButton("Register")
        layout.addWidget(self.register_button)
        self.setLayout(layout)

        self.register_button.clicked.connect(self.handle_register)

    def handle_register(self):
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if not name or not email or not password:
            QMessageBox.warning(self, "Error", "Semua field harus diisi!")
            return

        query = QSqlQuery()
        query.prepare("INSERT INTO users (name, email, password) VALUES (:name, :email, :password)")
        query.bindValue(":name", name)
        query.bindValue(":email", email)
        query.bindValue(":password", password)

        if query.exec():
            QMessageBox.information(self, "Success", "Registrasi berhasil!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Gagal registrasi. Email mungkin sudah terdaftar.")

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kuis Edukasi")
        self.setFixedSize(400, 300)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = QWidget()
        self.quiz_page = QWidget()
        self.setup_home_page()
        self.setup_quiz_page()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.quiz_page)

    def setup_home_page(self):
        layout = QVBoxLayout()

        self.time_label = QLabel()
        layout.addWidget(self.time_label)

        welcome_label = QLabel("Selamat Datang di Kuis Edukasi!")
        layout.addWidget(welcome_label)

        start_quiz_button = QPushButton("Mulai Kuis")
        logout_button = QPushButton("Keluar")

        layout.addWidget(start_quiz_button)
        layout.addWidget(logout_button)

        self.home_page.setLayout(layout)
        start_quiz_button.clicked.connect(self.start_quiz)
        logout_button.clicked.connect(self.logout)

    def setup_quiz_page(self):
        layout = QVBoxLayout()
        self.question_label = QLabel("Soal akan ditampilkan di sini.")
        layout.addWidget(self.question_label)
        self.answer_input = QLineEdit()
        layout.addWidget(self.answer_input)
        self.timer_label = QLabel("Waktu pengerjaan: 01:00")
        layout.addWidget(self.timer_label)
        submit_button = QPushButton("Submit Jawaban")
        layout.addWidget(submit_button)
        back_button = QPushButton("Kembali ke Beranda")
        layout.addWidget(back_button)
        self.quiz_page.setLayout(layout)
        submit_button.clicked.connect(self.submit_answer)
        back_button.clicked.connect(self.back_to_home)
        
        self.quiz_timer = QTimer(self)
        self.quiz_timer.timeout.connect(self.update_quiz_timer)
        self.time_left = 60

    def start_quiz(self):
        self.current_question = "Apa ibu kota Indonesia?"
        self.correct_answer = "Jakarta"
        self.question_label.setText(self.current_question)
        self.stack.setCurrentWidget(self.quiz_page)
        self.time_left = 60
        self.quiz_timer.start(1000)

    def update_quiz_timer(self):
        self.time_left -= 1
        self.timer_label.setText(f"Waktu pengerjaan: {QTime(0, 0).addSecs(self.time_left).toString('mm:ss')}")
        if self.time_left <= 0:
            self.time_up()

    def time_up(self):
        self.quiz_timer.stop()
        QMessageBox.warning(self, "Waktu Habis", "Waktu pengerjaan kuis telah habis!")
        self.back_to_home()

    def submit_answer(self):
        user_answer = self.answer_input.text().strip()
        if user_answer.lower() == self.correct_answer.lower():
            QMessageBox.information(self, "Benar!", "Jawaban Anda benar!")
        else:
            QMessageBox.warning(self, "Salah!", f"Jawaban yang benar: {self.correct_answer}.")
        self.answer_input.clear()
        self.back_to_home()

    def back_to_home(self):
        self.quiz_timer.stop()
        self.stack.setCurrentWidget(self.home_page)

    def logout(self):
        QMessageBox.information(self, "Logout", "Anda telah keluar.")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    initialize_database()
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
