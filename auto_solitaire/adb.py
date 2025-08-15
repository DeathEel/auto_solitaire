import cv2
import numpy as np
import subprocess
import time

class Screen:
    def __init__(self):
        self.full_img = None
        self.tableau_img = None
        self.foundation_img = None
        self.waste_img = None
        self.capture()

    def capture(self):
        result = subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
	        stdout=subprocess.PIPE
    	)
        img_array = np.frombuffer(result.stdout, np.uint8)
        self.full_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        self.tableau_img = self.full_img[550:, :]
        self.foundation_img = self.full_img[:550, :610]
        self.waste_img = self.full_img[:550, 610:910]

    def tap(self, x, y):
        subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])
        time.sleep(0.5)

    def swipe(self, x1, y1, x2, y2, duration_ms=300):
        subprocess.run(["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
        time.sleep(0.5)
