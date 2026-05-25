import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def set_plot_style():
    """
    Mengatur gaya visualisasi agar tampak profesional, modern, dan serasi dengan tema dashboard gelap.
    """
    plt.style.use('dark_background')
    plt.rcParams['figure.facecolor'] = '#0E1117'
    plt.rcParams['axes.facecolor'] = '#161B22'
    plt.rcParams['axes.edgecolor'] = '#30363D'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.color'] = '#30363D'
    plt.rcParams['grid.alpha'] = 0.5
    plt.rcParams['font.size'] = 9
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['axes.titlesize'] = 11
    plt.rcParams['legend.fontsize'] = 9
    plt.rcParams['xtick.color'] = '#8B949E'
    plt.rcParams['ytick.color'] = '#8B949E'

def plot_membership_functions(permintaan, persediaan, produksi):
    """
    Membuat grafik 3-panel horizontal untuk menampilkan fungsi keanggotaan fuzzy variabel input dan output.
    """
    set_plot_style()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # Variabel input: Permintaan
    axes[0].plot(permintaan.universe, permintaan['sedikit'].mf, '#38BDF8', linewidth=2, label='Sedikit')
    axes[0].plot(permintaan.universe, permintaan['sedang'].mf, '#F43F5E', linewidth=2, label='Sedang')
    axes[0].plot(permintaan.universe, permintaan['banyak'].mf, '#F59E0B', linewidth=2, label='Banyak')
    axes[0].set_title('Fungsi Keanggotaan: Permintaan')
    axes[0].set_xlabel('Jumlah Permintaan (Unit)')
    axes[0].set_ylabel('Derajat Keanggotaan (\u03bc)')
    axes[0].legend(frameon=True, facecolor='#161B22', edgecolor='#30363D')

    # Variabel input: Persediaan
    axes[1].plot(persediaan.universe, persediaan['sedikit'].mf, '#38BDF8', linewidth=2, label='Sedikit')
    axes[1].plot(persediaan.universe, persediaan['sedang'].mf, '#F43F5E', linewidth=2, label='Sedang')
    axes[1].plot(persediaan.universe, persediaan['banyak'].mf, '#F59E0B', linewidth=2, label='Banyak')
    axes[1].set_title('Fungsi Keanggotaan: Persediaan')
    axes[1].set_xlabel('Jumlah Persediaan (Unit)')
    axes[1].set_ylabel('Derajat Keanggotaan (\u03bc)')
    axes[1].legend(frameon=True, facecolor='#161B22', edgecolor='#30363D')

    # Variabel output: Produksi
    axes[2].plot(produksi.universe, produksi['sedikit'].mf, '#38BDF8', linewidth=2, label='Sedikit')
    axes[2].plot(produksi.universe, produksi['sedang'].mf, '#F43F5E', linewidth=2, label='Sedang')
    axes[2].plot(produksi.universe, produksi['banyak'].mf, '#F59E0B', linewidth=2, label='Banyak')
    axes[2].set_title('Fungsi Keanggotaan: Produksi')
    axes[2].set_xlabel('Jumlah Produksi (Unit)')
    axes[2].set_ylabel('Derajat Keanggotaan (\u03bc)')
    axes[2].legend(frameon=True, facecolor='#161B22', edgecolor='#30363D')

    plt.tight_layout()
    return fig

