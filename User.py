import json

class User(object):

    def __init__(self, email, password, salt, firstname, familyname, gender, city, country):
        self.firstname = firstname
        self.familyname = familyname
        self.email = email
        self.city = city
        self.country = country
        self.gender = gender
        self.password = password
        self.salt = salt
        

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
