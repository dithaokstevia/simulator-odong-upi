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
st.caption("Kelompok 6 - Proyek MSTR Kampus UPI Silihwangi 2026 (Presisi Mode Satelit HD & Klik Koordinat)")
st.markdown("---")

# ---------------------------------------------------------
# 2. SIDEBAR: PANEL KONTROL PARAMETER
# ---------------------------------------------------------
st.sidebar.header("⚙️ Panel Parameter Simulator")

sesi = st.sidebar.selectbox("Pilih Sesi Jam Operasional:", ["Pagi (06.30 - 08.00 WIB)", "Sore (16.00 - 16.30 WIB)"])
kecepatan_kmjam = st.sidebar.slider("Kecepatan Rata-Rata Odong-Odong (km/jam):", min_value=5, max_value=25, value=15, step=1)
dwell_time = st.sidebar.number_input("Waktu Henti di Halte / Dwell Time (Menit):", min_value=1, max_value=5, value=2, step=1)
jumlah_armada = 3  # Fixed 3 Armada Aktif

st.sidebar.info("💡 **Petunjuk Peta**: Klik area manapun pada peta di bawah untuk menampilkan titik koordinat latitude & longitude secara langsung!")

# ---------------------------------------------------------
# 3. TABEL MATRIKS JARAK DINAMIS (9 HALTE FAKULTAS)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")
st.write("Masukkan perkiraan jarak antar-halte (dalam Meter) pada tabel di bawah ini sesuai alur rute lingkar kampus:")

leg_list = [
    "Leg 1: Halte 1 (FPTI - Depan Gedung A-D) ➔ Halte 2 (FIP Baru - Jl. Mahaguru)",
    "Leg 2: Halte 2 (FIP Baru - Jl. Mahaguru) ➔ Halte 3 (FPMIPA - Gedung JICA / Jl. Harsojo)",
    "Leg 3: Halte 3 (FPMIPA - Gedung JICA) ➔ Halte 4 (FPOK - Samping Gymnasium / Jl. Harsojo)",
    "Leg 4: Halte 4 (FPOK - Jl. Harsojo) ➔ Halte 5 (FK - Fakultas Kedokteran / Jl. Mahaguru)",
    "Leg 5: Halte 5 (FK - Jl. Mahaguru) ➔ Halte 6 (FPEB - Depan LPPM / Jl. Roeslan Abdulgani)",
    "Leg 6: Halte 6 (FPEB - Jl. Roeslan Abdulgani) ➔ Halte 7 (FPSD - Depan FPSD / Taman)",
    "Leg 7: Halte 7 (FPSD - Taman / Jl. Roeslan) ➔ Halte 8 (FPBS - ATM Center FPBS / Jl. Sri Baduga)",
    "Leg 8: Halte 8 (FPBS - ATM Center FPBS) ➔ Halte 9 (FPIPS - Gedung FPIPS / Jl. Sri Baduga)",
    "Leg 9: Halte 9 (FPIPS - Jl. Sri Baduga) ➔ Halte 1 (FPTI - Depan Gedung A-D)"
]

jarak_list = [280, 300, 250, 300, 350, 200, 220, 250, 300]

data_jarak = {
    "Leg Rute Lingkar Kampus": leg_list,
    "Estimasi Jarak (Meter)": jarak_list
}

df_jarak = pd.DataFrame(data_jarak)
df_edited = st.data_editor(df_jarak, num_rows="fixed", use_container_width=True, key="editor_jarak_9")

# ---------------------------------------------------------
# 4. ENGINE KALKULASI MATEMATIKA PVRTP & WAKTU TUNGGU
# ---------------------------------------------------------
kecepatan_m_min = (kecepatan_kmjam * 1000) / 60
df_edited["Waktu Jalan (Menit)"] = (df_edited["Estimasi Jarak (Meter)"] / kecepatan_m_min).round(2)
df_edited["Total Waktu Leg (Menit)"] = (df_edited["Waktu Jalan (Menit)"] + dwell_time).round(2)

total_siklus_menit = df_edited["Total Waktu Leg (Menit)"].sum()
headway_menit = total_siklus_menit / jumlah_armada
waktu_tunggu_rata = headway_menit / 2
waktu_tunggu_maks = headway_menit

st.markdown("### 📊 Hasil Perhitungan Parameter & Waktu Tunggu Operasional")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total 1 Siklus Putar", f"{total_siklus_menit:.1f} Menit")
with col2:
    st.metric("Interval Kedatangan (Headway)", f"{headway_menit:.1f} Menit")
with col3:
    st.metric("Rata-Rata Waktu Tunggu", f"{waktu_tunggu_rata:.1f} Menit")
with col4:
    st.metric("Maksimum Waktu Tunggu", f"{waktu_tunggu_maks:.1f} Menit")

st.markdown("---")

# ---------------------------------------------------------
# 5. TABEL JADWAL KEBERANGKATAN TERSTRUKTUR (3 DEPOT AWAL)
# ---------------------------------------------------------
st.subheader("2️⃣ Draf Jadwal Keberangkatan Terstruktur (3 Depot Awal Berbeda)")

if "Pagi" in sesi:
    jam_keberangkatan = ["06.30 WIB", "06.45 WIB", "07.00 WIB", "07.15 WIB", "07.30 WIB", "07.45 WIB"]
