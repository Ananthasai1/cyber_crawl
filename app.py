#!/usr/bin/env python3
"""
CyberCrawl Spider Robot - Main Flask Server
Fixed for OV5647 Camera with YOLOv8 Detection
"""

from flask import Flask, render_template, Response, jsonify
import threading
import time
import cv2
import numpy as np
import config

# Import camera module
try:
    from camera.camera_yolo import EnhancedCameraYOLO
    CAMERA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Camera module import failed: {e}")
    CAMERA_AVAILABLE = False

app = Flask(__name__)

# Global variables
current_mode = "STOPPED"
mode_lock = threading.Lock()
camera = None

# Initialize camera
def init_camera():
    """Initialize camera system"""
    global camera
    
    if not CAMERA_AVAILABLE:
        print("❌ Camera module not available")
        return False
    
    try:
        print("📷 Initializing camera system...")
        camera = EnhancedCameraYOLO()
        camera.start_detection()
        print("✅ Camera system ready!")
        return True
    except Exception as e:
        print(f"❌ Camera initialization failed: {e}")
        camera = None
        return False

# Initialize on startup
camera_initialized = init_camera()

# Detection state
detection_state = {
    'auto_detection_active': False,
    'manual_detection_active': False,
}


def generate_frames():
    """Video streaming generator"""
    print("📹 Starting video stream...")
    frame_count = 0
    last_log = time.time()
    
    while True:
        try:
            if camera is None or not camera_initialized:
                # Generate error frame
                frame = np.zeros((config.CAMERA_RESOLUTION[1],
                                config.CAMERA_RESOLUTION[0], 3), dtype=np.uint8)
                cv2.putText(frame, "CAMERA NOT AVAILABLE", (80, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
                cv2.putText(frame, "Check camera connection", (90, 290),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            else:
                # Get frame with detections
                frame = camera.get_frame_with_detections()
                
                if frame is None:
                    # Fallback frame
                    frame = np.zeros((config.CAMERA_RESOLUTION[1],
                                    config.CAMERA_RESOLUTION[0], 3), dtype=np.uint8)
                    cv2.putText(frame, "Waiting for camera...", (100, 240),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2)
            
            # Validate frame
            if frame is None or frame.size == 0:
                time.sleep(0.1)
                continue
            
            # Encode as JPEG
            ret, buffer = cv2.imencode('.jpg', frame,
                                      [cv2.IMWRITE_JPEG_QUALITY, config.VIDEO_QUALITY])
            
            if ret and buffer is not None:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            frame_count += 1
            
            # Log every 5 seconds
            current_time = time.time()
            if current_time - last_log > 5:
                print(f"  📊 Streaming: {frame_count} frames sent")
                last_log = current_time
                frame_count = 0
            
            # Small delay
            time.sleep(0.033)  # ~30 FPS max
            
        except Exception as e:
            print(f"❌ Frame generation error: {e}")
            time.sleep(0.1)


def auto_mode_detection():
    """Detection thread for auto mode"""
    print("🤖 Auto mode detection started")
    detection_state['auto_detection_active'] = True
    
    while current_mode == "AUTO" and detection_state['auto_detection_active']:
        try:
            if camera:
                detections = camera.get_detections()
                
                # Process critical detections
                for det in detections:
                    if det['confidence'] > 0.7:
                        class_name = det['class']
                        critical = ['person', 'cat', 'dog', 'car', 'chair', 'couch']
                        
                        if class_name in critical:
                            print(f"  🎯 Detected: {class_name} ({det['confidence']:.2f})")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ Auto detection error: {e}")
            time.sleep(1)
    
    detection_state['auto_detection_active'] = False
    print("🤖 Auto detection stopped")


def manual_mode_detection():
    """Detection thread for manual mode"""
    print("⚙️ Manual mode detection started")
    detection_state['manual_detection_active'] = True
    
    while current_mode == "MANUAL" and detection_state['manual_detection_active']:
        try:
            if camera:
                detections = camera.get_detections()
                # Just track detections, no action needed
            
            time.sleep(0.2)
            
        except Exception as e:
            print(f"  ❌ Manual detection error: {e}")
            time.sleep(1)
    
    detection_state['manual_detection_active'] = False
    print("⚙️ Manual detection stopped")


# ===== ROUTES =====

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/status')
def get_status():
    """Get robot status"""
    if camera and camera_initialized:
        detections = camera.get_detections()
        stats = camera.get_performance_stats()
        distance = 150.0  # Placeholder (ultrasonic sensor)
    else:
        detections = []
        stats = {'fps': 0, 'detections_count': 0, 'model_loaded': False}
        distance = -1
    
    return jsonify({
        'mode': current_mode,
        'distance': distance,
        'detections': detections,
        'fps': stats.get('fps', 0),
        'detection_count': stats.get('detections_count', 0),
        'model_loaded': stats.get('model_loaded', False),
        'camera_ready': stats.get('camera_ready', False),
        'timestamp': time.time()
    })


@app.route('/api/start_auto', methods=['POST'])
def start_auto():
    """Start autonomous mode"""
    global current_mode
    
    with mode_lock:
        if current_mode != "STOPPED":
            return jsonify({'success': False, 'message': 'Stop current mode first'})
        
        try:
            current_mode = "AUTO"
            print("🚀 Starting AUTO mode...")
            
            # Start detection thread
            auto_thread = threading.Thread(
                target=auto_mode_detection,
                daemon=True,
                name="AutoDetection"
            )
            auto_thread.start()
            
            return jsonify({'success': True, 'message': 'Auto mode started'})
            
        except Exception as e:
            current_mode = "STOPPED"
            return jsonify({'success': False, 'message': str(e)})


@app.route('/api/manual_mode', methods=['POST'])
def manual_mode():
    """Switch to manual mode"""
    global current_mode
    
    with mode_lock:
        if current_mode != "STOPPED":
            return jsonify({'success': False, 'message': 'Stop robot first'})
        
        try:
            current_mode = "MANUAL"
            print("🎮 Starting MANUAL mode...")
            
            # Start detection thread
            manual_thread = threading.Thread(
                target=manual_mode_detection,
                daemon=True,
                name="ManualDetection"
            )
            manual_thread.start()
            
            return jsonify({'success': True, 'message': 'Manual mode activated'})
            
        except Exception as e:
            current_mode = "STOPPED"
            return jsonify({'success': False, 'message': str(e)})


@app.route('/api/stop', methods=['POST'])
def stop():
    """Stop all modes"""
    global current_mode
    
    with mode_lock:
        try:
            print("🛑 Stopping robot...")
            detection_state['auto_detection_active'] = False
            detection_state['manual_detection_active'] = False
            current_mode = "STOPPED"
            
            return jsonify({'success': True, 'message': 'Robot stopped'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})


@app.route('/api/manual_control/<action>', methods=['POST'])
def manual_control(action):
    """Manual control actions"""
    global current_mode
    
    if current_mode != "MANUAL":
        return jsonify({'success': False, 'message': 'Not in manual mode'})
    
    try:
        valid_actions = ['forward', 'backward', 'left', 'right',
                        'wave', 'shake', 'dance', 'stand', 'sit']
        
        if action not in valid_actions:
            return jsonify({'success': False, 'message': 'Unknown action'})
        
        action_icons = {
            'forward': '⬆️', 'backward': '⬇️', 'left': '⬅️', 'right': '➡️',
            'wave': '👋', 'shake': '🤝', 'dance': '💃', 'stand': '🧍', 'sit': '💺'
        }
        
        print(f"  {action_icons.get(action, '▶️')} Action: {action}")
        
        return jsonify({'success': True, 'message': f'Action {action} executed'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/detections')
def get_detections():
    """Get current detections"""
    if camera and camera_initialized:
        detections = camera.get_detections()
    else:
        detections = []
    
    return jsonify({
        'detections': detections,
        'count': len(detections),
        'timestamp': time.time()
    })


@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    if camera and camera_initialized:
        stats = camera.get_performance_stats()
    else:
        stats = {
            'fps': 0,
            'detections_count': 0,
            'model_loaded': False,
            'camera_ready': False,
            'frame_count': 0
        }
    
    return jsonify(stats)


# Cleanup on shutdown
def cleanup():
    """Cleanup on exit"""
    print("\n🧹 Cleaning up...")
    if camera:
        camera.cleanup()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🕷️  CyberCrawl Spider Robot - Control System")
    print("="*70)
    print(f"📷 Camera: {'✅ Ready' if camera_initialized else '❌ Not Available'}")
    print(f"🧠 YOLO: {'✅ Loaded' if camera and camera.model_loaded else '❌ Not Loaded'}")
    print("="*70)
    print("\n🌐 Starting Flask server...")
    print(f"🔗 Access at: http://localhost:{config.SERVER_PORT}")
    print("🔗 Or: http://<raspberry-pi-ip>:5000")
    print("\n🎮 Features:")
    print("   - Live camera stream with YOLOv8 detection")
    print("   - Real-time object detection with bounding boxes")
    print("   - Auto & Manual control modes")
    print("   - FPS counter and performance metrics")
    print("="*70 + "\n")
    
    try:
        app.run(
            host=config.SERVER_HOST,
            port=config.SERVER_PORT,
            debug=config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted by user")
    finally:
        cleanup()