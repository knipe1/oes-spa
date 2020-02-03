
# imports 
import csv

import modules.Universal as uni

# load config
config = uni.load_config()
DIALECT = config["DIALECT"]

class FileFramework:    
    def __init__(self):
        csv.register_dialect(DIALECT["name"], 
                             delimiter = DIALECT["delimiter"], 
                             quoting = DIALECT["quoting"])
        self.dialect = DIALECT["name"]