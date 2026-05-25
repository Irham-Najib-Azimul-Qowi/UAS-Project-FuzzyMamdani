# ⚡ Modern AI Analytics Dashboard & Mass Prediction - Fuzzy Mamdani

Aplikasi Web Dashboard Interaktif tingkat profesional (setara skripsi/portfolio) untuk sistem pendukung keputusan (Decision Support System) penentuan produksi optimal menggunakan logika fuzzy Mamdani. 

Proyek ini telah dikembangkan secara modular dan dilengkapi dengan fitur prediksi massal (batch prediction), evaluasi akurasi regresi statistik (MAE, RMSE, MAPE, Akurasi, R²), ekspor data in-memory ke Excel & CSV, serta visualisasi kurva keanggotaan interaktif.

---

## 📂 Struktur Project Modular

```text
fuzzy mamdani uas project/
│
├── app.py                  # Entry-point utama aplikasi dashboard Streamlit
├── requirements.txt        # Daftar dependensi modul Python yang dibutuhkan
├── README.md               # Dokumentasi panduan lengkap proyek (berkas ini)
│
├── dataset/                # Folder penyimpanan otomatis file dataset contoh
│   ├── contoh_dataset.csv
│   └── contoh_dataset.xlsx
│
├── assets/                 # Folder aset statis
│   └── style.css           # Custom styling premium (Glassmorphism & Dark Mode)
│
└── modules/                # Modul logika modular yang terpisah & reusable
    ├── fuzzy_system.py     # Algoritma fuzzy Mamdani (Antecedent, Consequent, Rules, Centroid)
    ├── visualization.py    # Pembuat grafik matplotlib (Kurva Keanggotaan, Tren Aktual vs Prediksi, Densitas Error)
    ├── evaluation.py       # Kalkulator statistik tingkat keakuratan (MAE, RMSE, MAPE, Akurasi, Kategori Error)
    └── utils.py            # Pembersih & validator dataset masukan, pembuat data contoh sintetis
```

---

## ✨ Fitur-Fitur Utama Dashboard

1. **Dashboard Ringkasan (Home):**
   * Metrik realtime yang melacak interaksi aktif sepanjang sesi.
   * Ringkasan alur kerja matematis logika fuzzy (Fuzzifikasi, Inferensi, Komposisi, Defuzzifikasi).

2. **Simulasi Prediksi Tunggal:**
   * Form masukan parameter permintaan & persediaan yang responsif.
   * Defuzzifikasi centroid instan.
   * **Visualisasi Garis Penanda:** Menampilkan posisi input dan output secara akurat pada kurva keanggotaan.

3. **Prediksi Massal Otomatis (Batch Processing):**
   * Upload file berbasis CSV maupun Excel (XLSX).
   * Fitur **Muat Contoh Dataset Otomatis** sekali klik bagi pengguna yang belum menyiapkan file.
   * Validasi tipe data dan penanganan baris kosong secara cerdas.
   * Tombol unduh hasil prediksi secara in-memory (CSV & Excel) yang instan.

4. **Analisis Evaluasi Skripsi:**
   * Menghitung **Mean Absolute Error (MAE)**, **Root Mean Squared Error (RMSE)**, **Mean Absolute Percentage Error (MAPE)**, dan **Akurasi Model**.
   * Grafik densitas distribusi kesalahan (*Error Density Fit Curve*).
   * Klasifikasi otomatis keakuratan per baris (*Sangat Akurat*, *Akurat*, *Cukup Akurat*, *Kurang Akurat*).

5. **Visualisasi Grafik Terintegrasi:**
   * Visualisasi 3-panel horizontal untuk kurva keanggotaan fuzzy.
   * Tren perbandingan nilai produksi aktual vs prediksi fuzzy untuk analisis deviasi visual.

---

## 🛠️ Cara Menjalankan Secara Lokal

### 1. Kloning Repositori
```bash
git clone https://github.com/Irham-Najib-Azimul-Qowi/UAS-Project-FuzzyMamdani.git
cd UAS-Project-FuzzyMamdani
```

### 2. Buat & Aktifkan Virtual Environment
```bash
# Di Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# Di Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```

---

## ☁️ Cara Deploy ke Streamlit Community Cloud (Gratis & Mudah)

1. Pastikan Anda telah melakukan `git push` seluruh kode dari folder proyek lokal Anda ke repositori GitHub:
   ```bash
   git add .
   git commit -m "Upgrade: Modern AI Dashboard & Mass Prediction"
   git push origin main
   ```
2. Kunjungi [Streamlit Community Cloud](https://share.streamlit.io/) dan masuk menggunakan akun GitHub Anda.
3. Klik tombol **New app** di dashboard Streamlit Anda.
4. Konfigurasikan halaman deployment:
   * **Repository:** Pilih `Irham-Najib-Azimul-Qowi/UAS-Project-FuzzyMamdani`.
   * **Branch:** Pilih `main` (atau `master`).
   * **Main file path:** Isi dengan `app.py`.
5. Klik **Deploy!** Aplikasi Anda akan langsung online dalam waktu 1-2 menit.

---

## 💡 Kualitas Kode & Best Practice
* **Modularitas:** Seluruh algoritma dipisah per fungsi khusus untuk mempermudah perawatan (*clean code*).
* **Caching:** Memanfaatkan `@st.cache_resource` dari Streamlit untuk memuat variabel dan model fuzzy agar pemrosesan data massal tidak memakan memori CPU berlebih.
* **Keamanan Data:** Penyimpanan dan pembuatan ekspor file dilakukan secara *in-memory* menggunakan `io.BytesIO()`, sehingga aman dari penulisan sampah di server.
