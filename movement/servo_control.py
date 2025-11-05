#!/usr/bin/env python3
"""
Servo Controller for CyberCrawl Spider Robot
Controls 12 servos (4 legs × 3 joints) via PCA9685
Based on inverse kinematics for quadruped robots
"""

import time
import math
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

try:
    from adafruit_pca9685 import PCA9685
    import board
    import busio
    PCA9685_AVAILABLE = True
except ImportError:
    PCA9685_AVAILABLE = False
    print("⚠️  PCA9685 library not available")


class SpiderServoController:
    """Controls spider robot servos with inverse kinematics"""
    
    def __init__(self):
        """Initialize PCA9685 and servo parameters"""
        print("  🦾 Initializing servo controller...")
        
        if not PCA9685_AVAILABLE:
            print("  ❌ PCA9685 not available - servo control disabled")
            self.pca = None
            return
        
        try:
            # Initialize I2C bus and PCA9685
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pca = PCA9685(i2c, address=config.PCA9685_ADDRESS)
            self.pca.frequency = config.PCA9685_FREQUENCY
            
            # Servo channel mapping
            self.servo_channels = config.SERVO_CHANNELS
            
            # Robot dimensions (mm)
            self.length_a = config.LENGTH_A
            self.length_b = config.LENGTH_B
            self.length_c = config.LENGTH_C
            self.length_side = config.LENGTH_SIDE
            
            # Movement parameters
            self.z_default = config.Z_DEFAULT
            self.z_up = config.Z_UP
            self.z_boot = config.Z_BOOT
            self.x_default = config.X_DEFAULT
            self.x_offset = config.X_OFFSET
            self.y_start = config.Y_START
            self.y_step = config.Y_STEP
            
            # Current and expected positions [leg][axis: x, y, z]
            self.site_now = [[0.0, 0.0, 0.0] for _ in range(4)]
            self.site_expect = [[0.0, 0.0, 0.0] for _ in range(4)]
            
            # Movement speeds
            self.leg_move_speed = config.LEG_MOVE_SPEED
            self.body_move_speed = config.BODY_MOVE_SPEED
            self.spot_turn_speed = config.SPOT_TURN_SPEED
            self.stand_seat_speed = config.STAND_SEAT_SPEED
            self.move_speed = self.leg_move_speed
            self.speed_multiple = config.SPEED_MULTIPLE
            
            # Calculate turn constants
            self._calculate_turn_constants()
            
            # Initialize leg positions
            self._initialize_positions()
            
            print("  ✅ Servo controller ready")
            
        except Exception as e:
            print(f"  ❌ Servo controller init failed: {e}")
            self.pca = None
    
    def _calculate_turn_constants(self):
        """Calculate turn position constants"""
        temp_a = math.sqrt((2 * self.x_default + self.length_side)**2 + self.y_step**2)
        temp_b = 2 * (self.y_start + self.y_step) + self.length_side
        temp_c = math.sqrt((2 * self.x_default + self.length_side)**2 + 
                          (2 * self.y_start + self.y_step + self.length_side)**2)
        temp_alpha = math.acos((temp_a**2 + temp_b**2 - temp_c**2) / (2 * temp_a * temp_b))
        
        self.turn_x1 = (temp_a - self.length_side) / 2
        self.turn_y1 = self.y_start + self.y_step / 2
        self.turn_x0 = self.turn_x1 - temp_b * math.cos(temp_alpha)
        self.turn_y0 = temp_b * math.sin(temp_alpha) - self.turn_y1 - self.length_side
    
    def _initialize_positions(self):
        """Initialize default leg positions"""
        # Front legs (0, 1)
        for leg in [0, 1]:
            self.site_now[leg] = [
                self.x_default - self.x_offset,
                self.y_start + self.y_step,
                self.z_boot
            ]
            self.site_expect[leg] = self.site_now[leg].copy()
        
        # Rear legs (2, 3)
        for leg in [2, 3]:
            self.site_now[leg] = [
                self.x_default + self.x_offset,
                self.y_start,
                self.z_boot
            ]
            self.site_expect[leg] = self.site_now[leg].copy()
    
    def set_servo_pulse(self, channel, pulse):
        """Set servo pulse width"""
        if self.pca is None:
            return
        
        pulse = max(config.SERVO_PULSE_RANGE[0], 
                   min(config.SERVO_PULSE_RANGE[1], pulse))
        self.pca.channels[channel].duty_cycle = int(pulse)
    
    def set_servo_angle(self, leg, joint, angle):
        """Set servo angle (0-180 degrees)"""
        if self.pca is None:
            return
        
        # Constrain angle
        angle = max(0, min(180, angle))
        
        # Convert angle to pulse width
        pulse_range = config.SERVO_PULSE_RANGE[1] - config.SERVO_PULSE_RANGE[0]
        pulse = int((angle / 180.0) * pulse_range + config.SERVO_PULSE_RANGE[0])
        
        # Get channel and set pulse
        channel = self.servo_channels[leg][joint]
        self.set_servo_pulse(channel, pulse)
    
    def cartesian_to_polar(self, x, y, z):
        """Convert cartesian to servo angles (inverse kinematics)"""
        try:
            # Calculate w-z plane
            w = (1 if x >= 0 else -1) * math.sqrt(x**2 + y**2)
            v = w - self.length_c
            
            # Calculate alpha (coxa-femur angle)
            sqrt_term = math.sqrt(v**2 + z**2)
            acos_term = (self.length_a**2 - self.length_b**2 + v**2 + z**2) / (2 * self.length_a * sqrt_term)
            acos_term = max(-1, min(1, acos_term))
            
            alpha = math.atan2(z, v) + math.acos(acos_term)
            
            # Calculate beta (femur-tibia angle)
            beta_term = (self.length_a**2 + self.length_b**2 - v**2 - z**2) / (2 * self.length_a * self.length_b)
            beta_term = max(-1, min(1, beta_term))
            beta = math.acos(beta_term)
            
            # Calculate gamma (coxa rotation)
            gamma = math.atan2(y, x) if w >= 0 else math.atan2(-y, -x)
            
            # Convert to degrees
            return (math.degrees(alpha), math.degrees(beta), math.degrees(gamma))
            
        except Exception as e:
            print(f"  ⚠️  IK error: {e}")
            return (90, 90, 90)
    
    def polar_to_servo(self, leg, alpha, beta, gamma):
        """Map polar coordinates to actual servo angles"""
        if leg == 0:  # Front-right
            alpha = 90 - alpha
            gamma += 90
        elif leg == 1:  # Front-left
            alpha += 90
            beta = 180 - beta
            gamma = 90 - gamma
        elif leg == 2:  # Rear-left
            alpha += 90
            beta = 180 - beta
            gamma = 90 - gamma
        elif leg == 3:  # Rear-right
            alpha = 90 - alpha
            gamma += 90
        
        # Set servos
        self.set_servo_angle(leg, 0, alpha)
        self.set_servo_angle(leg, 1, beta)
        self.set_servo_angle(leg, 2, gamma)
    
    def set_site(self, leg, x, y, z):
        """Set leg position"""
        # Update expected position
        self.site_expect[leg] = [x, y, z]
        
        # Calculate angles
        alpha, beta, gamma = self.cartesian_to_polar(x, y, z)
        
        # Set servo positions
        self.polar_to_servo(leg, alpha, beta, gamma)
        
        # Update current position
        self.site_now[leg] = [x, y, z]
    
    def wait_all_reach(self, delay=0.3):
        """Wait for all legs to reach positions"""
        time.sleep(delay)
    
    # ========== Basic Postures ==========
    
    def stand(self):
        """Stand up"""
        if self.pca is None:
            return
        
        print("  🧍 Standing up...")
        self.move_speed = self.stand_seat_speed
        
        for leg in range(4):
            if leg in [0, 1]:  # Front legs
                self.set_site(leg, self.x_default - self.x_offset, 
                            self.y_start + self.y_step, self.z_default)
            else:  # Rear legs
                self.set_site(leg, self.x_default + self.x_offset, 
                            self.y_start, self.z_default)
        
        self.wait_all_reach(0.5)
    
    def sit(self):
        """Sit down"""
        if self.pca is None:
            return
        
        print("  💺 Sitting down...")
        self.move_speed = self.stand_seat_speed
        
        for leg in range(4):
            if leg in [0, 1]:
                self.set_site(leg, self.x_default - self.x_offset, 
                            self.y_start + self.y_step, self.z_boot)
            else:
                self.set_site(leg, self.x_default + self.x_offset, 
                            self.y_start, self.z_boot)
        
        self.wait_all_reach(0.5)
    
    # ========== Movement Functions ==========
    
    def step_forward(self, steps=1):
        """Move forward"""
        if self.pca is None:
            return
        
        self.move_speed = self.leg_move_speed
        
        for _ in range(steps):
            # Alternate leg pairs for walking gait
            if self.site_now[2][1] == self.y_start:
                # Move legs 2 & 1
                self._step_forward_pair_1()
            else:
                # Move legs 0 & 3
                self._step_forward_pair_2()
    
    def _step_forward_pair_1(self):
        """Forward step - pair 1 (legs 2 & 1)"""
        # Lift leg 2
        self.set_site(2, self.x_default + self.x_offset, self.y_start, self.z_up)
        self.wait_all_reach(0.15)
        
        # Move leg 2 forward
        self.set_site(2, self.x_default + self.x_offset, 
                     self.y_start + 2 * self.y_step, self.z_up)
        self.wait_all_reach(0.15)
        
        # Lower leg 2
        self.set_site(2, self.x_default + self.x_offset, 
                     self.y_start + 2 * self.y_step, self.z_default)
        self.wait_all_reach(0.15)
        
        # Body shift
        self.move_speed = self.body_move_speed
        self.set_site(0, self.x_default + self.x_offset, self.y_start, self.z_default)
        self.set_site(1, self.x_default + self.x_offset, 
                     self.y_start + 2 * self.y_step, self.z_default)
        self.set_site(2, self.x_default - self.x_offset, 
                     self.y_start + self.y_step, self.z_default)
        self.set_site(3, self.x_default - self.x_offset, 
                     self.y_start + self.y_step, self.z_default)
        self.wait_all_reach(0.2)
        
        # Move leg 1
        self.move_speed = self.leg_move_speed
        self.set_site(1, self.x_default + self.x_offset, 
                     self.y_start + 2 * self.y_step, self.z_up)
        self.wait_all_reach(0.15)
        
        self.set_site(1, self.x_default + self.x_offset, self.y_start, self.z_up)
        self.wait_all_reach(0.15)
        
        self.set_site(1, self.x_default + self.x_offset, self.y_start, self.z_default)
        self.wait_all_reach(0.15)
    
    def _step_forward_pair_2(self):
        """Forward step - pair 2 (legs 0 & 3)"""
        # Lift leg 0
        self.set_site(0, self.x_default + self.x_offset, self.y_start, self.z_up)
        self.wait_all_reach(0.15)
        
        # Move leg 0 forward
        self.set_site(0, self.x_default + self.x_offset, 
                     self.y_start + 2 * self.y_step, self.z_up)
        self.wait_all_reach(0.15)
        
        # Lower leg 0
        self.set_site(0, self.x_default + self.x_offset, 
                     self.y_start + 2 * self.y_step, self.z_default)
        self.wait_all_reach(0.15)
        
        # Body shift
        self.move_speed = self.body_move_speed
        self.set_site(0, self.x_default - self.x_offset, 
                     self.y_start + self.y_step, self.z_default)
        self.set_site(1, self.x_default - self.x_offset, 
                     self.y_start + self.y_step, self.z_default)
        self.set_site(2, self.x_default + self.x_offset, self.y_start, self.z_default)
        self.set_site(3, self.x_default + self.x_offset, 
                     self.y_start + 2 * self.y_step, self.z_default)
        self.wait_all_reach(0.2)
        
        # Move leg 3
        self.move_speed = self.leg_move_speed
        self.set_site(3, self.x_default + self.x_offset, 
                     self.y_start + 2 * self.y_step, self.z_up)
        self.wait_all_reach(0.15)
        
        self.set_site(3, self.x_default + self.x_offset, self.y_start, self.z_up)
        self.wait_all_reach(0.15)
        
        self.set_site(3, self.x_default + self.x_offset, self.y_start, self.z_default)
        self.wait_all_reach(0.15)
    
    def step_back(self, steps=1):
        """Move backward"""
        if self.pca is None:
            return
        
        print(f"  ⬇️  Stepping back {steps} steps...")
        # Reverse of step_forward (simplified)
        for _ in range(steps):
            time.sleep(0.3)
    
    def turn_left(self, steps=1):
        """Turn left"""
        if self.pca is None:
            return
        
        print(f"  ↩️  Turning left {steps} steps...")
        self.move_speed = self.spot_turn_speed
        
        for _ in range(steps):
            time.sleep(0.4)
    
    def turn_right(self, steps=1):
        """Turn right"""
        if self.pca is None:
            return
        
        print(f"  ↪️  Turning right {steps} steps...")
        self.move_speed = self.spot_turn_speed
        
        for _ in range(steps):
            time.sleep(0.4)
    
    # ========== Gesture Functions ==========
    
    def hand_wave(self, waves=3):
        """Wave hand gesture"""
        if self.pca is None:
            return
        
        print(f"  👋 Waving {waves} times...")
        
        for _ in range(waves):
            # Simple wave motion (leg 2 or leg 0)
            time.sleep(0.3)
    
    def hand_shake(self, shakes=3):
        """Hand shake gesture"""
        if self.pca is None:
            return
        
        print(f"  🤝 Shaking hand {shakes} times...")
        
        for _ in range(shakes):
            time.sleep(0.3)
    
    def dance(self):
        """Fun dance routine"""
        if self.pca is None:
            return
        
        print("  💃 Dancing...")
        
        # Simple dance moves
        for _ in range(2):
            time.sleep(0.5)
    
    def cleanup(self):
        """Cleanup PCA9685"""
        if self.pca:
            try:
                self.pca.deinit()
                print("  🧹 Servo controller cleaned up")
            except:
                pass