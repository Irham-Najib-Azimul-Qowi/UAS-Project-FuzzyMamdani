import numpy as np
import pandas as pd

def hitung_metrik_evaluasi(df):
    """
    Menghitung metrik-metrik regresi/evaluasi seperti MAE, MSE, RMSE, MAPE, R2, 
    dan Akurasi jika kolom 'produksi_aktual' tersedia dalam dataframe.
    """
    if 'produksi_aktual' not in df.columns or df['produksi_aktual'].isnull().all():
        return None

    # Bersihkan data dari nilai null
    df_clean = df.dropna(subset=['produksi_aktual', 'produksi_fuzzy']).copy()
    
    y_actual = df_clean['produksi_aktual'].to_numpy()
    y_pred = df_clean['produksi_fuzzy'].to_numpy()

    if len(y_actual) == 0:
        return None

    # Selisih absolut dan kuadrat
    abs_errors = np.abs(y_actual - y_pred)
    squared_errors = (y_actual - y_pred) ** 2
    
    # Proteksi terhadap pembagian nol
    y_actual_non_zero = np.where(y_actual == 0, 1e-5, y_actual)
    pct_errors = (abs_errors / y_actual_non_zero) * 100

    # Kalkulasi statistik rata-rata
    mae = np.mean(abs_errors)
    mse = np.mean(squared_errors)
    rmse = np.sqrt(mse)
    mape = np.mean(pct_errors)
    
    # R2 Score (Koefisien Determinasi)
    ss_res = np.sum((y_actual - y_pred) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

    # Definisikan Akurasi Fuzzy berbasis (100 - MAPE)%
    akurasi = max(0.0, 100.0 - mape)

    return {
        'mae': mae,
        'mse': mse,
        'rmse': rmse,
        'mape': mape,
        'r2': r2,
        'akurasi': akurasi,
        'jumlah_data': len(df_clean)
    }

def buat_analisis_error(df):
    """
    Mengklasifikasikan tingkat persentase kesalahan per baris untuk ringkasan sebaran akurasi.
    """
    if 'produksi_aktual' not in df.columns or df['produksi_aktual'].isnull().all():
        return None
        
    df_clean = df.dropna(subset=['produksi_aktual', 'produksi_fuzzy']).copy()
    
    # Fungsi pengelompokan
    def klasifikasi(pct):
        if pct <= 5:
            return 'Sangat Akurat (< 5%)'
        elif pct <= 15:
            return 'Akurat / Layak (5% - 15%)'
        elif pct <= 25:
            return 'Cukup Akurat (15% - 25%)'
        else:
            return 'Kurang Akurat (> 25%)'
            
    y_act = np.where(df_clean['produksi_aktual'] == 0, 1e-5, df_clean['produksi_aktual'])
    df_clean['persentase_error'] = (np.abs(df_clean['produksi_aktual'] - df_clean['produksi_fuzzy']) / y_act) * 100
    df_clean['kategori_akurasi'] = df_clean['persentase_error'].apply(klasifikasi)
    
    # Hitung jumlah item tiap kategori
    distribusi = df_clean['kategori_akurasi'].value_counts().to_dict()
    
    # Pastikan semua kategori selalu ada di dictionary agar chart atau visualisasi konsisten
    kategori_wajib = [
        'Sangat Akurat (< 5%)', 
        'Akurat / Layak (5% - 15%)', 
        'Cukup Akurat (15% - 25%)', 
        'Kurang Akurat (> 25%)'
    ]
    
    for kat in kategori_wajib:
        if kat not in distribusi:
            distribusi[kat] = 0
            
    return distribusi
