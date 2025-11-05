# ✅ CyberCrawl Setup Verification Guide

Complete checklist to verify your spider robot is properly configured and ready for operation.

---

## 🎯 Purpose

This guide helps you:
- Verify all hardware is connected correctly
- Test each component individually
- Confirm software is working
- Benchmark performance
- Troubleshoot issues before first run

---

## 📋 Hardware Verification Checklist

### 1. Power Supply
- [ ] 5V 4A power supply connected to PCA9685
- [ ] Raspberry Pi powered separately (recommended)
- [ ] All voltage rails stable (check with multimeter if available)
- [ ] No power fluctuations during servo movement

**Test:**
```bash
# Monitor power (if using PiJuice or similar)
vcgencmd get_throttled
# Result: throttled=0x0 (good)
# If throttled: upgrade power supply
```

---

### 2. Camera Module (OV5647)

#### Physical Check
- [ ] Camera ribbon cable firmly seated in CSI port
- [ ] Red stripe on cable faces HDMI port
- [ ] Blue tape removed from lens
- [ ] No visible damage to camera board

#### Software Test
```bash
# Test 1: Basic camera detection
rpicam-still -t 0
# Should show preview. Press Ctrl+C to stop.

# Test 2: Capture test image
rpicam-still -o test.jpg
ls -lh test.jpg
# Should show ~1-3MB file

# Test 3: Check camera info
rpicam-hello --list-cameras
# Should show: "Available cameras" with imx219 or ov5647
```

#### Configuration Check
```bash
cat /boot/firmware/config.txt | grep camera
```

Expected output:
```
dtoverlay=ov5647
camera_auto_detect=0
```

**Status:** 
- [ ] ✅ Camera detected
- [ ] ✅ Test image captured
- [ ] ✅ Configuration correct

---

### 3. I2C Bus (PCA9685)

#### Physical Check
- [ ] VCC → 3.3V (Pin 1)
- [ ] GND → GND (Pin 6)
- [ ] SDA → GPIO 2 (Pin 3)
- [ ] SCL → GPIO 3 (Pin 5)
- [ ] No loose wires
- [ ] Servo power connected separately

#### Software Test
```bash
# Test 1: Detect I2C bus
sudo i2cdetect -y 1
```

Expected output (PCA9685 at 0x40):
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
```

```bash
# Test 2: Python I2C test
python3 << EOF
import board
import busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50
print("✅ PCA9685 initialized successfully")
pca.deinit()
EOF
```

**Status:**
- [ ] ✅ I2C device detected at 0x40
- [ ] ✅ PCA9685 Python initialization successful

---

### 4. Ultrasonic Sensor (HC-SR04)

#### Physical Check
- [ ] VCC → 5V
- [ ] GND → GND
- [ ] TRIG → GPIO 23 (Pin 16)
- [ ] ECHO → GPIO 24 (Pin 18)
- [ ] 1kΩ-2kΩ resistor on ECHO (voltage divider, optional but recommended)

#### Software Test
```bash
cd ~/cybercrawl
source venv/bin/activate
python -m sensors.ultrasonic
```

Expected output:
```
🧪 Testing Ultrasonic Sensor
==================================================

📡 Initializing ultrasonic sensor...
  ✅ Ultrasonic sensor ready (pins 23/24)
📏 Measuring distance (press Ctrl+C to stop)...

🟢 Distance:  45.23 cm | Status: SAFE
🟢 Distance:  42.87 cm | Status: SAFE
🟡 Distance:  35.12 cm | Status: WARNING
```

**Manual Test:**
- [ ] Wave hand in front of sensor
- [ ] Distance reading changes
- [ ] Readings stable (±2cm variation)
- [ ] Range: 2cm - 200cm working

**Status:**
- [ ] ✅ Sensor readings working
- [ ] ✅ Distance changes detected

---

### 5. Servo Motors (12x MG90S)

#### Physical Check
- [ ] All 12 servos connected to PCA9685
- [ ] Servo power (5V) connected
- [ ] Servos numbered correctly (see config.py)
- [ ] No mechanical binding

#### Software Test
```bash
cd ~/cybercrawl
source venv/bin/activate

# Test individual servo
python3 << EOF
from movement.servo_control import SpiderServoController
import time

servo = SpiderServoController()

if servo.pca:
    print("Testing Leg 0, Joint 0 (coxa)...")
    servo.set_servo_angle(0, 0, 45)
    time.sleep(1)
    servo.set_servo_angle(0, 0, 90)
    time.sleep(1)
    servo.set_servo_angle(0, 0, 135)
    print("✅ Servo test complete")
else:
    print("❌ Servo controller not available")

servo.cleanup()
EOF
```

**Manual Test:**
Test each leg:
- [ ] Leg 0 (Front-Right) - Channels 0, 1, 2
- [ ] Leg 1 (Front-Left) - Channels 4, 5, 6
- [ ] Leg 2 (Rear-Left) - Channels 8, 9, 10
- [ ] Leg 3 (Rear-Right) - Channels 12, 13, 14

**Status:**
- [ ] ✅ All servos respond
- [ ] ✅ No jittering or binding
- [ ] ✅ Full range of motion

---

## 💻 Software Verification

### 1. Python Environment

```bash
cd ~/cybercrawl
source venv/bin/activate