else:
    jam_keberangkatan = ["16.00 WIB", "16.15 WIB", "16.30 WIB", "16.45 WIB", "17.00 WIB", "17.15 WIB"]

jadwal_data = {
    "Jam Keberangkatan": jam_keberangkatan,
    "Odong-Odong 1 (Start: Halte 1 FPTI - Depan Gedung A-D)": [
        "FPTI ➔ FIP Baru ➔ FPMIPA",
        "FPOK ➔ FK ➔ FPEB",
        "FPSD ➔ FPBS ➔ FPIPS ➔ FPTI",
        "FPTI ➔ FIP Baru ➔ FPMIPA",
        "FPOK ➔ FK ➔ FPEB",
        "FPSD ➔ FPBS ➔ FPIPS ➔ FPTI"
    ],
    "Odong-Odong 2 (Start: Halte 3 FPMIPA - Gedung JICA / Harsojo)": [
        "FPMIPA ➔ FPOK ➔ FK ➔ FPEB",
        "FPSD ➔ FPBS ➔ FPIPS",
        "FPTI ➔ FIP Baru ➔ FPMIPA",
        "FPMIPA ➔ FPOK ➔ FK ➔ FPEB",
        "FPSD ➔ FPBS ➔ FPIPS",
        "FPTI ➔ FIP Baru ➔ FPMIPA"
    ],
    "Odong-Odong 3 (Start: Halte 6 FPEB - Depan LPPM / Roeslan Abdulgani)": [
        "FPEB ➔ FPSD ➔ FPBS ➔ FPIPS",
        "FPTI ➔ FIP Baru ➔ FPMIPA",
        "FPOK ➔ FK ➔ FPEB",
        "FPEB ➔ FPSD ➔ FPBS ➔ FPIPS",
        "FPTI ➔ FIP Baru ➔ FPMIPA",
        "FPOK ➔ FK ➔ FPEB"
    ]
}

df_jadwal = pd.DataFrame(jadwal_data)
st.table(df_jadwal)

# ---------------------------------------------------------
# 6. VISUALISASI PETA INTERAKTIF MODE SATELIT HD & LAYERS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte Mode Satelit HD & Fitur Klik Koordinat")

# Inisialisasi Peta Folium dengan default Satelit Esri HD
m = folium.Map(
    location=[-6.8610, 107.5925], 
    zoom_start=17,
    tiles="[suspicious link removed]{z}/{y}/{x}",
    attr="Esri Satellite HD"
)

# Menambahkan Peta Jalan (OpenStreetMap & CartoDB) sebagai Pilihan Layer
folium.TileLayer('OpenStreetMap', name='Peta Jalan (OSM)').add_to(m)
folium.TileLayer('CartoDB positron', name='Peta Minimalis Light').add_to(m)

# Fitur Klik Koordinat: Klik di peta untuk memunculkan Popup Lat/Lon secara presisi
folium.LatLngPopup().add_to(m)

# 9 Halte presisi sesuai posisi visual fisik fisik gedung di Kampus UPI Silihwangi:
halte_9 = [
    {"nama": "Halte 1: FPTI (Depan Gedung A-D FPTI - Gerbang Bawah - Depot 1)", "pos": [-6.8637, 107.5922], "color": "blue"},
    {"nama": "Halte 2: FIP (Gedung FIP Baru - Jalan Mahaguru / Purbasari)", "pos": [-6.8614, 107.5914], "color": "green"},
    {"nama": "Halte 3: FPMIPA (Gedung JICA / FPMIPA-A - Jalan Harsojo - Depot 2)", "pos": [-6.8618, 107.5898], "color": "red"},
    {"nama": "Halte 4: FPOK (Gedung FPOK - Jalan Harsojo)", "pos": [-6.8603, 107.5900], "color": "darkred"},
    {"nama": "Halte 5: FK (Fakultas Kedokteran - Jalan Mahaguru)", "pos": [-6.8600, 107.5918], "color": "cadetblue"},
    {"nama": "Halte 6: FPEB (Gedung FPEB / Depan LPPM - Jl. Roeslan Abdulgani - Depot 3)", "pos": [-6.8588, 107.5932], "color": "orange"},
    {"nama": "Halte 7: FPSD (Gedung FPSD / Taman - Jl. Roeslan Abdulgani)", "pos": [-6.8584, 107.5944], "color": "darkgreen"},
    {"nama": "Halte 8: FPBS (ATM Center FPBS - Jl. Sri Baduga / Muh Yamin)", "pos": [-6.8590, 107.5948], "color": "darkblue"},
    {"nama": "Halte 9: FPIPS (Gedung FPIPS - Jl. Sri Baduga)", "pos": [-6.8600, 107.5938], "color": "purple"}
]

coords = []
for h in halte_9:
    coords.append(h["pos"])
    folium.Marker(
        location=h["pos"],
        popup=h["nama"],
        tooltip=h["nama"],
        icon=folium.Icon(color=h["color"], icon="bus", prefix="fa")
    ).add_to(m)

# Menutup rute lingkar kampus
coords.append(halte_9[0]["pos"])

folium.PolyLine(coords, color="yellow", weight=4, opacity=0.9, tooltip="Rute Lingkar 9 Fakultas Presisi Satelit HD").add_to(m)

# Menambahkan Control Layer di kanan atas peta
folium.LayerControl().add_to(m)

st_folium(m, width=1100, height=550)
