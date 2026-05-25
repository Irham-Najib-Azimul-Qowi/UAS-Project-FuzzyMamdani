# Sistem Fuzzy Mamdani - Penentuan Produksi Optimal

Aplikasi web sederhana menggunakan Streamlit untuk menentukan jumlah produksi optimal berdasarkan jumlah permintaan dan persediaan dengan menggunakan metode logika Fuzzy Mamdani (`scikit-fuzzy`).

## Fitur
* Menghitung jumlah produksi optimal berdasarkan input **Permintaan** dan **Persediaan**.
* Menggunakan 9 rule fuzzy Mamdani yang disesuaikan untuk optimasi produksi.
* Antarmuka web interaktif dan cepat berbasis Streamlit.

## Persyaratan
Pastikan Anda sudah menginstal Python (versi 3.8 - 3.11 direkomendasikan).

## Cara Menjalankan Lokal

1. **Clone repository ini:**
   ```bash
   git clone <url-repo-anda>
   cd <nama-folder-repo>
   ```

2. **Buat dan aktifkan virtual environment (opsional tapi disarankan):**
   ```bash
   python -m venv venv
   # Di Linux/macOS:
   source venv/bin/activate
   # Di Windows (CMD):
   venv\Scripts\activate
   # Di Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   ```

3. **Instal dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi Streamlit:**
   ```bash
   streamlit run app.py
   ```

## Deploy ke Streamlit Community Cloud

1. Push seluruh file di folder ini (`app.py`, `requirements.txt`, `.gitignore`, `README.md`) ke repository GitHub baru.
2. Masuk ke [Streamlit Community Cloud](https://share.streamlit.io/).
3. Klik **New app**, pilih repository GitHub Anda, cabang (`main` atau `master`), lalu tentukan Main file path sebagai `app.py`.
4. Klik **Deploy!**