# Check Python version
python --version
# Should be: Python 3.9+ or 3.11+

# Check installed packages
pip list | grep -E "Flask|opencv|ultralytics|adafruit"
```

Expected packages:
```
Flask                 3.0.0
opencv-python         4.8.1.78
ultralytics           8.1.0
adafruit-circuitpython-pca9685  3.4.15
```

**Status:**
- [ ] ✅ Python 3.9+
- [ ] ✅ All packages installed

---

### 2. Module Imports

```bash
cd ~/cybercrawl
source venv/bin/activate

python3 << 'EOF'
print("Testing imports...")

try:
    import flask
    print("✅ Flask OK")
except ImportError as e:
    print(f"❌ Flask: {e}")

try:
    import cv2
    print("✅ OpenCV OK")
except ImportError as e:
    print(f"❌ OpenCV: {e}")

try:
    from ultralytics import YOLO
    print("✅ YOLOv8 OK")
except ImportError as e:
    print(f"❌ YOLOv8: {e}")

try:
    from picamera2 import Picamera2
    print("✅ picamera2 OK")
except ImportError as e:
    print(f"❌ picamera2: {e}")

try:
    import RPi.GPIO as GPIO
    print("✅ RPi.GPIO OK")
except ImportError as e:
    print(f"❌ RPi.GPIO: {e}")

try:
    from adafruit_pca9685 import PCA9685
    print("✅ Adafruit PCA9685 OK")
except ImportError as e:
    print(f"❌ PCA9685: {e}")

print("\n✅ All critical imports successful!")
EOF
```

**Status:**
- [ ] ✅ All imports successful

---

### 3. YOLO Model

```bash
cd ~/cybercrawl
ls -lh yolov8n.pt
# Should show ~6MB file

# Test model loading
python3 << 'EOF'
from ultralytics import YOLO
import time

print("Loading YOLO model...")
start = time.time()
model = YOLO('yolov8n.pt')
load_time = time.time() - start
print(f"✅ Model loaded in {load_time:.2f} seconds")

# Test inference
import numpy as np
print("Testing inference...")
dummy = np.zeros((480, 640, 3), dtype=np.uint8)
start = time.time()
results = model(dummy, verbose=False)
inference_time = time.time() - start
print(f"✅ Inference completed in {inference_time:.2f} seconds")
EOF
```

**Expected Performance:**
- Load time: 1-3 seconds (Pi 3), < 1s (Pi 4/5)
- Inference: 0.2-0.5s (Pi 3), < 0.1s (Pi 4/5)

**Status:**
- [ ] ✅ Model file exists
- [ ] ✅ Model loads without errors
- [ ] ✅ Inference working

---

### 4. Component Integration

```bash
cd ~/cybercrawl
source venv/bin/activate

python3 << 'EOF'
print("Testing component integration...\n")

from camera.camera_yolo import EnhancedCameraYOLO
from movement.servo_control import SpiderServoController
from sensors.ultrasonic import UltrasonicSensor
from movement.auto_walk import AutonomousController

# Test camera
print("1. Camera System:")
camera = EnhancedCameraYOLO()
print(f"   Camera ready: {camera.camera_ready}")
print(f"   Model loaded: {camera.model_loaded}")

# Test servo
print("\n2. Servo Controller:")
servo = SpiderServoController()
print(f"   PCA9685 available: {servo.pca is not None}")

# Test sensor
print("\n3. Ultrasonic Sensor:")
sensor = UltrasonicSensor()
print(f"   Sensor enabled: {sensor.enabled}")

# Test autonomous
print("\n4. Autonomous Controller:")
auto = AutonomousController(camera)
status = auto.get_status()
print(f"   Ultrasonic: {status['ultrasonic_enabled']}")
print(f"   Servos: {status['servo_enabled']}")

print("\n✅ All components initialized successfully!")

# Cleanup
camera.cleanup()
servo.cleanup()
sensor.cleanup()
auto.cleanup()
EOF
```

**Status:**
- [ ] ✅ Camera system working
- [ ] ✅ Servo controller working
- [ ] ✅ Ultrasonic sensor working
- [ ] ✅ Autonomous controller working

---

## 🚀 Application Test

### 1. Start Application

```bash
cd ~/cybercrawl
source venv/bin/activate
python app.py
```

Expected output:
```
======================================================================
🕷️  CyberCrawl Spider Robot - Control System
======================================================================
📷 Camera: ✅ Ready
🧠 YOLO: ✅ Loaded
======================================================================

🌐 Starting Flask server...
🔗 Access at: http://localhost:5000
🔗 Or: http://<raspberry-pi-ip>:5000

🎮 Features:
   - Live camera stream with YOLOv8 detection
   - Real-time object detection with bounding boxes
   - Auto & Manual control modes
   - FPS counter and performance metrics
