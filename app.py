import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN DASHBOARD
# ---------------------------------------------------------
st.set_page_config(
    page_title="Simulator Parametrik Odong-Odong UPI",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Simulator Parametrik Rute & Penjadwalan Odong-Odong UPI")
st.caption("Ditha Okstevia - Eisha Karima Fidareini - Nailah Amani Nuryaman - Nesa Dwi Rizqi Marsha Reneta - Wafa Nidaul Hasanah - Kelompok 6 - Proyek MSTR UPI")
st.markdown("---")

# ---------------------------------------------------------
# 2. SIDEBAR: PANEL KONTROL PARAMETER (FLEKSIBEL)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Panel Parameter Simulator")

# Pilihan Sesi Jam Operasional
sesi = st.sidebar.selectbox("Pilih Sesi Jam Operasional:", ["Pagi (06.30 - 08.00 WIB)", "Sore (16.00 - 16.30 WIB)"])

# Slider Kecepatan Armada (km/jam)
kecepatan_kmjam = st.sidebar.slider("Kecepatan Rata-Rata Odong-Odong (km/jam):", min_value=5, max_value=25, value=15, step=1)

# Input Waktu Henti / Dwell Time di Halte Tetap (Menit)
dwell_time = st.sidebar.number_input("Waktu Henti di Halte / Dwell Time (Menit):", min_value=1, max_value=5, value=2, step=1)

st.sidebar.info("💡 **Catatan**: Mengubah angka pada panel akan langsung menghitung ulang tabel jadwal dan estimasi waktu di bawah secara otomatis.")

# ---------------------------------------------------------
# 3. TABEL MATRIKS JARAK DINAMIS (BISA DIEDIT DI BROWSER)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap Fakultas (Dapat Diisi / Diedit)")
st.write("Masukkan perkiraan jarak antar-halte (dalam Meter) pada tabel di bawah ini:")

# Baseline data jarak antar-halte tetap
data_jarak = {
    "Rute Antar-Halte Tetap": [
        "FPTI ➔ FIP/FPSD", 
        "FIP/FPSD ➔ FPEB/Rektorat", 
        "FPEB/Rektorat ➔ FPMIPA", 
        "FPMIPA ➔ FPTK", 
        "FPTK ➔ FPOK/Gymnasium",
        "FPOK/Gymnasium ➔ FPTI"
    ],
    "Estimasi Jarak (Meter)": [450, 400, 500, 350, 450, 600]
}

df_jarak = pd.DataFrame(data_jarak)

# Editor tabel interaktif
df_edited = st.data_editor(
    df_jarak,
    num_rows="fixed",
    use_container_width=True,
    key="editor_jarak"
)

# ---------------------------------------------------------
# 4. MESIN KALKULASI KEBUTUHAN WAKTU & JADWAL OTOMATIS
# ---------------------------------------------------------
# Konversi kecepatan km/jam ke meter/menit
kecepatan_m_per_menit = (kecepatan_kmjam * 1000) / 60

# Kalkulasi waktu tempuh per leg
df_edited["Waktu Jalan (Menit)"] = df_edited["Estimasi Jarak (Meter)"] / kecepatan_m_per_menit
df_edited["Total Waktu Leg (Menit)"] = (df_edited["Waktu Jalan (Menit)"] + dwell_time).round(1)

st.markdown("### ⏱️ Hasil Kalkulasi Waktu Tempuh Otomatis")
st.dataframe(df_edited, use_container_width=True)

total_siklus_menit = df_edited["Total Waktu Leg (Menit)"].sum()
st.success(f"**Total Waktu 1 Siklus Putar Lengkap**: ± **{total_siklus_menit:.1f} Menit** (pada kecepatan {kecepatan_kmjam} km/jam & dwell time {dwell_time} menit)")

# ---------------------------------------------------------
# 5. TABEL JADWAL KEBERANGKATAN 3 ARMADA (DINAMIS SESUAI SESI)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("2️⃣ Draf Jadwal Keberangkatan Terstruktur (3 Titik Keberangkatan Berbeda)")

# Penyesuaian jam otomatis berdasarkan pilihan Sesi (Pagi / Sore)
if "Pagi" in sesi:
    jam_list = ["06.30 WIB", "06.45 WIB", "07.00 WIB", "07.15 WIB", "07.30 WIB", "07.45 WIB"]
else:
    jam_list = ["16.00 WIB", "16.15 WIB", "16.30 WIB", "16.45 WIB", "17.00 WIB", "17.15 WIB"]

# Jadwal simulative 3 armada dari 3 titik awal yang berbeda
jadwal_data = {
    "Jam Keberangkatan": jam_list,
    "Odong-Odong 1 (Start: FPTI)": ["FPTI (Gerbang Bawah)", "FIP / FPSD", "FPEB / Rektorat", "FPMIPA (Kampus Atas)", "FPTK", "FPOK / Gymnasium"],
    "Odong-Odong 2 (Start: FPMIPA)": ["FPMIPA (Kampus Atas)", "FPTK", "FPOK / Gymnasium", "FPTI (Gerbang Bawah)", "FIP / FPSD", "FPEB / Rektorat"],
    "Odong-Odong 3 (Start: FPEB)": ["FPEB / Rektorat", "FPMIPA (Kampus Atas)", "FPTK", "FPOK / Gymnasium", "FPTI (Gerbang Bawah)", "FIP / FPSD"]
}

df_jadwal = pd.DataFrame(jadwal_data)
st.table(df_jadwal)

# ---------------------------------------------------------
# 6. VISUALISASI PETA INTERAKTIF HALTE UPI (FOLIUM)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta Halte Tetap & Rute Kampus UPI")

# Koordinat pusat UPI Silihwangi
koordinat_upi = [-6.8604, 107.5900]
m = folium.Map(location=koordinat_upi, zoom_start=16)

# Daftar Halte Tetap
halte_list = [
    {"nama": "Halte 1: FPTI / Gerbang Bawah (Depot Armada 1)", "pos": [-6.8632, 107.5905], "color": "blue"},
    {"nama": "Halte 2: FIP & FPSD", "pos": [-6.8615, 107.5900], "color": "green"},
    {"nama": "Halte 3: FPEB & Rektorat (Depot Armada 3)", "pos": [-6.8600, 107.5892], "color": "orange"},
    {"nama": "Halte 4: FPMIPA / Kampus Atas (Depot Armada 2)", "pos": [-6.8580, 107.5895], "color": "red"},
    {"nama": "Halte 5: FPTK", "pos": [-6.8585, 107.5910], "color": "purple"},
    {"nama": "Halte 6: FPOK & Gymnasium", "pos": [-6.8610, 107.5918], "color": "cadetblue"}
]

# Tambahkan Marker Halte ke Peta
coords = []
for h in halte_list:
    coords.append(h["pos"])
    folium.Marker(
        location=h["pos"],
        popup=h["nama"],
        tooltip=h["nama"],
        icon=folium.Icon(color=h["color"], icon="bus", prefix="fa")
    ).add_to(m)

# Gambar garis rute jalur terhubung
coords.append(coords[0]) # Tutup siklus
folium.PolyLine(coords, color="darkblue", weight=3, opacity=0.8, tooltip="Jalur Rute Odong-Odong UPI").add_to(m)

# Tampilkan Peta di Streamlit
st_folium(m, width=1100, height=500)
folium.PolyLine(coords, color="darkblue", weight=3, opacity=0.8, tooltip="Jalur Rute Odong-Odong UPI").add_to(m)

# Tampilkan Peta di Streamlit
st_folium(m, width=1100, height=500)
