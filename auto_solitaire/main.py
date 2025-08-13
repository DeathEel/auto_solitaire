import cv2
import numpy as np
from PIL import Image
import subprocess

def capture_screen():
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE
    )
    img_array = np.frombuffer(result.stdout, np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

img = capture_screen()
cv2.imshow("Screen", img)
cv2.waitKey(0)
