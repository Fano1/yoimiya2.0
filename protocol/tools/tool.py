from langchain_core.tools import tool
import cv2 as cv

@tool
def openCamera():
    cam = cv.VideoCapture(0)
    while True:
        _, cap = cam.read()
        cv.imshow("camera", cap)

        if 0xFF and cv.waitKey(1) == ord("q"):
            break
            