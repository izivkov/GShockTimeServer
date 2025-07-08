#!/bin/bash

echo "== OLED display setup =="

# Update & upgrade
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv zip unzip \
    libfreetype6-dev libjpeg-dev zlib1g-dev libopenjp2-7-dev \
    libtiff5-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev \
    python3-tk p7zip-full wget

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install spidev smbus smbus2 gpiozero numpy luma.oled lgpio pillow

# Download and extract OLED code
wget https://files.waveshare.com/upload/5/53/1.3inch-OLED-HAT-Code.7z
7zr x 1.3inch-OLED-HAT-Code.7z -r -o.
sudo chmod 777 -R 1.3inch-OLED-HAT-Code

# Run the OLED script using the venv python via sudo
cd 1.3inch-OLED-HAT-Code/RaspberryPi/python
python main.py

echo "✅ Display setup complete!"
