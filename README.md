# 🕷️ CyberCrawl Spider Robot

**Advanced Quadruped Robot with AI Vision and Autonomous Navigation**

A sophisticated spider robot powered by Raspberry Pi with real-time object detection using YOLOv8, autonomous obstacle avoidance, and manual control capabilities.

---

## ✨ Features

### 🤖 **Autonomous Mode**
- Real-time obstacle detection with ultrasonic sensor
- Intelligent path planning and avoidance
- Stuck detection and escape maneuvers
- Integration with camera-based object recognition

### 🎮 **Manual Control**
- Web-based control interface
- Keyboard controls (Arrow keys / WASD)
- Direction control (Forward, Backward, Left, Right)
- Gesture actions (Wave, Shake, Dance, Stand, Sit)

### 📹 **AI Vision System**
- Live camera streaming (OV5647 Camera Module)
- YOLOv8 real-time object detection
- Bounding box visualization
- FPS monitoring and performance metrics

### 🌐 **Web Interface**
- Modern, responsive design
- Real-time video feed
- Live detection visualization
- System status monitoring
- Touch-friendly mobile controls

---

## 🛠️ Hardware Requirements

### Core Components
- **Raspberry Pi 3 Model B+** (or newer)
- **OV5647 Camera Module** (5MP, 1080p)
- **PCA9685 16-Channel Servo Driver**
- **12x MG90S Servos** (or equivalent)
- **HC-SR04 Ultrasonic Sensor**
- **5V 4A Power Supply** (for servos)

### Optional Components
- IR LEDs for night vision
- LiPo battery pack for mobile operation
- Custom 3D-printed chassis

### Connections
```
PCA9685 → Raspberry Pi:
  - VCC → 3.3V
  - GND → GND
  - SDA → GPIO 2 (Pin 3)
  - SCL → GPIO 3 (Pin 5)

HC-SR04 → Raspberry Pi:
  - VCC → 5V
  - GND → GND
  - TRIG → GPIO 23 (Pin 16)
  - ECHO → GPIO 24 (Pin 18)

OV5647 Camera → CSI Port
```

---

## 💻 Software Requirements

### Operating System
- **Raspberry Pi OS (64-bit)** - Bookworm or newer
- Debian 12+ based

### Python Version
- **Python 3.9+** (comes pre-installed)

### Key Dependencies
- Flask (Web server)
- OpenCV (Image processing)
- YOLOv8/Ultralytics (Object detection)
- picamera2 (Camera interface)
- Adafruit PCA9685 (Servo control)
- RPi.GPIO (GPIO control)

---

## 📦 Installation

### Quick Install (Recommended)

```bash
# Download and run the automated installer
cd ~
git clone https://github.com/yourusername/cybercrawl.git
cd cybercrawl
chmod +x install.sh
./install.sh
```

The installer will:
1. Update system packages
2. Install all dependencies
3. Configure camera and I2C
4. Download YOLO model
5. Create virtual environment
6. Setup systemd service

**⚠️ IMPORTANT:** After installation, **reboot your Raspberry Pi** to enable the camera.

```bash
sudo reboot
```

### Manual Installation

