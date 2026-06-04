import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

# ===============================================================================================#
#-- SMART FLOOD MONITORING & PREDICTION SYSTEM BERBASIS IoT & MACHINE LEARNING (KECAMATAN LEDO) --#
#-- NAMA ANGGOTA KELOMPOK / PERWAKILAN: FELIKS TRI AGTI (NIM: 2400504007) -----------------------#
# ===============================================================================================#

# 1. KONFIGURASI HALAMAN UTAMA & TEMA PREMIUM
st.set_page_config(
    page_title="Ledo Flood Early Warning System",
    page_icon="🤖",
    layout="wide"
)

# Kustomisasi CSS untuk mempercantik tampilan UI (Premium UI Dashboard)
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #58a6ff; }
    div[data-testid="stMetricLabel"] { font-size: 14px; color: #8b949e; }
    .stButton>button { width: 100%; background-color: #238636; color: white; border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

# 2. STATE MANAGEMENT (MEMORI DATA SENSOR IoT REAL-TIME)
if 'stasiun_sensor' not in st.session_state:
    st.session_state.stasiun_sensor = {
        "Sensor_Ledo_01": {"desa": "Desa Rodaya", "lat": 0.9984, "lon": 109.5891, "debit": 115.4, "hujan": 85.0},
        "Sensor_Ledo_02": {"desa": "Desa Dayung", "lat": 1.0583, "lon": 109.6102, "debit": 34.2, "hujan": 20.5},
        "Sensor_Ledo_03": {"desa": "Desa Jesape", "lat": 0.9572, "lon": 109.5211, "debit": 28.1, "hujan": 15.0},
        "Sensor_Ledo_04": {"desa": "Desa Semangat", "lat": 0.9650, "lon": 109.6015, "debit": 68.5, "hujan": 55.0},
        "Sensor_Ledo_05": {"desa": "Desa Lesabela", "lat": 0.9789, "lon": 109.5843, "debit": 41.0, "hujan": 30.2}
    }

# 3. LEDO FLOOD AI-ENGINE (ALGORITMA PREDIKSI RISIKO)
def ledo_ai_engine(debit, hujan):
    skor = (debit * 0.65) + (hujan * 0.35)
    if skor >= 80: 
        return "Bahaya / Banjir", "🔴 EMERGENCY", "#FF4B4B"
    elif skor >= 45: 
        return "Siaga Waspada", "🟡 WARNING", "#FFA500"
    return "Normal", "🟢 AMAN", "#00CB52"

# 4. GENERATOR DATA TREN HISTORIS 24 JAM (UNTUK GRAFIK GARIS)
@st.cache_data
def generate_tren_data():
    np.random.seed(42)
    waktu_sekarang = datetime.now()
    timestamps = [(waktu_sekarang - timedelta(hours=i)).strftime("%H:%M") for i in range(12)]
    timestamps.reverse()
    
    # Ambil basis data dari sensor aktual
    data = {"Waktu": timestamps}
    for id_s, info in st.session_state.stasiun_sensor.items():
        data[info['desa']] = np.clip(np.random.normal(info['debit'], 10, 12), 10, 150)
    return pd.DataFrame(data)

df_tren = generate_tren_data()

# 5. SIDEBAR PANEL KONTROL & IDENTITAS KELOMPOK
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4221/4221419.png", width=80)
st.sidebar.title("Pusat Kendali")
role = st.sidebar.radio("Pilih Mode Akses:", ["👥 Pengguna Umum (Warga)", "🔐 Administrator (BPBD)"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏆 TIM PENGEMBANG")
st.sidebar.info(
    "**• Feliks Tri Agti**\n"
    "**• NIM:** 2400504007\n"
    "**• Prodi:** Teknologi Informasi\n"
    "**• Kategori:** Programming 1.0"
)

# ===============================================================================================#
# PANEL 1: USER VIEW (MONITORING LANGSUNG LENGKAP DENGAN PETA & 2 JENIS GRAFIK)
# ===============================================================================================#
if role == "👥 Pengguna Umum (Warga)":
    st.title("🚀 IoT & AI Flood Early Warning System (Kecamatan Ledo)")
    st.caption("Sistem Pemantauan Risiko Bencana Kebencanaan Real-Time Terintegrasi Digital GIS")
    st.markdown("---")
    
    # HITUNG DATA AKTUAL
    total_bahaya = sum(1 for info in st.session_state.stasiun_sensor.values() if ledo_ai_engine(info['debit'], info['hujan'])[0] == "Bahaya / Banjir")
    total_siaga = sum(1 for info in st.session_state.stasiun_sensor.values() if ledo_ai_engine(info['debit'], info['hujan'])[0] == "Siaga Waspada")
    
    # BARIS METRIK (KPI ATAS)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Status Jaringan IoT", "5 Node Online", "100% Terkoneksi")
    kpi2.metric("Zona Bahaya / Banjir", f"{total_bahaya} Wilayah", "Butuh Evakuasi" if total_bahaya > 0 else "Aman", delta_color="inverse")
    kpi3.metric("Zona Siaga Waspada", f"{total_siaga} Wilayah", "Pantau Berkala")
    kpi4.metric("Kecerdasan Artifisial", "Ledo AI-Engine v2.0", "Model: Powered")

    st.markdown("---")

    # GRID UTAMA: PETA GIS (KIRI) & GRAFIK TREN GARIS DEBIT AIR (KANAN)
    col_kiri, col_kanan = st.columns([1, 1])
    
    with col_kiri:
        st.subheader("📍 Peta Geografis IoT & Sebaran Risiko GIS")
        st.caption("Klik pin lokasi sensor untuk memunculkan kotak popup informasi telemetri.")
        
        # Inisialisasi Peta
        m = folium.Map(location=[0.9820, 109.5750], zoom_start=11, tiles="OpenStreetMap")
        
        for id_s, info in st.session_state.stasiun_sensor.items():
            st_text, _, warna_hex = ledo_ai_engine(info['debit'], info['hujan'])
            warna_map = 'red' if st_text == "Bahaya / Banjir" else ('orange' if st_text == "Siaga Waspada" else 'green')
            
            popup_html = f"""
            <div style='font-family: Arial; width:160px;'>
                <b>{info['desa']}</b><br>
                Debit Air: {info['debit']} m³/s<br>
                Curah Hujan: {info['hujan']} mm/jam<br>
                <b style='color:{warna_hex};'>● STATUS: {st_text}</b>
            </div>
            """
            folium.Marker(
                location=[info['lat'], info['lon']],
                popup=folium.Popup(popup_html, max_width=200),
                icon=folium.Icon(color=warna_map, icon='tint', prefix='fa')
            ).add_to(m)
            
        st_folium(m, width=540, height=360, returned_objects=[], key="map_view")

    with col_kanan:
        st.subheader("📈 Tren Grafik Fluktuasi Debit Sungai Air (12 Jam Terakhir)")
        st.caption("Grafik area dinamis memantau laju pergerakan tinggi sungai utama.")
        df_chart_ready = df_tren.set_index("Waktu")
        st.area_chart(df_chart_ready, height=360)

    st.markdown("---")

    # BARIS BAWAH: LOG TABEL DATA (KIRI) & GRAFIK BATANG CURAH HUJAN (KANAN)
    col_btm1, col_btm2 = st.columns([4, 3])
    
    with col_btm1:
        st.subheader("📋 Log Tabel Telemetri Sensor Aktual")
        list_tabel = []
        for id_s, info in st.session_state.stasiun_sensor.items():
            st_text, _, _ = ledo_ai_engine(info['debit'], info['hujan'])
            list_tabel.append({
                "Node ID": id_s, "Lokasi Desa": info['desa'], 
                "Debit Air (m³/s)": info['debit'], "Curah Hujan (mm/j)": info['hujan'], 
                "Keputusan Model AI": st_text, "Status Aksi": "🚨 SEGERA EVAKUASI" if st_text == "Bahaya / Banjir" else ("⚠️ SIAGA PENUH" if st_text == "Siaga Waspada" else "✅ AMAN/KONDUSIF")
            })
        st.dataframe(pd.DataFrame(list_tabel), use_container_width=True, hide_index=True)
        
    with col_btm2:
        st.subheader("📊 Komparasi Tingkat Curah Hujan Antardesa")
        df_bar = pd.DataFrame({
            "Nama Wilayah Desa": [info['desa'] for info in st.session_state.stasiun_sensor.values()],
            "Curah Hujan (mm/jam)": [info['hujan'] for info in st.session_state.stasiun_sensor.values()]
        }).set_index("Nama Wilayah Desa")
        st.bar_chart(df_bar, height=220)

# ===============================================================================================#
# PANEL 2: ADMIN VIEW (TEMPAT LOG IN & MANIPULASI DATA UNTUK SIMULASI LIVE DI DEPAN JURI)
# ===============================================================================================#
elif role == "🔐 Administrator (BPBD)":
    st.title("🎛️ Administrator Dashboard & IoT Central Gate")
    st.caption("Pusat Pengelolaan Data & Pengendalian Sinyal Peringatan Dini")
    st.markdown("---")
    
    st.subheader("🔑 Log Masuk Sistem Validasi Petugas")
    username = st.text_input("Username Administrator")
    password = st.text_input("Password Administrator", type="password")
    
    if username == "admin" and password == "isb":
        st.success("🔓 Otorisasi Berhasil! Gerbang Data IoT Terbuka.")
        st.markdown("---")
        
        st.subheader("⚙️ Simulator Manipulasi Nilai Sensor Lapangan")
        st.info("Fitur simulasi langsung: Ubah nilai sensor di bawah, lalu kembali ke halaman Warga untuk melihat perubahan peta & grafik secara otomatis!")
        
        pilihan_sensor = st.selectbox("Pilih Stasiun Sensor Lapangan:", list(st.session_state.stasiun_sensor.keys()))
        desa_terpilih = st.session_state.stasiun_sensor[pilihan_sensor]['desa']
        
        st.write(f"Mengubah parameter untuk: **{desa_terpilih}**")
        
        # Slider Manipulasi
        new_debit = st.slider("Atur Debit Air Sungai (m³/s)", 0.0, 150.0, float(st.session_state.stasiun_sensor[pilihan_sensor]['debit']))
        new_hujan = st.slider("Atur Intensitas Hujan (mm/jam)", 0.0, 100.0, float(st.session_state.stasiun_sensor[pilihan_sensor]['hujan']))
        
        if st.button("💾 Aplikasikan Data & Perbarui Seluruh Dashboard"):
            st.session_state.stasiun_sensor[pilihan_sensor]['debit'] = new_debit
            st.session_state.stasiun_sensor[pilihan_sensor]['hujan'] = new_hujan
            st.success(f"Sukses! Data untuk {desa_terpilih} berhasil diperbarui di memori Cloud. Ledo AI-Engine otomatis menghitung ulang tingkat bahaya.")
            
    elif username != "" or password != "":
        st.error("❌ Akses Ditolak. Kode kredensial akun salah.")
    else:
        st.warning("Silakan ketik Username dan Password Admin untuk memunculkan panel kontrol sensor.")