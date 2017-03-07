import json
"""
This class defines the data object that the client is expecting to get
"""
class ReturnedData(object):

    def __init__(self, success, message, data = ''):
        self.success = success
        self.message = message
        self.data = data # sometimes data is not needed

    def createJSON(self):
        rdata = {}
        rdata["success"] = self.success
        rdata["message"] = self.message
        if self.data: # if data exists, add it to the json
            rdata["data"] = "DATAHERE"
            rt = json.dumps(rdata)
            rt = rt.replace('"DATAHERE"', self.data)
        else:
            rt = json.dumps(rdata)

        return rt
