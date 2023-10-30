import easyocr
import configparser
import Util.Methods


class OCR:
    def __init__(self) -> None:
        # ReadConfig
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.language = config["easyOCR"]["language"]
        self.whitelist = config["easyOCR"]["whitelist"]
        self.batchsize = int(config["easyOCR"]["batchsize"])
        self.custommodel = Util.Methods.str2bool(config["easyOCR"]["custommodel"])
        self.custommodelname = config["easyOCR"]["custommodelname"]
        if self.custommodel == True:
            self.reader = easyocr.Reader(
                [self.language], quantize=True, recog_network=self.custommodelname
            )
        else:
            self.reader = easyocr.Reader([self.language], quantize=True)
        print("easyOCR plugin initialized")

    def Rec(self, img):
        ocrresult = self.reader.recognize(
            img,
            # detail=0,
            # mag_ratio=2.0,  # ! keine ahnung was es macht, repariert aber die 1 und die 7 wenn sie alleine stehen. vermutlich eingabebilder zu klein ? evtl bilder hochskalieren und ohne testen
            allowlist=self.whitelist,
            batch_size=self.batchsize,
        )
        return ocrresult[0][1], ocrresult[0][2]

    def detect(self, img):
        detectresult = self.reader.readtext(img, mag_ratio=2)
        return detectresult

    def ReadText(self, img):
        ocrresult = self.reader.readtext(
            img,
            # detail=1,
            mag_ratio=2.0,  # ! keine ahnung was es macht, repariert aber die 1 und die 7 wenn sie alleine stehen. vermutlich eingabebilder zu klein ? evtl bilder hochskalieren und ohne testen
            allowlist=self.whitelist,
            text_threshold=0.3,
            batch_size=self.batchsize,
        )
        # print(ocrresult)
        # print(ocrresult[0][1], ocrresult[0][2])
        try:
            return ocrresult[0][1], ocrresult[0][2]
        except:
            return "", 0
