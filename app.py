import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN DASHBOARD
# ---------------------------------------------------------
st.set_page_config(
    page_title="Simulator Parametrik Odong-Odong UPI",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Simulator Parametrik Rute & Penjadwalan Odong-Odong UPI")
st.caption("Kelompok 6 - Ditha Okstevia, Eisha Karima Fidareini, Nailah Amani Nuryaman, Nesa Dwi Rizqi Marsha Reneta, Wafa Nidaul Hasanah - Proyek MSTR")
st.markdown("---")

# ---------------------------------------------------------
# 2. SIDEBAR: PANEL KONTROL PARAMETER
# ---------------------------------------------------------
st.sidebar.header("⚙️ Panel Parameter Simulator")

sesi = st.sidebar.selectbox("Pilih Sesi Jam Operasional:", ["Pagi (06.30 - 08.00 WIB)", "Sore (16.00 - 16.30 WIB)"])
kecepatan_kmjam = st.sidebar.slider("Kecepatan Rata-Rata Odong-Odong (km/jam):", min_value=5, max_value=25, value=15, step=1)
dwell_time = st.sidebar.number_input("Waktu Henti di Halte / Dwell Time (Menit):", min_value=1, max_value=5, value=2, step=1)
jumlah_armada = 3  # Fixed 3 Armada Aktif

st.sidebar.info("💡 **Petunjuk**: Mengubah kecepatan, dwell time, atau jarak leg di bawah akan secara otomatis mengalkulasi ulang seluruh jam & menit kedatangan bus di tiap halte pada Tabel Jadwal!")

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
# 5. TABEL JADWAL PRESISI WAKTU KEDATANGAN PER HALTE (TIMETABLE DINAMIS)
# ---------------------------------------------------------
st.subheader("2️⃣ Tabel Jadwal Presisi Waktu Kedatangan di Setiap Halte (Timetable Dinamis)")
st.write("Jadwal di bawah ini **terkalkulasi secara otomatis** berdasarkan waktu tempuh dan dwell time untuk setiap odong-odong:")

halte_names = [
    "Halte 1 (FPTI - Gerbang Bawah)",
    "Halte 2 (FIP Baru)",
    "Halte 3 (FPMIPA - JICA)",
    "Halte 4 (FPOK Utama)",
    "Halte 5 (FK Kedokteran)",
    "Halte 6 (FPEB Utama)",
    "Halte 7 (FPSD Utama)",
    "Halte 8 (FPBS / ATM Center)",
    "Halte 9 (FPIPS Utama)"
]

leg_durations = df_edited["Total Waktu Leg (Menit)"].tolist()

def build_timetable(start_halte_idx, start_hour_str, trips=2):
    sh, sm = map(int, start_hour_str.split('.'))
    base_dt = datetime.datetime(2026, 11, 6, sh, sm)
    
    rows = []
    num_haltes = len(halte_names)
    
    curr_dt = base_dt
    for trip in range(1, trips + 1):
        for step in range(num_haltes):
            h_idx = (start_halte_idx + step) % num_haltes
            h_name = halte_names[h_idx]
            
            rows.append({
                "Putaran / Trip": f"Trip {trip}",
                "Nama Halte Singgah": h_name,
                "Jam Kedatangan Presisi": curr_dt.strftime("%H.%M WIB")
            })
            
            # Tambah durasi leg ke halte berikutnya
            dur = leg_durations[h_idx]
            curr_dt += datetime.timedelta(minutes=dur)
            
        # Akhir putaran kembali ke halte asal
        origin_name = halte_names[start_halte_idx]
        rows.append({
            "Putaran / Trip": f"Trip {trip} (Selesai)",
            "Nama Halte Singgah": f"Kembali ke {origin_name}",
            "Jam Kedatangan Presisi": curr_dt.strftime("%H.%M WIB")
        })
        
    return pd.DataFrame(rows)

start_time_base = "06.30" if "Pagi" in sesi else "16.00"

tab1, tab2, tab3 = st.tabs([
    "🚌 Odong 1 (Start: Halte 1 FPTI)",
    "🚌 Odong 2 (Start: Halte 3 FPMIPA)",
    "🚌 Odong 3 (Start: Halte 6 FPEB)"
])

with tab1:
    st.markdown("**Jadwal Keberangkatan & Kedatangan Odong-Odong 1 (Start Halte 1 FPTI)**")
    df_o1 = build_timetable(0, start_time_base, trips=2)
    st.dataframe(df_o1, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("**Jadwal Keberangkatan & Kedatangan Odong-Odong 2 (Start Halte 3 FPMIPA)**")
    df_o2 = build_timetable(2, start_time_base, trips=2)
    st.dataframe(df_o2, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("**Jadwal Keberangkatan & Kedatangan Odong-Odong 3 (Start Halte 6 FPEB)**")
    df_o3 = build_timetable(5, start_time_base, trips=2)
    st.dataframe(df_o3, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 6. PANEL EDIT KOORDINAT LIVE & PETA INTERAKTIF (PRESISI SCREENSHOT 025247)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte & Panel Fine-Tuning Koordinat (Presisi Screenshot 025247)")
st.write("Angka koordinat di bawah disesuaikan presisi dengan tangkapan layar **Screenshot 2026-11-07 025247.png**. Anda tetap dapat mengedit angkanya secara live jika diperlukan:")

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
    "Latitude": [-6.8637, -6.8617, -6.8620, -6.8610, -6.8608, -6.8603, -6.8602, -6.8606, -6.8613],
    "Longitude": [107.5925, 107.5911, 107.5904, 107.5900, 107.5912, 107.5925, 107.5933, 107.5940, 107.5927],
    "Warna Icon": ["blue", "green", "red", "darkred", "cadetblue", "orange", "darkgreen", "darkblue", "purple"]
}

df_coords = pd.DataFrame(data_koordinat_awal)
df_coords_edited = st.data_editor(df_coords, num_rows="fixed", use_container_width=True, key="editor_coords_live")

# Server Direct OpenStreetMap (100% Gratis, Bebas API Key & Tanpa Watermark)
tile_url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

m = folium.Map(
    location=[-6.8610, 107.5925], 
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
