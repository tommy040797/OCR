import configparser

config = configparser.ConfigParser()
config["InterfacesToUse"] = {"Input": "captureNDI", "Output": "testout"}
config["Frequency"] = {"PollingRate": 1}
config["captureWebcam"] = {"ResolutionX": 1280, "ResolutionY": 720}
config["DEFAULT"] = {
    "PathToTesseract": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "TesseractCustomConfigString": "-c tessedit_char_whitelist=0123456789: --psm 6",
}
config["ImagePreprocessing"] = {
    "Grayscale": True,
    "NoiseRemoval": True,
    "Thresholding": True,
    "Negative": False,
}
with open("config.ini", "w") as configfile:
    config.write(configfile)
