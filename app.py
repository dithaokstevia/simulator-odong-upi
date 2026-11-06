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
# 3. TABEL MATRIKS JARAK DINAMIS (9 HALTE FAKULTAS LINGKAR KAMPUS)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")
st.write("Masukkan perkiraan jarak antar-halte (dalam Meter) pada tabel di bawah ini sesuai urutan rute lingkar kampus:")

data_jarak = {
    "Leg Rute Lingkar Kampus": [
        "Leg 1: Halte 1 (FPTK/FPTI) ➔ Halte 2 (FIP)",
        "Leg 2: Halte 2 (FIP) ➔ Halte 6 (FPMIPA / Kampus Atas)",
        "Leg 3: Halte 6 (FPMIPA) ➔ Halte 7 (FPOK / Gymnasium)",
        "Leg 4: Halte 7 (FPOK) ➔ Halte 5 (FPEB / Rektorat)",
        "Leg 5: Halte 5 (FPEB) ➔ Halte 3 (FPIPS)",
        "Leg 6: Halte 3 (FPIPS) ➔ Halte 4 (FPBS)",
        "Leg 7: Halte 4 (FPBS) ➔ Halte 8 (FPSD)",
        "Leg 8: Halte 8 (FPSD) ➔ Halte 9 (FK / Kedokteran)",
        "Leg 9: Halte 9 (FK) ➔ Halte 1 (FPTK/FPTI)"
    ],
    "Estimasi Jarak (Meter)": [280, 350, 300, 400, 220, 180, 200, 250, 270]
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
        "FPOK ➔ FPEB ➔ FPIPS",
        "FPBS ➔ FPSD ➔ FK",
        "FPTK/FPTI ➔ FIP ➔ FPMIPA",
        "FPOK ➔ FPEB ➔ FPIPS",
        "FPBS ➔ FPSD ➔ FK"
    ],
    "Odong-Odong 2 (Start: Halte 6 FPMIPA)": [
        "FPMIPA ➔ FPOK ➔ FPEB",
        "FPIPS ➔ FPBS ➔ FPSD",
        "FK ➔ FPTK/FPTI ➔ FIP",
        "FPMIPA ➔ FPOK ➔ FPEB",
        "FPIPS ➔ FPBS ➔ FPSD",
        "FK ➔ FPTK/FPTI ➔ FIP"
    ],
    "Odong-Odong 3 (Start: Halte 5 FPEB)": [
        "FPEB ➔ FPIPS ➔ FPBS",
        "FPSD ➔ FK ➔ FPTK/FPTI",
        "FIP ➔ FPMIPA ➔ FPOK",
        "FPEB ➔ FPIPS ➔ FPBS",
        "FPSD ➔ FK ➔ FPTK/FPTI",
        "FIP ➔ FPMIPA ➔ FPOK"
    ]
}

df_jadwal = pd.DataFrame(jadwal_data)
st.table(df_jadwal)

# ---------------------------------------------------------
# 6. VISUALISASI PETA INTERAKTIF 9 HALTE (FOLIUM)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte Tetap Fakultas & Rute Kampus UPI")

m = folium.Map(location=[-6.8612, 107.5930], zoom_start=17)

# Daftar 9 Halte dalam urutan geografis lintasan lingkar kampus
halte_9 = [
    {"nama": "Halte 1: FPTK / FPTI (Gerbang Bawah - Depot 1)", "pos": [-6.8638, 107.5930], "color": "blue"},
    {"nama": "Halte 2: FIP (Purbasari)", "pos": [-6.8618, 107.5922], "color": "green"},
    {"nama": "Halte 6: FPMIPA / Kampus Atas (Depot 2)", "pos": [-6.8605, 107.5908], "color": "red"},
    {"nama": "Halte 7: FPOK / Gymnasium", "pos": [-6.8582, 107.5900], "color": "darkred"},
    {"nama": "Halte 5: FPEB / Rektorat (Depot 3)", "pos": [-6.8600, 107.5942], "color": "orange"},
    {"nama": "Halte 3: FPIPS", "pos": [-6.8608, 107.5946], "color": "purple"},
    {"nama": "Halte 4: FPBS", "pos": [-6.8612, 107.5952], "color": "darkblue"},
    {"nama": "Halte 8: FPSD", "pos": [-6.8618, 107.5954], "color": "darkgreen"},
    {"nama": "Halte 9: FK (Poliklinik / Kedokteran)", "pos": [-6.8625, 107.5938], "color": "cadetblue"}
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

folium.PolyLine(coords, color="darkblue", weight=3, opacity=0.8, tooltip="Rute Lingkar Odong-Odong 9 Fakultas UPI").add_to(m)

st_folium(m, width=1100, height=500)