======================================================================
```

**Status:**
- [ ] ✅ Application starts without errors
- [ ] ✅ Server running on port 5000

---

### 2. Web Interface Access

Open browser: `http://<pi-ip>:5000`

**Check:**
- [ ] Page loads completely
- [ ] "CyberCrawl" title visible
- [ ] Status badge shows "STOPPED"
- [ ] Video feed starts (may take 3-5 seconds)
- [ ] FPS counter shows value (10-20 fps)
- [ ] Distance reading appears
- [ ] All buttons visible and clickable

**Status:**
- [ ] ✅ Web interface fully functional

---

### 3. Detection Test

Place objects in camera view:
- [ ] Person detected
- [ ] Cup/bottle detected
- [ ] Phone detected
- [ ] Bounding boxes appear
- [ ] Confidence scores shown
- [ ] Detection count updates

**Status:**
- [ ] ✅ Object detection working

---

### 4. Manual Mode Test

1. Click "Manual Mode" button
2. Try controls:
   - [ ] Forward button works
   - [ ] Backward button works
   - [ ] Left turn works
   - [ ] Right turn works
   - [ ] Keyboard controls work (if servos connected)
   - [ ] Gesture buttons respond

**Status:**
- [ ] ✅ Manual controls functional

---

### 5. Auto Mode Test

**⚠️ Only test if servos and sensor working!**

1. Clear space in front of robot
2. Click "Auto Mode"
3. Robot should:
   - [ ] Stand up
   - [ ] Start moving forward
   - [ ] Detect obstacles
   - [ ] Turn to avoid obstacles
   - [ ] Continue exploring

4. Click "Stop" button

**Status:**
- [ ] ✅ Autonomous navigation working

---

## 📊 Performance Benchmarks

### Camera & Detection

| Metric | Raspberry Pi 3 | Raspberry Pi 4 | Raspberry Pi 5 |
|--------|----------------|----------------|----------------|
| Camera FPS | 10-15 | 20-25 | 25-30 |
| Detection FPS | 5-8 | 10-15 | 15-20 |
| YOLO Load Time | 2-3s | 1-2s | < 1s |
| Inference Time | 0.3-0.5s | 0.1-0.2s | < 0.1s |

**Your Results:**
- Camera FPS: ______
- Detection Count: ______
- YOLO Load Time: ______s
- Inference Time: ______s

---

### Ultrasonic Sensor

| Test | Expected | Your Result |
|------|----------|-------------|
| Min Range | 2 cm | _____ cm |
| Max Range | 200 cm | _____ cm |
| Accuracy | ±1-2 cm | ±_____ cm |
| Update Rate | 10-20 Hz | _____ Hz |

---

### System Resources

```bash
# CPU usage
top -bn1 | grep "Cpu(s)" | awk '{print $2}'

# Memory usage
free -h

# Temperature
vcgencmd measure_temp
```

**Healthy Values:**
- CPU: < 80% average
- Memory: < 80% used
- Temperature: < 70°C under load

**Your System:**
- CPU Usage: _____%
- Memory Used: _____MB / _____MB
- Temperature: _____°C

---

## ✅ Final Checklist

### Hardware
- [ ] Camera module functional
- [ ] I2C communication working
- [ ] Ultrasonic sensor operational
- [ ] All 12 servos responding
- [ ] Power supply stable

### Software
- [ ] All dependencies installed
- [ ] Python environment correct
- [ ] All modules import successfully
- [ ] YOLO model loaded
- [ ] No critical errors in logs

### Application
- [ ] Flask server starts
- [ ] Web interface loads
- [ ] Video feed streaming
- [ ] Object detection working
- [ ] Manual controls responding
- [ ] Auto mode functional (if tested)

### Performance
- [ ] FPS within expected range
- [ ] Detection latency acceptable
- [ ] System temperature normal
- [ ] No throttling warnings

---

## 🎉 Setup Complete!

If all checkboxes are marked ✅:

**Congratulations! Your CyberCrawl Spider Robot is fully operational!** 🕷️

You can now:
1. Experiment with autonomous navigation
2. Customize detection settings
3. Fine-tune servo movements
4. Add new features

---

## 📝 Known Issues & Limitations

### Raspberry Pi 3
- Lower FPS (10-15) is normal
- Use yolov8n.pt (nano model) only
- Consider lowering resolution to 320x240 for better performance

### Camera
- First frame may take 3-5 seconds
- Auto-exposure needs 2-3 seconds warmup
- Low light performance limited (OV5647 limitation)

### Servos
- Jitter possible under low voltage
- Calibration may vary per servo
- Movement speed limited by servo specs

---

## 🔄 Next Steps

1. **Fine-tune Configuration**
   - Edit `config.py` for your setup
   - Calibrate servo ranges
   - Adjust detection thresholds

2. **Test in Real Environment**
   - Try different lighting conditions
   - Test obstacle avoidance
   - Verify range limitations

3. **Customize & Extend**
   - Add new gestures
   - Improve navigation algorithms
   - Integrate additional sensors

---

**Setup verification complete!** Save this document with your test results for future reference.

🕷️ **Happy Crawling!**