import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import streamlit as st

@st.cache_resource
def get_fuzzy_variables():
    """
    Membangun variabel fuzzy (Antecedent dan Consequent) beserta fungsinya.
    Menggunakan st.cache_resource agar tidak perlu dibuat berulang-ulang.
    """
    # Semesta Pembicaraan (Universe)
    permintaan = ctrl.Antecedent(np.arange(760, 7976, 1), 'permintaan')
    persediaan = ctrl.Antecedent(np.arange(135, 566, 1), 'persediaan')
    produksi = ctrl.Consequent(np.arange(1100, 9041, 1), 'produksi')

    # Membership Functions - Permintaan
    permintaan['sedikit'] = fuzz.trimf(permintaan.universe, [760, 760, 3988])
    permintaan['sedang'] = fuzz.trimf(permintaan.universe, [760, 3988, 7975])
    permintaan['banyak'] = fuzz.trimf(permintaan.universe, [3988, 7975, 7975])

    # Membership Functions - Persediaan
    persediaan['sedikit'] = fuzz.trimf(persediaan.universe, [135, 135, 283])
    persediaan['sedang'] = fuzz.trimf(persediaan.universe, [135, 283, 565])
    persediaan['banyak'] = fuzz.trimf(persediaan.universe, [283, 565, 565])

    # Membership Functions - Produksi
    produksi['sedikit'] = fuzz.trimf(produksi.universe, [1100, 1100, 4520])
    produksi['sedang'] = fuzz.trimf(produksi.universe, [1100, 4520, 9040])
    produksi['banyak'] = fuzz.trimf(produksi.universe, [4520, 9040, 9040])

    return permintaan, persediaan, produksi

@st.cache_resource
def get_fuzzy_control_system():
    """
    Membangun Control System Fuzzy berdasarkan Rule Base yang ditentukan (9 Rules).
    """
    permintaan, persediaan, produksi = get_fuzzy_variables()

    # Rule Base (9 Rules Mamdani)
    rule1 = ctrl.Rule(permintaan['sedikit'] & persediaan['sedikit'], produksi['sedikit'])
    rule2 = ctrl.Rule(permintaan['sedikit'] & persediaan['sedang'], produksi['sedikit'])
    rule3 = ctrl.Rule(permintaan['sedikit'] & persediaan['banyak'], produksi['sedikit'])
    
    rule4 = ctrl.Rule(permintaan['sedang'] & persediaan['sedikit'], produksi['banyak'])
    rule5 = ctrl.Rule(permintaan['sedang'] & persediaan['sedang'], produksi['sedang'])
    rule6 = ctrl.Rule(permintaan['sedang'] & persediaan['banyak'], produksi['sedikit'])
    
    rule7 = ctrl.Rule(permintaan['banyak'] & persediaan['sedikit'], produksi['banyak'])
    rule8 = ctrl.Rule(permintaan['banyak'] & persediaan['sedang'], produksi['banyak'])
    rule9 = ctrl.Rule(permintaan['banyak'] & persediaan['banyak'], produksi['banyak'])

    sistem_ctrl = ctrl.ControlSystem([
        rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9
    ])
    
    return sistem_ctrl

def hitung_produksi_optimal(permintaan_val, persediaan_val):
    """
    Menghitung defuzzifikasi centroid untuk satu set input permintaan dan persediaan.
    """
    sistem_ctrl = get_fuzzy_control_system()
    simulasi = ctrl.ControlSystemSimulation(sistem_ctrl)
    
    # Clip input ke batas minimum dan maksimum untuk menghindari error di luar batas semesta
    permintaan_val = np.clip(permintaan_val, 760, 7975)
    persediaan_val = np.clip(persediaan_val, 135, 565)
    
    simulasi.input['permintaan'] = permintaan_val
    simulasi.input['persediaan'] = persediaan_val
    simulasi.compute()
    
    return simulasi.output['produksi']
