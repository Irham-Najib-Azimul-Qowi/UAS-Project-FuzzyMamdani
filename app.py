import streamlit as st
import pandas as pd
import numpy as np
import io
import os

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

# Konfigurasi Halaman Utama (Simple & Clean)
st.set_page_config(
    page_title="Sistem Pendukung Keputusan Produksi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Buat dataset contoh secara otomatis jika belum ada
buat_dataset_contoh()

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
# NAVIGASI SIDEBAR
# ----------------------------------------------------
st.sidebar.title("Navigasi")
menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "Ringkasan Sistem",
        "Prediksi Tunggal",
        "Prediksi Massal",
        "Evaluasi Model",
        "Kurva Keanggotaan"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Unduh Template")

with open('dataset/contoh_dataset.csv', 'rb') as f:
    st.sidebar.download_button(
        label="Download Template CSV",
        data=f,
        file_name="contoh_dataset.csv",
        mime="text/csv",
        use_container_width=True
    )
    
with open('dataset/contoh_dataset.xlsx', 'rb') as f:
    st.sidebar.download_button(
        label="Download Template Excel",
        data=f,
        file_name="contoh_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.sidebar.markdown("---")
st.sidebar.caption(
    "Batas Nilai Universe:\n"
    "- Permintaan: 760 s.d 7975\n"
    "- Persediaan: 135 s.d 565\n"
    "- Produksi: 1100 s.d 9040"
)

# ----------------------------------------------------
# KONTEN UTAMA
# ----------------------------------------------------

# Halaman 1: Ringkasan Sistem
if menu == "Ringkasan Sistem":
    st.title("Sistem Pendukung Keputusan Produksi")
    st.write("Penentuan jumlah produksi optimal menggunakan logika fuzzy metode Mamdani.")
    
    # Deskripsi Utama (Menggunakan Container Border Bawaan Streamlit)
    with st.container(border=True):
        st.write(
            "Aplikasi ini dirancang untuk mempermudah perhitungan jumlah produksi barang secara presisi "
            "berdasarkan parameter masukan tingkat Permintaan Pasar dan kapasitas Sisa Persediaan Gudang. "
            "Dengan menerapkan 9 aturan logika fuzzy Mamdani dan defuzzifikasi Centroid, sistem memberikan rekomendasi "
            "produksi barang yang optimal guna meminimalkan risiko kelebihan maupun kekurangan stok barang."
        )
    
    # Ringkasan Statistik
    st.markdown("### Statistik Aktivitas Sesi")
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
    
    # Alur Kerja Fuzzy (Menggunakan st.container border=True agar ukuran konsisten penuh)
    st.markdown("### Tahapan Proses Inferensi Fuzzy")
    flow_col1, flow_col2, flow_col3, flow_col4 = st.columns(4)
    
    with flow_col1:
        with st.container(border=True):
            st.markdown("**1. Fuzzifikasi**")
            st.write("Mengubah nilai riil permintaan dan persediaan menjadi nilai linguistik fuzzy.")
            
    with flow_col2:
        with st.container(border=True):
            st.markdown("**2. Inferensi Fuzzy**")
            st.write("Menerapkan operator logika AND pada 9 aturan implikasi fuzzy.")
            
    with flow_col3:
        with st.container(border=True):
            st.markdown("**3. Komposisi Aturan**")
            st.write("Menggabungkan seluruh output aturan menggunakan metode MAX.")
            
    with flow_col4:
        with st.container(border=True):
            st.markdown("**4. Defuzzifikasi**")
            st.write("Menghitung nilai pusat gravitasi (Centroid) untuk hasil produksi.")

# Halaman 2: Prediksi Tunggal
elif menu == "Prediksi Tunggal":
    st.title("Prediksi Produksi Tunggal")
    st.write("Tentukan nilai masukan untuk menghitung jumlah produksi optimal.")
    
    col_input, col_output = st.columns([1, 1.2])
    
    with col_input:
        st.subheader("Parameter Input")
        
        permintaan_val = st.number_input(
            "Jumlah Permintaan (Unit)",
            min_value=760,
            max_value=7975,
            value=1420,
            step=10
        )
        
        persediaan_val = st.number_input(
            "Jumlah Persediaan (Unit)",
            min_value=135,
            max_value=565,
            value=385,
            step=5
        )
        
        btn_hitung = st.button("Hitung Produksi Optimal", use_container_width=True)
        
    with col_output:
        st.subheader("Hasil Perhitungan")
        
        if btn_hitung:
            with st.spinner("Menghitung..."):
                hasil_fuzzy = hitung_produksi_optimal(permintaan_val, persediaan_val)
                st.session_state.total_prediksi_tunggal += 1
                
                with st.container(border=True):
                    st.markdown("**Rekomendasi Produksi Optimal:**")
                    st.header(f"{round(hasil_fuzzy, 2)} Unit")
                    st.caption("Defuzzifikasi Centroid diselesaikan secara presisi.")
                
                st.markdown("---")
                st.markdown("### Posisi Parameter pada Kurva Keanggotaan")
                fig_single = plot_single_prediction_visual(
                    permintaan_fuzzy, persediaan_fuzzy, produksi_fuzzy, 
                    permintaan_val, persediaan_val, hasil_fuzzy
                )
                st.pyplot(fig_single)
        else:
            st.info("Masukkan parameter input di sebelah kiri, lalu klik tombol Hitung.")

# Halaman 3: Prediksi Massal
elif menu == "Prediksi Massal":
    st.title("Prediksi Massal Otomatis")
    st.write("Unggah dataset operasional untuk memproses banyak data sekaligus secara batch.")
    
    col_upload, col_actions = st.columns([2, 1.2])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Unggah File Dataset (.csv / .xlsx)", 
            type=["csv", "xlsx"]
        )
        
    with col_actions:
        st.markdown("**Simulasi Instan**")
        st.write("Gunakan contoh dataset bawaan untuk simulasi cepat:")
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
            st.error(f"Gagal membaca file: {e}")
            
    elif btn_load_sample:
        st.session_state.file_name_aktif = "contoh_dataset.xlsx"
        df_raw = pd.read_excel('dataset/contoh_dataset.xlsx')
        st.toast("Dataset contoh berhasil dimuat!")

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
            
            st.markdown("### Tabel Hasil Perhitungan")
            st.dataframe(
                df_clean,
                use_container_width=True,
                column_config={
                    "permintaan": st.column_config.NumberColumn("Permintaan", format="%d"),
                    "persediaan": st.column_config.NumberColumn("Persediaan", format="%d"),
                    "produksi_aktual": st.column_config.NumberColumn("Produksi Aktual", format="%.1f"),
                    "produksi_fuzzy": st.column_config.NumberColumn("Produksi Fuzzy", format="%.2f"),
                    "error": st.column_config.NumberColumn("Error", format="%.2f"),
                    "persentase_error": st.column_config.NumberColumn("Persentase Error (%)", format="%.2f %%")
                }
            )
            
            st.markdown("### Ekspor Laporan")
            col_d1, col_d2 = st.columns(2)
            
            # In-memory CSV
            csv_bytes = df_clean.to_csv(index=False).encode('utf-8')
            col_d1.download_button(
                label="Unduh Format CSV",
                data=csv_bytes,
                file_name="hasil_fuzzy_prediksi.csv",
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
                file_name="hasil_fuzzy_prediksi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# Halaman 4: Evaluasi Model
elif menu == "Evaluasi Model":
    st.title("Evaluasi Statistik Keakuratan Model")
    st.write("Analisis performa prediksi model logika fuzzy Mamdani dibandingkan dengan data produksi riil.")
    
    df_eval = st.session_state.df_prediksi_massal
    
    if df_eval is None:
        st.warning("Belum ada data massal yang aktif. Silakan muat dataset terlebih dahulu di menu Prediksi Massal.")
    elif 'produksi_aktual' not in df_eval.columns:
        st.error("Kolom 'produksi_aktual' tidak ditemukan pada dataset aktif untuk menghitung statistik evaluasi.")
    else:
        metrik = hitung_metrik_evaluasi(df_eval)
        
        if metrik is None:
            st.error("Gagal memproses metrik evaluasi.")
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
                    # Menampilkan dalam bentuk list visual yang rapi dan simple
                    for kategori, jumlah in analisis_kategori.items():
                        persen = (jumlah / metrik['jumlah_data']) * 100
                        with st.container(border=True):
                            col_l, col_r = st.columns([3, 1])
                            col_l.markdown(f"**{kategori}**")
                            col_l.caption(f"{jumlah} baris data")
                            col_r.subheader(f"{round(persen, 1)}%")

# Halaman 5: Kurva Keanggotaan
elif menu == "Kurva Keanggotaan":
    st.title("Visualisasi Kurva Keanggotaan")
    st.write("Kurva fungsi keanggotaan untuk variabel masukan dan luaran logika fuzzy.")
    
    st.markdown("### Kurva Fungsi Keanggotaan Fuzzy")
    fig_mf = plot_membership_functions(permintaan_fuzzy, persediaan_fuzzy, produksi_fuzzy)
    st.pyplot(fig_mf)
    
    df_eval = st.session_state.df_prediksi_massal
    if df_eval is not None and 'produksi_aktual' in df_eval.columns:
        st.markdown("---")
        st.markdown("### Perbandingan Grafik: Tren Aktual vs Prediksi")
        fig_trend = plot_actual_vs_predicted(df_eval)
        st.pyplot(fig_trend)

# Footer Sederhana & Bersih
st.markdown("---")
st.caption("Sistem Pendukung Keputusan Produksi (Fuzzy Mamdani)")
