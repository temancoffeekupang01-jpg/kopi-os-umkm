import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Coffee Shop Management OS", layout="wide", initial_sidebar_state="expanded")

# --- DATABASE SIMULASI (SESSION STATE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
if 'inventory' not in st.session_state:
    st.session_state.inventory = [
        {"Bahan": "Bijih Kopi Houseblend", "Stok": 15.0, "Satuan": "kg"},
        {"Bahan": "Susu Fresh Milk", "Stok": 24.0, "Satuan": "Liter"},
        {"Bahan": "Sirup Karamel", "Stok": 5.0, "Satuan": "Botol"}
    ]
if 'menu' not in st.session_state:
    st.session_state.menu = [
        {"Produk": "Es Kopi Susu Gula Aren", "Harga": 22000, "Modal": 8000},
        {"Produk": "Caramel Latte", "Harga": 28000, "Modal": 11000},
        {"Produk": "Manual Brew V60", "Harga": 25000, "Modal": 6000}
    ]
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# --- SISTEM LOGIN BERBASIS PERAN ---
if not st.session_state.authenticated:
    st.title("🔐 Coffee OS - Login System")
    st.write("Silakan masuk menggunakan kredensial akun Anda.")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Pilih Peran", ["Pemilik (Owner)", "Barista"])
    
    if st.button("Login", use_container_width=True):
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.role = role
            st.success(f"Selamat datang, {role}!")
            st.rerun()
        else:
            st.error("Username atau password salah!")
    st.stop()

