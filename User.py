import json

class User(object):

    def __init__(self, email, password, firstname, familyname, gender, city, country):
        self.firstname = firstname
        self.familyname = familyname
        self.email = email
        self.city = city
        self.country = country
        self.gender = gender
        self.password = password

    def User(self):
        return self

    def createJSON(self):
        data = {}
        data["firstname"] = self.firstname
        data["familyname"] = self.familyname
        data["email"] = self.email
        data["city"] = self.city
        data["country"] = self.country
        data["gender"] = self.gender
        # Password is not sent because security reasons

        return json.dumps(data)
