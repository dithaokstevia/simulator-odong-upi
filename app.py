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
st.caption("Kelompok 6 - Proyek MSTR Kampus UPI Silihwangi 2026 (Denah Resmi Kode A - I)")
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
# 3. TABEL MATRIKS JARAK DINAMIS (9 HALTE DENAH 2 CODE A-I)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")
st.write("Masukkan perkiraan jarak antar-halte (dalam Meter) pada tabel di bawah ini sesuai alur rute lingkar Denah 2 UPI:")

data_jarak = {
    "Leg Rute Lingkar Kampus (Denah 2 UPI)": [
        "Leg 1: Halte 1 (FPTK/FPTI - Gedung I) ➔ Halte 2 (FIP - Gedung C)",
        "Leg 2: Halte 2 (FIP - Gedung C) ➔ Halte 3 (FPMIPA - Gedung B)",
        "Leg 3: Halte 3 (FPMIPA - Gedung B) ➔ Halte 4 (FK - Gedung A)",
        "Leg 4: Halte 4 (FK - Gedung A) ➔ Halte 5 (FPOK - Gedung D)",
        "Leg 5: Halte 5 (FPOK - Gedung D) ➔ Halte 6 (FPEB - Gedung E)",
        "Leg 6: Halte 6 (FPEB - Gedung E) ➔ Halte 7 (FPSD - Gedung F)",
        "Leg 7: Halte 7 (FPSD - Gedung F) ➔ Halte 8 (FPIPS - Gedung G)",
        "Leg 8: Halte 8 (FPIPS - Gedung G) ➔ Halte 9 (FPBS - Gedung H)",
        "Leg 9: Halte 9 (FPBS - Gedung H) ➔ Halte 1 (FPTK/FPTI - Gedung I)"
    ],
    "Estimasi Jarak (Meter)": [200, 150, 120, 180, 400, 150, 220, 150, 350]
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
    "Odong-Odong 1 (Start: Halte 1 FPTK/FPTI - Gedung I)": [
        "FPTK/FPTI ➔ FIP ➔ FPMIPA ➔ FK",
        "FPOK ➔ FPEB ➔ FPSD",
        "FPIPS ➔ FPBS ➔ FPTK/FPTI",
        "FPTK/FPTI ➔ FIP ➔ FPMIPA ➔ FK",
        "FPOK ➔ FPEB ➔ FPSD",
        "FPIPS ➔ FPBS ➔ FPTK/FPTI"
    ],
    "Odong-Odong 2 (Start: Halte 3 FPMIPA - Gedung B)": [
        "FPMIPA ➔ FK ➔ FPOK ➔ FPEB",
        "FPSD ➔ FPIPS ➔ FPBS",
        "FPTK/FPTI ➔ FIP ➔ FPMIPA",
        "FPMIPA ➔ FK ➔ FPOK ➔ FPEB",
        "FPSD ➔ FPIPS ➔ FPBS",
        "FPTK/FPTI ➔ FIP ➔ FPMIPA"
    ],
    "Odong-Odong 3 (Start: Halte 6 FPEB - Gedung E)": [
        "FPEB ➔ FPSD ➔ FPIPS ➔ FPBS",
        "FPTK/FPTI ➔ FIP ➔ FPMIPA",
        "FK ➔ FPOK ➔ FPEB",
        "FPEB ➔ FPSD ➔ FPIPS ➔ FPBS",
        "FPTK/FPTI ➔ FIP ➔ FPMIPA",
        "FK ➔ FPOK ➔ FPEB"
    ]
}

df_jadwal = pd.DataFrame(jadwal_data)
st.table(df_jadwal)

# ---------------------------------------------------------
# 6. VISUALISASI PETA INTERAKTIF 9 HALTE (DENAH 2 UPI)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte Tetap Fakultas (Denah 2 Kode A - I)")

m = folium.Map(location=[-6.8605, 107.5925], zoom_start=16)

# 9 Halte sesuai posisi geografis presisi Denah 2 UPI
halte_9 = [
    {"nama": "Halte 1: FPTK / FPTI (Gedung I - Gerbang Bawah - Depot 1)", "pos": [-6.8632, 107.5925], "color": "blue"},
    {"nama": "Halte 2: FIP (Gedung C - Ilmu Pendidikan)", "pos": [-6.8618, 107.5912], "color": "green"},
    {"nama": "Halte 3: FPMIPA (Gedung B - MIPA - Depot 2)", "pos": [-6.8612, 107.5900], "color": "red"},
    {"nama": "Halte 4: FK (Gedung A - Kedokteran)", "pos": [-6.8603, 107.5903], "color": "cadetblue"},
    {"nama": "Halte 5: FPOK (Gedung D - Olahraga & Kesehatan)", "pos": [-6.8588, 107.5898], "color": "darkred"},
    {"nama": "Halte 6: FPEB (Gedung E - Ekonomi & Bisnis - Depot 3)", "pos": [-6.8580, 107.5932], "color": "orange"},
    {"nama": "Halte 7: FPSD (Gedung F - Seni & Desain)", "pos": [-6.8580, 107.5945], "color": "darkgreen"},
    {"nama": "Halte 8: FPIPS (Gedung G - Ilmu Pengetahuan Sosial)", "pos": [-6.8598, 107.5942], "color": "purple"},
    {"nama": "Halte 9: FPBS (Gedung H - Bahasa & Sastra)", "pos": [-6.8608, 107.5948], "color": "darkblue"}
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

folium.PolyLine(coords, color="darkblue", weight=4, opacity=0.8, tooltip="Rute Lingkar 9 Fakultas Denah 2 UPI").add_to(m)

st_folium(m, width=1100, height=500)
