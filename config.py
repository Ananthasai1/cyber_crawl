#!/usr/bin/env python3
"""
Configuration settings for CyberCrawl Spider Robot
Optimized for Raspberry Pi 3 with OV5647 Camera (64-bit OS)
"""

# ===== Flask Server Settings =====
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
DEBUG = False

# ===== GPIO Pin Assignments =====
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24
NIGHT_VISION_GPIO = 18  # Optional IR LED control

# ===== PCA9685 Servo Driver Settings =====
PCA9685_ADDRESS = 0x40
PCA9685_FREQUENCY = 50  # Hz (standard for servos)

# ===== Servo Channel Mapping =====
# Leg numbering: 0=Front-Right, 1=Front-Left, 2=Rear-Left, 3=Rear-Right
# Joint numbering: 0=Coxa, 1=Femur, 2=Tibia
SERVO_CHANNELS = [
    [0, 1, 2],    # Leg 0 (Front-Right)
    [4, 5, 6],    # Leg 1 (Front-Left)
    [8, 9, 10],   # Leg 2 (Rear-Left)
    [12, 13, 14]  # Leg 3 (Rear-Right)
]

# ===== Servo Calibration =====
SERVO_PULSE_RANGE = [150, 600]  # Pulse width for 0-180 degrees

# ===== Robot Physical Dimensions (mm) =====
LENGTH_A = 55.0      # Upper leg length
LENGTH_B = 77.5      # Lower leg length
LENGTH_C = 27.5      # Coxa length
LENGTH_SIDE = 71.0   # Body side length

# ===== Movement Parameters =====
Z_DEFAULT = -50.0    # Default standing height
Z_UP = -30.0         # Leg lift height
Z_BOOT = -28.0       # Boot/sit position
X_DEFAULT = 62.0     # Default X position
X_OFFSET = 0.0       # X offset for body
Y_START = 0.0        # Starting Y position
Y_STEP = 40.0        # Step length

# ===== Movement Speeds =====
LEG_MOVE_SPEED = 8.0
BODY_MOVE_SPEED = 3.0
SPOT_TURN_SPEED = 4.0
STAND_SEAT_SPEED = 1.0
SPEED_MULTIPLE = 1.2

# ===== Ultrasonic Sensor Settings =====
OBSTACLE_THRESHOLD = 20  # cm - distance to trigger avoidance
MAX_DISTANCE = 200       # cm - maximum detection range

# ===== Camera Settings (OV5647 Optimized) =====
CAMERA_RESOLUTION = (640, 480)
CAMERA_FPS = 15  # Lower FPS for better stability on RPi 3
CAMERA_WARMUP_TIME = 2  # Seconds to allow camera to adjust
CAMERA_ROTATION = 0  # 0, 90, 180, 270

# ===== YOLOv8 Detection Settings =====
YOLO_MODEL_PATH = 'yolov8n.pt'  # Nano model (fastest)
YOLO_CONFIDENCE_THRESHOLD = 0.5
YOLO_IOU_THRESHOLD = 0.45
YOLO_MAX_DETECTIONS = 10  # Limit for performance

# ===== Performance Settings =====
DETECTION_INTERVAL = 0.1  # Seconds between YOLO inferences
VIDEO_QUALITY = 85  # JPEG quality (1-100)
ENABLE_THREADING = True

# ===== Auto Mode Settings =====
AUTO_MODE_LOOP_DELAY = 0.05  # seconds between sensor readings
AUTO_DETECTION_FREQUENCY = 0.5  # seconds between object checks

# ===== Night Vision Settings =====
NIGHT_VISION_THRESHOLD = 50  # Brightness threshold
ENABLE_NIGHT_VISION = False  # Set to True if IR LEDs are connected