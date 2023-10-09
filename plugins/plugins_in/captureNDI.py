"""
PLugin2
"""

import Util.Methods as Methods
import configparser


# pyNDI Import
import Util.ndi.finder as finder
import Util.ndi.receiver as receiver
import Util.ndi.lib as lib


class ImageGetter:
    def __init__(self) -> None:
        # Imagepreprocessing Variables
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.blur = config["ImagePreprocessing"]["noiseremoval"]
        self.grayscale = config["ImagePreprocessing"]["grayscale"]
        self.thresholding = config["ImagePreprocessing"]["thresholding"]
        self.negative = config["ImagePreprocessing"]["negative"]
        self.find = finder.create_ndi_finder()
        self.NDIsources = self.find.get_sources()
        if not self.NDIsources:
            print("no NDI Stream found")
            quit()
        self.receiveSource = self.NDIsources[0]
        self.receiver = receiver.create_receiver(self.receiveSource)
        if self.receiver is not None:
            print("NDI Stream init")

    def GetImage(self):
        img = self.receiver.read()
        img = Methods.preProcessing(
            img, self.blur, self.grayscale, self.thresholding, self.negative
        )
        return img
