import importlib
import configparser
import cv2
import time
import json
import Util.Methods as dictcreator
import pytesseract
import sys
import os


importlib.import_module

sys.path.insert(0, "./Util/ndi")


class Rectangle:
    def __init__(self, name, xstart, ystart, xend, yend):
        self.name = name
        self.x = xstart
        self.y = ystart
        self.width = xend - xstart
        self.height = yend - ystart


# READ CURRENT CONFIG
config = configparser.ConfigParser()
config.read("config.ini")
inpluginname = config["InterfacesToUse"]["input"]
outpluginname = config["InterfacesToUse"]["output"]
pollingrate = 1 / float(config["Frequency"]["pollingrate"])
camresx = int(config["captureWebcam"]["ResolutionX"])
camresy = int(config["captureWebcam"]["ResolutionY"])
tesseractpath = config["DEFAULT"]["pathtotesseract"]
custom_config = config["DEFAULT"]["tesseractcustomconfigstring"]

# Initialize PLugins
pytesseract.pytesseract.tesseract_cmd = tesseractpath
inpluginstringprefix = "plugins.plugins_in."
outpluginstringprefix = "plugins.plugins_out."
inmodule = importlib.import_module(inpluginstringprefix + inpluginname, ".")
outmodule = importlib.import_module(outpluginstringprefix + outpluginname, ".")

if inpluginname == "captureWebcam":
    inplugin = inmodule.ImageGetter(camresx, camresy)
elif inpluginname == "captureNDI":
    inplugin = inmodule.ImageGetter()


# Read Rectangles subject to OCR
with open("Rectangles.json", "r") as openfile:
    json_object = json.load(openfile)
    rectangles = []
    for item in json_object["Rectangles"]:
        rectangles.append(
            Rectangle(
                item["name"], item["xstart"], item["ystart"], item["xend"], item["yend"]
            )
        )

lastresultdict = {}
resultdict = {}

while True:
    img = inplugin.GetImage()
    rectangleDict = dictcreator.dictRectangles(rectangles, inplugin.GetImage())
    for item in rectangleDict:
        resultdict[item] = pytesseract.image_to_string(
            rectangleDict[item],
            lang="deu",
            config=custom_config,
        )
        if item == "Zeit":
            print(resultdict[item])
            h, w = rectangleDict[item].shape

            boxes = pytesseract.image_to_boxes(
                rectangleDict[item], lang="deu", config="--psm 7"
            )
            imgboxes = rectangleDict[item]
            for b in boxes.splitlines():
                b = b.split(" ")
                imgboxes = cv2.rectangle(
                    rectangleDict[item],
                    (int(b[1]), h - int(b[2])),
                    (int(b[3]), h - int(b[4])),
                    (0, 255, 0),
                    2,
                )
            print(boxes)
            cv2.imshow("test", imgboxes)
            cv2.waitKey(0)

    # if lastresultdict != resultdict:
    # with open("log.json", "a") as f:
    # json.dump(resultdict, f)
    # f.write(os.linesep)
    # lastresultdict = resultdict.copy()
    # time.sleep(pollingrate)
