import json

class Message(object):

    def __init__(self, writer, reader, content): #writer and reader are emails
        self.writer = writer
        self.reader = reader
        self.content = content

    def Message(self):
        return self

    def createJSON(self):
        rdata = {}
        rdata["writer"] = self.writer
        rdata["reader"] = self.reader
        rdata["content"] = self.content

        return json.dumps(rdata)

class MessageList(object):

    def __init__(self):
        self.messages = []

    def append(self, msg):
        self.messages.append(msg)

    def createJSON(self):
        data = ""
        for msg in self.messages:
            data += msg.createJSON()+","

        data = "["+data[:-1]+"]"

        return data
