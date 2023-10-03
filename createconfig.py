import configparser

config = configparser.ConfigParser()
config["InterfacesToUse"] = {"Input": "testone", "Output": "testout"}
config["Frequency"] = {"PollingRate": 5}
with open("config.ini", "w") as configfile:
    config.write(configfile)
