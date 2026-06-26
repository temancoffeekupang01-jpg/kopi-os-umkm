import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 1. KONFIGURASI HALAMAN & TEMA
st.set_page_config(page_title="TITIK KOMA COFFEE - OS", layout="wide")

# Gaya CSS Custom untuk mempercantik tampilan seperti aplikasi profesional
st.markdown(body="""
    <style>
    .card-penjualan { background-color: #00c853; color: white; padding: 20px; border-radius: 10px; }
    .card-profit { background-color: #00b0ff; color: white; padding: 20px; border-radius: 10px; }
    .card-pengeluaran { background-color: #ff9100; color: white; padding: 20px; border-radius: 10px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allowed_html=True)


# 2. DATABASE SIMULASI (SESSION STATE)
if 'transactions' not in st.session_state:
    st.session_state.transactions = [
        {"Waktu": "14:54", "Produk": "Butterscout, Renjana", "Qty": 2, "Total": 24000, "Modal": 10000, "Tipe": "Tunai"},
        {"Waktu": "14:35", "Produk": "Renjana, Kahwa, Sakala", "Qty": 3, "Total": 102000, "Modal": 40000, "Tipe": "Tunai"},
        {"Waktu": "12:46", "Produk": "Americano", "Qty": 1, "Total": 8000, "Modal": 3000, "Tipe": "QRIS"}
    ]

if 'menu_kopi' not in st.session_state:
    st.session_state.menu_kopi = [
        {"Produk": "Americano", "Harga": 8000, "Modal": 3000, "Stok": 1, "Kategori": "COFFEE", "Foto": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400"},
        {"Produk": "Renjana", "Harga": 11000, "Modal": 4000, "Stok": 7, "Kategori": "SIGNATURE", "Foto": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400"},
        {"Produk": "Kahwa", "Harga": 10000, "Modal": 3500, "Stok": 2, "Kategori": "SIGNATURE", "Foto": "https://images.unsplash.com/photo-1541167760496-1628856ab772?w=400"},
        {"Produk": "Caramel Latte", "Harga": 13000, "Modal": 5000, "Stok": 1, "Kategori": "PREMIUM", "Foto": "https://images.unsplash.com/photo-1534778101976-62847782c213?w=400"}
    ]

# 3. SIDEBAR NAVIGASI
st.sidebar.title("🏪 TITIK KOMA COFFEE")
st.sidebar.write("📍 Jl. Sesawi No. 22")
menu = st.sidebar.radio("AKSES CEPAT", ["🏠 Halaman Utama (Dashboard)", "🛒 Kasir (POS)", "📦 Produk & Stok", "📊 Laporan Detail"])

# ==========================================
# MENU 1: HALAMAN UTAMA (DASHBOARD)
# ==========================================
if menu == "🏠 Halaman Utama (Dashboard)":
    st.title("Jumat, 26 Juni 2026")
    st.subheader("TITIK KOMA COFFEE")
    
    # Hitung Statistik harian
    df_tx = pd.DataFrame(st.session_state.transactions)
    total_penjualan = df_tx["Total"].sum() if not df_tx.empty else 0
    total_modal = df_tx["Modal"].sum() if not df_tx.empty else 0
    profit = total_penjualan - total_modal
    
    # Baris Kartu Ringkasan (Mewah)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='card-penjualan'><h5>Penjualan Hari Ini</h5><h2>Rp {total_penjualan:,}</h2><p>{len(df_tx)} Transaksi</p></div>", unsafe_allowed_html=True)
    with col2:
        st.markdown(f"<div class='card-profit'><h5>Profit Hari Ini</h5><h2>Rp {profit:,}</h2><p>Bersih</p></div>", unsafe_allowed_html=True)
    with col3:
        st.markdown("<div class='card-pengeluaran'><h5>Pengeluaran Hari Ini</h5><h2>Rp 0</h2><p>0 Catatan</p></div>", unsafe_allowed_html=True)
        
    st.write("---")
    
    # Live Notifikasi Stok Menipis (Seperti di Video)
    st.subheader("⚠️ Stok Menipis")
    for item in st.session_state.menu_kopi:
        if item["Stok"] <= 2:
            st.error(f"🔴 **{item['Produk']}** — Sisa {item['Stok']} cup")

    st.write("---")
    st.subheader("🧾 Transaksi Terakhir")
    if not df_tx.empty:
        st.dataframe(df_tx[["Waktu", "Produk", "Total", "Tipe"]], use_container_width=True)

# ==========================================
# MENU 2: KASIR (POS DENGAN FOTO)
# ==========================================
elif menu == "🛒 Kasir (POS)":
    st.title("🛒 Sistem Kasir Digital")
    
    # Tampilan Grid Menu Berjejer dengan Foto Produk
    st.subheader("Menu Kasir")
    
    # Bagi layout menjadi kolom untuk menampilkan produk berbentuk Grid
    cols = st.columns(4)
    for index, item in enumerate(st.session_state.menu_kopi):
        with cols[index % 4]:
            st.image(item["Foto"], use_container_width=True)
            st.write(f"**{item['Produk']}**")
            st.caption(f"Harga: Rp {item['Harga']:,} | Stok: {item['Stok']}")
            
            if st.button(f"Tambah {item['Produk']}", key=f"btn_{index}"):
                if item["Stok"] > 0:
                    item["Stok"] -= 1
                    st.session_state.transactions.append({
                        "Waktu": datetime.now().strftime("%H:%M"),
                        "Produk": item["Produk"],
                        "Qty": 1,
                        "Total": item["Harga"],
                        "Modal": item["Modal"],
                        "Tipe": "Tunai"
                    })
                    st.success(f"{item['Produk']} ditambahkan ke keranjang!")
                    st.rerun()
                else:
                    st.error("Stok Habis!")

# ==========================================
# MENU 3: PRODUK & STOK
# ==========================================
elif menu == "📦 Produk & Stok":
    st.title("📦 Master Data & Stok Produk")
    df_prod = pd.DataFrame(st.session_state.menu_kopi)
    st.dataframe(df_prod[["Produk", "Kategori", "Harga", "Modal", "Stok"]], use_container_width=True)
    
    st.write("---")
    st.subheader("Tambah Produk / Tambah Stok Baru")
    with st.form("form_produk"):
        nama = st.text_input("Nama Produk Kopi")
        kat = st.selectbox("Kategori", ["COFFEE", "SIGNATURE COFFEE", "PREMIUM COFFEE", "NON-COFFEE"])
        harga_jual = st.number_input("Harga Jual (Rp)", min_value=0, step=1000)
        harga_modal = st.number_input("Harga Modal/HPP (Rp)", min_value=0, step=1000)
        jumlah_stok = st.number_input("Jumlah Stok Awal", min_value=0, step=1)
        
        if st.form_submit_button("Simpan Produk"):
            st.session_state.menu_kopi.append({
                "Produk": nama, "Harga": harga_jual, "Modal": harga_modal, 
                "Stok": jumlah_stok, "Kategori": kat, 
                "Foto": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400"
            })
            st.success("Produk baru berhasil didaftarkan!")
            st.rerun()

# ==========================================
# MENU 4: LAPORAN DETAIL
# ==========================================
elif menu == "📊 Laporan Detail":
    st.title("📊 Laporan Penjualan & Closing")
    
    tab1, tab2 = st.tabs(["Harian", "Analisis Grafik"])
    
    df_tx = pd.DataFrame(st.session_state.transactions)
    
    with tab1:
        st.date_input("Tanggal Laporan", datetime.now())
        if st.button("🖨️ Cetak Laporan Closing", type="primary"):
            st.success("Laporan berhasil dikirim ke printer kasir / diunduh!")
            
        st.write("---")
        if not df_tx.empty:
            st.dataframe(df_tx, use_container_width=True)
        else:
            st.info("Belum ada transaksi.")
            
    with tab2:
        if not df_tx.empty:
            st.subheader("Grafik Omzet Hari Ini")
            fig, ax = plt.subplots(figsize=(6, 2.5))
            ax.bar(df_tx["Waktu"], df_tx["Total"], color="#00b0ff")
            ax.set_ylabel("Rupiah (Rp)")
            ax.set_xlabel("Jam Transaksi")
            st.pyplot(fig)
        else:
            st.info("Data belum cukup untuk membuat grafik.")