If you prefer manual setup, see [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

---

## 🚀 Usage

### Starting the Robot

1. **Activate virtual environment:**
   ```bash
   cd ~/cybercrawl
   source venv/bin/activate
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Access web interface:**
   - From Raspberry Pi: `http://localhost:5000`
   - From other device: `http://<raspberry-pi-ip>:5000`
   - Find IP: `hostname -I`

### Control Modes

#### 🤖 Auto Mode
1. Click **"Auto Mode"** button
2. Robot will navigate autonomously
3. Avoids obstacles automatically
4. Press **"Stop"** to halt

#### ⚙️ Manual Mode
1. Click **"Manual Mode"** button
2. Use on-screen buttons or keyboard:
   - **Arrow Keys / WASD:** Movement
   - **Space:** Emergency stop
3. Try gesture actions (Wave, Dance, etc.)

---

## 🎮 Keyboard Controls

| Key | Action |
|-----|--------|
| `↑` or `W` | Move Forward |
| `↓` or `S` | Move Backward |
| `←` or `A` | Turn Left |
| `→` or `D` | Turn Right |
| `Space` | Emergency Stop |

*Note: Keyboard controls only work in Manual Mode*

---

## 📁 Project Structure

```
cybercrawl/
├── app.py                      # Main Flask server
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── install.sh                  # Automated installer
│
├── camera/
│   ├── __init__.py
│   └── camera_yolo.py          # Camera + YOLO detection
│
├── movement/
│   ├── __init__.py
│   ├── servo_control.py        # Servo/kinematics control
│   └── auto_walk.py            # Autonomous navigation
│
├── sensors/
│   ├── __init__.py
│   └── ultrasonic.py           # Distance sensor
│
├── templates/
│   └── index.html              # Web interface
│
└── static/
    ├── css/
    │   └── style.css           # Styling
    └── js/
        └── script.js           # Frontend logic
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Camera settings
CAMERA_RESOLUTION = (640, 480)
CAMERA_FPS = 15
CAMERA_ROTATION = 0  # 0, 90, 180, 270

# Detection settings
YOLO_CONFIDENCE_THRESHOLD = 0.5
YOLO_MODEL_PATH = 'yolov8n.pt'

# Obstacle avoidance
OBSTACLE_THRESHOLD = 20  # cm
MAX_DISTANCE = 200       # cm

# Servo calibration
SERVO_PULSE_RANGE = [150, 600]
```

---

## 🔧 Troubleshooting

### Camera Not Working

```bash
# Test camera
rpicam-still -t 0

# Check config
cat /boot/firmware/config.txt | grep camera

# Should see:
# dtoverlay=ov5647
# camera_auto_detect=0
```

### I2C Not Detected

```bash
# Check I2C devices
sudo i2cdetect -y 1

# Should see 0x40 (PCA9685)

# Enable I2C
sudo raspi-config
# Interface Options → I2C → Enable
```

### YOLO Running Slow

- Lower resolution: `CAMERA_RESOLUTION = (320, 240)`
- Reduce FPS: `CAMERA_FPS = 10`
- Use nano model: `YOLO_MODEL_PATH = 'yolov8n.pt'`
- Increase detection interval: `DETECTION_INTERVAL = 0.2`

### Servos Not Moving

- Check power supply (needs 5V 4A minimum)
- Verify I2C connection
- Test individual servos
- Calibrate servo ranges in config.py

### Web Interface Not Loading

```bash
# Check if Flask is running
ps aux | grep python

# Check firewall
sudo ufw allow 5000

# Check server logs
python app.py  # Look for errors
```

---

## 🧪 Testing Components

### Test Camera
```bash
cd ~/cybercrawl
source venv/bin/activate
python -c "from camera.camera_yolo import EnhancedCameraYOLO; c = EnhancedCameraYOLO()"
```

### Test Ultrasonic Sensor
```bash
python -m sensors.ultrasonic
```

### Test Servos
```bash
python -c "from movement.servo_control import SpiderServoController; s = SpiderServoController(); s.stand()"
```

### Test Autonomous Mode
```bash
python -m movement.auto_walk
```

---

## 🚀 Auto-Start on Boot

Enable systemd service:

```bash
sudo cp ~/cybercrawl/cybercrawl.service /etc/systemd/system/
sudo systemctl enable cybercrawl
sudo systemctl start cybercrawl

# Check status
sudo systemctl status cybercrawl

# View logs
sudo journalctl -u cybercrawl -f
```

---

## 📊 Performance Tips

### For Raspberry Pi 3
- Use `yolov8n.pt` (nano model)
- Set `CAMERA_FPS = 10-15`
- Resolution: `640x480` or lower
- Disable desktop: `sudo systemctl set-default multi-user.target`

### For Raspberry Pi 4/5
- Can use `yolov8s.pt` (small model)
- Higher FPS: `20-30`
- Better resolution: `1280x720`

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Ultralytics** for YOLOv8
- **Adafruit** for PCA9685 library
- **Raspberry Pi Foundation** for picamera2
- Inspired by hexapod/quadruped robotics community

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/cybercrawl/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/cybercrawl/discussions)
- **Email:** your.email@example.com

---

## 🎯 Roadmap

- [ ] Add ROS2 integration
- [ ] Implement SLAM mapping
- [ ] Add voice control
- [ ] Mobile app (iOS/Android)
- [ ] Multi-robot coordination
- [ ] Advanced gait patterns
- [ ] Machine learning for terrain adaptation

---

**Made with ❤️ and lots of ☕ by the CyberCrawl Team**

🕷️ Happy Crawling!