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
st.caption("Kelompok 6 - Proyek MSTR Kampus UPI Silihwangi 2026 (Presisi 9 Gedung Fakultas)")
st.markdown("---")

# ---------------------------------------------------------
# 2. SIDEBAR: PANEL KONTROL PARAMETER
# ---------------------------------------------------------
st.sidebar.header("⚙️ Panel Parameter Simulator")

sesi = st.sidebar.selectbox("Pilih Sesi Jam Operasional:", ["Pagi (06.30 - 08.00 WIB)", "Sore (16.00 - 16.30 WIB)"])
kecepatan_kmjam = st.sidebar.slider("Kecepatan Rata-Rata Odong-Odong (km/jam):", min_value=5, max_value=25, value=15, step=1)
dwell_time = st.sidebar.number_input("Waktu Henti di Halte / Dwell Time (Menit):", min_value=1, max_value=5, value=2, step=1)
jumlah_armada = 3  # Fixed 3 Armada Aktif

st.sidebar.info("💡 **Petunjuk**: Anda dapat mengedit jarak rute atau koordinat halte secara langsung pada tabel di bawah untuk menyesuaikan posisi penanda di peta.")

# ---------------------------------------------------------
# 3. TABEL MATRIKS JARAK DINAMIS (9 HALTE FAKULTAS)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")

leg_list = [
    "Leg 1: Halte 1 (FPTI - Gedung A-D Gerbang Bawah) ➔ Halte 2 (FIP Baru - Jl. Mahaguru)",
    "Leg 2: Halte 2 (FIP Baru - Jl. Mahaguru) ➔ Halte 3 (FPMIPA - Gedung JICA / Harsojo)",
    "Leg 3: Halte 3 (FPMIPA - Gedung JICA) ➔ Halte 4 (FPOK - Gedung FPOK Utama)",
    "Leg 4: Halte 4 (FPOK - Gedung FPOK) ➔ Halte 5 (FK - Gedung Fakultas Kedokteran)",
    "Leg 5: Halte 5 (FK - Gedung Kedokteran) ➔ Halte 6 (FPEB - Gedung FPEB Utama)",
    "Leg 6: Halte 6 (FPEB - Gedung FPEB) ➔ Halte 7 (FPSD - Gedung FPSD Utama)",
    "Leg 7: Halte 7 (FPSD - Gedung FPSD) ➔ Halte 8 (FPBS - Gedung FPBS / ATM Center)",
    "Leg 8: Halte 8 (FPBS - Gedung FPBS) ➔ Halte 9 (FPIPS - Gedung FPIPS Utama)",
    "Leg 9: Halte 9 (FPIPS - Gedung FPIPS) ➔ Halte 1 (FPTI - Gedung A-D Gerbang Bawah)"
]

jarak_list = [
    280,
    300,
    250,
    300,
    350,
    200,
    220,
    250,
    300
]

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
    "Odong-Odong 1 (Start: Halte 1 FPTI - Gedung A-D)": [
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
    "Odong-Odong 3 (Start: Halte 6 FPEB - Gedung FPEB Utama)": [
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
# 6. PANEL EDIT KOORDINAT LIVE & PETA INTERAKTIF
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte & Panel Fine-Tuning Koordinat")
st.write("Ubah angka Latitude / Longitude langsung pada tabel di bawah ini untuk menggeser titik halte secara live:")

data_koordinat_awal = {
    "Nama Halte": [
        "Halte 1: FPTI (Gedung A-D Gerbang Bawah)",
        "Halte 2: FIP Baru (Gedung FIP Baru)",
        "Halte 3: FPMIPA (Gedung JICA FPMIPA)",
        "Halte 4: FPOK (Gedung FPOK Utama)",
        "Halte 5: FK (Gedung Fakultas Kedokteran)",
        "Halte 6: FPEB (Gedung FPEB Utama)",
        "Halte 7: FPSD (Gedung FPSD Utama)",
        "Halte 8: FPBS (Gedung FPBS / ATM Center)",
        "Halte 9: FPIPS (Gedung FPIPS Utama)"
    ],
    "Latitude": [-6.8637, -6.8614, -6.8612, -6.8600, -6.8596, -6.8588, -6.8582, -6.8588, -6.8598],
    "Longitude": [107.5925, 107.5914, 107.5898, 107.5898, 107.5914, 107.5928, 107.5942, 107.5948, 107.5938],
    "Warna Icon": ["blue", "green", "red", "darkred", "cadetblue", "orange", "darkgreen", "darkblue", "purple"]
}

df_coords = pd.DataFrame(data_koordinat_awal)
df_coords_edited = st.data_editor(df_coords, num_rows="fixed", use_container_width=True, key="editor_coords_live")

# Server Direct OpenStreetMap (100% Gratis, Bebas API Key & Tanpa Watermark)
tile_url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

m = folium.Map(
    location=[-6.8608, 107.5925], 
    zoom_start=17, 
    tiles=tile_url,
    attr="&copy; OpenStreetMap contributors"
)

folium.LatLngPopup().add_to(m)

# Membaca data koordinat hasil editan live
coords = []
for index, row in df_coords_edited.iterrows():
    pos = [float(row["Latitude"]), float(row["Longitude"])]
    coords.append(pos)
    folium.Marker(
        location=pos,
        popup=row["Nama Halte"],
        tooltip=row["Nama Halte"],
        icon=folium.Icon(color=row["Warna Icon"], icon="bus", prefix="fa")
    ).add_to(m)

# Menutup rute lingkar kampus (menghubungkan kembali Halte 9 ke Halte 1)
if len(coords) > 0:
    route_coords = coords + [coords[0]]
    folium.PolyLine(route_coords, color="blue", weight=4, opacity=0.8, tooltip="Rute Lingkar 9 Halte UPI").add_to(m)

st_folium(m, width=1100, height=550)
