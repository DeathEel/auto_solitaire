import cv2
import numpy as np
import subprocess

class Screen:
    def __init__(self):
        pass

    def capture(self):
        result = subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
	        stdout=subprocess.PIPE
    	)
        img_array = np.frombuffer(result.stdout, np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    def tap(self, x, y):
        subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1, y1, x2, y2, duration_ms=300):
        subprocess.run(["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
