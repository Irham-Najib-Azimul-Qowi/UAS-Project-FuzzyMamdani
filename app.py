import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Function Fuzzy
@st.cache_data
def fuzzy_produksi(permintaan_input, persediaan_input):
    # Variabel fuzzy
    permintaan = ctrl.Antecedent(np.arange(760, 7976, 1), 'permintaan')
    persediaan = ctrl.Antecedent(np.arange(135, 566, 1), 'persediaan')
    produksi = ctrl.Consequent(np.arange(1100, 9041, 1), 'produksi')

    # membership function
    permintaan['sedikit'] = fuzz.trimf(permintaan.universe, [760, 760, 3988])
    permintaan['sedang'] = fuzz.trimf(permintaan.universe, [760, 3988, 7975])
    permintaan['banyak'] = fuzz.trimf(permintaan.universe, [3988, 7975, 7975])

    persediaan['sedikit'] = fuzz.trimf(persediaan.universe, [135, 135, 283])
    persediaan['sedang'] = fuzz.trimf(persediaan.universe, [135, 283, 565])
    persediaan['banyak'] = fuzz.trimf(persediaan.universe, [283, 565, 565])

    produksi['sedikit'] = fuzz.trimf(produksi.universe, [1100, 1100, 4520])
    produksi['sedang'] = fuzz.trimf(produksi.universe, [1100, 4520, 9040])
    produksi['banyak'] = fuzz.trimf(produksi.universe, [4520, 9040, 9040])

    # Rule fuzzy
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

    simulasi = ctrl.ControlSystemSimulation(sistem_ctrl)

    simulasi.input['permintaan'] = permintaan_input
    simulasi.input['persediaan'] = persediaan_input
    simulasi.compute()
    
    hasil = simulasi.output['produksi']
    return hasil

# Streamlit UI
st.title("Sistem Fuzzy Mamdani")
st.write("Penentuan Produksi Optimal Menggunakan Logika Fuzzy Mamdani")

# Input user
permintaan_user = st.number_input(
    "Masukan Jumlah Permintaan",
    min_value=760,
    max_value=7975,
    value=1420
)

persediaan_user = st.number_input(
    "Masukan Jumlah Persediaan",
    min_value=135,
    max_value=565,
    value=385
)

# Tombol
if st.button("hitung Produksi"):
    hasil = fuzzy_produksi(permintaan_user, persediaan_user)
    st.success(f"Jumlah Produksi Optimal: {round(hasil, 2)}")
