#!/usr/bin/python

from flask import Flask, request, render_template, abort
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import database_helper as db
import checker
import string
import random
import json
import re
import crypto

from User import User
from Message import Message, MessageList
from ReturnedData import ReturnedData

app = Flask(__name__)

LPORT = 8080
LADDR = "127.0.0.1"

connected_users = dict()# dict (email and socket)

# START route declarations
@app.route("/lib/cryptoJS-3.1.2/rollups/hmac-sha256.js")
def libcryptojshmacsha256():
    return app.send_static_file("lib/cryptoJS-3.1.2/rollups/hmac-sha256.js")

@app.route("/lib/cryptoJS-3.1.2/components/core-min.js")
def libcryptojscore():
    return app.send_static_file("lib/cryptoJS-3.1.2/components/core-min.js")

@app.route("/lib/cryptoJS-3.1.2/components/hmac.js")
def libcryptojshmac():
    return app.send_static_file("lib/cryptoJS-3.1.2/components/hmac.js")

@app.route("/lib/jquery/jquery-3.1.1.min.js")
def libJqueryjs():
    return app.send_static_file("lib/jquery/jquery-3.1.1.min.js")

@app.route("/lib/bootstrap-3.3.7/css/bootstrap.min.css")
def libBootstrapcss():
    return app.send_static_file("lib/bootstrap-3.3.7/css/bootstrap.min.css")

@app.route("/lib/bootstrap-3.3.7/js/bootstrap.min.js")
def libBootstrapjs():
    return app.send_static_file("lib/bootstrap-3.3.7/js/bootstrap.min.js")

@app.route("/lib/c3-0.4.11/c3.min.css")
def libc3css():
    return app.send_static_file("lib/c3-0.4.11/c3.min.css")

@app.route("/lib/c3-0.4.11/c3.min.js")
def libc3js():
    return app.send_static_file("lib/c3-0.4.11/c3.min.js")

@app.route("/lib/d3/d3.v3.min.js")
def libd3js():
    return app.send_static_file("lib/d3/d3.min.js")

@app.route("/client.js")
def clientjs():
    return app.send_static_file("client.js")

@app.route("/client.css")
def clientcss():
    return app.send_static_file("client.css")

@app.route("/wimage.png")
def wimage():
    return app.send_static_file("twidder_header.png")

@app.route("/dragImage.png")
def dragImage():
    return app.send_static_file("dragimage.png")

@app.route('/')
def index():
    return render_template('client.html')

# END route declarations

