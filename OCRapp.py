import importlib
import configparser
import cv2
import time

importlib.import_module


# READ CURRENT CONFIG
config = configparser.ConfigParser()
config.read("config.ini")
inpluginname = config["InterfacesToUse"]["input"]
outpluginname = config["InterfacesToUse"]["output"]
pollingrate = 1 / int(config["Frequency"]["pollingrate"])

# Initialize PLugins
inpluginstringprefix = "plugins.plugins_in."
outpluginstringprefix = "plugins.plugins_out."

inmodule = importlib.import_module(inpluginstringprefix + inpluginname, ".")
outmodule = importlib.import_module(outpluginstringprefix + outpluginname, ".")

inplugin = inmodule.ImageGetter()

# test zum anzeigen von gecapturten Bildern die OCRt werden
for i in range(20):
    img = inplugin.GetImage()
    print(i)
    cv2.imshow("test", img)
    cv2.waitKey(1)
    time.sleep(pollingrate)


cv2.waitKey(0)
cv2.destroyAllWindows()


# img = cv2.imread("img.jpg")


# input("Press Enter to continue...")

# dummy = 5

# print(dummy)
