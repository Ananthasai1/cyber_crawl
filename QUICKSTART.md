# 🚀 CyberCrawl - Quick Start Guide

Get your spider robot up and running in **30 minutes**!

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Raspberry Pi 3/4/5** with Raspberry Pi OS (64-bit) installed
- ✅ **OV5647 Camera** connected to CSI port
- ✅ **PCA9685 Servo Driver** wired to I2C (SDA/SCL)
- ✅ **HC-SR04 Ultrasonic Sensor** connected to GPIO
- ✅ **Internet connection** (for downloading packages)
- ✅ **SSH access or monitor** connected to Pi

---

## ⚡ 5-Minute Automated Setup

### Step 1: Download the Project

```bash
cd ~
git clone https://github.com/yourusername/cybercrawl.git
cd cybercrawl
```

### Step 2: Run the Installer

```bash
chmod +x install.sh
./install.sh
```

⏳ **Wait 20-30 minutes** for installation to complete.

### Step 3: Reboot

```bash
sudo reboot
```

### Step 4: Start the Robot

```bash
cd ~/cybercrawl
source venv/bin/activate
python app.py
```

### Step 5: Access Web Interface

Open browser: `http://<your-pi-ip>:5000`

Find IP: `hostname -I`

---

## 🔧 Manual Setup (If Automated Fails)

### Step 1: System Update

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Enable Camera

```bash
# For Raspberry Pi OS Bookworm (new):
sudo nano /boot/firmware/config.txt

# For older OS:
sudo nano /boot/config.txt
```

Add these lines:
```
dtoverlay=ov5647
camera_auto_detect=0
```

Save (`Ctrl+O`, `Enter`, `Ctrl+X`) and reboot:
```bash
sudo reboot
```

### Step 3: Enable I2C

```bash
sudo raspi-config
```

Navigate: `Interface Options` → `I2C` → `Enable`

```bash
sudo reboot
```

### Step 4: Install System Dependencies

```bash
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-picamera2 \
    i2c-tools \
    python3-opencv \
    libopencv-dev \
    cmake \
    build-essential
```

### Step 5: Create Project Directory

```bash
cd ~
mkdir cybercrawl
cd cybercrawl
```

Copy all your project files to this directory.

### Step 6: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 7: Install Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏳ This takes 30-60 minutes on Raspberry Pi 3.

### Step 8: Download YOLO Model

```bash
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### Step 9: Test Components

#### Test Camera
```bash
rpicam-still -t 0
```

Press `Ctrl+C` to stop. If you see camera preview, ✅ camera works!

#### Test I2C
```bash
sudo i2cdetect -y 1
```

You should see `40` in the grid (PCA9685 address).

#### Test Python Imports
```bash
python -c "from camera.camera_yolo import EnhancedCameraYOLO; print('✅ Camera module OK')"
python -c "from movement.servo_control import SpiderServoController; print('✅ Servo module OK')"
python -c "from sensors.ultrasonic import UltrasonicSensor; print('✅ Sensor module OK')"
```

### Step 10: Run the Application

```bash
python app.py
```

Look for:
```
📷 Camera: ✅ Ready
🧠 YOLO: ✅ Loaded
🌐 Starting Flask server...
🔗 Access at: http://localhost:5000
```

---

## 🎮 First Run Checklist

### ✅ Web Interface Loading
1. Open `http://<pi-ip>:5000` in browser
2. Should see CyberCrawl interface
3. Video feed should start within 5 seconds

### ✅ Camera Working
- Live video feed visible
- FPS counter showing (10-20 fps)
- "Camera: Ready ✅" in status

### ✅ YOLO Detection
- Place object in view (person, cup, phone)
- Should see bounding boxes appear
- Detection count updates

### ✅ Distance Sensor
- Distance reading should show in cm
- Wave hand in front of sensor
- Reading should change

### ✅ Manual Mode
1. Click "Manual Mode" button
2. Try arrow keys or on-screen buttons
3. Check console for action logs

### ✅ Servo Movement (if connected)
1. Click "Stand" button
2. Robot should stand up
3. Try other gestures

---

## 🐛 Quick Troubleshooting

### Camera Not Working

```bash
# Check camera cable connection
# Red stripe should face HDMI port

# Test camera
rpicam-still -t 0

# If error "Camera not detected":
sudo raspi-config
# Enable camera in Interface Options

# Check config
cat /boot/firmware/config.txt | grep camera
```

