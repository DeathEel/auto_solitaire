import cv2
import numpy as np
import subprocess

def capture_screen():
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE
    )
    img_array = np.frombuffer(result.stdout, np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

def find_card(screen, template_path, threshold=0.9):
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    positions = list(zip(*loc[::-1]))
    return positions
