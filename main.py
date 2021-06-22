"""Overlay the Laughing Man logo from Ghost in the Shell: SAC on any faces in webcam input,
then pipe the output to a virtual webcam. The logo is animated.

By default, you must press "ESC" to stop the program.

pyfakewebcam requires additional setup https://github.com/jremmons/pyfakewebcam
"""

import numpy
import cv2 as cv
import pyfakewebcam
from PIL import Image

# YOU SHOULD PROBABLY CONFIGURE THESE
INPUT_WEBCAM_NO = 2 # 0 is /dev/video0, 1 is /dev/video1, etc.
VIRTUAL_WEBCAM_PATH = "/dev/video4" # /dev/ path to pyfakewebcam virtual webcam (use v4l2-ctl --list-devices)
FACE_CASCADE_MODEL_PATH = "haarcascade_frontalface_alt.xml"

# YOU PROBABLY DON'T NEED TO TOUCH THESE
EXIT_KEY_ASCII_CODE = 27 # used to set exit keybind. 27 is Escape
VIRTUAL_WEBCAM_WIDTH = 640
VIRTUAL_WEBCAM_HEIGHT = 480

def split_animated_gif(gif_file_path):
    """Split an animated GIF into OpenCV image frames in an array"""
    ret = []
    gif = Image.open(gif_file_path)
    for frame_index in range(gif.n_frames):
        gif.seek(frame_index)
        frame_rgba = gif.convert("RGBA")
        opencv_img = numpy.array(frame_rgba)
        opencv_img = cv.cvtColor(opencv_img, cv.COLOR_RGBA2BGRA)
        ret.append(opencv_img)
    return ret

def detectAndDisplay(frame, frame_no, virtual_webcam):
    """Detects faces in the input frame, overlays the logo, and sends output to the virtual
    webcam as well as cv.imdraw
    """
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.equalizeHist(frame_gray)
    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray)
    for (x,y,w,h) in faces:
        center = (x + w//2, y + h//2)

        logo = laughing_man_frames[frame_no % len(laughing_man_frames)]
        logo = cv.resize(logo, (w + 30, h + 30))
        x_offset=center[0] - w//2
        y_offset=center[1] - h//2 - 30
        y1, y2 = y_offset, y_offset + logo.shape[0]
        x1, x2 = x_offset, x_offset + logo.shape[1]

        logo_alpha = logo[:, :, 3] / 255.0
        frame_alpha = 1.0 - logo_alpha

        try:
            for c in range(0, 3):
                frame[y1:y2, x1:x2, c] = (logo_alpha * logo[:, :, c] +
                                        frame_alpha * frame[y1:y2, x1:x2, c])
        except ValueError: # this happens if we try to draw the logo out of frame, I think. Need more testing
            print("problem", frame_no) # the frame number has nothing to do with the error. it's essentially a timestamp

    cv.imshow("Laughing Man Filter", frame)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    frame = cv.flip(frame, 1) # Discord flips webcam input along Y axis, so we have to flip it back
    virtual_webcam.schedule_frame(frame)

# Load face classifier model
face_cascade = cv.CascadeClassifier()
if not face_cascade.load(cv.samples.findFile(FACE_CASCADE_MODEL_PATH)):
    print("Couldn't load cascade model", FACE_CASCADE_MODEL_PATH)
    exit(0)

# Initialize input webcam
cap = cv.VideoCapture(INPUT_WEBCAM_NO)
if not cap.isOpened:
    print("Couldn't load webcam", INPUT_WEBCAM_NO)
    exit(0)

# Initialize virtual webcam and prepare GIF
virtual_webcam = pyfakewebcam.FakeWebcam(VIRTUAL_WEBCAM_PATH, VIRTUAL_WEBCAM_WIDTH, VIRTUAL_WEBCAM_HEIGHT)
laughing_man_frames = split_animated_gif("laughing_man.gif")
frame_no = 0 # used to keep track of which frame to display next

# Profit
while True:
    ret, frame = cap.read()
    if frame is None:
        print("Failed to get input from webcam", INPUT_WEBCAM_NO)
        break
    frame_no += 1
    detectAndDisplay(frame, frame_no, virtual_webcam)
    if cv.waitKey(10) == EXIT_KEY_ASCII_CODE:
        break
