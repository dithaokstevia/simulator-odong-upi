# ---------------------------------------------------------
# 6. VISUALISASI PETA INTERAKTIF 9 HALTE (FOLIUM)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta 9 Halte Tetap Fakultas & Rute Kampus UPI")

# Center peta tepat di tengah Kampus UPI Silihwangi
m = folium.Map(location=[-6.8615, 107.5925], zoom_start=16)

halte_9 = [
    {"nama": "Halte 1: FPTK / FPTI (Gerbang Bawah - Depot 1)", "pos": [-6.8638, 107.5930], "color": "blue"},
    {"nama": "Halte 2: FIP", "pos": [-6.8618, 107.5922], "color": "green"},
    {"nama": "Halte 3: FPIPS", "pos": [-6.8612, 107.5942], "color": "purple"},
    {"nama": "Halte 4: FPBS", "pos": [-6.8610, 107.5950], "color": "darkblue"},
    {"nama": "Halte 5: FPSD", "pos": [-6.8620, 107.5952], "color": "darkgreen"},
    {"nama": "Halte 6: FPEB / Rektorat (Depot 3)", "pos": [-6.8600, 107.5945], "color": "orange"},
    {"nama": "Halte 7: FPMIPA / Kampus Atas (Depot 2)", "pos": [-6.8615, 107.5905], "color": "red"},
    {"nama": "Halte 8: FPOK / Gymnasium", "pos": [-6.8588, 107.5888], "color": "darkred"},
    {"nama": "Halte 9: FK (Fakultas Kedokteran)", "pos": [-6.8628, 107.5938], "color": "cadetblue"}
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

# Menutup siklus rute lingkar (kembali ke Halte 1)
coords.append(coords[0])
folium.PolyLine(coords, color="darkblue", weight=3, opacity=0.8, tooltip="Rute Odong-Odong 9 Fakultas UPI").add_to(m)

st_folium(m, width=1100, height=500)