def token_generator(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# Sends a websocket message to the connected users
def send_to_websocket(msg, email=False):
    if email:
        if email in connected_users:
            s = connected_users[email]
            s.send(ReturnedData(False, msg).createJSON())
    else: # if email is false, the message is broadcast
        for m, s in connected_users.iteritems():
            s.send(ReturnedData(False, msg).createJSON())

# START WS functions

"""
Gets a request from the client and saves the websocket to use it in the
future.
"""
@app.route("/connect")
def connect():
    try:
        if request.environ.get("wsgi.websocket"):
            ws = request.environ['wsgi.websocket']
            jdata = ws.receive()
            data = json.loads(jdata)["data"]
            hmac = json.loads(jdata)["hmac"]
            valid, response = checker.check_HMAC(data, hmac)
            if not valid:
                ws.send(response)
                return ""
            data = json.loads(data)
            userId = db.get_userId_by_email(data["email"])
            if userId == None:
                ws.send(ReturnedData(False, "You are not loged in!").createJSON())
                return ""

            email = db.get_user_by_id(userId).email
            connected_users[email] = ws

            while True: # keep socket open
                try:
                    obj = ws.receive()
                    if obj == None:
                        del connected_users[email]
                        ws.close()
                except:
                    break
            return ''
        else:
            ws.send(ReturnedData(False, "Bad request!").createJSON())

        return ""
    except:
        abort(500)


"""
Returns the number of current users and the connected users.
"""
@app.route("/get_current_conn_users")
def get_current_conn_users():
    try:
        ws = request.environ['wsgi.websocket']
        jdata = ws.receive()
        data = json.loads(jdata)["data"]
        hmac = json.loads(jdata)["hmac"]
        valid, response = checker.check_HMAC(data, hmac)
        if not valid:
            ws.send(response)
            return ""
        data = json.loads(data)
        userId = db.get_userId_by_email(data["email"])
        if userId == None:
            ws.send(ReturnedData(False, "You are not loged in!").createJSON())
            return ""

        total_users = db.get_user_number()
        conn_users = db.get_session_number()
        rt = {}
        rt["totalUsers"] = total_users
        rt["connectedUsers"] = conn_users
        rt = json.dumps(rt)
        ws.send(ReturnedData(True, "Got Data", rt).createJSON())
        return ""
    except:
        abort(500)

"""
Returns a list with the connections per hour.
"""
@app.route("/get_conn_user_history")
def get_conn_user_history():
    try:
        ws = request.environ['wsgi.websocket']
        jdata = ws.receive()
        data = json.loads(jdata)["data"]
        hmac = json.loads(jdata)["hmac"]
        valid, response = checker.check_HMAC(data, hmac)
        if not valid:
            ws.send(response)
            return ""
        data = json.loads(data)
        userId = db.get_userId_by_email(data["email"])
        if userId == None:
            ws.send(ReturnedData(False, "You are not loged in!").createJSON())
            return ""

        conn = db.get_today_logs()
        conn = json.dumps(conn)
        ws.send(ReturnedData(True, "Got Data", conn).createJSON())
        return ""
    except:
        abort(500)


# END WS functions

# START HTTP functions

"""
Handles sign ins, checks if the imput data is correct, if so it returns a token
and stores the user as connected.
"""
@app.route("/sign_in", methods=["POST"])
def sign_in():
    try:
        data = request.get_json(silent = True)["data"]
    except:
        abort(400)

    valid, response = checker.check_sign_in_data(data)
    if not valid:
        return response

    try:
        data = json.loads(data)
        userId = db.get_userId_by_email(data["email"])
        if userId == None:
            return ReturnedData(False, "Email not found").createJSON()
        else:
            user = db.get_user_by_id(userId)
            if user.password != crypto.get_hash(data["password"], user.salt):
                return ReturnedData(False, "The password is not correct").createJSON()
            else:

                if data["email"] in connected_users:
                    send_to_websocket("close:session", data["email"])
                    del connected_users[data["email"]]

                db.delete_session_by_email(data["email"])

                token = token_generator()

                jToken = {}
                jToken["token"] = token
                jToken["email"] = user.email
                jToken = json.dumps(jToken)


                if not create_session(token, userId):
                    abort(500)
                if not insert_log(userId):
                    abort(500)

                return ReturnedData(True, "User signed in", jToken).createJSON()
    except:
        abort(500)

# Creates a session and makes all the clients to update their diagrams
def create_session(token, userId):
    send_to_websocket("reload:connected")
    return db.create_session(token, userId)

# Inserts a user to the log and makes all the clients to update their diagrams
def insert_log(userId):
    send_to_websocket("reload:log")
    return db.insert_log(userId)


"""
Checks if sign up data is correct, if so a new user is created.
"""
@app.route("/sign_up", methods=["POST"])
def sign_up():
    try:
        data = request.get_json(silent = True)["data"] # get data
    except:
        abort(400)
    valid, response = checker.check_sign_up_data(data)
    if not valid:
        return response
    try:
        data = json.loads(data)
        if db.get_userId_by_email(data["email"]) != None:  # no success
            return ReturnedData(False, "Email already exists").createJSON()
        else:
            salt = crypto.create_salt()
            hashed_pw = crypto.get_hash(data["password"], salt) # hash the password with salt
            user = User(data["email"], hashed_pw, salt, data["firstname"],
                        data["familyname"], data["gender"], data["city"], data["country"])
            db.insert_user(user)
            return ReturnedData(True, "User successfully created").createJSON()
    except:
        abort(500)


"""
Deletes a user from the session table so it's not longer connected.
"""
@app.route("/sign_out", methods=["POST"])
def sign_out():
    try:
        data = request.get_json(silent = True)["data"]
        hmac = request.get_json(silent = True)["hmac"]
    except:
        abort(400)
    valid, response = checker.check_HMAC(data, hmac)
    if not valid:
        return response
    try:
        data = json.loads(data)
        if delete_session_by_email(data["email"]):
            del connected_users[data["email"]]
        return ReturnedData(True, "Signed out").createJSON()
    except:
        abort(500)

# Deletes a session and makes all the clients to update their diagrams
def delete_session_by_email(email):
    send_to_websocket("reload:connected")
    return db.delete_session_by_email(email)


"""
Checks if the password is correct, if so the new password and the new salt are
stored in the database.
"""
@app.route("/change_password", methods=["POST"])
def change_password():
    try:
        data = request.get_json(silent = True)["data"]
        hmac = request.get_json(silent = True)["hmac"]
    except:
        abort(400)
    valid, response = checker.check_change_password_data(data, hmac)
    if not valid:
        return response
    try:
        data = json.loads(data)
        userId = db.get_userId_by_email(data["email"])
        user = db.get_user_by_id(userId)
        if user.password != crypto.get_hash(data["old_password"], user.salt):
            return ReturnedData(False, "The password is not correct").createJSON()
        else:
            salt = crypto.create_salt()
            enc_password = crypto.get_hash(data["new_password"], salt)
            db.change_user_password(userId, enc_password, salt)
            return ReturnedData(True, "Password changed").createJSON()
    except:
        abort(500)

"""
Returns data from the current user.
"""
@app.route("/get_user_data", methods=["POST"])
def get_user_data():
    try:
        data = request.get_json(silent = True)["data"]
        hmac = request.get_json(silent = True)["hmac"]
    except:
        abort(400)
    valid, response = checker.check_HMAC(data, hmac)
    if not valid:
        return response
    try:
        data = json.loads(data)
        userId = db.get_userId_by_email(data["email"])
        user = db.get_user_by_id(userId)
        return ReturnedData(True, "User found", user.createJSON()).createJSON()
    except:
        abort(500)


"""
Returns data from a user knowing it's email.
"""
@app.route("/get_user_data_by_email", methods=["POST"])
def get_user_data_by_email():
    try:
        data = request.get_json(silent = True)["data"]
        hmac = request.get_json(silent = True)["hmac"]
    except:
        abort(400)
    valid, response = checker.check_search_data(data, hmac)
    if not valid:
        return response
    try:
        data = json.loads(data)
        userId = db.get_userId_by_email(data["userEmail"])
        if userId == None:
            return ReturnedData(False, "Invalid email").createJSON()
        else:
            user = db.get_user_by_id(userId)
            return ReturnedData(True, "User found", user.createJSON()).createJSON()
    except:
        abort(500)


"""
Returns all the messages of the current user
"""
@app.route("/get_user_messages", methods=["POST"])
def get_user_messages():
    try:
        data = request.get_json(silent = True)["data"]
        hmac = request.get_json(silent = True)["hmac"]
    except:
        abort(400)
    valid, response = checker.check_HMAC(data, hmac)
    if not valid:
        return response
    try:
        data = json.loads(data)
        userId = db.get_userId_by_email(data["email"])
        messages = db.get_messages_by_user(userId)
        return ReturnedData(True, "Messages found", messages.createJSON()).createJSON()
    except:
        abort(500)

"""
Returns all the messages of a user knowing it's email
"""
@app.route("/get_user_messages_by_email", methods=["POST"])
def get_user_messages_by_email():
    try:
        data = request.get_json(silent = True)["data"]
        hmac = request.get_json(silent = True)["hmac"]
    except:
     abort(400)
    valid, response = checker.check_search_data(data, hmac)
    if not valid:
        return response
    try:
        data = json.loads(data)
        userId = db.get_userId_by_email(data["userEmail"])
        if userId == None:
            return ReturnedData(False, "Invalid email").createJSON()
        else:
            messages = db.get_messages_by_user(userId)
            return ReturnedData(True, "Messages found", messages.createJSON()).createJSON()
    except:
        abort(500)

"""
Sends a message from the current user to a given user.
"""
@app.route("/send_message", methods=["POST"])
def send_message():
    try:
        data = request.get_json(silent = True)["data"]
        hmac = request.get_json(silent = True)["hmac"]
    except:
        abort(400)
    valid, response = checker.check_send_message_data(data, hmac)
    if not valid:
        return response
    try:
        data = json.loads(data)
        writerId = db.get_userId_by_email(data["email"])
        writer = db.get_user_by_id(writerId)

        msg = Message(writer.email, data["reader"], data["msg"])
        toId = db.get_userId_by_email(msg.reader)
        if toId == None:
            return ReturnedData(False, "Invalid reader").createJSON()

        fromId = db.get_userId_by_email(msg.writer)
        if fromId == None:
            return ReturnedData(False, "Invalid writer").createJSON()
        else:
            insert_message(msg)
            return ReturnedData(True, "Message sent").createJSON()
    except:
        abort(500)

# Inserts a message to the reader and makes him reload the messages
def insert_message(msg):
    db.insert_message(msg)
    send_to_websocket("reload:messages", msg.reader)


if __name__ == "__main__":
    print "Starting test server at "+LADDR+":"+str(LPORT)
    http_server = pywsgi.WSGIServer((LADDR, LPORT), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
