# Laughing Man Filter
![Laughing Man logo](https://raw.githubusercontent.com/fechan/laughing-man-webcam-filter/master/laughing_man.gif)

Overlay the animated Laughing Man logo from Ghost in the Shell: SAC on any faces in webcam input,
then pipe the output to a virtual webcam usable in Discord or Zoom or whatever.

Uses OpenCV and pyfakewebcam. pyfakewebcam requires [additional setup](https://github.com/jremmons/pyfakewebcam)
which currently only works on Linux.

You will likely need to configure the global variables/constants in `main.py`.
Also by default, you must press "ESC" to stop the program.