def plot_single_prediction_visual(permintaan, persediaan, produksi, permintaan_val, persediaan_val, output_val):
    """
    Visualisasi posisi input user dan output hasil pada fungsi keanggotaan masing-masing variabel.
    """
    set_plot_style()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # Permintaan dengan garis posisi
    axes[0].plot(permintaan.universe, permintaan['sedikit'].mf, '#38BDF8', alpha=0.4, label='Sedikit')
    axes[0].plot(permintaan.universe, permintaan['sedang'].mf, '#F43F5E', alpha=0.4, label='Sedang')
    axes[0].plot(permintaan.universe, permintaan['banyak'].mf, '#F59E0B', alpha=0.4, label='Banyak')
    axes[0].axvline(x=permintaan_val, color='#FFFFFF', linestyle='--', linewidth=2, label=f'Input: {permintaan_val}')
    axes[0].set_title('Posisi Input Permintaan')
    axes[0].set_xlabel('Permintaan')
    axes[0].set_ylabel('Derajat Keanggotaan')
    axes[0].legend(frameon=True, facecolor='#161B22', edgecolor='#30363D')

    # Persediaan dengan garis posisi
    axes[1].plot(persediaan.universe, persediaan['sedikit'].mf, '#38BDF8', alpha=0.4, label='Sedikit')
    axes[1].plot(persediaan.universe, persediaan['sedang'].mf, '#F43F5E', alpha=0.4, label='Sedang')
    axes[1].plot(persediaan.universe, persediaan['banyak'].mf, '#F59E0B', alpha=0.4, label='Banyak')
    axes[1].axvline(x=persediaan_val, color='#FFFFFF', linestyle='--', linewidth=2, label=f'Input: {persediaan_val}')
    axes[1].set_title('Posisi Input Persediaan')
    axes[1].set_xlabel('Persediaan')
    axes[1].set_ylabel('Derajat Keanggotaan')
    axes[1].legend(frameon=True, facecolor='#161B22', edgecolor='#30363D')

    # Produksi dengan garis defuzzifikasi
    axes[2].plot(produksi.universe, produksi['sedikit'].mf, '#38BDF8', alpha=0.4, label='Sedikit')
    axes[2].plot(produksi.universe, produksi['sedang'].mf, '#F43F5E', alpha=0.4, label='Sedang')
    axes[2].plot(produksi.universe, produksi['banyak'].mf, '#F59E0B', alpha=0.4, label='Banyak')
    axes[2].axvline(x=output_val, color='#10B981', linestyle='-', linewidth=2.5, label=f'Fuzzy Hasil: {round(output_val, 1)}')
    axes[2].set_title('Hasil Defuzzifikasi Produksi')
    axes[2].set_xlabel('Produksi')
    axes[2].set_ylabel('Derajat Keanggotaan')
    axes[2].legend(frameon=True, facecolor='#161B22', edgecolor='#30363D')

    plt.tight_layout()
    return fig

def plot_actual_vs_predicted(df):
    """
    Membuat grafik garis perbandingan antara Produksi Aktual vs Produksi Hasil Fuzzy.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    
    indices = np.arange(len(df))
    ax.plot(indices, df['produksi_aktual'], marker='o', color='#38BDF8', label='Produksi Aktual', linewidth=2.5)
    ax.plot(indices, df['produksi_fuzzy'], marker='s', color='#F59E0B', label='Produksi Fuzzy (Prediksi)', linewidth=2.5, linestyle='--')
    
    ax.set_title('Grafik Perbandingan: Produksi Aktual vs Prediksi Fuzzy')
    ax.set_xlabel('Nomor Baris Data')
    ax.set_ylabel('Jumlah Produksi (Unit)')
    
    # Sesuaikan sumbu X agar terlihat bagus jika jumlah datanya tidak terlalu banyak
    if len(df) <= 30:
        ax.set_xticks(indices)
        ax.set_xticklabels(indices + 1)
    
    ax.legend(frameon=True, facecolor='#161B22', edgecolor='#30363D')
    plt.tight_layout()
    return fig

def plot_error_distribution(df):
    """
    Membuat histogram untuk menganalisis penyebaran (distribusi) kesalahan / error prediksi.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=(6, 4.5))
    
    errors = df['error']
    # Histogram frekuensi relatif
    n, bins, patches = ax.hist(errors, bins=10, color='#A855F7', edgecolor='#161B22', alpha=0.7, density=True, label='Error Aktual')
    
    # Line fitting distribusi normal secara statistik
    try:
        from scipy.stats import norm
        mu, std = norm.fit(errors)
        xmin, xmax = ax.get_xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mu, std)
        ax.plot(x, p, '#10B981', linewidth=2, label=f'Kepadatan Normal\n(\u03bc={round(mu,1)}, \u03c3={round(std,1)})')
    except Exception:
        pass
        
    ax.set_title('Distribusi Kesalahan (Error)')
    ax.set_xlabel('Selisih Error (Unit)')
    ax.set_ylabel('Densitas Frekuensi')
    ax.legend(frameon=True, facecolor='#161B22', edgecolor='#30363D')
    
    plt.tight_layout()
    return fig
