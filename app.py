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

st.sidebar.info("💡 **Petunjuk**: Anda dapat mengedit jarak rute atau koordinat halte langsung pada tabel untuk menggeser posisi penanda secara live!")

# ---------------------------------------------------------
# 3. TABEL MATRIKS JARAK DINAMIS (9 HALTE FAKULTAS)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")

leg_list = [
    "Leg 1: Halte 1 (FPTI - Depan Gedung A-D) ➔ Halte 2 (FIP Baru - Jl. Mahaguru)",
    "Leg 2: Halte 2 (FIP Baru - Jl. Mahaguru) ➔ Halte 3 (FPMIPA - Gedung JICA / Jl. Harsojo)",
    "Leg 3: Halte 3 (FPMIPA - Gedung JICA) ➔ Halte 4 (FPOK - Jl. Harsojo)",
    "Leg 4: Halte 4 (FPOK - Jl. Harsojo) ➔ Halte 5 (FK - Fakultas Kedokteran / Jl. Mahaguru)",
    "Leg 5: Halte 5 (FK - Jl. Mahaguru) ➔ Halte 6 (FPEB - Jl. Roeslan Abdulgani)",
    "Leg 6: Halte 6 (FPEB - Jl. Roeslan Abdulgani) ➔ Halte 7 (FPSD - Jl. Roeslan Abdulgani)",
    "Leg 7: Halte 7 (FPSD - Jl. Roeslan Abdulgani) ➔ Halte 8 (FPBS - ATM Center FPBS / Jl. Sri Baduga)",
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
# 6. PANEL EDIT KOORDINAT LIVE & PETA INTERAKTIF
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte & Panel Fine-Tuning Koordinat")
st.write("Ubah angka Latitude / Longitude langsung pada tabel di bawah ini untuk menggeser titik halte secara live:")

data_koordinat_awal = {
    "Nama Halte": [
        "Halte 1: FPTI (Depan Gedung A-D)",
        "Halte 2: FIP Baru (Jl. Mahaguru)",
        "Halte 3: FPMIPA (Gedung JICA / Harsojo)",
        "Halte 4: FPOK (Gedung FPOK / Harsojo)",
        "Halte 5: FK (Fakultas Kedokteran)",
        "Halte 6: FPEB (Depan LPPM / Roeslan)",
        "Halte 7: FPSD (Depan FPSD / Roeslan)",
        "Halte 8: FPBS (ATM Center FPBS)",
        "Halte 9: FPIPS (Gedung FPIPS)"
    ],
    "Latitude": [-6.8637, -6.8614, -6.8618, -6.8603, -6.8600, -6.8588, -6.8584, -6.8590, -6.8600],
    "Longitude": [107.5922, 107.5914, 107.5898, 107.5900, 107.5918, 107.5932, 107.5944, 107.5948, 107.5938],
    "Warna Icon": ["blue", "green", "red", "darkred", "cadetblue", "orange", "darkgreen", "darkblue", "purple"]
}

df_coords = pd.DataFrame(data_koordinat_awal)
df_coords_edited = st.data_editor(df_coords, num_rows="fixed", use_container_width=True, key="editor_coords_live")

# Inisialisasi Peta Folium dengan URL CDN Direct Carto Voyager (100% Bebas Watermark & API Key)
m = folium.Map(
    location=[-6.8610, 107.5925], 
    zoom_start=17, 
    tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{y}/{x}{r}.png",
    attr="&copy; OpenStreetMap &copy; CARTO"
)

# Layer Peta Tambahan: Esri World Street Map HD
folium.TileLayer(
    tiles="[suspicious link removed]{z}/{y}/{x}",
    attr="Tiles &copy; Esri",
    name="Peta Jalan Esri HD"
).add_to(m)

# Layer Peta Tambahan: Carto Light
folium.TileLayer(
    tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{y}/{x}{r}.png",
    attr="&copy; CARTO",
    name="Peta Minimalis Light"
).add_to(m)

folium.LatLngPopup().add_to(m)

# Membaca data koordinat hasil editan live
coords = []
for index, row in df_coords_edited.iterrows():
    pos = [row["Latitude"], row["Longitude"]]
    coords.append(pos)
    folium.Marker(
        location=pos,
        popup=row["Nama Halte"],
        tooltip=row["Nama Halte"],
        icon=folium.Icon(color=row["Warna Icon"], icon="bus", prefix="fa")
    ).add_to(m)

# Menutup rute lingkar kampus (menghubungkan kembali ke Halte 1)
if len(coords) > 0:
    route_coords = list(coords) + [coords[0]]
    folium.PolyLine(route_coords, color="blue", weight=4, opacity=0.8, tooltip="Rute Lingkar 9 Halte UPI").add_to(m)

folium.LayerControl().add_to(m)
st_folium(m, width=1100, height=550)
