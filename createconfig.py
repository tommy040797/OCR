import configparser

config = configparser.ConfigParser()
config["InterfacesToUse"] = {"Input": "captureWebcam", "Output": "testout"}
config["Frequency"] = {"PollingRate": 3}
with open("config.ini", "w") as configfile:
    config.write(configfile)
