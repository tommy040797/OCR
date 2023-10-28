import pytesseract
import configparser


class OCR:
    def __init__(self) -> None:
        # ReadConfig
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.path = config["Tesseract"]["pathtotesseract"]
        self.config = config["Tesseract"]["tesseractcustomconfigstring"]
        self.language = config["Tesseract"]["Language"]
        pytesseract.pytesseract.tesseract_cmd = self.path

        print("Tesseract plugin initialized")

    def Rec(self, img):
        ocrresult = pytesseract.image_to_string(
            img,
            lang=self.language,
            config=self.config,
        )
        ocrresult = ocrresult.strip()
        return ocrresult
