import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import time

# Import modul internal
from modules.fuzzy_system import get_fuzzy_variables, hitung_produksi_optimal
from modules.visualization import (
    plot_membership_functions, 
    plot_single_prediction_visual, 
    plot_actual_vs_predicted, 
    plot_error_distribution
)
from modules.evaluation import hitung_metrik_evaluasi, buat_analisis_error
from modules.utils import validasi_dataframe, buat_dataset_contoh

# ----------------------------------------------------
# 1. KONFIGURASI HALAMAN UTAMA & TEMA
# ----------------------------------------------------
st.set_page_config(
    page_title="Fuzzy Mamdani - Decision Support Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Buat dataset contoh secara otomatis jika belum ada di folder 'dataset/'
buat_dataset_contoh()

# Memuat custom CSS untuk mempercantik UI/UX (Glassmorphism & Dark Theme)
css_path = 'assets/style.css'
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inisialisasi Session State untuk melacak data sepanjang sesi aplikasi
if 'total_prediksi_tunggal' not in st.session_state:
    st.session_state.total_prediksi_tunggal = 0
if 'df_prediksi_massal' not in st.session_state:
    st.session_state.df_prediksi_massal = None
if 'file_name_aktif' not in st.session_state:
    st.session_state.file_name_aktif = ""

# Ambil objek variabel fuzzy untuk visualisasi default
permintaan_fuzzy, persediaan_fuzzy, produksi_fuzzy = get_fuzzy_variables()

# ----------------------------------------------------
# 2. SIDEBAR KIRI (MODERN & INFOMATIF)
# ----------------------------------------------------
with st.sidebar:
    st.markdown('<div style="text-align: center; padding: 10px 0;"><h2 style="color: #38BDF8; font-weight: 800;">⚡ FUZZY ENGINE PRO</h2><span style="color: #64748B; font-size: 0.8rem;">Decision Support System v2.1</span></div>', unsafe_allow_html=True)
    st.markdown('---')
    
    st.markdown("### 📋 Panduan Unggah Dataset")
    st.info(
        "Untuk **Prediksi Massal**, unggah file Excel (.xlsx) atau CSV dengan format:\n"
        "- Kolom Wajib: **permintaan**, **persediaan**\n"
        "- Kolom Opsional: **produksi_aktual** *(jika disertakan, fitur evaluasi statistik akan otomatis aktif)*"
    )
    
    # Tombol Download Contoh Dataset langsung dari sidebar
    st.markdown("### 📥 Unduh Berkas Contoh")
    col_dl1, col_dl2 = st.columns(2)
    
    with open('dataset/contoh_dataset.csv', 'rb') as f:
        col_dl1.download_button(
            label="📄 Unduh CSV",
            data=f,
            file_name="contoh_dataset.csv",
            mime="text/csv"
        )
        
    with open('dataset/contoh_dataset.xlsx', 'rb') as f:
        col_dl2.download_button(
            label="📊 Unduh Excel",
            data=f,
            file_name="contoh_dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    st.markdown('---')
    st.markdown("### 🛠️ Spesifikasi Sistem Fuzzy")
    st.markdown(
        "- **Metode:** Mamdani Centroid\n"
        "- **Fungsi Keanggotaan:** Triangular (Trimf)\n"
        "- **Jumlah Aturan (Rules):** 9 Rule Base\n"
        "- **Semesta Permintaan:** 760 - 7975\n"
        "- **Semesta Persediaan:** 135 - 565\n"
        "- **Semesta Produksi:** 1100 - 9040"
    )

# ----------------------------------------------------
# 3. HEADER DASHBOARD UTAMA
# ----------------------------------------------------
st.markdown('<h1 class="main-header">Fuzzy Mamdani Decision Support System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Platform kecerdasan buatan berbasis fuzzy logic untuk optimalisasi jumlah produksi pabrik secara presisi dan efisien.</p>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. PEMBAGIAN TABS (STRUKTUR DASHBOARD MODERN)
# ----------------------------------------------------
tab_home, tab_single, tab_mass, tab_eval, tab_viz = st.tabs([
    "🏠 Ringkasan Sistem", 
    "👤 Prediksi Tunggal", 
    "📊 Prediksi Massal", 
    "📉 Dashboard Evaluasi", 
    "🎨 Visualisasi Grafik"
])

# ====================================================
# TAB 1: HOME/SUMMARY DASHBOARD
# ====================================================
with tab_home:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Selamat Datang di Fuzzy Mamdani Dashboard")
    st.write(
        "Aplikasi Dashboard Analitik ini dirancang khusus untuk membantu proses pengambilan keputusan (Decision Support System) "
        "dalam menentukan jumlah produksi optimal. Sistem ini memproses variabel **Permintaan** dan **Persediaan** menggunakan "
        "logika fuzzy metode Mamdani dengan defuzzifikasi centroid."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time Metrics Row
    st.markdown("### 📈 Ringkasan Statistik Realtime")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    # Cek jumlah data massal aktif
    jumlah_data_massal = 0
    rata_rata_produksi = 0
    akurasi_tercatat = "N/A"
    
    if st.session_state.df_prediksi_massal is not None:
        df_eval = st.session_state.df_prediksi_massal
        jumlah_data_massal = len(df_eval)
        rata_rata_produksi = df_eval['produksi_fuzzy'].mean()
        
        metrik = hitung_metrik_evaluasi(df_eval)
        if metrik is not None:
            akurasi_tercatat = f"{round(metrik['akurasi'], 2)} %"
            
    m_col1.metric("Prediksi Tunggal Sesi Ini", f"{st.session_state.total_prediksi_tunggal} Kali")
    m_col2.metric("Data Massal Terproses", f"{jumlah_data_massal} Item")
    m_col3.metric("Rata-Rata Produksi Fuzzy", f"{round(rata_rata_produksi, 1)} Unit" if rata_rata_produksi > 0 else "0.0 Unit")
    m_col4.metric("Tingkat Akurasi Model", akurasi_tercatat)
    
    # Alur Kerja Fuzzy Mamdani
    st.markdown("---")
    st.markdown("### 🔄 Alur Pemrosesan Logika Fuzzy")
    flow_col1, flow_col2, flow_col3, flow_col4 = st.columns(4)
    
    with flow_col1:
        st.markdown('<div class="glass-card" style="min-height: 180px;">', unsafe_allow_html=True)
        st.markdown("**1. Fuzzifikasi**")
        st.caption("Mengubah nilai numerik permintaan dan persediaan (crisp input) menjadi derajat keanggotaan fuzzy berdasarkan fungsi keanggotaan segitiga.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with flow_col2:
        st.markdown('<div class="glass-card" style="min-height: 180px;">', unsafe_allow_html=True)
        st.markdown("**2. Evaluasi Aturan (Inferensi)**")
        st.caption("Menerapkan operator logika fuzzy AND (&) pada 9 aturan implikasi Mamdani untuk merumuskan output area keanggotaan produksi.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with flow_col3:
        st.markdown('<div class="glass-card" style="min-height: 180px;">', unsafe_allow_html=True)
        st.markdown("**3. Komposisi Aturan**")
        st.caption("Menggabungkan seluruh output aturan konduktif implikasi fuzzy menggunakan metode MAX untuk membangun satu daerah keputusan terpadu.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with flow_col4:
        st.markdown('<div class="glass-card" style="min-height: 180px;">', unsafe_allow_html=True)
        st.markdown("**4. Defuzzifikasi**")
        st.caption("Menghitung nilai pusat gravitasi (Centroid) dari gabungan daerah fuzzy untuk menghasilkan satu nilai pasti jumlah produksi optimal (crisp output).")
        st.markdown('</div>', unsafe_allow_html=True)

# ====================================================
# TAB 2: SINGLE PREDICTION
# ====================================================
with tab_single:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("👤 Simulasi Prediksi Produksi Tunggal")
    st.write("Masukkan jumlah permintaan dan persediaan di bawah ini untuk melihat hasil perhitungan fuzzy secara realtime.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_input, col_output = st.columns([1, 1.2])
    
    with col_input:
        st.markdown("### ⚙️ Input Variabel Riil")
        
        permintaan_val = st.number_input(
            "Masukkan Jumlah Permintaan (Unit)",
            min_value=760,
            max_value=7975,
            value=1420,
            step=10,
            help="Jumlah permintaan pasar dalam satu periode perencanaan."
        )
        
        persediaan_val = st.number_input(
            "Masukkan Jumlah Persediaan (Unit)",
            min_value=135,
            max_value=565,
            value=385,
            step=5,
            help="Jumlah stok persediaan barang jadi yang tersisa di gudang."
        )
        
        btn_hitung = st.button("🚀 Hitung Produksi Optimal", use_container_width=True)
        
    with col_output:
        st.markdown("### 📊 Hasil Perhitungan Centroid")
        
        if btn_hitung:
            with st.spinner("Mengeksekusi Inferensi Fuzzy Mamdani..."):
                time.sleep(0.5) # Efek micro-interaction/loading professional
                hasil_fuzzy = hitung_produksi_optimal(permintaan_val, persediaan_val)
                st.session_state.total_prediksi_tunggal += 1
                
                # Kartu Hasil Desain Premium
                st.markdown(
                    f'<div style="background: rgba(16, 185, 129, 0.1); border: 2px solid #10B981; border-radius: 12px; padding: 20px; text-align: center;">'
                    f'<h4 style="margin: 0; color: #E2E8F0; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.05em;">Rekomendasi Produksi Optimal</h4>'
                    f'<h1 style="margin: 10px 0 0 0; color: #10B981; font-size: 3rem; font-weight: 800;">{round(hasil_fuzzy, 2)} <span style="font-size: 1.5rem;">Unit</span></h1>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
                # Informasi Interpretasi
                st.success("Defuzzifikasi Centroid berhasil diselesaikan dengan presisi numerik.")
        else:
            st.warning("Silakan klik tombol **Hitung Produksi Optimal** untuk memproses nilai.")
            hasil_fuzzy = None

    # Tampilkan grafik tracking nilai keanggotaan jika hasil sudah ada
    if hasil_fuzzy is not None:
        st.markdown("---")
        st.markdown("### 📍 Posisi Parameter Nilai pada Kurva Keanggotaan")
        fig_single = plot_single_prediction_visual(
            permintaan_fuzzy, persediaan_fuzzy, produksi_fuzzy, 
            permintaan_val, persediaan_val, hasil_fuzzy
        )
        st.pyplot(fig_single)

# ====================================================
# TAB 3: MASS PREDICTION
# ====================================================
with tab_mass:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Sistem Prediksi Massal Otomatis (Batch Prediction)")
    st.write(
        "Unggah file dataset Anda (CSV atau Excel) berisi banyak baris data untuk melakukan prediksi fuzzy "
        "secara serentak dalam hitungan detik. Data hasil prediksi dapat diunduh kembali secara instan."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_upload, col_actions = st.columns([2, 1.2])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Unggah Dokumen Dataset (.csv / .xlsx)", 
            type=["csv", "xlsx"],
            help="Sistem akan mendeteksi kolom permintaan dan persediaan secara otomatis."
        )
        
    with col_actions:
        st.markdown("### 📥 Muat Data Simulasi Cepat")
        st.write("Belum memiliki file data? Klik tombol di bawah untuk langsung memuat contoh dataset simulasi skripsi yang sudah terkonfigurasi lengkap:")
        
        btn_load_sample = st.button("📁 Muat Contoh Dataset Otomatis", use_container_width=True)

    # Logika Pemrosesan Berkas Unggahan
    df_raw = None
    if uploaded_file is not None:
        st.session_state.file_name_aktif = uploaded_file.name
        try:
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Gagal membaca file berkas: {e}")
            
    elif btn_load_sample:
        st.session_state.file_name_aktif = "contoh_dataset.xlsx"
        df_raw = pd.read_excel('dataset/contoh_dataset.xlsx')
        st.toast("Berhasil memuat dataset contoh!", icon="✅")

    # Jika data berhasil dibaca, lakukan prediksi massal
    if df_raw is not None:
        is_valid, pesan, df_clean = validasi_dataframe(df_raw)
        
        if not is_valid:
            st.error(pesan)
        else:
            st.success(pesan)
            
            st.markdown("### 🚀 Melakukan Kalkulasi Prediksi...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Eksekusi kalkulasi fuzzy untuk setiap baris data
            pred_results = []
            total_baris = len(df_clean)
            
            # Membuat container kosong untuk progress simulasi modern
            for idx, row in df_clean.iterrows():
                # Simulasi animasi tipis jika data sedikit agar terlihat professional
                if total_baris < 100:
                    time.sleep(0.01)
                
                fuzzy_val = hitung_produksi_optimal(row['permintaan'], row['persediaan'])
                pred_results.append(round(fuzzy_val, 2))
                
                # Update progress bar
                pct = int(((idx + 1) / total_baris) * 100)
                progress_bar.progress(pct)
                status_text.text(f"Memproses baris ke-{idx + 1} dari {total_baris}...")
                
            progress_bar.empty()
            status_text.empty()
            
            # Masukkan hasil prediksi
            df_clean['produksi_fuzzy'] = pred_results
            
            # Hitung error jika kolom produksi_aktual tersedia
            if 'produksi_aktual' in df_clean.columns:
                df_clean['error'] = np.abs(df_clean['produksi_aktual'] - df_clean['produksi_fuzzy'])
                df_clean['error'] = df_clean['error'].round(2)
                
                y_act_no_zero = np.where(df_clean['produksi_aktual'] == 0, 1e-5, df_clean['produksi_aktual'])
                df_clean['persentase_error'] = (df_clean['error'] / y_act_no_zero) * 100
                df_clean['persentase_error'] = df_clean['persentase_error'].round(2)
                
            # Simpan dataframe hasil ke session state agar dapat diakses oleh Tab Evaluasi & Visualisasi
            st.session_state.df_prediksi_massal = df_clean
            
            # Tampilkan dataframe interaktif
            st.markdown("### 📋 Hasil Prediksi Berhasil Dibuat")
            st.dataframe(
                df_clean,
                use_container_width=True,
                column_config={
                    "permintaan": st.column_config.NumberColumn("Permintaan (Unit)", format="%d"),
                    "persediaan": st.column_config.NumberColumn("Persediaan (Unit)", format="%d"),
                    "produksi_aktual": st.column_config.NumberColumn("Produksi Aktual", format="%.1f"),
                    "produksi_fuzzy": st.column_config.NumberColumn("Produksi Fuzzy (Centroid)", format="%.2f"),
                    "error": st.column_config.NumberColumn("Error (Selisih)", format="%.2f"),
                    "persentase_error": st.column_config.NumberColumn("Persentase Error (%)", format="%.2f %%")
                }
            )
            
            # Opsi Download
            st.markdown("### 📥 Ekspor Hasil Prediksi")
            col_d1, col_d2 = st.columns(2)
            
            # In-memory CSV
            csv_bytes = df_clean.to_csv(index=False).encode('utf-8')
            col_d1.download_button(
                label="📥 Unduh Data Hasil (Format CSV)",
                data=csv_bytes,
                file_name=f"hasil_fuzzy_prediksi_{st.session_state.file_name_aktif.split('.')[0]}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # In-memory Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_clean.to_excel(writer, index=False, sheet_name="Fuzzy Mamdani")
            excel_bytes = excel_buffer.getvalue()
            
            col_d2.download_button(
                label="📥 Unduh Data Hasil (Format Excel)",
                data=excel_bytes,
                file_name=f"hasil_fuzzy_prediksi_{st.session_state.file_name_aktif.split('.')[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ====================================================
# TAB 4: EVALUATION DASHBOARD
# ====================================================
with tab_eval:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📉 Evaluasi Statistik Model Mamdani")
    st.write(
        "Menu ini menganalisis tingkat keakuratan dan performa prediksi logika fuzzy Mamdani "
        "dibandingkan dengan data produksi aktual di lapangan."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Periksa ketersediaan dataset aktif
    df_eval = st.session_state.df_prediksi_massal
    
    if df_eval is None:
        st.warning("Belum ada data massal yang dimuat. Silakan unggah berkas atau muat contoh dataset di **Tab Prediksi Massal** terlebih dahulu.")
    elif 'produksi_aktual' not in df_eval.columns:
        st.error("Kolom 'produksi_aktual' tidak ditemukan pada dataset saat ini, sehingga perhitungan evaluasi akurasi skripsi tidak dapat ditampilkan.")
    else:
        metrik = hitung_metrik_evaluasi(df_eval)
        
        if metrik is None:
            st.error("Gagal melakukan perhitungan metrik evaluasi. Periksa kembali tipe data kolom Anda.")
        else:
            # Tampilkan Ringkasan Metrik Skripsi
            st.markdown("### 📊 Ringkasan Indikator Keakuratan")
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            
            col_met1.metric(
                label="Mean Absolute Error (MAE)",
                value=f"{round(metrik['mae'], 2)} Unit",
                help="Rata-rata kesalahan absolut dari deviasi prediksi."
            )
            col_met2.metric(
                label="Root Mean Squared Error (RMSE)",
                value=f"{round(metrik['rmse'], 2)} Unit",
                help="Akar rata-rata kesalahan kuadrat. Memberikan penalti lebih tinggi untuk selisih besar."
            )
            col_met3.metric(
                label="Mean Absolute Percentage Error (MAPE)",
                value=f"{round(metrik['mape'], 2)} %",
                help="Rata-rata persentase kesalahan terhadap nilai aktual."
            )
            col_met4.metric(
                label="Akurasi Fuzzy",
                value=f"{round(metrik['akurasi'], 2)} %",
                help="Persentase tingkat kecocokan prediksi dihitung sebagai (100 - MAPE)."
            )
            
            st.markdown("---")
            
            # Grafik Distribusi Error dan Kategori Akurasi
            col_chart1, col_chart2 = st.columns([1.2, 1])
            
            with col_chart1:
                st.markdown("#### 📐 Kurva Kepadatan Distribusi Kesalahan (Error Density)")
                fig_err = plot_error_distribution(df_eval)
                st.pyplot(fig_err)
                
            with col_chart2:
                st.markdown("#### 📂 Pengelompokan Kategori Akurasi")
                analisis_kategori = buat_analisis_error(df_eval)
                
                if analisis_kategori:
                    # Tampilkan dalam bentuk representasi tabel/list visual premium
                    for kategori, jumlah in analisis_kategori.items():
                        # Hitung persentase kontribusi kategori
                        persen = (jumlah / metrik['jumlah_data']) * 100
                        
                        # Pilih pill kelas CSS
                        pill_type = "success" if "Sangat Akurat" in kategori or "Akurat" in kategori else "warning"
                        
                        st.markdown(
                            f'<div class="metric-container">'
                            f'<div>'
                            f'<span class="metric-title">{kategori}</span><br/>'
                            f'<span class="indicator-pill {pill_type}">{jumlah} Item Data</span>'
                            f'</div>'
                            f'<div class="metric-value">{round(persen, 1)}%</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
            
            st.markdown("---")
            with st.expander("📚 Interpretasi Ilmiah Metrik Evaluasi"):
                st.write(
                    "1. **Mean Absolute Error (MAE):** Nilai MAE menggambarkan rata-rata selisih mutlak antara "
                    "produksi yang diprediksi oleh sistem fuzzy dengan produksi riil di lapangan. Semakin mendekati nol, "
                    "kinerja model semakin optimal.\n"
                    "2. **Mean Absolute Percentage Error (MAPE):** Nilai MAPE mengukur deviasi dalam bentuk persentase. "
                    "Menurut kriteria Lewis (1982), nilai MAPE < 10% menunjukkan model prediksi memiliki kinerja **sangat kuat/sangat baik**.\n"
                    "3. **Akurasi Fuzzy:** Merepresentasikan persentase kedekatan model. Nilai akurasi yang tinggi membuktikan "
                    "bahwa 9 aturan fuzzy yang didefinisikan sangat representatif dengan pola data operasional perusahaan."
                )

# ====================================================
# TAB 5: GRAPHICAL VISUALIZATION
# ====================================================
with tab_viz:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🎨 Visualisasi Grafik dan Kurva Pendukung")
    st.write(
        "Halaman visualisasi grafik interaktif untuk mendukung pemaparan skripsi, laporan, "
        "atau presentasi hasil analisis model logika fuzzy Mamdani."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 📈 Grafik Fungsi Keanggotaan Variabel Fuzzy")
    fig_mf = plot_membership_functions(permintaan_fuzzy, persediaan_fuzzy, produksi_fuzzy)
    st.pyplot(fig_mf)
    
    # Grafik Perbandingan Aktual vs Prediksi (jika data massal ada kolom aktual)
    df_eval = st.session_state.df_prediksi_massal
    if df_eval is not None and 'produksi_aktual' in df_eval.columns:
        st.markdown("---")
        st.markdown("### 📊 Kurva Tren Perbandingan: Produksi Aktual vs Prediksi Fuzzy")
        fig_trend = plot_actual_vs_predicted(df_eval)
        st.pyplot(fig_trend)

# ----------------------------------------------------
# 5. FOOTER DASHBOARD PROFESSIONAL
# ----------------------------------------------------
st.markdown(
    '<div class="custom-footer">'
    '<p>© 2026 Fuzzy Mamdani Analytics Dashboard Pro. Dibuat dengan cinta untuk kebutuhan Skripsi & Riset Akademik.</p>'
    '<p>Didukung oleh <a href="https://streamlit.io" target="_blank">Streamlit</a> | '
    '<a href="https://github.com/Irham-Najib-Azimul-Qowi/UAS-Project-FuzzyMamdani" target="_blank">Repositori GitHub</a></p>'
    '</div>',
    unsafe_allow_html=True
)
