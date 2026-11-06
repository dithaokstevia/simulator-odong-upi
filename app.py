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
st.caption("Kelompok 6 - Proyek MSTR Kampus UPI Silihwangi 2026 (Presisi 9 Fakultas dari Screenshot OSM)")
st.markdown("---")

# ---------------------------------------------------------
# 2. SIDEBAR: PANEL KONTROL PARAMETER
# ---------------------------------------------------------
st.sidebar.header("⚙️ Panel Parameter Simulator")

sesi = st.sidebar.selectbox("Pilih Sesi Jam Operasional:", ["Pagi (06.30 - 08.00 WIB)", "Sore (16.00 - 16.30 WIB)"])
kecepatan_kmjam = st.sidebar.slider("Kecepatan Rata-Rata Odong-Odong (km/jam):", min_value=5, max_value=25, value=15, step=1)
dwell_time = st.sidebar.number_input("Waktu Henti di Halte / Dwell Time (Menit):", min_value=1, max_value=5, value=2, step=1)
jumlah_armada = 3  # Fixed 3 Armada Aktif

st.sidebar.info("💡 **Catatan**: Mengubah angka pada panel akan otomatis mengalkulasi rumus matematika waktu tempuh, headway, waktu tunggu, dan tabel jadwal di bawah.")

# ---------------------------------------------------------
# 3. TABEL MATRIKS JARAK DINAMIS (9 HALTE FAKULTAS MATCHING SCREENSHOTS)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")
st.write("Masukkan perkiraan jarak antar-halte (dalam Meter) pada tabel di bawah ini sesuai alur rute lingkar kampus (Tangkapan Layar OSM):")

data_jarak = {
    "Leg Rute Lingkar Kampus (Sesuai Tangkapan Layar OSM)": [
        "Leg 1: Halte 1 (FPTK/FPTI - Gerbang Bawah) ➔ Halte 2 (FIP Baru - Jl. Mahaguru)",
        "Leg 2: Halte 2 (FIP Baru) ➔ Halte 3 (FK - Fakultas Kedokteran)",
        "Leg 3: Halte 3 (FK) ➔ Halte 4 (FPMIPA - Gedung JICA / Jl. Harsojo)",
        "Leg 4: Halte 4 (FPMIPA) ➔ Halte 5 (FPOK - Jl. Harsojo)",
        "Leg 5: Halte 5 (FPOK) ➔ Halte 6 (FPEB - Jl. Roeslan Abdulgani)",
        "Leg 6: Halte 6 (FPEB) ➔ Halte 7 (FPSD - Jl. Roeslan Abdulgani / Sri Baduga)",
        "Leg 7: Halte 7 (FPSD) ➔ Halte 8 (FPIPS - Jl. Sri Baduga)",
        "Leg 8: Halte 8 (FPIPS) ➔ Halte 9 (FPBS - Jl. Sri Baduga / Muh Yamin)",
        "Leg 9: Halte 9 (FPBS) ➔ Halte 1 (FPTK/FPTI - Gerbang Bawah)"
    ],
    "Estimasi Jarak (Meter)": [280, 200, 350, 250, 400, 220, 250, 220, 430]
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
    "Odong-Odong 1 (Start: Halte 1 FPTK/FPTI - Gerbang Bawah)": [
        "FPTK/FPTI ➔ FIP ➔ FK ➔ FPMIPA",
        "FPOK ➔ FPEB ➔ FPSD",
        "FPIPS ➔ FPBS ➔ FPTK/FPTI",
        "FPTK/FPTI ➔ FIP ➔ FK ➔ FPMIPA",
        "FPOK ➔ FPEB ➔ FPSD",
        "FPIPS ➔ FPBS ➔ FPTK/FPTI"
    ],
    "Odong-Odong 2 (Start: Halte 4 FPMIPA - Gedung JICA)": [
        "FPMIPA ➔ FPOK ➔ FPEB ➔ FPSD",
        "FPIPS ➔ FPBS ➔ FPTK/FPTI",
        "FIP ➔ FK ➔ FPMIPA",
        "FPMIPA ➔ FPOK ➔ FPEB ➔ FPSD",
        "FPIPS ➔ FPBS ➔ FPTK/FPTI",
        "FIP ➔ FK ➔ FPMIPA"
    ],
    "Odong-Odong 3 (Start: Halte 6 FPEB - Jl. Roeslan Abdulgani)": [
        "FPEB ➔ FPSD ➔ FPIPS ➔ FPBS",
        "FPTK/FPTI ➔ FIP ➔ FK",
        "FPMIPA ➔ FPOK ➔ FPEB",
        "FPEB ➔ FPSD ➔ FPIPS ➔ FPBS",
        "FPTK/FPTI ➔ FIP ➔ FK",
        "FPMIPA ➔ FPOK ➔ FPEB"
    ]
}

df_jadwal = pd.DataFrame(jadwal_data)
st.table(df_jadwal)

# ---------------------------------------------------------
# 6. VISUALISASI PETA INTERAKTIF 9 HALTE (MATCHING SCREENSHOTS)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte Tetap Fakultas (Presisi Tangkapan Layar OSM)")

m = folium.Map(location=[-6.8610, 107.5928], zoom_start=16)

# 9 Halte presisi sesuai posisi lingkaran hijau pada 9 tangkapan layar OSM:
halte_9 = [
    {"nama": "Halte 1: FPTK / FPTI (Gedung A-D FPTI - Gerbang Bawah - Depot 1)", "pos": [-6.8633, 107.5932], "color": "blue"},
    {"nama": "Halte 2: FIP (FIP Baru - Jalan Mahaguru)", "pos": [-6.8617, 107.5925], "color": "green"},
    {"nama": "Halte 3: FK (Fakultas Kedokteran - Jalan Mahaguru)", "pos": [-6.8605, 107.5925], "color": "cadetblue"},
    {"nama": "Halte 4: FPMIPA (Gedung JICA / FPMIPA-A - Jalan Harsojo - Depot 2)", "pos": [-6.8615, 107.5905], "color": "red"},
    {"nama": "Halte 5: FPOK (Fakultas Pendidikan Olahraga & Kesehatan - Jalan Harsojo)", "pos": [-6.8600, 107.5905], "color": "darkred"},
    {"nama": "Halte 6: FPEB (Fakultas Ekonomi & Bisnis - Jalan Roeslan Abdulgani - Depot 3)", "pos": [-6.8588, 107.5932], "color": "orange"},
    {"nama": "Halte 7: FPSD (Fakultas Seni & Desain - Jalan Roeslan Abdulgani / Sri Baduga)", "pos": [-6.8585, 107.5945], "color": "darkgreen"},
    {"nama": "Halte 8: FPIPS (Fakultas Ilmu Pengetahuan Sosial - Jalan Sri Baduga)", "pos": [-6.8600, 107.5942], "color": "purple"},
    {"nama": "Halte 9: FPBS (Fakultas Bahasa & Sastra - Jalan Sri Baduga / Muh Yamin)", "pos": [-6.8605, 107.5950], "color": "darkblue"}
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

# Menutup rute lingkar kampus (kembali ke Halte 1 FPTK/FPTI)
coords.append(halte_9[0]["pos"])

folium.PolyLine(coords, color="darkblue", weight=4, opacity=0.8, tooltip="Rute Lingkar 9 Fakultas Presisi OSM").add_to(m)

st_folium(m, width=1100, height=500)
