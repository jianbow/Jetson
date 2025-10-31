import cv2
import time
import threading
import sys
import apriltag 
import numpy
from flask import Response, Flask

# Image frame sent to the Flask object
global video_frame
video_frame = None

# Use locks for thread-safe viewing of frames in multiple browsers
global thread_lock 
thread_lock = threading.Lock()

camera_config = [6330,5298,743,210]


# GStreamer Pipeline to access the Raspberry Pi camera
GSTREAMER_PIPELINE = 'nvarguscamerasrc exposuretimerange="1000 1000" aelock=true ! video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12, framerate=21/1 ! nvvidconv flip-method=0 ! video/x-raw, width=960, height=616, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink wait-on-eos=false max-buffers=1 drop=True'

# Create the Flask object for the application
app = Flask(__name__)

def captureFrames():
    global video_frame, thread_lock
    once_flag = False
    # Video capturing from OpenCV
    print(camera_config)

    video_capture = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
    options = apriltag.DetectorOptions(families="tag36h11", quad_decimate = 2.0, quad_blur = 1.0)
    detector = apriltag.Detector(options)
    while True and video_capture.isOpened():
        return_key, frame = video_capture.read()
        if not return_key:
            break

        # Create a copy of the frame and store it in the global variable,
        # with thread safe access
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # extract the bounding box (x, y)-coordinates for the AprilTag
        # and convert each of the (x, y)-coordinate pairs to integers
        (ptA, ptB, ptC, ptD) = r.corners
        ptB = (int(ptB[0]), int(ptB[1]))
        ptC = (int(ptC[0]), int(ptC[1]))
        ptD = (int(ptD[0]), int(ptD[1]))
        ptA = (int(ptA[0]), int(ptA[1]))

        (cX, cY) = (int(r.center[0]), int(r.center[1]))
        cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)
        # draw the tag family on the image
        tagFamily = r.tag_family.decode("utf-8")
        # _draw_pose(frame, (6330,5298,743,210), )
        fov = 160 #fov for innomakerov9281
        angle=fov*cX/1280
        angle=angle-(1/2)*fov
        angle = str(angle)
        cv2.putText(frame, "Angle:" + angle, (200,200),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        with thread_lock:
            video_frame = frame.copy()
        
        key = cv2.waitKey(30) & 0xff
        if key == 27:
            break

    video_capture.release()
        
def encodeFrame():
    global thread_lock
    while True:
        # Acquire thread_lock to access the global video_frame object
        with thread_lock:
            global video_frame
            if video_frame is None:
                continue
            return_key, encoded_image = cv2.imencode(".jpg", video_frame)
            if not return_key:
                continue

        # Output image as a byte array
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encoded_image) + b'\r\n')

@app.route("/")
def streamFrames():
    return Response(encodeFrame(), mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':

    # Create a thread and attach the method that captures the image frames, to it
    process_thread = threading.Thread(target=captureFrames)
    process_thread.daemon = True

    # Start the thread
    process_thread.start()

    # start the Flask Web Application
    # While it can be run on any feasible IP, IP = 0.0.0.0 renders the web app on
    # the host machine's localhost and is discoverable by other machines on the same network 
    app.run("0.0.0.0", port="8000")
