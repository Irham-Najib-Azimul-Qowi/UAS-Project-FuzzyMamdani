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

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Sistem Pendukung Keputusan Produksi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Buat dataset contoh secara otomatis jika belum ada di folder 'dataset/'
buat_dataset_contoh()

# Memuat custom CSS untuk mempercantik UI/UX
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

# Ambil objek variabel fuzzy
permintaan_fuzzy, persediaan_fuzzy, produksi_fuzzy = get_fuzzy_variables()

# ----------------------------------------------------
# NAVIGATION (SIDEBAR)
# ----------------------------------------------------
st.sidebar.markdown(
    '<div style="padding: 10px 0;"><h3 style="color: #F8FAFC; font-weight: 700; margin: 0;">Fuzzy Mamdani</h3>'
    '<span style="color: #64748B; font-size: 0.8rem;">Decision Support System</span></div>', 
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Menu Utama",
    [
        "Ringkasan Sistem",
        "Prediksi Tunggal",
        "Prediksi Massal",
        "Evaluasi Model",
        "Kurva Keanggotaan"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #94A3B8; margin-bottom: 8px;">Unduh Template Data</div>', unsafe_allow_html=True)

with open('dataset/contoh_dataset.csv', 'rb') as f:
    st.sidebar.download_button(
        label="Unduh CSV Template",
        data=f,
        file_name="contoh_dataset.csv",
        mime="text/csv",
        use_container_width=True
    )
    
with open('dataset/contoh_dataset.xlsx', 'rb') as f:
    st.sidebar.download_button(
        label="Unduh Excel Template",
        data=f,
        file_name="contoh_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<div style="font-size: 0.8rem; color: #64748B;">'
    'Batas Universe:<br/>'
    '- Permintaan: 760 s.d 7975<br/>'
    '- Persediaan: 135 s.d 565<br/>'
    '- Produksi: 1100 s.d 9040'
    '</div>',
    unsafe_allow_html=True
)

# ----------------------------------------------------
# MAIN CONTENT CHANNELS
# ----------------------------------------------------

# PAGE 1: RINGKASAN SISTEM
if menu == "Ringkasan Sistem":
    st.markdown('<h1 style="color: #F8FAFC; font-weight: 700; margin-bottom: 4px;">Sistem Pendukung Keputusan Produksi</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94A3B8; font-size: 1rem; margin-bottom: 24px;">Penentuan jumlah produksi optimal menggunakan pendekatan logika fuzzy metode Mamdani.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #E2E8F0; font-size: 0.95rem; line-height: 1.6;">'
        'Aplikasi ini dirancang untuk mempermudah perhitungan jumlah produksi barang secara presisi '
        'berdasarkan parameter masukkan tingkat <b>Permintaan Pasar</b> dan kapasitas <b>Sisa Persediaan Gudang</b>. '
        'Dengan menerapkan 9 aturan logika fuzzy Mamdani dan defuzzifikasi Centroid, sistem memberikan rekomendasi '
        'produksi barang yang optimal guna meminimalkan resiko kelebihan maupun kekurangan stok.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Ringkasan Statistik
    st.markdown('<h3 style="color: #F8FAFC; font-weight: 600; margin-top: 30px; margin-bottom: 16px;">Indikator Aktivitas Sesi</h3>', unsafe_allow_html=True)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    jumlah_data_massal = 0
    rata_rata_produksi = 0
    akurasi_tercatat = "N/A"
    
    if st.session_state.df_prediksi_massal is not None:
        df_eval = st.session_state.df_prediksi_massal
        jumlah_data_massal = len(df_eval)
        rata_rata_produksi = df_eval['produksi_fuzzy'].mean()
        
        metrik = hitung_metrik_evaluasi(df_eval)
        if metrik is not None:
            akurasi_tercatat = f"{round(metrik['akurasi'], 2)}%"
            
    m_col1.metric("Prediksi Tunggal Sesi Ini", f"{st.session_state.total_prediksi_tunggal} kali")
    m_col2.metric("Data Massal Terproses", f"{jumlah_data_massal} baris")
    m_col3.metric("Rata-Rata Produksi Fuzzy", f"{round(rata_rata_produksi, 1)} unit" if rata_rata_produksi > 0 else "0.0 unit")
    m_col4.metric("Tingkat Akurasi Model", akurasi_tercatat)
    
    # Langkah Alur Kerja Fuzzy (Fixed Empty Box Bug)
    st.markdown('<h3 style="color: #F8FAFC; font-weight: 600; margin-top: 30px; margin-bottom: 16px;">Tahapan Proses Inferensi Fuzzy</h3>', unsafe_allow_html=True)
    flow_col1, flow_col2, flow_col3, flow_col4 = st.columns(4)
    
    with flow_col1:
        st.markdown(
            '<div class="glass-card" style="min-height: 180px;">'
            '<div style="font-weight: 600; color: #F8FAFC; margin-bottom: 8px; font-size: 0.95rem;">1. Fuzzifikasi</div>'
            '<div style="color: #94A3B8; font-size: 0.82rem; line-height: 1.55;">Mengubah nilai riil permintaan dan persediaan menjadi derajat keanggotaan menggunakan himpunan fuzzy (sedikit, sedang, banyak).</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
    with flow_col2:
        st.markdown(
            '<div class="glass-card" style="min-height: 180px;">'
            '<div style="font-weight: 600; color: #F8FAFC; margin-bottom: 8px; font-size: 0.95rem;">2. Inferensi Fuzzy</div>'
            '<div style="color: #94A3B8; font-size: 0.82rem; line-height: 1.55;">Menerapkan operator AND (&) pada 9 aturan implikasi fuzzy untuk menentukan derajat kebenaran hipotesis konklusi produksi.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
    with flow_col3:
        st.markdown(
            '<div class="glass-card" style="min-height: 180px;">'
            '<div style="font-weight: 600; color: #F8FAFC; margin-bottom: 8px; font-size: 0.95rem;">3. Komposisi Aturan</div>'
            '<div style="color: #94A3B8; font-size: 0.82rem; line-height: 1.55;">Menggabungkan seluruh konklusi aturan implikasi fuzzy menggunakan metode MAX untuk membangun suatu daerah keputusan fuzzy tunggal.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
    with flow_col4:
        st.markdown(
            '<div class="glass-card" style="min-height: 180px;">'
            '<div style="font-weight: 600; color: #F8FAFC; margin-bottom: 8px; font-size: 0.95rem;">4. Defuzzifikasi</div>'
            '<div style="color: #94A3B8; font-size: 0.82rem; line-height: 1.55;">Menghitung nilai pusat gravitasi (Centroid) daerah keputusan fuzzy untuk mendapatkan output nilai riil produksi optimal.</div>'
            '</div>',
            unsafe_allow_html=True
        )

# PAGE 2: PREDIKSI TUNGGAL
elif menu == "Prediksi Tunggal":
    st.markdown('<h1 style="color: #F8FAFC; font-weight: 700; margin-bottom: 4px;">Kalkulator Prediksi Tunggal</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94A3B8; font-size: 1rem; margin-bottom: 24px;">Hitung rekomendasi produksi optimal untuk satu kali analisis.</p>', unsafe_allow_html=True)
    
    col_input, col_output = st.columns([1, 1.2])
    
    with col_input:
        st.markdown('<h3 style="color: #F8FAFC; font-weight: 600; margin-bottom: 16px;">Parameter Masukkan</h3>', unsafe_allow_html=True)
        
        permintaan_val = st.number_input(
            "Masukkan Jumlah Permintaan (Unit)",
            min_value=760,
            max_value=7975,
            value=1420,
            step=10
        )
        
        persediaan_val = st.number_input(
            "Masukkan Jumlah Persediaan (Unit)",
            min_value=135,
            max_value=565,
            value=385,
            step=5
        )
        
        btn_hitung = st.button("Hitung Produksi Optimal", use_container_width=True)
        
    with col_output:
        st.markdown('<h3 style="color: #F8FAFC; font-weight: 600; margin-bottom: 16px;">Hasil Rekomendasi</h3>', unsafe_allow_html=True)
        
        if btn_hitung:
            with st.spinner("Menghitung..."):
                hasil_fuzzy = hitung_produksi_optimal(permintaan_val, persediaan_val)
                st.session_state.total_prediksi_tunggal += 1
                
                st.markdown(
                    f'<div style="background: rgba(16, 185, 129, 0.08); border: 1px solid #10B981; border-radius: 8px; padding: 24px; text-align: center; margin-top: 10px;">'
                    f'<div style="color: #94A3B8; font-size: 0.85rem; text-transform: uppercase; font-weight: 500;">Jumlah Produksi yang Disarankan</div>'
                    f'<div style="color: #10B981; font-size: 2.8rem; font-weight: 700; margin-top: 8px;">{round(hasil_fuzzy, 2)} <span style="font-size: 1.2rem; color: #F1F5F9;">Unit</span></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown("---")
                st.markdown("### Posisi Parameter pada Kurva Keanggotaan")
                fig_single = plot_single_prediction_visual(
                    permintaan_fuzzy, persediaan_fuzzy, produksi_fuzzy, 
                    permintaan_val, persediaan_val, hasil_fuzzy
                )
                st.pyplot(fig_single)
        else:
            st.info("Tentukan nilai permintaan dan persediaan di sebelah kiri, kemudian klik tombol Hitung.")

# PAGE 3: PREDIKSI MASSAL
elif menu == "Prediksi Massal":
    st.markdown('<h1 style="color: #F8FAFC; font-weight: 700; margin-bottom: 4px;">Prediksi Massal Otomatis</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94A3B8; font-size: 1rem; margin-bottom: 24px;">Pemrosesan batch data sekaligus melalui file CSV atau Excel.</p>', unsafe_allow_html=True)
    
    col_upload, col_actions = st.columns([2, 1.2])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Unggah File Dataset (.csv / .xlsx)", 
            type=["csv", "xlsx"]
        )
        
    with col_actions:
        st.markdown('<div style="font-weight: 600; color: #F8FAFC; margin-bottom: 8px;">Simulasi Cepat</div>', unsafe_allow_html=True)
        st.write("Klik di bawah untuk memuat dataset contoh berisikan riwayat data produksi:")
        btn_load_sample = st.button("Muat Contoh Dataset", use_container_width=True)

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
        st.toast("Dataset contoh berhasil dimuat!")

    # Pemrosesan Data
    if df_raw is not None:
        is_valid, pesan, df_clean = validasi_dataframe(df_raw)
        
        if not is_valid:
            st.error(pesan)
        else:
            st.success(pesan)
            
            # Hitung prediksi massal fuzzy
            pred_results = []
            for idx, row in df_clean.iterrows():
                fuzzy_val = hitung_produksi_optimal(row['permintaan'], row['persediaan'])
                pred_results.append(round(fuzzy_val, 2))
                
            df_clean['produksi_fuzzy'] = pred_results
            
            # Hitung error jika ada kolom aktual
            if 'produksi_aktual' in df_clean.columns:
                df_clean['error'] = np.abs(df_clean['produksi_aktual'] - df_clean['produksi_fuzzy'])
                df_clean['error'] = df_clean['error'].round(2)
                
                y_act_no_zero = np.where(df_clean['produksi_aktual'] == 0, 1e-5, df_clean['produksi_aktual'])
                df_clean['persentase_error'] = (df_clean['error'] / y_act_no_zero) * 100
                df_clean['persentase_error'] = df_clean['persentase_error'].round(2)
                
            st.session_state.df_prediksi_massal = df_clean
            
            st.markdown('<h3 style="color: #F8FAFC; font-weight: 600; margin-top: 24px; margin-bottom: 12px;">Tabel Hasil Kalkulasi</h3>', unsafe_allow_html=True)
            st.dataframe(
                df_clean,
                use_container_width=True,
                column_config={
                    "permintaan": st.column_config.NumberColumn("Permintaan (Unit)", format="%d"),
                    "persediaan": st.column_config.NumberColumn("Persediaan (Unit)", format="%d"),
                    "produksi_aktual": st.column_config.NumberColumn("Produksi Aktual", format="%.1f"),
                    "produksi_fuzzy": st.column_config.NumberColumn("Produksi Fuzzy", format="%.2f"),
                    "error": st.column_config.NumberColumn("Error", format="%.2f"),
                    "persentase_error": st.column_config.NumberColumn("Persentase Error (%)", format="%.2f %%")
                }
            )
            
            # Ekspor File
            st.markdown('<h3 style="color: #F8FAFC; font-weight: 600; margin-top: 24px; margin-bottom: 12px;">Ekspor Laporan</h3>', unsafe_allow_html=True)
            col_d1, col_d2 = st.columns(2)
            
            # In-memory CSV
            csv_bytes = df_clean.to_csv(index=False).encode('utf-8')
            col_d1.download_button(
                label="Unduh Format CSV",
                data=csv_bytes,
                file_name=f"hasil_fuzzy_prediksi.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # In-memory Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_clean.to_excel(writer, index=False, sheet_name="Fuzzy Mamdani")
            excel_bytes = excel_buffer.getvalue()
            
            col_d2.download_button(
                label="Unduh Format Excel (XLSX)",
                data=excel_bytes,
                file_name=f"hasil_fuzzy_prediksi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# PAGE 4: EVALUASI MODEL
elif menu == "Evaluasi Model":
    st.markdown('<h1 style="color: #F8FAFC; font-weight: 700; margin-bottom: 4px;">Dashboard Analisis Akurasi</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94A3B8; font-size: 1rem; margin-bottom: 24px;">Statistik performa keakuratan keputusan model fuzzy Mamdani.</p>', unsafe_allow_html=True)
    
    df_eval = st.session_state.df_prediksi_massal
    
    if df_eval is None:
        st.warning("Belum ada data massal yang aktif. Silakan muat dataset terlebih dahulu di menu Prediksi Massal.")
    elif 'produksi_aktual' not in df_eval.columns:
        st.error("Kolom 'produksi_aktual' tidak ditemukan pada dataset aktif untuk menghitung statistik evaluasi.")
    else:
        metrik = hitung_metrik_evaluasi(df_eval)
        
        if metrik is None:
            st.error("Gagal melakukan perhitungan metrik evaluasi.")
        else:
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            
            col_met1.metric("Mean Absolute Error (MAE)", f"{round(metrik['mae'], 2)} Unit")
            col_met2.metric("Root Mean Squared Error (RMSE)", f"{round(metrik['rmse'], 2)} Unit")
            col_met3.metric("Mean Absolute Percentage Error (MAPE)", f"{round(metrik['mape'], 2)}%")
            col_met4.metric("Tingkat Akurasi Model", f"{round(metrik['akurasi'], 2)}%")
            
            st.markdown("---")
            col_chart1, col_chart2 = st.columns([1.2, 1])
            
            with col_chart1:
                st.markdown("### Kurva Kepadatan Distribusi Kesalahan (Error)")
                fig_err = plot_error_distribution(df_eval)
                st.pyplot(fig_err)
                
            with col_chart2:
                st.markdown("### Pembagian Kategori Akurasi")
                analisis_kategori = buat_analisis_error(df_eval)
                
                if analisis_kategori:
                    for kategori, jumlah in analisis_kategori.items():
                        persen = (jumlah / metrik['jumlah_data']) * 100
                        st.markdown(
                            f'<div class="metric-container">'
                            f'<div>'
                            f'<div class="metric-title">{kategori}</div>'
                            f'<div style="font-size: 0.8rem; color: #64748B; margin-top: 4px;">{jumlah} baris data</div>'
                            f'</div>'
                            f'<div class="metric-value">{round(persen, 1)}%</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

# PAGE 5: KURVA KEANGGOTAAN
elif menu == "Kurva Keanggotaan":
    st.markdown('<h1 style="color: #F8FAFC; font-weight: 700; margin-bottom: 4px;">Visualisasi Kurva Keanggotaan</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94A3B8; font-size: 1rem; margin-bottom: 24px;">Visualisasi parameter logika fuzzy untuk variabel masukan dan luaran.</p>', unsafe_allow_html=True)
    
    st.markdown("### Kurva Fungsi Keanggotaan Fuzzy")
    fig_mf = plot_membership_functions(permintaan_fuzzy, persediaan_fuzzy, produksi_fuzzy)
    st.pyplot(fig_mf)
    
    df_eval = st.session_state.df_prediksi_massal
    if df_eval is not None and 'produksi_aktual' in df_eval.columns:
        st.markdown("---")
        st.markdown("### Perbandingan Grafik: Tren Aktual vs Prediksi")
        fig_trend = plot_actual_vs_predicted(df_eval)
        st.pyplot(fig_trend)

# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------
st.markdown(
    '<div class="custom-footer">'
    '<p>Sistem Pendukung Keputusan Produksi (Fuzzy Mamdani) - Analisis Dashboard</p>'
    '</div>',
    unsafe_allow_html=True
)
