import keras_ocr
import numpy as np


class OCR:
    def __init__(self) -> None:
        # ReadConfig
        self.pipeline = keras_ocr.pipeline.Pipeline()
        self.recognizer = keras_ocr.recognition.Recognizer()
        print("keras plugin initialized")

    def ReadText(self, img):
        img = keras_ocr.tools.read(img)
        print(img.shape)
        img = np.expand_dims(
            img, axis=2
        )  # funktioniert mit importiertem bild, so aber nicht
        print(img.shape)
        ocrresult = self.pipeline.recognize([img])[0]
        print(ocrresult)
        # return ocrresult
