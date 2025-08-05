import pyfirmata2 as pyf
import time as t
import cv2 as cv
from typing import Optional

class ProtocolHardwareAccess:
    def __init__(self):
        self.PORT =  pyf.Arduino.AUTODETECT
        self.board = pyf.Arduino(self.PORT)
    
    def selectPin(self, pin, mode):
        portSet = self.board.get_pin(f'd:{pin}:{mode}')
        return portSet

    def SetPowerPin(self, pow, pin, mode):
        ps = self.selectPin(pin, mode)
        ps.write(pow)
    
    def SetPowerToggle(self, n, time , pin, mode):
        ps = self.selectPin(pin, mode)
        for write in range(n):
            ps.write(pow)
            t.sleep(time)

class ProtocolFunction:    
    def cameraOn(portNum: Optional[int] = 0):
        cam = cv.VideoCapture(portNum)
        while True:
            _, ctx = cam.read()
            cv.imshow("cameraWindow", ctx)
            if(cv.waitKey(1) & 0xFF == ord("q")):
                break

