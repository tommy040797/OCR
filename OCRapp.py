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

import math

# TODO:rechtecke augmenten

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
pollingratenotreziprog = float(config["Frequency"]["pollingrate"])
augmentrectangles = config["Default"]["augmentrectangles"]

debugging = config["DEBUGGING"]["JedesBildEinzelnBestaetigen"]
profiling = config["DEBUGGING"]["profiling"]
outputresult = config["DEBUGGING"]["outputresult"]
profilinglines = int(config["DEBUGGING"]["profilingzeilen"])

# Initialize Plugins
inpluginstringprefix = "plugins.plugins_in."
outpluginstringprefix = "plugins.plugins_out."
ocrpluginprefix = "plugins.plugins_ocr."
inmodule = importlib.import_module(inpluginstringprefix + inpluginname, ".")
outmodule = importlib.import_module(outpluginstringprefix + outpluginname, ".")
ocrmodule = importlib.import_module(ocrpluginprefix + ocrpluginname, ".")

inplugin = inmodule.ImageGetter()
ocrplugin = ocrmodule.OCR()
outplugin = outmodule.Output()

if profiling == "True":
    prof = profile.Profile()
    prof.enable()

# Read Rectangles subject to OCR
with open("Rectangles.json", "r") as openfile:
    json_object = json.load(openfile)
    rectangles = []
    rectanglesartificial = []
    for item in json_object["Rectangles"]:
        if item["artificial"] == "False":
            rectangles.append(
                Rectangle(
                    item["name"],
                    item["xstart"],
                    item["ystart"],
                    item["xend"],
                    item["yend"],
                )
            )
        else:
            rectanglesartificial.append(
                Rectangle(
                    item["name"],
                    item["xstart"],
                    item["ystart"],
                    item["xend"],
                    item["yend"],
                )
            )

if augmentrectangles == "True":
    print("erstmalige Detection")
    detectresult = {}
    img = inplugin.GetImage()
    rectangleDict = dictcreator.dictRectangles(rectangles, img)
    rectangleDictArt = dictcreator.dictRectangles(rectanglesartificial, img)
    color = (0, 0, 0)
    # print rectangles before aug
    image = img.copy()
    for item in rectangles:
        image = cv2.rectangle(
            image,
            (item.x, item.y),
            (item.x + item.width, item.y + item.height),
            color,
            1,
        )
    for item in rectanglesartificial:
        image = cv2.rectangle(
            image,
            (item.x, item.y),
            (item.x + item.width, item.y + item.height),
            color,
            1,
        )
    cv2.imshow("test", image)
    cv2.waitKey(0)

    # augmenting rectangles
    for item in rectangleDict:
        detectresult[item] = ocrplugin.detect(rectangleDict[item])
        print(detectresult[item])  # TODO: minuten und sekunde werden falsch gemacht
        rectangle = next((x for x in rectangles if x.name == item), None)
        rectangle.x = rectangle.x + detectresult[item][0][0][0][0] - 10
        rectangle.y = rectangle.y + detectresult[item][0][0][0][1] - 10
        rectangle.width = math.ceil(
            (detectresult[item][0][0][1][0] - detectresult[item][0][0][0][0] + 10)
            * 1.05
        )
        rectangle.height = math.ceil(
            (detectresult[item][0][0][3][1] - detectresult[item][0][0][0][1] + 10)
            * 1.05
        )

    for item in rectangleDictArt:
        detectresult[item] = ocrplugin.detect(rectangleDictArt[item])
        # print(detectresult[item])
        if detectresult[item] == []:
            continue
        rectangle = next((x for x in rectanglesartificial if x.name == item), None)
        rectangle.x = rectangle.x + detectresult[item][0][0][0][0] - 10
        rectangle.y = rectangle.y + detectresult[item][0][0][0][1] - 10
        rectangle.width = math.ceil(
            (detectresult[item][0][0][1][0] - detectresult[item][0][0][0][0] + 10)
            * 1.05
        )
        rectangle.height = math.ceil(
            (detectresult[item][0][0][3][1] - detectresult[item][0][0][0][1] + 10)
            * 1.05
        )
    image = img.copy()
    # print augmented rectangles
    for item in rectangles:
        image = cv2.rectangle(
            image,
            (item.x, item.y),
            (item.x + item.width, item.y + item.height),
            color,
            1,
        )
    for item in rectanglesartificial:
        image = cv2.rectangle(
            image,
            (item.x, item.y),
            (item.x + item.width, item.y + item.height),
            color,
            1,
        )
    cv2.imshow("test", image)
    cv2.waitKey(0)

