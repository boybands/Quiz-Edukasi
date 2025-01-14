import sqlite3
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QComboBox, QFrame, QDialog, QFileDialog,
                             QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QRadioButton, QButtonGroup,
                             QLineEdit, QStyle, QTextEdit, QTableWidget, QStackedLayout, QFormLayout, QTableWidgetItem, QTabWidget)
from PySide6.QtCore import Qt, QSize, QDateTime, QTimer
from PySide6.QtGui import QIcon, QPixmap

NUM_OPTIONS = 4  # Konstanta untuk jumlah opsi jawaban

class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Quiz")  # Judul jendela aplikasi
        self.setGeometry(300, 200, 800, 600)  # Ukuran dan posisi jendela

        self.current_question_index = 0  # Indeks pertanyaan saat ini
        self.score = 0  # Skor pengguna
        self.user_name = ""  # Nama pengguna
        self.logged_in_user = None  # Menyimpan informasi pengguna yang sedang login
        self.start_time = None  # Waktu mulai kuis
        self.end_time = None  # Waktu selesai kuis
        self.init_database()  # Inisialisasi database
        self.questions = []  # Daftar pertanyaan
        self.results = []  # Daftar hasil
        self.makul_list = []  # Daftar mata kuliah
        self.initUI()  # Inisialisasi antarmuka pengguna

    def init_database(self):
        self.conn = sqlite3.connect("quizapp.db")  # Koneksi ke database SQLite
        self.cursor = self.conn.cursor()  # Membuat objek cursor untuk eksekusi perintah SQL

        # Membuat tabel pengguna
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                Name TEXT NOT NULL,
                                Email TEXT UNIQUE NOT NULL,
                                Password TEXT NOT NULL,
                                Role TEXT NOT NULL)''')
        self.conn.commit()  # Menyimpan perubahan ke database
       
        # Membuat tabel pertanyaan
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                question TEXT NOT NULL,
                                option1 TEXT NOT NULL,
                                option2 TEXT NOT NULL,
                                option3 TEXT NOT NULL,
                                option4 TEXT NOT NULL,
                                correct_option INTEGER NOT NULL,
                                subject TEXT NOT NULL)''')
        self.conn.commit()
        
        try:
            self.cursor.execute("ALTER TABLE questions ADD COLUMN subject TEXT")  # Menambahkan kolom subject jika belum ada
        except sqlite3.OperationalError:
            # Kolom sudah ada, tidak melakukan apa-apa
            pass
        
        # Membuat tabel hasil
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        score INTEGER NOT NULL,
                        correct_answers INTEGER NOT NULL,
                        time_limit INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
        self.conn.commit()
        
        try:
            self.cursor.execute("ALTER TABLE results ADD COLUMN time_limit INTEGER")  # Menambahkan kolom time_limit jika belum ada
        except sqlite3.OperationalError:
            pass
        try:
            self.cursor.execute("ALTER TABLE results ADD COLUMN start_time TEXT")  # Menambahkan kolom start_time jika belum ada
        except sqlite3.OperationalError:
            pass
        try:
            self.cursor.execute("ALTER TABLE results ADD COLUMN end_time TEXT")  # Menambahkan kolom end_time jika belum ada
        except sqlite3.OperationalError:
            # Kolom sudah ada, tidak melakukan apa-apa
            pass
        
    def initUI(self):
        with open("style.qss", "r") as file:
            stylesheet = file.read()  # Membaca file stylesheet
            QApplication.instance().setStyleSheet(stylesheet)  # Mengatur stylesheet aplikasi

        self.central_widget = QWidget()  # Widget pusat untuk antarmuka
        self.setCentralWidget(self.central_widget)  # Mengatur widget pusat
        self.layout = QStackedLayout()  # Layout bertumpuk untuk mengelola beberapa tampilan
        self.central_widget.setLayout(self.layout)  # Mengatur layout untuk widget pusat

        self.buat_halaman_login()  # Membuat tampilan login
        self.buat_halaman_register()  # Membuat tampilan pendaftaran
        self.buat_halaman_utama()  # Membuat tampilan utama kuis
        self.buat_panel_admin()  # Membuat panel admin

        self.layout.setCurrentWidget(self .login_widget)  # Menampilkan tampilan login sebagai tampilan awal

    def show_message(self, title, message, icon=QMessageBox.Information):
        QMessageBox(icon, title, message, QMessageBox.Ok, self).exec()  # Menampilkan pesan kepada pengguna

    def atur_batas_waktu(self):
        self.time_limits = {}  # Dictionary untuk menyimpan waktu per mata kuliah
        
        for subject, time_input in self.time_inputs.items():
            time_limit = time_input.text().strip()  # Mengambil waktu dari input
            
            if not time_limit.isdigit() or int(time_limit) <= 0:
                self.show_message("Peringatan", f"Waktu untuk {subject} tidak valid.", QMessageBox.Warning)  # Peringatan jika waktu tidak valid
                return
            
            self.time_limits[subject] = int(time_limit)  # Simpan waktu dalam dictionary

        self.show_message("Berhasil", "Waktu pengerjaan berhasil diatur untuk semua mata kuliah.")  # Konfirmasi pengaturan waktu

    def perbarui_timer(self):
        minutes, seconds = divmod(self.remaining_time, 60)  # Menghitung menit dan detik dari waktu tersisa
        self.timer_label.setText(f"Sisa Waktu: {minutes:02}:{seconds:02}")  # Menampilkan waktu tersisa

        if self.remaining_time == 0:
            self.timer.stop()  # Hentikan timer jika waktu habis
            self.show_message("Waktu Habis", "Waktu pengerjaan kuis telah habis.")  # Peringatan waktu habis
            self.selesai_quiz()  # Akhiri kuis jika waktu habis

        self.remaining_time -= 1  # Mengurangi waktu tersisa
        
    def buat_halaman_login(self):
        self.login_widget = QWidget()  # Widget untuk tampilan login
        login_layout = QVBoxLayout()  # Layout vertikal untuk tampilan login
        self.login_widget.setObjectName("loginn")  # Memberi ID untuk tampilan login
        login_layout = QVBoxLayout()

        self.image_label = QLabel()  # Label untuk gambar
        pixmap = QPixmap("login_icon.jpg")  # Mengambil gambar untuk tampilan login
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Mengatur ukuran gambar
            self.image_label.setPixmap(scaled_pixmap)  # Menampilkan gambar
            self.image_label.setAlignment(Qt.AlignCenter)  # Mengatur posisi gambar
        login_layout.addWidget(self.image_label)  # Menambahkan gambar ke layout

        login_form_layout = QFormLayout()  # Layout untuk form login
        email_layout = QHBoxLayout()  # Layout horizontal untuk input email
        email_icon = QLabel()  # Label untuk ikon email
        email_icon.setPixmap(QPixmap("email.png").scaled(17, 17, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Mengatur ikon email
        self.email_input = QLineEdit()  # Input untuk email
        email_layout.addWidget(email_icon)  # Menambahkan ikon email ke layout
        email_layout.addWidget(self.email_input)  # Menambahkan input email ke layout
        login_form_layout.addRow("Email:", email_layout)  # Menambahkan baris email ke form

        password_layout = QHBoxLayout()  # Layout horizontal untuk input password
        password_icon = QLabel()  # Label untuk ikon password
        password_icon.setPixmap(QPixmap("password.jpg").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Mengatur ikon password
        self.password_input = QLineEdit()  # Input untuk password
        self.password_input.setEchoMode(QLineEdit.Password)  # Mengatur mode input password
        password_layout.addWidget(password_icon)  # Menambahkan ikon password ke layout
        password_layout.addWidget(self.password_input)  # Menambahkan input password ke layout
        login_form_layout.addRow("Password:", password_layout)  # Menambahkan baris password ke form
        
        self.label_quiz = QLabel('Jenis Soal:')  # Label untuk jenis soal
        self.combo_quiz = QComboBox()  # ComboBox untuk memilih jenis soal
        self.combo_quiz.setMinimumWidth(160)  # Menetapkan lebar minimum untuk ComboBox
        self.combo_quiz.addItems(["Bahasa Indonesia", "Matematika", "Bahasa Inggris", "Agama", "Pkn", "Seni Budaya"])  # Menambahkan pilihan jenis soal
        self.combo_quiz.setToolTip("Pilih quiz yang diinginkan")  # Tooltip untuk ComboBox
        
        login_form_layout.addRow(self .label_quiz, self.combo_quiz)  # Menambahkan label dan ComboBox ke form login

        self.login_button = QPushButton("Login")  # Tombol untuk login
        self.login_button.setObjectName("login")  # Memberi ID untuk tombol login
        self.login_button.setObjectName("btnlogin")  # Memberi ID untuk tombol login
        self.login_button.clicked.connect(self.proses_login)  # Menghubungkan tombol login dengan fungsi proses_login

        self.register_button = QPushButton("Sign Up")  # Tombol untuk pendaftaran
        self.register_button.setObjectName("btnsignup")  # Memberi ID untuk tombol pendaftaran
        self.register_button.clicked.connect(lambda: self.layout.setCurrentWidget(self.register_widget))  # Menghubungkan tombol pendaftaran untuk berpindah ke tampilan pendaftaran

        login_layout.addLayout(login_form_layout)  # Menambahkan form login ke layout
        login_layout.addWidget(self.login_button)  # Menambahkan tombol login ke layout
        login_layout.addWidget(self.register_button)  # Menambahkan tombol pendaftaran ke layout

        self.login_widget.setLayout(login_layout)  # Mengatur layout untuk widget login
        self.layout.addWidget(self.login_widget)  # Menambahkan widget login ke layout bertumpuk

    def buat_halaman_register(self):
        self.register_widget = QWidget()  # Widget untuk tampilan pendaftaran
        register_layout = QVBoxLayout()  # Layout vertikal untuk tampilan pendaftaran

        self.register_label = QLabel("Sign Up")  # Label untuk tampilan pendaftaran
        self.register_label.setPixmap(QPixmap("signup_icon.jpg").scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Mengatur gambar untuk tampilan pendaftaran
        self.register_label.setAlignment(Qt.AlignCenter)  # Mengatur posisi label
        self.register_label.setStyleSheet("font-size: 18px; font-weight: bold;")  # Mengatur gaya label

        register_form_layout = QFormLayout()  # Layout untuk form pendaftaran
        self.reg_name_input = QLineEdit()  # Input untuk nama
        self.reg_email_input = QLineEdit()  # Input untuk email
        self.reg_password_input = QLineEdit()  # Input untuk password
        self.reg_password_input.setEchoMode(QLineEdit.Password)  # Mengatur mode input password
        self.reg_role_input = QLineEdit()  # Input untuk peran (role)
        self.reg_role_input.setPlaceholderText("Sebagai 'admin'/'peserta'")  # Placeholder untuk input role

        register_form_layout.addRow("Nama:", self.reg_name_input)  # Menambahkan baris nama ke form
        register_form_layout.addRow("Email:", self.reg_email_input)  # Menambahkan baris email ke form
        register_form_layout.addRow("Password:", self.reg_password_input)  # Menambahkan baris password ke form
        register_form_layout.addRow("Role:", self.reg_role_input)  # Menambahkan baris role ke form

        self.register_submit_button = QPushButton("Submit")  # Tombol untuk mengirim pendaftaran
        self.register_submit_button.clicked.connect(self.proses_register)  # Menghubungkan tombol dengan fungsi proses_register

        self.back_to_login_button = QPushButton("Back to Login")  # Tombol untuk kembali ke tampilan login
        self.back_to_login_button.clicked.connect(lambda: self.layout.setCurrentWidget(self.login_widget))  # Menghubungkan tombol untuk berpindah ke tampilan login

        register_layout.addWidget(self.register_label)  # Menambahkan label pendaftaran ke layout
        register_layout.addLayout(register_form_layout)  # Menambahkan form pendaftaran ke layout
        register_layout.addWidget(self.register_submit_button)  # Menambahkan tombol submit ke layout
        register_layout.addWidget(self.back_to_login_button)  # Menambahkan tombol kembali ke login ke layout

        self.register_widget.setLayout(register_layout)  # Mengatur layout untuk widget pendaftaran
        self.layout.addWidget(self.register_widget)  # Menambahkan widget pendaftaran ke layout bertumpuk

    def buat_halaman_utama(self):
        self.main_widget = QWidget()  # Widget untuk tampilan utama kuis
        main_layout = QVBoxLayout()  # Layout vertikal untuk tampilan utama

        self.question_label = QLabel("Selamat datang di Aplikasi Quiz! Klik Start untuk memulai.")  # Label untuk menyambut pengguna
        self.question_label.setAlignment(Qt.AlignCenter)  # Mengatur posisi label
        self.question_label.setStyleSheet("font-size: 18px;")  # Mengatur gaya label

        self.option_buttons = [QRadioButton() for _ in range(NUM_OPTIONS)]  # Membuat tombol radio untuk opsi jawaban
        self.option_group = QButtonGroup()  # Grup untuk mengelompokkan tombol radio
        for button in self.option_buttons:
            self.option_group.addButton(button)  # Menambahkan tombol ke grup
            
        self.timer_label = QLabel("Sisa Waktu: --:--")  # Label untuk menampilkan waktu tersisa
        self.timer_label.setAlignment(Qt.AlignCenter)  # Mengatur posisi label
        main_layout.addWidget(self.timer_label)  # Menambahkan label waktu ke layout

        self.option_buttons = [QRadioButton() for _ in range(NUM_OPTIONS)]
        self.option_group = QButtonGroup()
        for button in self.option_buttons:
            self.option_group.addButton(button)
            
        self.previous_button = QPushButton()  # Tombol untuk kembali ke pertanyaan sebelumnya
        icon = QApplication.style().standardIcon(QStyle.SP_ArrowLeft)  # Ikon untuk tombol sebelumnya
        self.previous_button.setIcon(icon)  # Mengatur ikon untuk tombol
        self.previous_button.setIconSize(QSize(24, 24))  # Mengatur ukuran ikon
        self.previous_button.clicked.connect(self.tampilkan_pertanyaan_sebelumnya)  # Menghubungkan tombol dengan fungsi untuk menampilkan pertanyaan sebelumnya
        self.previous_button.setEnabled(False)  # Menonaktifkan tombol sebelumnya di awal

        self.next_button = QPushButton()  # Tombol untuk melanjutkan ke pertanyaan berikutnya
        icon = QApplication.style().standardIcon(QStyle.SP_ArrowForward)  # Ikon untuk tombol berikutnya
        self.next_button.setIcon(icon)  # Mengatur ikon untuk tombol
        self.next_button.setIconSize(QSize(24, 24))  # Mengatur ukuran ikon
        self.next_button.clicked.connect(self.tampilkan_pertanyaan_berikutnya)  # Menghubungkan tombol dengan fungsi untuk menampilkan pertanyaan berikutnya
        self.next_button.setEnabled(False)  # Menonaktifkan tombol berikutnya di awal

        self.finish_button = QPushButton("Finish")  # Tombol untuk menyelesaikan kuis
        self.finish_button.clicked.connect(self.selesai_quiz)  # Menghubungkan tombol dengan fungsi untuk menyelesaikan kuis
    
        navigation_layout = QHBoxLayout()  # Layout horizontal untuk navigasi
        navigation_layout.addWidget(self.previous_button)  # Menambahkan tombol sebelumnya ke layout
        navigation_layout.addWidget(self.next_button)  # Menambahkan tombol berikutnya ke layout

        main_layout.addWidget(self.question_label)  # Menambahkan label pertanyaan ke layout
        for button in self.option_buttons:
            main_layout.addWidget(button)  # Menambahkan tombol opsi ke layout
        main_layout.addLayout(navigation_layout)  # Menambahkan layout navigasi ke layout utama
        main_layout.addWidget(self.finish_button)  # Menambahkan tombol selesai ke layout

        self.main_widget.setLayout(main_layout)  # Mengatur layout untuk widget utama
        self.layout.addWidget(self.main_widget)  # Menambahkan widget utama ke layout bertumpuk

    def buat_panel_admin(self):
        self.admin_widget = QWidget()  # Widget untuk panel admin
        admin_layout = QVBoxLayout()  # Layout vertikal untuk panel admin

        self.logout_button = QPushButton()  # Tombol untuk logout
        self.logout_button.setIcon(QIcon("logout.png"))  # Mengatur ikon untuk tombol logout
        self.logout_button.setObjectName("btnlogout")  # Memberi ID untuk tombol logout
        self.logout_button.clicked.connect(self.logout)  # Menghubungkan tombol logout dengan fungsi logout
        
        logout_layout = QHBoxLayout()  # Layout horizontal untuk logout
        logout_layout.addWidget(self.logout_button)  # Menambahkan tombol logout ke layout
        logout_layout.addStretch()  # Menambahkan ruang kosong di sebelah kanan tombol logout
        admin_layout.addLayout(logout_layout)  # Menambahkan layout logout ke layout admin
        
        self.tabs = QTabWidget()  # Tab widget untuk panel admin

        layout = QVBoxLayout()  # Layout vertikal untuk tab

        line = QFrame()  # Garis pemisah
        line.setFrameShape(QFrame.HLine)  # Mengatur bentuk garis
        layout.addWidget(line)  # Menambahkan garis ke layout

        waktu = QDateTime.currentDateTime()  # Mengambil waktu saat ini
        formatted_time = waktu.toString("yyyy-MM-dd HH:mm:ss")  # Mengatur format waktu
        label = QLabel(formatted_time)  # Label untuk menampilkan waktu
        label.setStyleSheet("font-size: 10pt; color: gray;")  # Mengatur gaya label
        layout.addWidget(label)  # Menambahkan label waktu ke layout

        admin_layout.addLayout(layout)  # Menambahkan layout waktu ke layout admin

        self.tabs = QTabWidget()  # Membuat tab widget
        tab1 = QWidget()  # Tab untuk menambah pertanyaan
        tab1_layout = QVBoxLayout()
        
        self.tambah_pertanyaan_label = QLabel("Tambah Pertanyaan Baru")  # Label untuk menambah pertanyaan baru
        tab1_layout.addWidget(self.tambah_pertanyaan_label)  # Menambahkan label ke layout tab

        self.new_question_input = QLineEdit()  # Input untuk pertanyaan baru
        self.new_question_input.setPlaceholderText("Masukkan teks pertanyaan")  # Placeholder untuk input pertanyaan
        tab1_layout.addWidget(self.new_question_input)  # Menambahkan input pertanyaan ke layout

        self.subject_input = QComboBox()  # ComboBox untuk memilih jenis soal
        self.subject_input.setPlaceholderText("Pilih Jenis Soal")  # Placeholder untuk ComboBox
        self.subject_input.addItems(["Bahasa Indonesia", "Matematika", "Bahasa Inggris", "Agama", "Pkn", "Seni Budaya"])  # Menambahkan pilihan jenis soal
        tab1_layout.addWidget(self.subject_input)  # Menambahkan ComboBox ke layout

        self.new_options_input = QTextEdit()  # TextEdit untuk memasukkan opsi jawaban
        self.new_options_input.setPlaceholderText("Masukkan opsi-opsi, dipisahkan dengan koma")  # Placeholder untuk opsi
        tab1_layout.addWidget(self.new_options_input)  # Menambahkan TextEdit ke layout

        self.correct_option_input = QLineEdit()  # Input untuk indeks jawaban benar
        self.correct_option_input.setPlaceholderText("Masukkan indeks jawaban benar (0-3)")  # Placeholder untuk input indeks
        tab1_layout.addWidget(self.correct_option_input)  # Menambahkan input indeks ke layout

        self.tambah_pertanyaan_button = QPushButton("Tambah Pertanyaan")  # Tombol untuk menambah pertanyaan
        self.tambah_pertanyaan_button.setObjectName("tambahpertanyaan")  # Memberi ID untuk tombol tambah pertanyaan
        self.tambah_pertanyaan_button.clicked.connect(self.tambah_pertanyaan)  # Menghubungkan tombol dengan fungsi untuk menambah soal
        tab1_layout.addWidget(self.tambah_pertanyaan_button)  # Menambahkan tombol ke layout

        tab1.setLayout(tab1_layout)  # Mengatur layout untuk tab1
        self.tabs.addTab(tab1, "Tambah Pertanyaan Baru")  # Menambahkan tab untuk menambah pertanyaan
        admin_layout.addWidget(self.tabs)  # Menambahkan tab widget ke layout admin

        self.admin_widget.setLayout(admin_layout)
      
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()

        self.questions_label = QLabel("Daftar Pertanyaan")
        tab2_layout.addWidget(self.questions_label)

        self.questions_table = QTableWidget()
        self.questions_table.setColumnCount(8)  
        self.questions_table.setHorizontalHeaderLabels(["ID", "Pertanyaan", "Opsi 1", "Opsi 2", "Opsi 3", "Opsi 4", "Jawaban Benar", "Jenis Soal"])
        tab2_layout.addWidget(self.questions_table)

        self.edit_button = QPushButton("Edit Soal")
        self.edit_button.setObjectName("btneditsoal")
        self.edit_button.clicked.connect(self.edit_pertanyaan)

        self.delete_button = QPushButton("Hapus Soal")
        self.delete_button.setObjectName("btnhapussoal")
        self.delete_button.clicked.connect(self.hapus_pertanyaan)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        tab2_layout.addLayout(button_layout)

        tab2.setLayout(tab2_layout)

        tab3 = QWidget()
        tab3_layout = QVBoxLayout()

        self.results_label = QLabel("Hasil Peserta")
        tab3_layout.addWidget(self.results_label)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Nama", "Skor", "Jawaban Benar", "Waktu Mulai", "Waktu Selesai"])
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setStretchLastSection(True)  # Memastikan kolom terakhir mengisi ruang
        self.results_table.resizeColumnsToContents()  # Menyesuaikan ukuran kolom dengan konten

        self.results_table.setColumnWidth(3, 200)  # Lebar kolom "Waktu Mulai"
        self.results_table.setColumnWidth(4, 200)  # Lebar kolom "Waktu Selesai"

        tab3_layout.addWidget(self.results_table)

        self.delete_result_button = QPushButton("Hapus Hasil")
        self.delete_result_button.setObjectName("btnhapusresults")
        self.delete_result_button.clicked.connect(self.hapus_btnhasil)

        buttonrsl_layout = QHBoxLayout()
        buttonrsl_layout.addWidget(self.delete_result_button)
                
        tab3_layout.addLayout(buttonrsl_layout)
        
        tab3.setLayout(tab3_layout)

        self.tabs.addTab(tab1, 'Tambah Pertanyaan Baru')
        self.tabs.addTab(tab2, 'Daftar Pertanyaan')
        self.tabs.addTab(tab3, 'Hasil Peserta')

        admin_layout.addWidget(self.tabs)  # Menambahkan QTabWidget ke layout admin
        
        self.admin_widget.setLayout(admin_layout)  # Mengatur layout untuk widget admin
        self.layout.addWidget(self.admin_widget)  # Menambahkan widget admin ke layout bertumpuk
        
        self.muat_pertanyaan()  # Memuat pertanyaan dari database
        self.muat_hasil()  # Memuat hasil dari database

    def proses_login(self):
        email = self.email_input.text().strip()  # Mengambil email dari input
        password = self.password_input.text().strip()  # Mengambil password dari input

        self.email_input.setStyleSheet("") # Reset warna latar belakang
        self.password_input.setStyleSheet("")
        
        if "@gmail.com" not in email:  # Validasi format email
            QMessageBox.warning(self, "Login Gagal", "Format email tidak valid. Harus menggunakan '@gmail.com'.")  # Peringatan jika email tidak valid
            self.email_input.setStyleSheet("background-color: #FFCCCC;")  # Warna merah muda untuk kesalahan            
            return

        if len(password) < 8:  # Validasi panjang password
            QMessageBox.warning(self, "Login Gagal", "Password harus berisi minimal 8 karakter.")  # Peringatan jika password terlalu pendek
            self.password_input.setStyleSheet("background-color: #FFCCCC;")  # Warna merah muda untuk kesalahan         
            return

        self.cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))  # Mencari pengguna di database
        user = self.cursor.fetchone()  # Mengambil hasil pencarian

        if user:  # Jika pengguna ditemukan
            role = user[4]  # Mengambil peran pengguna
            self.logged_in_user = {"id": user[0], "name": user[1], "email": user[2], "role": role}  # Menyimpan informasi pengguna
            
            self.email_input.setStyleSheet("background-color: #D4EDDA;")  # Light green
            self.password_input.setStyleSheet("background-color: #D4EDDA;")
            
            if role == "admin":  # Jika pengguna adalah admin
                QMessageBox.information(self, "Login Berhasil", "Selamat datang, Admin!")  # Menampilkan pesan selamat datang
                self.layout.setCurrentWidget(self.admin_widget)  # Berpindah ke panel admin
                self.muat_pertanyaan()  # Memuat semua soal tanpa filter
                self.muat_hasil()  # Memuat semua hasil

            else:  # Jika pengguna adalah peserta
                QMessageBox.information(self, "Login Berhasil", f"Selamat datang, {user[1]}!")  # Menampilkan pesan selamat datang
                selected_subject = self.combo_quiz.currentText()  # Mengambil jenis soal yang dipilih
                self.muat_pertanyaan(filter_by_subject=selected_subject)  # Memuat soal berdasarkan mata pelajaran
                self.layout .setCurrentWidget(self.main_widget)  # Berpindah ke tampilan utama kuis
        else:  # Jika email atau password salah
            QMessageBox.warning(self, "Login Gagal", "Email atau password salah.")  # Menampilkan pesan kesalahan
            self.email_input.setStyleSheet("background-color: #FFCCCC;")  # Warna merah muda untuk kesalahan
            self.password_input.setStyleSheet("background-color: #FFCCCC;")
            
    def proses_register(self):
        name = self.reg_name_input.text().strip()  # Mengambil nama dari input
        email = self.reg_email_input.text().strip()  # Mengambil email dari input
        password = self.reg_password_input.text().strip()  # Mengambil password dari input
        role = self.reg_role_input.text().strip().lower()  # Mengambil role dari input dan mengubah ke huruf kecil

        self.reg_name_input.setStyleSheet("")
        self.reg_email_input.setStyleSheet("")
        self.reg_password_input.setStyleSheet("")
        self.reg_role_input.setStyleSheet("")
        
        # Validasi email dan password
        if "@gmail.com" not in email:  # Validasi format email
            QMessageBox.warning(self, "Pendaftaran Gagal", "Format email tidak valid. Harus menggunakan '@gmail.com'.")  # Peringatan jika email tidak valid
            self.reg_email_input.setStyleSheet("background-color: #FFCCCC;")  # Warna merah muda untuk kesalahan    
            return

        if len(password) < 8:  # Validasi panjang password
            QMessageBox.warning(self, "Pendaftaran Gagal", "Password harus berisi minimal 8 karakter.")  # Peringatan jika password terlalu pendek
            self.reg_password_input.setStyleSheet("background-color: #FFCCCC;")  # Warna merah muda untuk kesalahan
            return

        if not name: # Validasi nama dan peran
            QMessageBox.warning(self, "Pendaftaran Gagal", "Nama tidak boleh kosong.")
            self.reg_name_input.setStyleSheet("background-color: #FFCCCC;")  # Warna merah muda untuk kesalahan
            return

        if role not in ["admin", "peserta"]:
            QMessageBox.warning(self, "Pendaftaran Gagal", "Peran harus diisi dengan 'admin' atau 'peserta'.")
            self.reg_role_input.setStyleSheet("background-color: #FFCCCC;")  # Warna merah muda untuk kesalahan
            return
        
        try:
            self.cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                                (name, email, password, role))  # Menambahkan pengguna baru ke database
            self.conn.commit()  # Menyimpan perubahan ke database

            self.reg_name_input.setStyleSheet("background-color: #D4EDDA;")  # Light green
            self.reg_email_input.setStyleSheet("background-color: #D4EDDA;")
            self.reg_password_input.setStyleSheet("background-color: #D4EDDA;")
            self.reg_role_input.setStyleSheet("background-color: #D4EDDA;")
                        
            QMessageBox.information(self, "Pendaftaran Berhasil", "Akun berhasil dibuat! Silakan login.")  # Konfirmasi pendaftaran berhasil
            self.layout.setCurrentWidget(self.login_widget)  # Kembali ke tampilan login
            
        except sqlite3.IntegrityError:  # Jika email sudah terdaftar
            QMessageBox.warning(self, "Pendaftaran Gagal", "Email sudah terdaftar.")  # Menampilkan pesan kesalahan
            self.reg_email_input.setStyleSheet("background-color: #FFCCCC;")  # Warna merah muda untuk kesalahan

    def muat_pertanyaan(self, filter_by_subject=None):
        if filter_by_subject:  # Jika ada filter berdasarkan mata kuliah
            self.cursor.execute("SELECT * FROM questions WHERE subject = ?", (filter_by_subject,))  # Mengambil pertanyaan berdasarkan mata kuliah
        else:
            self.cursor.execute("SELECT * FROM questions")  # Mengambil semua pertanyaan
        self.questions = self.cursor.fetchall()  # Menyimpan hasil ke dalam daftar pertanyaan
        
        if not self.questions:  # Jika tidak ada soal yang dimuat
            QMessageBox.warning(self, "Error", "Tidak ada pertanyaan yang dimuat!")  # Menampilkan pesan kesalahan
            return  # Keluar dari fungsi jika tidak ada soal
        
        random.shuffle(self.questions)  # Mengacak urutan pertanyaan

        # Menampilkan soal dalam QTableWidget untuk panel admin (questions_table)
        if hasattr(self, 'questions_table'):  # Pastikan questions_table ada sebelum digunakan
            self.questions_table.setRowCount(len(self.questions))  # Menyesuaikan jumlah baris dengan jumlah soal
            for row_idx, question in enumerate(self.questions):
                self.questions_table.setItem(row_idx, 0, QTableWidgetItem(str(question[0])))  # ID
                self.questions_table.setItem(row_idx, 1, QTableWidgetItem(question[1]))  # Pertanyaan
                self.questions_table.setItem(row_idx, 2, QTableWidgetItem(question[2]))  # Opsi 1
                self.questions_table.setItem(row_idx, 3, QTableWidgetItem(question[3]))  # Opsi 2
                self.questions_table.setItem(row_idx, 4, QTableWidgetItem(question[4]))  # Opsi 3
                self.questions_table.setItem(row_idx, 5, QTableWidgetItem(question[5]))  # Opsi 4
                
                # Menampilkan jawaban benar berdasarkan indeks
                correct_option_index = question[6]  # Indeks jawaban benar
                correct_answer_text = question[correct_option_index + 2]  # Ambil teks jawaban benar
                self.questions_table.setItem(row_idx, 6, QTableWidgetItem(correct_answer_text))  # Jawaban Benar
                self.questions_table.setItem(row_idx, 7, QTableWidgetItem(question[7]))  # 

        self.mulai_quiz()  # Panggil mulai_quiz untuk menginisialisasi
 
    def tambah_pertanyaan(self):
        question_text = self.new_question_input.text().strip()  # Meng ambil teks pertanyaan dari input
        subject_text = self.subject_input.currentText().strip()  # Mengambil jenis soal dari QComboBox
        options_text = self.new_options_input.toPlainText().strip()  # Mengambil opsi jawaban dari TextEdit
        correct_option = self.correct_option_input.text().strip()  # Mengambil indeks jawaban benar dari input

        if not question_text or not subject_text or not options_text or not correct_option.isdigit():  # Validasi input
            self.show_message("Peringatan", "Harap isi semua bidang dengan benar.", QMessageBox.Warning)  # Peringatan jika ada input yang kosong
            return

        options = options_text.split(",")  # Memisahkan opsi jawaban berdasarkan koma
        if len(options) != NUM_OPTIONS:  # Memastikan jumlah opsi adalah 4
            self.show_message("Peringatan", "Harap masukkan tepat 4 opsi.", QMessageBox.Warning)  # Peringatan jika jumlah opsi tidak sesuai
            return

        correct_option = int(correct_option)  # Mengubah indeks jawaban benar menjadi integer
        if correct_option < 0 or correct_option >= NUM_OPTIONS:  # Validasi indeks jawaban benar
            self.show_message("Peringatan", "Indeks jawaban benar harus antara 0 dan 3.", QMessageBox.Warning)  # Peringatan jika indeks tidak valid
            return

        self.cursor.execute('''INSERT INTO questions (question, option1, option2, option3, option4, correct_option, subject)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (question_text, options[0], options[1], options[2], options[3], correct_option, subject_text))  # Menambahkan pertanyaan baru ke database
        self.conn.commit()  # Menyimpan perubahan ke database

        self.show_message("Berhasil", "Pertanyaan berhasil ditambahkan.")  # Konfirmasi pertanyaan berhasil ditambahkan

        self.new_question_input.clear()  # Mengosongkan input pertanyaan
        self.subject_input.setCurrentIndex(0)  # Reset QComboBox ke pilihan pertama
        self.new_options_input.clear()  # Mengosongkan input opsi
        self.correct_option_input.clear()  # Mengosongkan input indeks jawaban benar

        self.muat_pertanyaan()  # Muat ulang pertanyaan di tabel admin setelah menambahkan
 
    def edit_pertanyaan(self):
        selected_row = self.questions_table.currentRow()  # Mengambil baris yang dipilih di tabel pertanyaan
        if selected_row == -1:  # Jika tidak ada baris yang dipilih
            self.show_message("Peringatan", "Harap pilih soal yang ingin diedit.", QMessageBox.Warning)  # Peringatan untuk memilih soal
            return

        question_id = self.questions_table.item(selected_row, 0).text()  # Mengambil ID pertanyaan yang dipilih
        new_question_text = self.new_question_input.text()  # Mengambil teks pertanyaan baru
        new_options_text = self.new_options_input.toPlainText()  # Mengambil opsi jawaban baru
        new_correct_option = self.correct_option_input.text()  # Mengambil indeks jawaban benar baru

        if not new_question_text or not new_options_text or not new_correct_option.isdigit():  # Validasi input
            self.show_message("Peringatan", "Harap isi semua bidang dengan benar.", QMessageBox.Warning)  # Peringatan jika ada input yang kosong
            return

        options = new_options_text.split(",")  # Memisahkan opsi jawaban baru
        if len(options) != NUM_OPTIONS:  # Memastikan jumlah opsi adalah 4
            self.show_message("Peringatan", "Harap masukkan tepat 4 opsi.", QMessageBox.Warning)  # Peringatan jika jumlah opsi tidak sesuai
            return

        correct_option = int(new_correct_option)  # Mengubah indeks jawaban benar baru menjadi integer
        if correct_option < 0 or correct_option >= NUM_OPTIONS:  # Validasi indeks jawaban benar
            self.show_message("Peringatan", "Indeks jawaban benar harus antara 0 dan 3.", QMessageBox.Warning)  # Peringatan jika indeks tidak valid
            return

        self.cursor.execute('''UPDATE questions SET question = ?, option1 = ?, option2 = ?, option3 = ?, option4 = ?, correct_option = ? 
                            WHERE id = ?''',
                            (new_question_text, options[0], options[1], options[2], options[3], correct_option, question_id))  # Memperbarui pertanyaan di database
        self.conn.commit()  # Menyimpan perubahan ke database

        self.show_message("Berhasil", " Pertanyaan berhasil diperbarui.")  # Konfirmasi pertanyaan berhasil diperbarui
        self.muat_pertanyaan()  # Memuat ulang pertanyaan setelah pembaruan

    def hapus_pertanyaan(self):
        selected_row = self.questions_table.currentRow()  # Mengambil baris yang dipilih di tabel pertanyaan
        if selected_row == -1:  # Jika tidak ada baris yang dipilih
            self.show_message("Peringatan", "Harap pilih soal yang ingin dihapus.", QMessageBox.Warning)  # Peringatan untuk memilih soal
            return

        question_id = self.questions_table.item(selected_row, 0).text()  # Mengambil ID pertanyaan yang dipilih
        confirm = QMessageBox.question(self, "Konfirmasi Hapus", "Apakah Anda yakin ingin menghapus soal ini?", 
                                    QMessageBox.Yes | QMessageBox.No)  # Konfirmasi penghapusan
        if confirm == QMessageBox.Yes:  # Jika pengguna mengonfirmasi
            self.cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))  # Menghapus pertanyaan dari database
            self.conn.commit()  # Menyimpan perubahan ke database
            self.show_message("Berhasil", "Pertanyaan berhasil dihapus.")  # Konfirmasi penghapusan berhasil
            self.muat_pertanyaan()  # Memuat ulang pertanyaan setelah penghapusan
        
    def mulai_quiz(self):
        self.current_question_index = 0  # Mengatur indeks pertanyaan saat ini ke 0
        self.user_answers = [None] * len(self.questions)  # Inisialisasi jawaban pengguna dengan None
        self.perbarui_tampilan_pertanyaan()  # Memperbarui tampilan pertanyaan
        
        selected_subject = self.combo_quiz.currentText()  # Mengambil jenis soal yang dipilih peserta
        self.selected_subject = selected_subject  # Menyimpan jenis soal yang dipilih
        
        if hasattr(self, 'time_limits') and selected_subject in self.time_limits:  # Jika ada batas waktu untuk mata kuliah
            self.remaining_time = self.time_limits[selected_subject] * 60  # Mengubah waktu ke detik
        else:
            self.remaining_time = 1200  # Mengatur waktu default ke 20 menit
            
        self.start_time = QDateTime.currentDateTime()  # Mengambil waktu mulai
        
        self.timer = QTimer()  # Membuat timer
        self.timer.timeout.connect(self.perbarui_timer)  # Menghubungkan timer dengan fungsi perbarui_timer
        self.timer.start(1000)  # Memulai timer untuk update setiap detik
         
    def perbarui_tampilan_pertanyaan(self):
        if self.current_question_index < len(self.questions):  # Jika indeks pertanyaan saat ini valid
            question_data = self.questions[self.current_question_index]  # Mengambil data pertanyaan
            self.question_label.setText(question_data[1])  # Menampilkan teks pertanyaan
            
            for i, button in enumerate(self.option_buttons):  # Mengatur teks untuk setiap tombol opsi
                button.setText(question_data[i + 2])  # Mengatur teks opsi
                button.setChecked(self.user_answers[self.current_question_index] == i)  # Menandai jawaban yang dipilih

            self.previous_button.setEnabled(self.current_question_index > 0)  # Mengaktifkan tombol sebelumnya jika bukan pertanyaan pertama
            self.next_button.setEnabled(self.current_question_index < len(self.questions) - 1)  # Mengaktifkan tombol berikutnya jika bukan pertanyaan terakhir

    def tampilkan_pertanyaan_sebelumnya(self):
        if self.current_question_index > 0:  # Jika ada pertanyaan sebelumnya
            self.current_question_index -= 1  # Mengurangi indeks pertanyaan saat ini
            self.perbarui_tampilan_pertanyaan()  # Memperbarui tampilan pertanyaan
            
    def tampilkan_pertanyaan_berikutnya(self):
        self.simpan_jawaban_pengguna()  # Simpan jawaban pengguna sebelum berpindah ke pertanyaan berikutnya

        # Periksa apakah jawaban untuk pertanyaan saat ini sudah dipilih
        if self.user_answers[self.current_question_index] is None:  # Jika tidak ada jawaban yang dipilih
            self.show_message("Peringatan", "Harap pilih jawaban sebelum melanjutkan.", QMessageBox.Warning)  # Peringatan untuk memilih jawaban
            return

        if self.current_question_index < len(self.questions) - 1:  # Jika ada pertanyaan berikutnya
            self.current_question_index += 1  # Mengurangi indeks pertanyaan saat ini
            self.perbarui_tampilan_pertanyaan()  # Memperbarui tampilan pertanyaan
             
    def selesai_quiz(self):
        self.timer.stop()  # Hentikan timer
        self.simpan_jawaban_pengguna()  # Simpan jawaban pengguna sebelum menghitung skor
        self.hitung_score()
        # Hitung skor sebelum menampilkan hasil
        self.end_time = QDateTime.currentDateTime()  # Ambil waktu selesai

        confirm = QMessageBox.question(
            self, "Konfirmasi Selesai", 
            "Apakah Anda yakin ingin menyelesaikan kuis? Skor Anda akan disimpan.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:  # Jika pengguna mengonfirmasi
            self.simpan_hasil()  # Simpan hasil ke database
            self.tampilan_hasil()  # Tampilkan hasil
            self.layout.setCurrentWidget(self.login_widget)  # Kembali ke layar login
        else:
            self.show_message("Batal Selesai", "Anda bisa melanjutkan kuis.")  # Pesan jika batal menyelesaikan kuis

    # Periksa apakah jawaban untuk pertanyaan saat ini sudah dipilih
        if self.user_answers[self.current_question_index] is None:
            self.show_message("Peringatan", "Harap pilih jawaban sebelum melanjutkan.", QMessageBox.Warning)
            return

        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.perbarui_tampilan_pertanyaan()
            
    def simpan_jawaban_pengguna(self):
        for i, button in enumerate(self.option_buttons):  # Simpan jawaban yang dipilih oleh pengguna
            if button.isChecked():  # Jika tombol dipilih
                self.user_answers[self.current_question_index] = i  # Simpan indeks jawaban yang dipilih
                return  # Keluar setelah menyimpan jawaban
        self.user_answers[self.current_question_index] = None  # Jika tidak ada jawaban yang dipilih, simpan None
                
    def hitung_score(self):
        correct_answers = 0  # Reset jumlah jawaban benar
        for i, question in enumerate(self.questions):  # Iterasi melalui semua pertanyaan
            user_answer = self.user_answers[i]  # Ambil jawaban pengguna
            correct_answer = question[6]  # Indeks jawaban yang benar
            if user_answer is not None and user_answer == correct_answer:  # Pastikan user_answer tidak None
                correct_answers += 1  # Hitung jawaban benar

        if len(self.questions) > 0:  # Hitung skor sebagai persentase
            self.score = (correct_answers / len(self.questions)) * 100  # Skor dalam persen
        else:
            self.score = 0  # Jika tidak ada soal, skor adalah 0
             
    def simpan_hasil(self):
        start_time_str = self.start_time.toString("yyyy-MM-dd HH:mm:ss")  # Format waktu mulai
        end_time_str = self.end_time.toString("yyyy-MM-dd HH:mm:ss")  # Format waktu selesai
        
        user_id = self.logged_in_user["id"]  # Mengambil ID pengguna yang sedang login
        correct_answers = sum(1 for i, question in enumerate(self.questions) if self.user_answers[i] == question[6])  # Hitung jawaban benar
        score = self.score  # Gunakan skor yang sudah dihitung

        time_taken = self.start_time.secsTo(self.end_time)  # Menghitung waktu yang dihabiskan

        self.cursor.execute('''
            INSERT INTO results (user_id, score, correct_answers, time_taken, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?)''', (user_id, score, correct_answers, time_taken, start_time_str, end_time_str))  # Menyimpan hasil ke database
        self.conn.commit()  # Menyimpan perubahan ke database
       
    def tampilan_hasil(self):
        if not self.start_time or not self.end_time:
            self.show_message("Error", "Waktu mulai atau selesai tidak diatur dengan benar.")
            return
        
        start_time_str = self.start_time.toString("yyyy-MM-dd HH:mm:ss")
        end_time_str = self.end_time.toString("yyyy-MM-dd HH:mm:ss")
        
        self.result_message = f"Quiz Results\n\n"  # Menyimpan pesan hasil kuis ke dalam variabel kelas
        self.result_message += f"Subject: {self.selected_subject}\n"
        self.result_message += f"Start Time: {start_time_str}\n"
        self.result_message += f"End Time: {end_time_str}\n"
        self.result_message += "-" * 40 + "\n"
        self.result_message += f"Your score: {self.score:.2f}/{100:.2f}\n\n"
        self.result_message += "Your answers:\n"

        for i, question in enumerate(self.questions):
            user_answer = self.user_answers[i]
            correct_answer = question[6]
            self.result_message += f"Q{i + 1}: {question[1]}\n"
            self.result_message += f"Your answer: {question[user_answer + 2] if user_answer is not None else 'No answer'}\n"
            self.result_message += f"Correct answer: {question[correct_answer + 2]}\n\n"

        # Menampilkan hasil di dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Quiz Results")

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)
        text_edit.setText(self.result_message)

        layout.addWidget(text_edit)

        # Menambahkan opsi untuk menyimpan hasil kuis
        save_button = QPushButton("Simpan Hasil Quiz?", dialog)
        save_button.clicked.connect(self.simpan_hasil_to_file)
        layout.addWidget(save_button)

        dialog.resize(900, 700)
        dialog.exec()

    def simpan_hasil_to_file(self):
        # Membuka dialog untuk memilih lokasi dan nama file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Quiz Results", "", "Text Files (*.txt)")

        if file_name:
            try:
                # Menyimpan hasil ke dalam file
                with open(file_name, 'w') as file:
                    file.write(self.result_message)  # Menyimpan message hasil kuis yang sudah disimpan di variabel kelas
                self.show_message("Success", f"Hasil kuis berhasil disimpan di {file_name}")
            except Exception as e:
                self.show_message("Error", f"Terjadi kesalahan saat menyimpan hasil kuis: {str(e)}")
                    
    def muat_hasil(self):
        try:
            self.cursor.execute('''
                SELECT u.Name, r.score, r.correct_answers, r.start_time, r.end_time
                FROM results r
                JOIN users u ON r.user_id = u.id
            ''')  # Mengambil hasil dari database
            results = self.cursor.fetchall()  # Menyimpan hasil ke dalam daftar

            self.results_table.setRowCount(len(results))  # Menyesuaikan jumlah baris dengan jumlah hasil
            for row_idx, result in enumerate(results):  # Iterasi melalui semua hasil
                for col_idx, value in enumerate(result):  # Iterasi melalui setiap kolom hasil
                    self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))  # Menampilkan hasil di tabel
        except sqlite3.Error as e:  # Menangani kesalahan saat memuat hasil
            self.show_message("Error", f"Terjadi kesalahan saat memuat hasil: {str(e)}")  # Menampilkan pesan kesalahan
 
    def menambahkan_hasil(self, score):  # Menambahkan hasil ke dalam tabel
        row_count = self.results_table.rowCount()  # Mengambil jumlah baris saat ini
        self.results_table.insertRow(row_count)  # Menambahkan baris baru
        self.results_table.setItem(row_count, 0, QTableWidgetItem(self.participant_name))  # Nama peserta
        self.results_table.setItem(row_count, 1, QTableWidgetItem(str(score)))  # Skor
        
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Menonaktifkan pengeditan pada tabel
        self.results_table.resizeColumnsToContents()  # Menyesuaikan ukuran kolom dengan konten
        self.results_table.setAlternatingRowColors(True)  # Mengatur warna baris bergantian

        score = self.hitung_score()  # Fungsi yang menghitung skor
        self.menambahkan_hasil(score)  # Menambahkan hasil ke tabel
                                   
    def hapus_btnhasil(self):
        selected_row = self.results_table.currentRow()  # Mengambil baris yang dipilih di tabel hasil
        if selected_row == -1:  # Jika tidak ada baris yang dipilih
            self.show_message("Peringatan", "Harap pilih hasil yang ingin dihapus.", QMessageBox.Warning)  # Peringatan untuk memilih hasil
            return

        # Ambil user_id dari hasil yang dipilih
        user_name = self.results_table.item(selected_row, 0).text()  # Nama peserta
        self.cursor.execute("SELECT id FROM users WHERE Name = ?", (user_name,))  # Mencari ID pengguna berdasarkan nama
        user_id = self.cursor.fetchone()  # Mengambil hasil pencarian

        if user_id is None:  # Jika pengguna tidak ditemukan
            self.show_message("Error", "Peserta tidak ditemukan.")  # Menampilkan pesan kesalahan
            return

        confirm = QMessageBox.question(
            self, "Konfirmasi Hapus", 
            f"Apakah Anda yakin ingin menghapus hasil untuk peserta '{user_name}'?", 
            QMessageBox.Yes | QMessageBox.No
        )  # Konfirmasi penghapusan hasil
        if confirm == QMessageBox.Yes:  # Jika pengguna mengonfirmasi
            try:
                self.cursor.execute("DELETE FROM results WHERE user_id = ?", (user_id[0],))  # Menghapus hasil berdasarkan user_id
                self.conn.commit()  # Menyimpan perubahan ke database
                self.show_message("Berhasil", "Hasil berhasil dihapus.")  # Konfirmasi penghapusan berhasil
                self.muat_hasil()  # Memuat ulang hasil setelah penghapusan
            except sqlite3.Error as e:  # Menangani kesalahan saat menghapus hasil
                self.show_message("Error", f"Terjadi kesalahan saat menghapus hasil: {str(e)}")  # Menampilkan pesan kesalahan

    def logout(self):
        confirm = QMessageBox.question(
            self, "Konfirmasi Logout", 
            "Apakah Anda yakin ingin logout?",  # Konfirmasi logout
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:  # Jika pengguna mengonfirmasi logout
                        self.logged_in_user = None  # Menghapus informasi pengguna yang sedang login
                        self.layout.setCurrentWidget(self.login_widget)  # Kembali ke tampilan login
        else:
            self.show_message("Batal Logout", "Anda tetap login.")  # Pesan jika batal logout

    def closeEvent(self, event):
        self.conn.close()  # Menutup koneksi database saat aplikasi ditutup
        event.accept()  # Menerima event penutupan

app = QApplication([])  # Membuat instance QApplication
window = QuizApp()  # Membuat instance QuizApp
window.show()  # Menampilkan jendela aplikasi
app.exec()  # Menjalankan aplikasi