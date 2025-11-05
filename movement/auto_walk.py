#!/usr/bin/env python3
"""
Autonomous Navigation Module for CyberCrawl Spider Robot
Combines ultrasonic sensor, YOLO detection, and servo control
"""

import time
import random
import threading
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from sensors.ultrasonic import UltrasonicSensor
from movement.servo_control import SpiderServoController


class AutonomousController:
    """Autonomous navigation controller with obstacle avoidance"""
    
    def __init__(self, camera=None):
        """Initialize autonomous controller"""
        print("🤖 Initializing autonomous controller...")
        
        # Components
        self.ultrasonic = UltrasonicSensor()
        self.servo = SpiderServoController()
        self.camera = camera
        
        # State variables
        self.is_running = False
        self.current_state = "IDLE"
        self.obstacle_count = 0
        self.step_count = 0
        
        # Navigation parameters
        self.safe_distance = config.OBSTACLE_THRESHOLD + 10  # cm
        self.critical_distance = config.OBSTACLE_THRESHOLD
        self.stuck_threshold = 5  # attempts before random turn
        
        print("✅ Autonomous controller ready")
    
    def start(self):
        """Start autonomous navigation"""
        if self.is_running:
            print("⚠️  Already running")
            return
        
        print("🚀 Starting autonomous navigation...")
        self.is_running = True
        self.current_state = "EXPLORING"
        
        # Stand up first
        if self.servo.pca:
            self.servo.stand()
            time.sleep(0.5)
        
        # Start navigation thread
        nav_thread = threading.Thread(
            target=self._navigation_loop,
            daemon=True,
            name="AutonomousNav"
        )
        nav_thread.start()
        
        print("✅ Autonomous navigation started")
    
    def stop(self):
        """Stop autonomous navigation"""
        print("🛑 Stopping autonomous navigation...")
        self.is_running = False
        self.current_state = "IDLE"
        
        # Sit down
        if self.servo.pca:
            time.sleep(0.3)
            self.servo.sit()
        
        print("✅ Autonomous navigation stopped")
    
    def _navigation_loop(self):
        """Main navigation loop"""
        print("  🔄 Navigation loop started")
        
        consecutive_obstacles = 0
        last_turn_direction = None
        
        while self.is_running:
            try:
                # Check distance
                distance = self.ultrasonic.get_average_distance(samples=3, delay=0.03)
                
                # Get camera detections if available
                critical_objects = self._check_critical_objects()
                
                # Decision making
                if distance < 0:
                    # Sensor error, proceed cautiously
                    self._handle_sensor_error()
                    consecutive_obstacles = 0
                
                elif distance < self.critical_distance or critical_objects:
                    # Critical - immediate action required
                    print(f"  🔴 CRITICAL: {distance:.1f}cm")
                    self._handle_critical_obstacle(consecutive_obstacles, last_turn_direction)
                    consecutive_obstacles += 1
                    self.obstacle_count += 1
                
                elif distance < self.safe_distance:
                    # Warning - start avoiding
                    print(f"  🟡 WARNING: {distance:.1f}cm")
                    self._handle_warning_obstacle(last_turn_direction)
                    consecutive_obstacles += 1
                
                else:
                    # Safe - move forward
                    if consecutive_obstacles > 0:
                        print(f"  🟢 CLEAR: {distance:.1f}cm - resuming")
                    
                    self._move_forward()
                    consecutive_obstacles = 0
                    last_turn_direction = None
                
                # Check if stuck
                if consecutive_obstacles >= self.stuck_threshold:
                    print("  ⚠️  Stuck detected - executing escape maneuver")
                    self._escape_maneuver()
                    consecutive_obstacles = 0
                
                # Small delay
                time.sleep(config.AUTO_MODE_LOOP_DELAY)
                
            except Exception as e:
                print(f"  ❌ Navigation error: {e}")
                time.sleep(0.5)
        
        print("  🛑 Navigation loop stopped")
    
    def _move_forward(self):
        """Move forward one step"""
        if not self.servo.pca:
            time.sleep(0.3)
            return
        
        self.servo.step_forward(steps=1)
        self.step_count += 1
        
        # Log progress every 10 steps
        if self.step_count % 10 == 0:
            print(f"  📊 Progress: {self.step_count} steps, {self.obstacle_count} obstacles avoided")
    
    def _handle_sensor_error(self):
        """Handle ultrasonic sensor errors"""
        # Move forward cautiously with reduced speed
        if self.servo.pca:
            print("  ⚠️  Sensor error - proceeding cautiously")
            time.sleep(0.5)
    
    def _handle_critical_obstacle(self, consecutive_count, last_direction):
        """Handle critical obstacle (very close)"""
        if not self.servo.pca:
            time.sleep(0.5)
            return
        
        # Stop and back up
        time.sleep(0.2)
        self.servo.step_back(steps=2)
        time.sleep(0.3)
        
        # Decide turn direction
        if consecutive_count >= 3:
            # Stuck - try opposite direction or random
            direction = self._choose_escape_direction(last_direction)
        else:
            # Normal avoidance - alternate or random
            direction = 'right' if last_direction == 'left' else 'left'
            if random.random() < 0.3:  # 30% randomness
                direction = random.choice(['left', 'right'])
        
        # Execute turn
        print(f"  ↩️  Turning {direction}")
        if direction == 'left':
            self.servo.turn_left(steps=2)
        else:
            self.servo.turn_right(steps=2)
        
        time.sleep(0.3)
        return direction
    
    def _handle_warning_obstacle(self, last_direction):
        """Handle warning level obstacle"""
        if not self.servo.pca:
            time.sleep(0.3)
            return
        
        # Slow down and turn slightly
        time.sleep(0.2)
        
        # Decide turn direction
        direction = 'right' if last_direction == 'left' else 'left'
        if random.random() < 0.4:  # 40% randomness
            direction = random.choice(['left', 'right'])
        
        print(f"  ↪️  Minor correction {direction}")
        if direction == 'left':
            self.servo.turn_left(steps=1)
        else:
            self.servo.turn_right(steps=1)
        
        time.sleep(0.2)
        return direction
    
    def _choose_escape_direction(self, last_direction):
        """Choose direction for escape maneuver"""
        # Try opposite of last direction first
        if last_direction == 'left':
            return 'right'
        elif last_direction == 'right':
            return 'left'
        else:
            # Random if no previous direction
            return random.choice(['left', 'right'])
    
    def _escape_maneuver(self):
        """Execute escape maneuver when stuck"""
        if not self.servo.pca:
            time.sleep(1.0)
            return
        
        print("  🔄 Executing escape maneuver...")
        
        # Back up more
        self.servo.step_back(steps=3)
        time.sleep(0.4)
        
        # Random large turn
        direction = random.choice(['left', 'right'])
        steps = random.randint(3, 5)
        
        print(f"  🔀 Large turn {direction} ({steps} steps)")
        if direction == 'left':
            self.servo.turn_left(steps=steps)
        else:
            self.servo.turn_right(steps=steps)
        
        time.sleep(0.5)
        
        # Small forward test
        self.servo.step_forward(steps=1)
        time.sleep(0.3)
    
    def _check_critical_objects(self):
        """Check for critical objects from camera detections"""
        if not self.camera:
            return False
        
        try:
            detections = self.camera.get_detections()
            
            # Check for high-priority obstacles
            critical_classes = ['person', 'dog', 'cat', 'chair', 'couch', 'car']
            
            for det in detections:
                if det['class'] in critical_classes and det['confidence'] > 0.7:
                    # Check if object is centered (in path)
                    center_x = det['center_x']
                    frame_center = config.CAMERA_RESOLUTION[0] / 2
                    
                    # If within center 60% of frame
                    if abs(center_x - frame_center) < frame_center * 0.6:
                        print(f"  🚨 Critical object detected: {det['class']}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"  ⚠️  Detection check error: {e}")
            return False
    
    def get_status(self):
        """Get current status"""
        return {
            'state': self.current_state,
            'is_running': self.is_running,
            'step_count': self.step_count,
            'obstacle_count': self.obstacle_count,
            'ultrasonic_enabled': self.ultrasonic.enabled,
            'servo_enabled': self.servo.pca is not None
        }
    
    def cleanup(self):
        """Cleanup resources"""
        print("  🧹 Cleaning up autonomous controller...")
        self.stop()
        self.ultrasonic.cleanup()
        self.servo.cleanup()


# Test function
def test_autonomous():
    """Test autonomous navigation"""
    print("\n" + "="*60)
    print("🧪 Testing Autonomous Navigation")
    print("="*60 + "\n")
    
    controller = AutonomousController()
    
    if not controller.ultrasonic.enabled:
        print("❌ Ultrasonic sensor not available")
        return
    
    if not controller.servo.pca:
        print("⚠️  Servo controller not available - limited test")
    
    try:
        print("🚀 Starting autonomous mode for 30 seconds...")
        print("Press Ctrl+C to stop\n")
        
        controller.start()
        
        # Run for 30 seconds or until interrupted
        for i in range(30):
            time.sleep(1)
            if i % 5 == 0:
                status = controller.get_status()
                print(f"  📊 Status: {status['step_count']} steps, "
                      f"{status['obstacle_count']} obstacles")
        
        print("\n⏰ Test duration complete")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Test stopped by user")
    finally:
        controller.cleanup()
        print("\n✅ Test complete")


if __name__ == "__main__":
    test_autonomous()