### I2C Not Working

```bash
# Check connections:
# SDA → GPIO 2 (Pin 3)
# SCL → GPIO 3 (Pin 5)

# Test I2C
sudo i2cdetect -y 1

# If no devices shown:
sudo raspi-config
# Enable I2C in Interface Options
```

### Video Feed Black Screen

```bash
# Refresh page (Ctrl+F5)
# Check camera permissions
sudo usermod -a -G video $USER

# Restart app
cd ~/cybercrawl
source venv/bin/activate
python app.py
```

### Slow Performance

Edit `config.py`:
```python
CAMERA_RESOLUTION = (320, 240)  # Lower resolution
CAMERA_FPS = 10                 # Lower FPS
DETECTION_INTERVAL = 0.2        # Less frequent detection
```

### Import Errors

```bash
# Activate virtual environment
cd ~/cybercrawl
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Kill existing process
sudo lsof -ti:5000 | xargs kill -9

# Or use different port in config.py
SERVER_PORT = 8080
```

---

## 📱 Access from Phone/Tablet

1. **Find Pi IP address:**
   ```bash
   hostname -I
   ```

2. **Connect phone to same WiFi**

3. **Open browser on phone:**
   ```
   http://192.168.1.XXX:5000
   ```

4. **Add to home screen** for app-like experience

---

## 🔒 Security Tips

### For Local Network Only (Default)
- Already configured in `config.py`:
  ```python
  SERVER_HOST = '0.0.0.0'  # All interfaces
  ```

### For Public Access (Not Recommended)
Add password protection:

```bash
pip install flask-httpauth
```

Edit `app.py` to add authentication.

---

## 🚀 Auto-Start on Boot

Make robot start automatically:

```bash
# Copy service file
sudo cp ~/cybercrawl/cybercrawl.service /etc/systemd/system/

# Enable service
sudo systemctl enable cybercrawl

# Start service
sudo systemctl start cybercrawl

# Check status
sudo systemctl status cybercrawl
```

To disable auto-start:
```bash
sudo systemctl disable cybercrawl
sudo systemctl stop cybercrawl
```

---

## 📊 Monitoring Logs

### Real-time Logs
```bash
# Application logs
cd ~/cybercrawl
source venv/bin/activate
python app.py

# System service logs
sudo journalctl -u cybercrawl -f
```

### Check Errors
```bash
# Last 100 lines
sudo journalctl -u cybercrawl -n 100

# Since boot
sudo journalctl -u cybercrawl -b
```

---

## 🎯 Next Steps

### 1. Calibrate Servos
Edit `config.py`:
```python
SERVO_PULSE_RANGE = [150, 600]  # Adjust if needed
```

Test each servo:
```bash
python -c "from movement.servo_control import SpiderServoController; s = SpiderServoController(); s.set_servo_angle(0, 0, 90)"
```

### 2. Tune Navigation
Adjust in `config.py`:
```python
OBSTACLE_THRESHOLD = 20  # Distance to avoid (cm)
```

### 3. Improve Detection
Try different models:
```python
YOLO_MODEL_PATH = 'yolov8s.pt'  # Slower but more accurate
```

### 4. Customize Interface
Edit files in `templates/` and `static/` directories.

---

## ❓ Still Having Issues?

### Check Setup Status
```bash
cd ~/cybercrawl
python -c "
from camera.camera_yolo import EnhancedCameraYOLO
from movement.servo_control import SpiderServoController
from sensors.ultrasonic import UltrasonicSensor

print('Testing components...')
camera = EnhancedCameraYOLO()
servo = SpiderServoController()
sensor = UltrasonicSensor()
print('✅ All components initialized')
"
```

### Get Help
- Read full [README.md](README.md)
- Check [SETUP_COMPLETE.md](SETUP_COMPLETE.md)
- Open [GitHub Issue](https://github.com/yourusername/cybercrawl/issues)

---

## 🎉 Success!

If you've made it here with:
- ✅ Web interface loading
- ✅ Video feed working
- ✅ Detection working
- ✅ Controls responding

**Congratulations! Your CyberCrawl is ready! 🕷️**

Try:
1. **Auto Mode** - Let it explore autonomously
2. **Manual Mode** - Drive it around with keyboard
3. **Gestures** - Make it wave and dance!

---

**Need more help?** Check [README.md](README.md) for detailed documentation.

🕷️ **Happy Crawling!**