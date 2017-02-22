import json

class ReturnedData(object):

    def __init__(self, success, message, data = ''):
        self.success = success
        self.message = message
        self.data = data

    def createJSON(self):
        rdata = {}
        rdata["success"] = self.success
        rdata["message"] = self.message
        if self.data:
            rdata["data"] = "DATAHERE"
            rt = json.dumps(rdata)
            rt = rt.replace('"DATAHERE"', self.data)
        else:
            rt = json.dumps(rdata)

        return rt
