"""
Plugin 1
"""
import cv2


class ImageGetter:
    def __init__(self) -> None:
        self.cam = cv2.VideoCapture(0)
        print("Cam init successful")
        # todo: Check if cam is being used already

    def GetImage(self):
        result, img = self.cam.read()
        if result:
            return img
        else:
            print("ERROR CAPTURING IMG")
            return None
