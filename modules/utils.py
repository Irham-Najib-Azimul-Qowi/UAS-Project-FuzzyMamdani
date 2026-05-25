import pandas as pd
import numpy as np
import os
from modules.fuzzy_system import hitung_produksi_optimal

def validasi_dataframe(df):
    """
    Memvalidasi kesesuaian kolom dan tipe data pada dataframe hasil unggahan.
    Mengembalikan tuple (is_valid, pesan_error, df_clean).
    """
    # Bersihkan nama kolom dari spasi dan ubah ke lowercase
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # Cek ketersediaan kolom wajib (permintaan dan persediaan)
    if 'permintaan' not in df.columns or 'persediaan' not in df.columns:
        return False, "Kolom wajib 'permintaan' dan/atau 'persediaan' tidak ditemukan pada berkas.", None
        
    # Salin data untuk dibersihkan
    df_clean = df.copy()
    
    # Pastikan data permintaan dan persediaan bertipe numerik, jika invalid diubah ke NaN
    df_clean['permintaan'] = pd.to_numeric(df_clean['permintaan'], errors='coerce')
    df_clean['persediaan'] = pd.to_numeric(df_clean['persediaan'], errors='coerce')
    
    # Opsional kolom: produksi_aktual
    if 'produksi_aktual' in df_clean.columns:
        df_clean['produksi_aktual'] = pd.to_numeric(df_clean['produksi_aktual'], errors='coerce')
        
    # Drop baris yang memiliki nilai NaN pada kolom wajib (permintaan atau persediaan)
    initial_rows = len(df_clean)
    df_clean = df_clean.dropna(subset=['permintaan', 'persediaan'])
    dropped_rows = initial_rows - len(df_clean)
    
    if len(df_clean) == 0:
        return False, "Seluruh baris data tidak valid (kosong atau bukan berupa angka).", None
        
    pesan_sukses = f"Validasi berhasil. Terbaca {len(df_clean)} baris data valid."
    if dropped_rows > 0:
        pesan_sukses += f" (Mengabaikan {dropped_rows} baris yang tidak lengkap/invalid)."
        
    return True, pesan_sukses, df_clean

def buat_dataset_contoh(target_dir='dataset'):
    """
    Membuat file contoh dataset (CSV & Excel) yang realistis jika belum tersedia.
    Berisi kolom permintaan, persediaan, dan produksi_aktual dengan korelasi alami.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    csv_path = os.path.join(target_dir, 'contoh_dataset.csv')
    xlsx_path = os.path.join(target_dir, 'contoh_dataset.xlsx')
    
    # Cek jika file sudah ada, tidak perlu ditimpa (overwrite)
    if os.path.exists(csv_path) and os.path.exists(xlsx_path):
        return
        
    # Generate data sintetis (20 baris data agar grafik tidak terlalu padat)
    np.random.seed(42)
    jumlah_baris = 20
    
    # Sesuai rentang semesta fuzzy
    permintaan = np.random.randint(900, 7500, size=jumlah_baris)
    persediaan = np.random.randint(150, 550, size=jumlah_baris)
    
    # Hitung produksi_aktual dengan fuzzy logic ditambah noise (derau) wajar +-5%
    produksi_aktual = []
    for perm, pers in zip(permintaan, persediaan):
        fuzzy_pred = hitung_produksi_optimal(perm, pers)
        # Tambahkan noise gaussian kecil agar terlihat alami pada perbandingan grafik
        noise = np.random.normal(0, fuzzy_pred * 0.04)
        prod_val = max(1100, min(9040, fuzzy_pred + noise))
        produksi_aktual.append(round(prod_val, 1))
        
    df = pd.DataFrame({
        'permintaan': permintaan,
        'persediaan': persediaan,
        'produksi_aktual': produksi_aktual
    })
    
    # Simpan ke folder dataset
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)
