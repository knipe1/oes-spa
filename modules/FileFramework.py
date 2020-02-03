
# imports 
import csv

import modules.Universal as uni

# load config
config = uni.load_config()


class FileFramework:    
    SAVE = config["SAVE"]
    LOAD = config["LOAD"]
    MARKER = config["MARKER"]
    DIALECT = config["DIALECT"]
    
    def __init__(self):
        csv.register_dialect(self.DIALECT["name"], 
                             delimiter = self.DIALECT["delimiter"], 
                             quoting = self.DIALECT["quoting"])
        self.dialect = self.DIALECT["name"]