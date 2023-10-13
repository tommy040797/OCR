import configparser

config = configparser.ConfigParser()
config["InterfacesToUse"] = {
    "Input": "captureNDI",
    "Output": "testout",
    "OCR": "easyOCR",
}
config["Frequency"] = {"PollingRate": 1}
config["captureWebcam"] = {"ResolutionX": 1280, "ResolutionY": 720}
config["Tesseract"] = {
    "PathToTesseract": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "TesseractCustomConfigString": "-c tessedit_char_whitelist=0123456789: --psm 6",
    "Language": "deu",
}
config["easyOCR"] = {"Language": "de", "whitelist": "0123456789:", "batchsize": 1}
config["logs"] = {"logname": "logs", "log": True}
config["ImagePreprocessing"] = {
    "Grayscale": True,
    "NoiseRemoval": True,
    "Thresholding": True,
    "Negative": True,
}

config["DEBUGGING"] = {"JedesBildEinzelnBestaetigen": True, "Profiling": True}

with open("config.ini", "w") as configfile:
    config.write(configfile)
