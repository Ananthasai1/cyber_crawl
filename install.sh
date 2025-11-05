#!/bin/bash
# CyberCrawl Spider Robot - Complete Installation Script
# For Raspberry Pi OS 64-bit with OV5647 Camera

set -e  # Exit on error

echo "🕷️  CyberCrawl Spider Robot - Installation"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Please do not run as root (no sudo)${NC}"
    exit 1
fi

# Check if Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}📦 Step 1: Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo -e "${GREEN}🔧 Step 2: Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    i2c-tools \
    git \
    cmake \
    build-essential \
    libopencv-dev \
    python3-opencv \
    python3-picamera2 \
    libcamera-apps

echo ""
echo -e "${GREEN}📷 Step 3: Configuring camera...${NC}"

# Check if camera is already enabled
if ! grep -q "^dtoverlay=ov5647" /boot/firmware/config.txt 2>/dev/null && \
   ! grep -q "^dtoverlay=ov5647" /boot/config.txt 2>/dev/null; then
    
    echo "Enabling OV5647 camera..."
    
    # Try new location first (Bookworm)
    if [ -f /boot/firmware/config.txt ]; then
        echo "dtoverlay=ov5647" | sudo tee -a /boot/firmware/config.txt
        echo "camera_auto_detect=0" | sudo tee -a /boot/firmware/config.txt
    # Fallback to old location
    elif [ -f /boot/config.txt ]; then
        echo "dtoverlay=ov5647" | sudo tee -a /boot/config.txt
        echo "camera_auto_detect=0" | sudo tee -a /boot/config.txt
    fi
    
    echo -e "${GREEN}✅ Camera configuration added${NC}"
    NEED_REBOOT=true
else
    echo -e "${GREEN}✅ Camera already configured${NC}"
fi

echo ""
echo -e "${GREEN}⚙️  Step 4: Enabling I2C...${NC}"

# Enable I2C
sudo raspi-config nonint do_i2c 0

# Add user to i2c group
sudo usermod -a -G i2c $USER

echo -e "${GREEN}✅ I2C enabled${NC}"

echo ""
echo -e "${GREEN}📁 Step 5: Creating project directory...${NC}"

PROJECT_DIR="$HOME/cybercrawl"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory $PROJECT_DIR already exists${NC}"
    read -p "Remove and reinstall? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        rm -rf "$PROJECT_DIR"
    else
        echo "Installation cancelled"
        exit 1
    fi
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create directory structure
echo "Creating directory structure..."
mkdir -p movement sensors camera templates static/css static/js static/images

# Create __init__.py files
touch movement/__init__.py sensors/__init__.py camera/__init__.py

echo ""
echo -e "${GREEN}🐍 Step 6: Creating Python virtual environment...${NC}"

python3 -m venv venv
source venv/bin/activate

echo ""
echo -e "${GREEN}📚 Step 7: Installing Python packages...${NC}"
echo -e "${YELLOW}⏳ This may take 30-60 minutes on Raspberry Pi 3...${NC}"

pip install --upgrade pip

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.0
Werkzeug==3.0.1
RPi.GPIO==0.7.1
smbus2==0.4.3
adafruit-circuitpython-pca9685==3.4.15
adafruit-blinka==8.25.0
opencv-python==4.8.1.78
numpy==1.24.4
ultralytics==8.1.0
Pillow==10.1.0
EOF

pip install -r requirements.txt

echo ""
echo -e "${GREEN}🧠 Step 8: Downloading YOLO model...${NC}"

# Download YOLOv8 nano model
if [ ! -f yolov8n.pt ]; then
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
    echo -e "${GREEN}✅ YOLO model downloaded${NC}"
else
    echo -e "${GREEN}✅ YOLO model already exists${NC}"
fi

echo ""
echo -e "${GREEN}🔍 Step 9: Testing hardware connections...${NC}"

# Test I2C
echo "Testing I2C bus..."
if command -v i2cdetect &> /dev/null; then
    echo "I2C devices detected:"
    sudo i2cdetect -y 1 || true
else
    echo -e "${YELLOW}⚠️  i2cdetect not available${NC}"
fi

# Test camera
echo ""
echo "Testing camera..."
if command -v rpicam-still &> /dev/null; then
    echo "Camera test (3 seconds)..."
    timeout 3 rpicam-still -t 0 --nopreview 2>/dev/null || true
    echo -e "${GREEN}✅ Camera test complete${NC}"
else
    echo -e "${YELLOW}⚠️  rpicam-still not available${NC}"
fi

echo ""
echo -e "${GREEN}📝 Step 10: Creating run scripts...${NC}"

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python app.py
EOF
chmod +x run.sh

# Create systemd service
cat > cybercrawl.service << EOF
[Unit]
Description=CyberCrawl Spider Robot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo ""
echo "=========================================="
echo -e "${YELLOW}📋 IMPORTANT NEXT STEPS:${NC}"
echo "=========================================="
echo ""
echo "1️⃣  Copy your Python files to: $PROJECT_DIR"
echo "   Required files:"
echo "   - app.py"
echo "   - config.py"
echo "   - camera/camera_yolo.py"
echo "   - templates/index.html"
echo "   - static/css/style.css"
echo "   - static/js/script.js"
echo ""

if [ "$NEED_REBOOT" = true ]; then
    echo -e "${RED}2️⃣  REBOOT REQUIRED to enable camera!${NC}"
    echo "   Run: sudo reboot"
    echo ""
fi

echo "3️⃣  After reboot, test the camera:"
echo "   rpicam-still -t 0"
echo ""
echo "4️⃣  Run the application:"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "5️⃣  Access web interface:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "6️⃣  (Optional) Enable auto-start on boot:"
echo "   sudo cp $PROJECT_DIR/cybercrawl.service /etc/systemd/system/"
echo "   sudo systemctl enable cybercrawl"
echo "   sudo systemctl start cybercrawl"
echo ""
echo "=========================================="
echo -e "${GREEN}📚 Troubleshooting:${NC}"
echo "=========================================="
echo ""
echo "Camera not working?"
echo "  - Check connection: rpicam-still -t 0"
echo "  - Verify cable is in CAM port (not DISP)"
echo "  - Check config: cat /boot/firmware/config.txt | grep camera"
echo ""
echo "I2C not working?"
echo "  - Check wiring to PCA9685"
echo "  - Run: sudo i2cdetect -y 1"
echo "  - Should see 0x40"
echo ""
echo "YOLO slow?"
echo "  - Use yolov8n.pt (nano model)"
echo "  - Lower FPS in config.py"
echo "  - Reduce CAMERA_RESOLUTION"
echo ""
echo "🕷️  Happy Crawling!"