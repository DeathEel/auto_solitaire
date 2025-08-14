import cv2
import numpy as np
from PIL import Image
import subprocess
import adb
import game

img = adb.capture_screen()
cv2.imshow("Screen", img)
cv2.waitKey(0)

cards_found = adb.find_card(img, "templates/AceHearts.png")
print(cards_found)
