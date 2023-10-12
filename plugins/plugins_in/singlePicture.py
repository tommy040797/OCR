import cv2
import Util.Methods as Methods
import configparser


class ImageGetter:
    def __init__(self) -> None:
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.blur = config["ImagePreprocessing"]["noiseremoval"]
        self.grayscale = config["ImagePreprocessing"]["grayscale"]
        self.thresholding = config["ImagePreprocessing"]["thresholding"]
        self.negative = config["ImagePreprocessing"]["negative"]

    def GetImage(self):
        img = cv2.imread("Unbenannt.jpg")
        img = Methods.preProcessing(
            img, self.blur, self.grayscale, self.thresholding, self.negative
        )
        return img
