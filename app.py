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
st.caption("Kelompok 6 - Proyek MSTR Kampus UPI Silihwangi 2026")
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
# 3. TABEL MATRIKS JARAK DINAMIS (9 HALTE SESUAI DENAH RESMI UPI)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")
st.write("Masukkan perkiraan jarak antar-halte (dalam Meter) pada tabel di bawah ini sesuai rute lingkar denah resmi UPI:")

data_jarak = {
    "Leg Rute Lingkar Kampus (Denah UPI)": [
        "Leg 1: Halte 1 (FPTK/FPTI - Gerbang Bawah) ➔ Halte 2 (FIP)",
        "Leg 2: Halte 2 (FIP) ➔ Halte 3 (FPMIPA)",
        "Leg 3: Halte 3 (FPMIPA) ➔ Halte 4 (FK / Kedokteran)",
        "Leg 4: Halte 4 (FK) ➔ Halte 5 (FPOK / Gymnasium)",
        "Leg 5: Halte 5 (FPOK) ➔ Halte 6 (FPEB)",
        "Leg 6: Halte 6 (FPEB) ➔ Halte 7 (FPSD)",
        "Leg 7: Halte 7 (FPSD) ➔ Halte 8 (FPIPS)",
        "Leg 8: Halte 8 (FPIPS) ➔ Halte 9 (FPBS)",
        "Leg 9: Halte 9 (FPBS) ➔ Halte 1 (FPTK/FPTI - Gerbang Bawah)"
    ],
    "Estimasi Jarak (Meter)": [280, 250, 200, 300, 450, 220, 250, 200, 350]
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
    "Odong-Odong 1 (Start: Halte 1 FPTK/FPTI)": [
        "FPTK/FPTI ➔ FIP ➔ FPMIPA",
        "FK ➔ FPOK ➔ FPEB",
        "FPSD ➔ FPIPS ➔ FPBS",
        "FPTK/FPTI ➔ FIP ➔ FPMIPA",
        "FK ➔ FPOK ➔ FPEB",
        "FPSD ➔ FPIPS ➔ FPBS"
    ],
    "Odong-Odong 2 (Start: Halte 3 FPMIPA)": [
        "FPMIPA ➔ FK ➔ FPOK",
        "FPEB ➔ FPSD ➔ FPIPS",
        "FPBS ➔ FPTK/FPTI ➔ FIP",
        "FPMIPA ➔ FK ➔ FPOK",
        "FPEB ➔ FPSD ➔ FPIPS",
        "FPBS ➔ FPTK/FPTI ➔ FIP"
    ],
    "Odong-Odong 3 (Start: Halte 6 FPEB)": [
        "FPEB ➔ FPSD ➔ FPIPS",
        "FPBS ➔ FPTK/FPTI ➔ FIP",
        "FPMIPA ➔ FK ➔ FPOK",
        "FPEB ➔ FPSD ➔ FPIPS",
        "FPBS ➔ FPTK/FPTI ➔ FIP",
        "FPMIPA ➔ FK ➔ FPOK"
    ]
}

df_jadwal = pd.DataFrame(jadwal_data)
st.table(df_jadwal)

# ---------------------------------------------------------
# 6. VISUALISASI PETA INTERAKTIF 9 HALTE (DENAH RESMI UPI)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte Tetap Fakultas (Sesuai Denah Resmi UPI)")

m = folium.Map(location=[-6.8610, 107.5925], zoom_start=16)

# Daftar 9 Halte Fakultas berdasarkan Denah Resmi UPI
halte_9 = [
    {"nama": "Halte 1: FPTK / FPTI (No. 9/I - Gerbang Bawah - Depot 1)", "pos": [-6.8635, 107.5930], "color": "blue"},
    {"nama": "Halte 2: FIP (No. 3/C - Fakultas Ilmu Pendidikan)", "pos": [-6.8620, 107.5915], "color": "green"},
    {"nama": "Halte 3: FPMIPA (No. 2/B - Depot 2)", "pos": [-6.8610, 107.5900], "color": "red"},
    {"nama": "Halte 4: FK (No. 1/A - Fakultas Kedokteran)", "pos": [-6.8600, 107.5902], "color": "cadetblue"},
    {"nama": "Halte 5: FPOK (No. 4/D - Gymnasium / Olahraga)", "pos": [-6.8585, 107.5895], "color": "darkred"},
    {"nama": "Halte 6: FPEB (No. 5/E - Depot 3)", "pos": [-6.8580, 107.5935], "color": "orange"},
    {"nama": "Halte 7: FPSD (No. 6/F - Seni dan Desain)", "pos": [-6.8580, 107.5950], "color": "darkgreen"},
    {"nama": "Halte 8: FPIPS (No. 7/G - Ilmu Pengetahuan Sosial)", "pos": [-6.8598, 107.5948], "color": "purple"},
    {"nama": "Halte 9: FPBS (No. 8/H - Bahasa dan Sastra)", "pos": [-6.8612, 107.5952], "color": "darkblue"}
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

folium.PolyLine(coords, color="darkblue", weight=3, opacity=0.8, tooltip="Rute Lingkar Odong-Odong 9 Fakultas (Denah UPI)").add_to(m)

st_folium(m, width=1100, height=500)
