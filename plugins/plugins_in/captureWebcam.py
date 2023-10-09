"""
Plugin 1
"""
import cv2
import configparser
import Util.Methods as Methods


class ImageGetter:
    def __init__(self) -> None:
        # Imagepreprocessing Variables
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.blur = config["ImagePreprocessing"]["noiseremoval"]
        self.grayscale = config["ImagePreprocessing"]["grayscale"]
        self.thresholding = config["ImagePreprocessing"]["thresholding"]
        self.negative = config["ImagePreprocessing"]["negative"]
        self.xres = int(config["captureWebcam"]["resolutionx"])
        self.yres = int(config["captureWebcam"]["resolutiony"])

        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, self.xres)
        self.cam.set(4, self.yres)
        if self.cam.isOpened():
            print("Cam init successful")
        else:
            print("Alert ! Camera disconnected")

        # * hier drunter wird abgefragt ob die Kamera funktional ist, bzw nicht schon benutzt wird
        try:
            ret, frame = self.cam.read()
        except Exception as e:
            print("camera already used, close the other Application")
            cv2.waitKey(0)

    def GetImage(self):
        result, img = self.cam.read()
        if result:
            img = Methods.preProcessing(
                img, self.blur, self.grayscale, self.thresholding, self.negative
            )
            return img
        else:
            print("ERROR CAPTURING IMG")
            return None
