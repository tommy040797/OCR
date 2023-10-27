import easyocr
import configparser


class OCR:
    def __init__(self) -> None:
        # ReadConfig
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.language = config["easyOCR"]["language"]
        self.whitelist = config["easyOCR"]["whitelist"]
        self.batchsize = int(config["easyOCR"]["batchsize"])
        self.reader = easyocr.Reader([self.language], quantize=True)
        print("easyOCR plugin initialized")

    def Rec(self, img):
        ocrresult = self.reader.recognize(
            img,
            detail=0,
            # mag_ratio=2.0,  # ! keine ahnung was es macht, repariert aber die 1 und die 7 wenn sie alleine stehen. vermutlich eingabebilder zu klein ? evtl bilder hochskalieren und ohne testen
            allowlist=self.whitelist,
            batch_size=self.batchsize,
        )
        return ocrresult

    def detect(self, img):
        detectresult = self.reader.readtext(img, mag_ratio=2)
        return detectresult

    def ReadText(self, img):
        ocrresult = self.reader.readtext(
            img,
            # detail=1,
            mag_ratio=2.0,  # ! keine ahnung was es macht, repariert aber die 1 und die 7 wenn sie alleine stehen. vermutlich eingabebilder zu klein ? evtl bilder hochskalieren und ohne testen
            allowlist=self.whitelist,
            batch_size=self.batchsize,
        )
        return ocrresult
