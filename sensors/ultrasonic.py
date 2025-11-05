#!/usr/bin/env python3
"""
Ultrasonic Distance Sensor Module for CyberCrawl
HC-SR04 Sensor with obstacle detection
"""

import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO not available")


class UltrasonicSensor:
    """HC-SR04 Ultrasonic Distance Sensor"""
    
    def __init__(self, trigger_pin=None, echo_pin=None):
        """Initialize ultrasonic sensor"""
        print("  📡 Initializing ultrasonic sensor...")
        
        self.trigger_pin = trigger_pin or config.ULTRASONIC_TRIGGER_PIN
        self.echo_pin = echo_pin or config.ULTRASONIC_ECHO_PIN
        self.max_distance = config.MAX_DISTANCE
        self.obstacle_threshold = config.OBSTACLE_THRESHOLD
        
        if not GPIO_AVAILABLE:
            print("  ❌ GPIO not available - sensor disabled")
            self.enabled = False
            return
        
        try:
            # Setup GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup pins
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            
            # Initialize trigger to low
            GPIO.output(self.trigger_pin, False)
            time.sleep(0.1)
            
            self.enabled = True
            print(f"  ✅ Ultrasonic sensor ready (pins {self.trigger_pin}/{self.echo_pin})")
            
        except Exception as e:
            print(f"  ❌ Sensor initialization failed: {e}")
            self.enabled = False
    
    def measure_distance(self, timeout=0.05):
        """
        Measure distance in centimeters
        
        Args:
            timeout: Maximum time to wait for echo (seconds)
        
        Returns:
            float: Distance in cm, or -1 if error
        """
        if not self.enabled:
            return -1
        
        try:
            # Send 10us pulse
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(self.trigger_pin, False)
            
            # Wait for echo start
            pulse_start = time.time()
            timeout_start = pulse_start
            
            while GPIO.input(self.echo_pin) == 0:
                pulse_start = time.time()
                if pulse_start - timeout_start > timeout:
                    return -1
            
            # Wait for echo end
            pulse_end = time.time()
            timeout_start = pulse_end
            
            while GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()
                if pulse_end - timeout_start > timeout:
                    return -1
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound = 343 m/s
            distance = round(distance, 2)
            
            # Validate distance
            if distance < 2 or distance > self.max_distance:
                return -1
            
            return distance
            
        except Exception as e:
            print(f"  ❌ Measurement error: {e}")
            return -1
    
    def get_average_distance(self, samples=3, delay=0.05):
        """
        Get average distance over multiple measurements
        
        Args:
            samples: Number of measurements to average
            delay: Delay between measurements
        
        Returns:
            float: Average distance in cm
        """
        if not self.enabled:
            return -1
        
        valid_readings = []
        
        for _ in range(samples):
            distance = self.measure_distance()
            if distance > 0:
                valid_readings.append(distance)
            time.sleep(delay)
        
        if not valid_readings:
            return -1
        
        return round(sum(valid_readings) / len(valid_readings), 2)
    
    def is_obstacle_detected(self, distance=None):
        """
        Check if obstacle is within threshold
        
        Args:
            distance: Pre-measured distance (optional)
        
        Returns:
            bool: True if obstacle detected
        """
        if distance is None:
            distance = self.measure_distance()
        
        if distance < 0:
            return False
        
        return distance < self.obstacle_threshold
    
    def get_obstacle_severity(self, distance=None):
        """
        Get obstacle severity level
        
        Args:
            distance: Pre-measured distance (optional)
        
        Returns:
            str: 'safe', 'warning', 'danger', or 'critical'
        """
        if distance is None:
            distance = self.measure_distance()
        
        if distance < 0:
            return 'unknown'
        
        if distance < 10:
            return 'critical'
        elif distance < 20:
            return 'danger'
        elif distance < 50:
            return 'warning'
        else:
            return 'safe'
    
    def cleanup(self):
        """Cleanup GPIO"""
        if self.enabled and GPIO_AVAILABLE:
            try:
                GPIO.cleanup([self.trigger_pin, self.echo_pin])
                print("  🧹 Ultrasonic sensor cleaned up")
            except:
                pass


# Test function
def test_sensor():
    """Test ultrasonic sensor"""
    print("\n" + "="*50)
    print("🧪 Testing Ultrasonic Sensor")
    print("="*50 + "\n")
    
    sensor = UltrasonicSensor()
    
    if not sensor.enabled:
        print("❌ Sensor not available")
        return
    
    try:
        print("📏 Measuring distance (press Ctrl+C to stop)...\n")
        
        while True:
            distance = sensor.get_average_distance(samples=3)
            
            if distance > 0:
                severity = sensor.get_obstacle_severity(distance)
                
                # Emoji indicators
                if severity == 'critical':
                    emoji = '🔴'
                elif severity == 'danger':
                    emoji = '🟠'
                elif severity == 'warning':
                    emoji = '🟡'
                else:
                    emoji = '🟢'
                
                print(f"{emoji} Distance: {distance:6.2f} cm | Status: {severity.upper()}")
            else:
                print("⚠️  Out of range or error")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Test stopped")
    finally:
        sensor.cleanup()


if __name__ == "__main__":
    test_sensor()