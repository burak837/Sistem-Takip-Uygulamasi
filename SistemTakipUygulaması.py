
import tkinter as tk
from tkinter import messagebox
import psutil
import datetime
import sqlite3

# Veritabanı bağlantısı ve tablo oluşturma
conn = sqlite3.connect("veritabani.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sistem_kayitlari (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih TEXT,
        cpu_kullanim REAL,
        ram_kullanim REAL,
        disk_kullanim REAL,
        net_gonderilen REAL,
        net_alinan REAL
    )
""")
conn.commit()

# Sistem verilerini yenileyen fonksiyon
def guncelle():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    net = psutil.net_io_counters()
    gonderilen = round(net.bytes_sent / (1024 * 1024), 2)
    alinan = round(net.bytes_recv / (1024 * 1024), 2)

    cpu_label.config(text=f"CPU Kullanımı: %{cpu}")
    ram_label.config(text=f"RAM Kullanımı: %{ram}")
    disk_label.config(text=f"Disk Kullanımı: %{disk}")
    net_label.config(text=f"Ağ Verisi: Gönderilen: {gonderilen} MB / Alınan: {alinan} MB")

    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_satiri = f"[{tarih}] CPU: %{cpu}, RAM: %{ram}, Disk: %{disk}\n"

    with open("log.txt", "a", encoding="utf-8") as log:
        log.write(log_satiri)

    cursor.execute("""
        INSERT INTO sistem_kayitlari (tarih, cpu_kullanim, ram_kullanim, disk_kullanim, net_gonderilen, net_alinan)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tarih, cpu, ram, disk, gonderilen, alinan))
    conn.commit()

    # Uyarı sistemi
    if cpu > 90 or ram > 90:
        uyari_label.config(text="⚠️ Sistem Yüksek: CPU veya RAM %90 üzeri!", fg="red")
    else:
        uyari_label.config(text="")

    if cpu > 90:
        messagebox.showwarning("CPU Uyarısı", f"⚠️ CPU kullanımı çok yüksek: %{cpu}")
    if ram > 90:
        messagebox.showwarning("RAM Uyarısı", f"⚠️ RAM kullanımı çok yüksek: %{ram}")

# Kayıtları gösteren yeni pencere
def kayitlari_goster():
    pencere2 = tk.Toplevel()
    pencere2.title("Kayıtlı Veriler")
    pencere2.geometry("650x400")

    baslik = tk.Label(pencere2, text="Tarih - CPU - RAM - Disk - Gönderilen - Alınan", font=("Arial", 10, "bold"))
    baslik.pack(pady=5)

    cursor.execute("SELECT tarih, cpu_kullanim, ram_kullanim, disk_kullanim, net_gonderilen, net_alinan FROM sistem_kayitlari ORDER BY id DESC LIMIT 50")
    veriler = cursor.fetchall()

    for kayit in veriler:
        satir = f"{kayit[0]} - %{kayit[1]} - %{kayit[2]} - %{kayit[3]} - {kayit[4]} MB - {kayit[5]} MB"
        etiket = tk.Label(pencere2, text=satir, font=("Arial", 10))
        etiket.pack(anchor="w", padx=10)

# Rapor gösteren pencere
def rapor_al():
    cursor.execute("""
        SELECT AVG(cpu_kullanim) FROM (
            SELECT cpu_kullanim FROM sistem_kayitlari ORDER BY id DESC LIMIT 50
        )
    """)
    ortalama = cursor.fetchone()[0]
    ortalama = round(ortalama, 2) if ortalama else 0.0

    messagebox.showinfo("Ortalama CPU Kullanımı", f"📊 Son 50 kaydın ortalama CPU kullanımı: %{ortalama}")

# Ana pencere
pencere = tk.Tk()
pencere.title("Sistem Takip ve Destek Otomasyonu")
pencere.geometry("400x370")

cpu_label = tk.Label(pencere, text="CPU Kullanımı: ...", font=("Arial", 12))
cpu_label.pack(pady=5)

ram_label = tk.Label(pencere, text="RAM Kullanımı: ...", font=("Arial", 12))
ram_label.pack(pady=5)

disk_label = tk.Label(pencere, text="Disk Kullanımı: ...", font=("Arial", 12))
disk_label.pack(pady=5)

net_label = tk.Label(pencere, text="Ağ Verisi: ...", font=("Arial", 12))
net_label.pack(pady=5)

guncelle_btn = tk.Button(pencere, text="Verileri Güncelle", command=guncelle)
guncelle_btn.pack(pady=10)

goruntule_btn = tk.Button(pencere, text="Kayıtları Göster", command=kayitlari_goster)
goruntule_btn.pack(pady=5)

rapor_btn = tk.Button(pencere, text="📊 Rapor Al (Ortalama CPU)", command=rapor_al)
rapor_btn.pack(pady=5)

uyari_label = tk.Label(pencere, text="", font=("Arial", 12, "bold"))
uyari_label.pack(pady=5)

pencere.mainloop()