lastresultdict = {}
resultdict = {}
isStopped = True

# erstmaliges befüllen der ergebnisse
img = inplugin.GetImage()
rectangleDict = dictcreator.dictRectangles(rectangles, img)
rectangleDictArt = dictcreator.dictRectangles(rectanglesartificial, img)
for item in rectangleDict:
    resultdict[item] = int(ocrplugin.ReadText(rectangleDict[item])[0] or 0)
    if debugging == "True":
        print(item + ": ")
        print(resultdict[item])
        cv2.imshow("test", rectangleDict[item])
        cv2.waitKey(0)
for item in rectangleDictArt:
    resultdict[item] = int(ocrplugin.ReadText(rectangleDictArt[item])[0] or 0)
    if debugging == "True":
        print(item + ": ")
        print(resultdict[item])
        cv2.imshow("test", rectangleDictArt[item])
        cv2.waitKey(0)
if lastresultdict != resultdict:
    outplugin.putResult(resultdict)
    lastresultdict = resultdict.copy()


# loop
stoppedcounter = 0
counter = 0
rotiercounter = 0
artdictlist = list(rectangleDictArt)  # für länge


if profiling == "True":
    for i in range(10):
        start = timer()
        # uhr ist nicht gestoppt
        if isStopped == False:
            img = inplugin.GetImage()
            rectangleDict = dictcreator.dictRectangles(rectangles, img)
            rectangleDictArt = dictcreator.dictRectangles(rectanglesartificial, img)
            # read clock
            for item in rectangleDict:
                resultdict[item] = int(ocrplugin.ReadText(rectangleDict[item])[0])

                if debugging == "True":
                    print(item + ": ")
                    print(resultdict[item])
                    cv2.imshow("test", rectangleDict[item])
                    cv2.waitKey(0)
            # check if clock is stopped
            if (
                resultdict["Minutes"] == lastresultdict["Minutes"]
                and resultdict["Seconds"] == lastresultdict["Seconds"]
            ):
                if stoppedcounter == pollingratenotreziprog - 1:
                    isStopped = True
                    stoppedcounter = 0
                stoppedcounter += 1
            else:
                stoppedcounter = 0

            # rotierer zum periodischen überprüfen
            for item in rectangleDictArt:
                if artdictlist.index(item) == rotiercounter:
                    # print(artdictlist[rotiercounter], "uhr läuft rotierer")
                    if item == "ScoreHome":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "ScoreGuest":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty1Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty1Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["HomePenalty1Seconds"] = int(
                            ocrplugin.ReadText(rectangleDictArt["HomePenalty1Seconds"])[
                                0
                            ]
                            or 0
                        )
                    elif item == "HomePenalty2Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty2Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["HomePenalty2Seconds"] = int(
                            ocrplugin.ReadText(rectangleDictArt["HomePenalty2Seconds"])[
                                0
                            ]
                            or 0
                        )
                    elif item == "GuestPenalty1Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "GuestPenalty1Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["GuestPenalty1Seconds"] = int(
                            ocrplugin.ReadText(
                                rectangleDictArt["GuestPenalty1Seconds"]
                            )[0]
                            or 0
                        )
                    elif item == "HomePenalty2Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "GuestPenalty2Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["GuestPenalty2Seconds"] = int(
                            ocrplugin.ReadText(
                                rectangleDictArt["GuestPenalty2Seconds"]
                            )[0]
                            or 0
                        )
                    elif item == "Period":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                # falls nicht im rotiercounter ai fill
                else:
                    match item:
                        case "HomePenalty1Number":
                            if (
                                lastresultdict["HomePenalty1Seconds"] == 0
                                and lastresultdict["HomePenalty1Minutes"] == 0
                            ):
                                resultdict[item] = 0
                        case "HomePenalty1Minutes":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["HomePenalty1Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict["HomePenalty1Seconds"] == 0:
                                        resultdict[item] = lastresultdict[item] - 1
                                    else:
                                        resultdict[item] = lastresultdict[item]
                        case "HomePenalty1Seconds":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["HomePenalty1Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict[item] == 0:
                                        resultdict[item] = 59
                                    else:
                                        resultdict[item] = lastresultdict[item] - 1
                                else:
                                    resultdict[item] = lastresultdict[item]
                        case "HomePenalty2Number":
                            if (
                                lastresultdict["HomePenalty2Seconds"] == 0
                                and lastresultdict["HomePenalty2Minutes"] == 0
                            ):
                                resultdict[item] = 0
                        case "HomePenalty2Minutes":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["HomePenalty2Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict["HomePenalty2Seconds"] == 0:
                                        resultdict[item] = lastresultdict[item] - 1
                                    else:
                                        resultdict[item] = lastresultdict[item]
                        case "HomePenalty2Seconds":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["HomePenalty2Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict[item] == 0:
                                        resultdict[item] = 59
                                    else:
                                        resultdict[item] = lastresultdict[item] - 1
                                else:
                                    resultdict[item] = lastresultdict[item]
                        case "GuestPenalty1Number":
                            if (
                                lastresultdict["GuestPenalty1Seconds"] == 0
                                and lastresultdict["GuestPenalty1Minutes"] == 0
                            ):
                                resultdict[item] = 0
                        case "GuestPenalty1Minutes":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["GuestPenalty1Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict["GuestPenalty1Seconds"] == 0:
                                        resultdict[item] = lastresultdict[item] - 1
                                    else:
                                        resultdict[item] = lastresultdict[item]
                        case "GuestPenalty1Seconds":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["GuestPenalty1Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict[item] == 0:
                                        resultdict[item] = 59
                                    else:
                                        resultdict[item] = lastresultdict[item] - 1
                                else:
                                    resultdict[item] = lastresultdict[item]
                        case "GuestPenalty2Number":
                            if (
                                lastresultdict["GuestPenalty2Seconds"] == 0
                                and lastresultdict["GuestPenalty2Minutes"] == 0
                            ):
                                resultdict[item] = 0
                        case "GuestPenalty2Minutes":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["GuestPenalty2Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict["GuestPenalty2Seconds"] == 0:
                                        resultdict[item] = lastresultdict[item] - 1
                                    else:
                                        resultdict[item] = lastresultdict[item]
                        case "GuestPenalty2Seconds":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["GuestPenalty2Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict[item] == 0:
                                        resultdict[item] = 59
                                    else:
                                        resultdict[item] = lastresultdict[item] - 1
                                else:
                                    resultdict[item] = lastresultdict[item]
            if outputresult == "True":
                print(resultdict)
            if lastresultdict != resultdict:
                outplugin.putResult(resultdict)
                lastresultdict = resultdict.copy()
            if counter < pollingratenotreziprog - 1:
                counter += 1
            else:
                counter = 0
        # Uhr ist gestoppt
        else:
            img = inplugin.GetImage()
            rectangleDict = dictcreator.dictRectangles(rectangles, img)
            rectangleDictArt = dictcreator.dictRectangles(rectanglesartificial, img)
            for item in rectangleDict:
                resultdict[item] = int(ocrplugin.ReadText(rectangleDict[item])[0] or 0)
                if debugging == "True":
                    print(item + ": ")
                    print(resultdict[item])
                    cv2.imshow("test", rectangleDict[item])
                    cv2.waitKey(0)
            for item in rectangleDictArt:
                if artdictlist.index(item) == rotiercounter:
                    # print(artdictlist[rotiercounter], "uhr läuft nicht rotierer")
                    if item == "ScoreHome":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "ScoreGuest":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty1Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty1Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["HomePenalty1Seconds"] = int(
                            ocrplugin.ReadText(rectangleDictArt["HomePenalty1Seconds"])[
                                0
                            ]
                            or 0
                        )
                    elif item == "HomePenalty2Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty2Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["HomePenalty2Seconds"] = int(
                            ocrplugin.ReadText(rectangleDictArt["HomePenalty2Seconds"])[
                                0
                            ]
                            or 0
                        )
                    elif item == "GuestPenalty1Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "GuestPenalty1Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["GuestPenalty1Seconds"] = int(
                            ocrplugin.ReadText(
                                rectangleDictArt["GuestPenalty1Seconds"]
                            )[0]
                            or 0
                        )
                    elif item == "HomePenalty2Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "GuestPenalty2Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["GuestPenalty2Seconds"] = int(
                            ocrplugin.ReadText(
                                rectangleDictArt["GuestPenalty2Seconds"]
                            )[0]
                            or 0
                        )
                    elif item == "Period":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
            if resultdict["Seconds"] != lastresultdict["Seconds"]:
                isStopped = False
                stoppedcounter = 0

            if outputresult == "True":
                print(resultdict)
            if lastresultdict != resultdict:
                outplugin.putResult(resultdict)
                lastresultdict = resultdict.copy()
        # überlauf und verwaltung der rotation
        if rotiercounter == len(artdictlist) - 1:
            rotiercounter = 0
        else:
            if (
                (artdictlist[rotiercounter] == "HomePenalty1Minutes")
                or (artdictlist[rotiercounter] == "HomePenalty2Minutes")
                or (artdictlist[rotiercounter] == "GuestPenalty1Minutes")
                or (artdictlist[rotiercounter] == "GuestPenalty2Minutes")
            ):
                rotiercounter += 2

            else:
                rotiercounter += 1
        # auffüllen pollingrate
        end = timer()
        rest = pollingrate - (end - start)
        if rest < 0:
            rest = 0
            print("UPDATERATE KANN NICHT EINGEHALTEN WERDEN, ERGEBNISSE FALSCH")
        time.sleep(rest)
else:
    while True:
        start = timer()
        # uhr ist nicht gestoppt
        if isStopped == False:
            img = inplugin.GetImage()
            rectangleDict = dictcreator.dictRectangles(rectangles, img)
            rectangleDictArt = dictcreator.dictRectangles(rectanglesartificial, img)
            # read clock
            for item in rectangleDict:
                resultdict[item] = int(ocrplugin.ReadText(rectangleDict[item])[0])

                if debugging == "True":
                    print(item + ": ")
                    print(resultdict[item])
                    cv2.imshow("test", rectangleDict[item])
                    cv2.waitKey(0)
            # check if clock is stopped
            if (
                resultdict["Minutes"] == lastresultdict["Minutes"]
                and resultdict["Seconds"] == lastresultdict["Seconds"]
            ):
                if stoppedcounter == pollingratenotreziprog - 1:
                    isStopped = True
                    stoppedcounter = 0
                stoppedcounter += 1
            else:
                stoppedcounter = 0

            # rotierer zum periodischen überprüfen
            for item in rectangleDictArt:
                if artdictlist.index(item) == rotiercounter:
                    # print(artdictlist[rotiercounter], "uhr läuft rotierer")
                    if item == "ScoreHome":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "ScoreGuest":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty1Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty1Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["HomePenalty1Seconds"] = int(
                            ocrplugin.ReadText(rectangleDictArt["HomePenalty1Seconds"])[
                                0
                            ]
                            or 0
                        )
                    elif item == "HomePenalty2Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty2Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["HomePenalty2Seconds"] = int(
                            ocrplugin.ReadText(rectangleDictArt["HomePenalty2Seconds"])[
                                0
                            ]
                            or 0
                        )
                    elif item == "GuestPenalty1Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "GuestPenalty1Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["GuestPenalty1Seconds"] = int(
                            ocrplugin.ReadText(
                                rectangleDictArt["GuestPenalty1Seconds"]
                            )[0]
                            or 0
                        )
                    elif item == "HomePenalty2Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "GuestPenalty2Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["GuestPenalty2Seconds"] = int(
                            ocrplugin.ReadText(
                                rectangleDictArt["GuestPenalty2Seconds"]
                            )[0]
                            or 0
                        )
                    elif item == "Period":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                # falls nicht im rotiercounter ai fill
                else:
                    match item:
                        case "HomePenalty1Number":
                            if (
                                lastresultdict["HomePenalty1Seconds"] == 0
                                and lastresultdict["HomePenalty1Minutes"] == 0
                            ):
                                resultdict[item] = 0
                        case "HomePenalty1Minutes":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["HomePenalty1Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict["HomePenalty1Seconds"] == 0:
                                        resultdict[item] = lastresultdict[item] - 1
                                    else:
                                        resultdict[item] = lastresultdict[item]
                        case "HomePenalty1Seconds":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["HomePenalty1Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict[item] == 0:
                                        resultdict[item] = 59
                                    else:
                                        resultdict[item] = lastresultdict[item] - 1
                                else:
                                    resultdict[item] = lastresultdict[item]
                        case "HomePenalty2Number":
                            if (
                                lastresultdict["HomePenalty2Seconds"] == 0
                                and lastresultdict["HomePenalty2Minutes"] == 0
                            ):
                                resultdict[item] = 0
                        case "HomePenalty2Minutes":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["HomePenalty2Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict["HomePenalty2Seconds"] == 0:
                                        resultdict[item] = lastresultdict[item] - 1
                                    else:
                                        resultdict[item] = lastresultdict[item]
                        case "HomePenalty2Seconds":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["HomePenalty2Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict[item] == 0:
                                        resultdict[item] = 59
                                    else:
                                        resultdict[item] = lastresultdict[item] - 1
                                else:
                                    resultdict[item] = lastresultdict[item]
                        case "GuestPenalty1Number":
                            if (
                                lastresultdict["GuestPenalty1Seconds"] == 0
                                and lastresultdict["GuestPenalty1Minutes"] == 0
                            ):
                                resultdict[item] = 0
                        case "GuestPenalty1Minutes":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["GuestPenalty1Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict["GuestPenalty1Seconds"] == 0:
                                        resultdict[item] = lastresultdict[item] - 1
                                    else:
                                        resultdict[item] = lastresultdict[item]
                        case "GuestPenalty1Seconds":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["GuestPenalty1Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict[item] == 0:
                                        resultdict[item] = 59
                                    else:
                                        resultdict[item] = lastresultdict[item] - 1
                                else:
                                    resultdict[item] = lastresultdict[item]
                        case "GuestPenalty2Number":
                            if (
                                lastresultdict["GuestPenalty2Seconds"] == 0
                                and lastresultdict["GuestPenalty2Minutes"] == 0
                            ):
                                resultdict[item] = 0
                        case "GuestPenalty2Minutes":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["GuestPenalty2Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict["GuestPenalty2Seconds"] == 0:
                                        resultdict[item] = lastresultdict[item] - 1
                                    else:
                                        resultdict[item] = lastresultdict[item]
                        case "GuestPenalty2Seconds":
                            if (
                                lastresultdict[item] != 0
                                or lastresultdict["GuestPenalty2Minutes"] != 0
                            ):
                                if counter == pollingratenotreziprog - 1:
                                    if lastresultdict[item] == 0:
                                        resultdict[item] = 59
                                    else:
                                        resultdict[item] = lastresultdict[item] - 1
                                else:
                                    resultdict[item] = lastresultdict[item]
            if outputresult == "True":
                print(resultdict)
            if lastresultdict != resultdict:
                outplugin.putResult(resultdict)
                lastresultdict = resultdict.copy()
            if counter < pollingratenotreziprog - 1:
                counter += 1
            else:
                counter = 0
        # Uhr ist gestoppt
        else:
            img = inplugin.GetImage()
            rectangleDict = dictcreator.dictRectangles(rectangles, img)
            rectangleDictArt = dictcreator.dictRectangles(rectanglesartificial, img)
            for item in rectangleDict:
                resultdict[item] = int(ocrplugin.ReadText(rectangleDict[item])[0] or 0)
                if debugging == "True":
                    print(item + ": ")
                    print(resultdict[item])
                    cv2.imshow("test", rectangleDict[item])
                    cv2.waitKey(0)
            for item in rectangleDictArt:
                if artdictlist.index(item) == rotiercounter:
                    # print(artdictlist[rotiercounter], "uhr läuft nicht rotierer")
                    if item == "ScoreHome":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "ScoreGuest":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty1Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty1Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["HomePenalty1Seconds"] = int(
                            ocrplugin.ReadText(rectangleDictArt["HomePenalty1Seconds"])[
                                0
                            ]
                            or 0
                        )
                    elif item == "HomePenalty2Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "HomePenalty2Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["HomePenalty2Seconds"] = int(
                            ocrplugin.ReadText(rectangleDictArt["HomePenalty2Seconds"])[
                                0
                            ]
                            or 0
                        )
                    elif item == "GuestPenalty1Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "GuestPenalty1Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["GuestPenalty1Seconds"] = int(
                            ocrplugin.ReadText(
                                rectangleDictArt["GuestPenalty1Seconds"]
                            )[0]
                            or 0
                        )
                    elif item == "HomePenalty2Number":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                    elif item == "GuestPenalty2Minutes":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
                        resultdict["GuestPenalty2Seconds"] = int(
                            ocrplugin.ReadText(
                                rectangleDictArt["GuestPenalty2Seconds"]
                            )[0]
                            or 0
                        )
                    elif item == "Period":
                        resultdict[item] = int(
                            ocrplugin.ReadText(rectangleDictArt[item])[0] or 0
                        )
            if resultdict["Seconds"] != lastresultdict["Seconds"]:
                isStopped = False
                stoppedcounter = 0

            if outputresult == "True":
                print(resultdict)
            if lastresultdict != resultdict:
                outplugin.putResult(resultdict)
                lastresultdict = resultdict.copy()
        # überlauf und verwaltung der rotation
        if rotiercounter == len(artdictlist) - 1:
            rotiercounter = 0
        else:
            if (
                (artdictlist[rotiercounter] == "HomePenalty1Minutes")
                or (artdictlist[rotiercounter] == "HomePenalty2Minutes")
                or (artdictlist[rotiercounter] == "GuestPenalty1Minutes")
                or (artdictlist[rotiercounter] == "GuestPenalty2Minutes")
            ):
                rotiercounter += 2

            else:
                rotiercounter += 1
        # auffüllen pollingrate
        end = timer()
        rest = pollingrate - (end - start)
        if rest < 0:
            rest = 0
            print("UPDATERATE KANN NICHT EINGEHALTEN WERDEN, ERGEBNISSE FALSCH")
        time.sleep(rest)

if profiling == "True":
    prof.disable()
    stats = pstats.Stats(prof).strip_dirs().sort_stats("cumtime")
    stats.print_stats(profilinglines)  # top 10 rows
