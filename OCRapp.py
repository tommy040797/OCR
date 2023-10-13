import importlib
import configparser
import cv2
import time
import json
import Util.Methods as dictcreator
import sys
import os
from timeit import default_timer as timer
import cProfile as profile
import pstats


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
ocrpluginname = config["InterfacesToUse"]["ocr"]
pollingrate = 1 / float(config["Frequency"]["pollingrate"])
logname = config["logs"]["logname"]
log = config["logs"]["log"]
debugging = config["DEBUGGING"]["JedesBildEinzelnBestaetigen"]

# Initialize Plugins
inpluginstringprefix = "plugins.plugins_in."
outpluginstringprefix = "plugins.plugins_out."
ocrpluginprefix = "plugins.plugins_ocr."
inmodule = importlib.import_module(inpluginstringprefix + inpluginname, ".")
outmodule = importlib.import_module(outpluginstringprefix + outpluginname, ".")
ocrmodule = importlib.import_module(ocrpluginprefix + ocrpluginname, ".")

inplugin = inmodule.ImageGetter()
ocrplugin = ocrmodule.OCR()


prof = profile.Profile()
prof.enable()


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
for i in range(10):
    start = timer()

    img = inplugin.GetImage()
    rectangleDict = dictcreator.dictRectangles(rectangles, inplugin.GetImage())
    for item in rectangleDict:
        resultdict[item] = ocrplugin.ReadText(rectangleDict[item])
        if debugging == "True":
            print(resultdict[item])
            cv2.imshow("test", rectangleDict[item])
            cv2.waitKey(0)

    if lastresultdict != resultdict:
        if log == "True":  # TODO: das hier als Plugin implementieren
            loglocation = "./logs/" + logname + ".json"
            with open(loglocation, "a") as f:
                json.dump(resultdict, f)
                f.write(os.linesep)
        lastresultdict = resultdict.copy()
    end = timer()
    rest = pollingrate - (end - start)
    # print(rest)
    if rest < 0:
        rest = 0
    time.sleep(rest)

prof.disable()
stats = pstats.Stats(prof).strip_dirs().sort_stats("cumtime")
stats.print_stats(30)  # top 10 rows
