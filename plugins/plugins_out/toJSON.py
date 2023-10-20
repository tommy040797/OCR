import configparser
import json
import os


class Output:
    def __init__(self) -> None:
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.logname = config["logs"]["logname"]
        self.log = config["logs"]["log"]

    def putResult(self, resultdict):
        if self.log == "True":
            loglocation = "./logs/" + self.logname + ".json"
            with open(loglocation, "a") as f:
                json.dump(resultdict, f)
                f.write(os.linesep)