# --- SIDEBAR LOGOUT & INFO ---
st.sidebar.title("☕ EspressoOS v1.0")
st.sidebar.write(f"Peran Anda: **{st.session_state.role}**")
if st.sidebar.button("Log Out", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.role = None
    st.rerun()

# --- MENU UTAMA BERDASARKAN PERAN ---
if st.session_state.role == "Pemilik (Owner)":
    menu_options = ["📊 Dashboard & Laporan Analitik", "📦 Inventory & Stock Control", "🧾 Sistem Kasir (POS)", "🔥 Roasting Monitor", "⏳ Smart Brew Guide"]
else: # Barista
    menu_options = ["🧾 Sistem Kasir (POS)", "⏳ Smart Brew Guide", "🔥 Roasting Monitor", "📦 Inventory & Stock Control"]

choice = st.sidebar.radio("Navigasi Menu", menu_options)

# ==========================================
# 1. DASHBOARD & LAPORAN ANALITIK (Owner Only)
# ==========================================
if choice == "📊 Dashboard & Laporan Analitik":
    st.title("📊 Dashboard & Laporan Analitik Real-Time")
    
    df_tx = pd.DataFrame(st.session_state.transactions)
    total_sales = df_tx["Total"].sum() if not df_tx.empty else 0
    total_qty = df_tx["Qty"].sum() if not df_tx.empty else 0
    total_profit = (df_tx["Total"] - df_tx["Total Modal"]).sum() if not df_tx.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pendapatan", f"Rp {total_sales:,}")
    col2.metric("Total Produk Terjual", f"{total_qty} Cups")
    col3.metric("Estimasi Keuntungan Bersih", f"Rp {total_profit:,}")
    
    st.subheader("📝 Histori Transaksi Penjualan")
    if not df_tx.empty:
        st.dataframe(df_tx, use_container_width=True)
        
        csv = df_tx.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Ekspor Laporan ke CSV",
            data=csv,
            file_name=f"Laporan_Penjualan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
    else:
        st.info("Belum ada data transaksi masuk hari ini.")

# ==========================================
# 2. INVENTORY & STOCK CONTROL
# ==========================================
elif choice == "📦 Inventory & Stock Control":
    st.title("📦 Manajemen Inventaris & Resep Modal")
    
    tab1, tab2 = st.tabs(["Stok Bahan Baku", "Manajemen Harga & Modal Resep"])
    
    with tab1:
        st.subheader("Persediaan Gudang")
        df_inv = pd.DataFrame(st.session_state.inventory)
        st.table(df_inv)
        
        if st.session_state.role == "Pemilik (Owner)":
            st.write("---")
            st.caption("Update/Tambah Stok Baru")
            with st.form("tambah_stok"):
                nama_bahan = st.text_input("Nama Bahan Baku")
                jumlah = st.number_input("Jumlah", min_value=0.0, step=0.1)
                satuan = st.text_input("Satuan (kg/Liter/Botol)")
                if st.form_submit_button("Simpan Ke Gudang"):
                    st.session_state.inventory.append({"Bahan": nama_bahan, "Stok": jumlah, "Satuan": satuan})
                    st.success(f"{nama_bahan} berhasil diperbarui!")
                    st.rerun()

    with tab2:
        st.subheader("Harga Jual vs Estimasi Modal Produk")
        df_menu = pd.DataFrame(st.session_state.menu)
        st.dataframe(df_menu, use_container_width=True)

# ==========================================
# 3. SISTEM KASIR (POS)
# ==========================================
elif choice == "🧾 Sistem Kasir (POS)":
    st.title("🧾 Sistem Kasir Penjualan (POS)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Pilih Menu Pesanan")
        selected_product = st.selectbox("Nama Menu", [p["Produk"] for p in st.session_state.menu])
        qty = st.number_input("Jumlah (Qty)", min_value=1, step=1)
        
        prod_detail = next(p for p in st.session_state.menu if p["Produk"] == selected_product)
        total_harga = prod_detail["Harga"] * qty
        total_modal = prod_detail["Modal"] * qty
        
        st.write(f"Harga Satuan: **Rp {prod_detail['Harga']:,}**")
        st.markdown(f"### Subtotal: **Rp {total_harga:,}**")
        
    with col2:
        st.subheader("Pembayaran")
        bayar = st.number_input("Nominal Uang Tunai (Rp)", min_value=0, step=1000)
        kembalian = bayar - total_harga
        
        if bayar > 0:
            if kembalian >= 0:
                st.success(f"Kembalian: **Rp {kembalian:,}**")
            else:
                st.error(f"Uang kurang: **Rp {abs(kembalian):,}**")
                
        if st.button("PROSES TRANSAKSI & CETAK", use_container_width=True, type="primary"):
            if bayar >= total_harga:
                st.session_state.transactions.append({
                    "Waktu": datetime.now().strftime("%H:%M:%S"),
                    "Produk": selected_product,
                    "Qty": qty,
                    "Total": total_harga,
                    "Total Modal": total_modal
                })
                st.balloons()
                st.success("Transaksi Sukses Tercatat!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Gagal! Uang pembayaran belum mencukupi.")

# ==========================================
# 4. ROASTING MONITOR (With Live Charts)
# ==========================================
elif choice == "🔥 Roasting Monitor":
    st.title("🔥 Roasting Profile Monitor & Logger")
    st.write("Pantau pergerakan grafik suhu mesin Roasting secara Real-Time.")
    
    col_btn1, col_btn2 = st.columns(2)
    start_roast = col_btn1.button("🟢 Mulai Proses Roasting", use_container_width=True)
    
    chart_placeholder = st.empty()
    log_placeholder = st.empty()
    
    if start_roast:
        suhu_logs = []
        waktu_logs = []
        
        for t in range(0, 61, 5):
            waktu_logs.append(t)
            temp = 100 + (100 / (1 + np.exp(-(t-30)/10))) + np.random.normal(0, 2)
            suhu_logs.append(temp)
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(waktu_logs, suhu_logs, marker='o', color='#ff4b4b', label='Suhu Bean (°C)')
            ax.set_title("Kurva Suhu Roasting Real-Time")
            ax.set_xlabel("Waktu (Detik)")
            ax.set_ylabel("Suhu (°C)")
            ax.grid(True, linestyle='--')
            ax.legend()
            
            chart_placeholder.pyplot(fig)
            plt.close(fig)
            
            log_placeholder.caption(f"Detik ke-{t}: Suhu saat ini **{temp:.1f}°C**")
            time.sleep(0.4)
        st.success("🔥 Proses Roasting Selesai! Data Log Profil Berhasil Dikunci.")

# ==========================================
# 5. SMART BREW GUIDE (Timer Modul Barista)
# ==========================================
elif choice == "⏳ Smart Brew Guide":
    st.title("⏳ Smart Brew Guide & Pouring Timer")
    st.write("Panduan menyeduh kopi filter konvensional (V60 / Kalita Wave) langkah demi langkah.")
    
    metode = st.selectbox("Pilih Profil Seduh", ["V60 Fruity Sweet (1:15)", "V60 Bold Body (1:12)"])
    st.info("💡 **Instruksi**: Siapkan server, basahi paper filter, masukkan 15g bubuk kopi. Klik tombol di bawah.")
    
    if st.button("🚀 MULAI TIMER MENYEDUH", use_container_width=True):
        progress_bar = st.progress(0)
        
        st.subheader("🌊 Tahap 1: Blooming (30 Detik)")
        for i in range(1, 31):
            progress_bar.progress(int((i/90)*100))
            time.sleep(0.1)
            
        st.subheader("☕ Tahap 2: Tuangan Kedua & Akhir (60 Detik)")
        for i in range(31, 91):
            progress_bar.progress(int((i/90)*100))
            time.sleep(0.1)
            
        st.balloons()
        st.success("🏁 Proses Seduh Selesai! Kopi Siap Disajikan Ke Pelanggan.")
