#!/usr/bin/env python3
"""
Camera Module for CyberCrawl Spider Robot

This module provides camera functionality with YOLOv8 object detection
for the spider robot. It handles video capture, processing, and 
real-time object detection visualization.

Components:
    - camera_yolo.py: Main camera class with YOLO integration

Usage:
    from camera.camera_yolo import EnhancedCameraYOLO
    
    camera = EnhancedCameraYOLO()
    camera.start_detection()
    
    # Get frame with detections
    frame = camera.get_frame_with_detections()
    
    # Get detection data
    detections = camera.get_detections()
    
    camera.cleanup()
"""

__version__ = "2.0.0"
__author__ = "CyberCrawl Team"

from .camera_yolo import EnhancedCameraYOLO

__all__ = ['EnhancedCameraYOLO']