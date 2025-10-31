import cv2
import time
import threading
import sys
import apriltag 
from flask import Response, Flask

# Image frame sent to the Flask object
global video_frame
video_frame = None

# GStreamer Pipeline to access the Raspberry Pi camera
GSTREAMER_PIPELINE = 'nvarguscamerasrc aelock=true ! video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12, framerate=21/1 ! nvvidconv flip-method=0 ! video/x-raw, width=960, height=616, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink wait-on-eos=false max-buffers=1 drop=True'


once_flag = False
# Video capturing from OpenCV
video_capture = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)

while True and video_capture.isOpened():
    return_key, frame = video_capture.read()
    if not return_key:
        break
    cv2.imwrite("test2.jpg", frame)
    break

video_capture.release()
    
