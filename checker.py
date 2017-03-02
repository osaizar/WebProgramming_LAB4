#!/usr/bin/python

from flask import Flask, request, render_template, abort
import database_helper as db
import crypto
import string
import random
import json
import re
import time

from User import User
from Message import Message, MessageList
from ReturnedData import ReturnedData

MAIL_RE = "[^@]+@[^@]" # something followed by @ followed by something

def check_sign_in_data(data):
    if data == None:
        abort(400)
    try:
        data = json.loads(data)
        if not (data["email"] and data["password"]):
            return False, ReturnedData(False, "Fill all fields").createJSON()
    except:
        abort(400)

    return True, None


def check_sign_up_data(data):
    if data == None:
        abort(400)
    try:
        data = json.loads(data)
        if not (data["email"] and data["firstname"] and data["familyname"] \
            and data["gender"] and data["password"] and data["city"] and data["country"]):

            return False, ReturnedData(False, "Fill all fields").createJSON()
    except:
        abort(400)

    if data["email"].isspace() or data["firstname"].isspace() or data["familyname"].isspace() \
        or data["gender"].isspace() or data["password"].isspace() or data["city"].isspace() \
        or data["country"].isspace():

        return False, ReturnedData(False, "You can't fill the fields with spaces").createJSON()
    elif len(data["password"]) < 6:
        return False, ReturnedData(False, "The password is too short").createJSON()
    elif not re.match(MAIL_RE, data["email"]):
        return False, ReturnedData(False, "The email is not valid").createJSON()
    elif data["gender"] != "Male" and data["gender"] != "Female":
        return False, ReturnedData(False, "The gender is not valid").createJSON()
    else:
        return True, None


def check_change_password_data(data, hmac):
    valid, response = check_HMAC(data, hmac)
    if not valid:
        return valid, response
    try:
        data = json.loads(data)
        if not (data["old_password"] and data["new_password"]):
            abort(400)
    except:
        abort(400)

    if len(data["new_password"]) < 6:
        return False, ReturnedData(False, "The password is too short").createJSON()
    else:
        return True, None


def check_send_message_data(data, hmac):
    valid, response = check_HMAC(data, hmac)
    if not valid:
        return valid, response
    try:
        data = json.loads(data)
        if not (data["msg"] and data["reader"]):
            abort(400)
    except:
        abort(400)

    if data["msg"].isspace():
        return False, ReturnedData(False, "The message is too short").createJSON()
    else:
        return True, None


def check_search_data(data, hmac):
    valid, response = check_HMAC(data, hmac)
    if not valid:
        return valid, response
    try:
        data = json.loads(data)
        if not data["userEmail"]:
            abort(400)
    except:
        abort(400)
    return True, None


def check_HMAC(data, hmac):
    valid, response = check_email(data)
    if not valid:
        return valid, response

    valid, response = check_timestamp(data)
    if not valid:
        return valid, response


    if hmac == None:
        abort(400)

    jdata = json.loads(data)
    token = db.get_session_token_by_email(jdata["email"])

    if token == None:
        return False, ReturnedData(False, "You are not logged in!").createJSON()

    generated_hmac = crypto.get_hmac(data, token);

    if generated_hmac == None:
        return False, ReturnedData(False, "Ilegal character in message").createJSON()

    if generated_hmac != hmac:
        return False, ReturnedData(False, "HMAC is not correct").createJSON()

    return True, None


def check_email(data):
    if data == None:
        abort(400)
    try:
        data = json.loads(data)
        if not (data["email"]):
            abort(400)
    except:
        abort(400)

    return True, None


def check_timestamp(data):
    if data == None:
        abort(400)
    try:
        data = json.loads(data)
        if not (data["timestamp"]):
            abort(400)

        timestamp  = int(time.time() / (60*5))

        if data["timestamp"] != timestamp:
            return False, ReturnedData(False, "The timestamp is not correct").createJSON()
    except:
        abort(400)

    return True, None
