import keras_ocr


class OCR:
    def __init__(self) -> None:
        # ReadConfig
        self.pipeline = keras_ocr.pipeline.Pipeline()

        print("keras plugin initialized")

    def ReadText(self, img):
        ocrresult = self.pipeline.recognize(img)
        # print(ocrresult)
        # return ocrresult
