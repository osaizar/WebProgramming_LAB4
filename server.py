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


#TODO: WS exceptions
#TODO: Dividir en archivos

app = Flask(__name__)

LPORT = 8080
LADDR = "127.0.0.1"

connected_users = dict()# dict (email and socket)

# START route declarations

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
    return app.send_static_file("wimage.png")

@app.route("/dragImage.png")
def dragImage():
    return app.send_static_file("dragimage.png")

@app.route('/')
def index():
    return render_template('client.html')

# END route declarations


# START WS functions
@app.route("/connect")
def connect():
    if request.environ.get("wsgi.websocket"):
        ws = request.environ['wsgi.websocket']
        data = ws.receive()
        data = json.loads(data)
        valid, response = checker.check_token(data)
        if not valid:
            ws.send(response)
            return ""
        userId = db.get_userId_by_token(data["token"])
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

@app.route("/get_current_conn_users")
def get_current_conn_users():
    ws = request.environ['wsgi.websocket']
    data = ws.receive()
    data = json.loads(data)
    valid, response = checker.check_token(data)
    if not valid:
        ws.send(response)
        return ""
    userId = db.get_userId_by_token(data["token"])
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


@app.route("/get_conn_user_history")
def get_conn_user_history():
    ws = request.environ['wsgi.websocket']
    data = ws.receive()
    data = json.loads(data)
    valid, response = checker.check_token(data)
    if not valid:
        ws.send(response)
        return ""
    userId = db.get_userId_by_token(data["token"])
    if userId == None:
        ws.send(ReturnedData(False, "You are not loged in!").createJSON())
        return ""

    conn = db.get_today_logs()
    conn = json.dumps(conn)
    ws.send(ReturnedData(True, "Got Data", conn).createJSON())
    return ""


# END WS functions

def token_generator(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json(silent = True) # get data
    valid, response = checker.check_sign_in_data(data)
    if not valid:
        return response
    try:
        userId = db.get_userId_by_email(data["email"])
        if userId == None:
            return ReturnedData(False, "Email not found").createJSON()
        else:
            user = db.get_user_by_id(userId)
            if user.password != crypto.get_hash(data["password"], user.salt):
                return ReturnedData(False, "The password is not correct").createJSON()
            else:
                if data["email"] in connected_users:
                    s = connected_users[data["email"]]
                    s.send(ReturnedData(False, "close:session").createJSON())
                    db.delete_token_by_email(data["email"])
                    del connected_users[data["email"]]

                token = token_generator()

                db.insert_token(token, userId)
                jToken = {}
                jToken["token"] = token
                jToken = json.dumps(jToken)

                db.insert_log(userId)

                return ReturnedData(True, "User signed in", jToken).createJSON()
    except:
        abort(500)

@app.route("/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json(silent = True) # get data
    valid, response = checker.check_sign_up_data(data)
    if not valid:
        return response
    try:
        if db.get_userId_by_email(data["email"]) != None:  # no success
            return ReturnedData(False, "Email already exists").createJSON()
        else:
            salt = crypto.create_salt()
            hashed_pw = crypto.get_hash(data["password"], salt)
            user = User(data["email"], hashed_pw, salt, data["firstname"],
                        data["familyname"], data["gender"], data["city"], data["country"])
            db.insert_user(user)
            return ReturnedData(True, "User successfully created").createJSON()
    except:
        abort(500)

@app.route("/sign_out", methods=["POST"])
def sign_out():
    data = request.get_json(silent = True)
    valid, response = checker.check_token(data)
    if not valid:
        return response
    try:
        userId = db.get_userId_by_token(data["token"])
        if userId != None:
            email = db.get_user_by_id(userId).email
            if email != None:
                if db.delete_token(data["token"]):
                    del connected_users[email]
                return ReturnedData(True, "Signed out").createJSON()
            else:
                return ReturnedData(True, "Invalid email").createJSON() # no deberia salir nunca

        else:
            return ReturnedData(False, "You are not logged in (Invalid token)").createJSON()
    except:
        abort(500)


@app.route("/change_password", methods=["POST"])
def change_password():
    data = request.get_json(silent = True)
    valid, response = checker.check_change_password_data(data)
    if not valid:
        return response
    try:
        userId = db.get_userId_by_token(data["token"])
        user = user = db.get_user_by_id(userId)
        if userId == None:
            return ReturnedData(False, "The token is not correct").createJSON()
        elif user.password != crypto.get_hash(data["old_password"], user.salt):
            return ReturnedData(False, "The password is not correct").createJSON()
        else:
            salt = crypto.create_salt()
            enc_password = crypto.get_hash(data["new_password"], salt)
            db.change_user_password(userId, enc_password, salt)
            return ReturnedData(True, "Password changed").createJSON()
    except:
        abort(500)

@app.route("/get_user_data_by_token", methods=["POST"])
def get_user_data_by_token():
    data = request.get_json(silent = True)
    valid, response = checker.check_token(data)
    if not valid:
        return response
    try:
        userId = db.get_userId_by_token(data["token"])
        if userId == None:
            return ReturnedData(False, "You are not logged in (Invalid token)").createJSON()
        else:
            user = db.get_user_by_id(userId)
            return ReturnedData(True, "User found", user.createJSON()).createJSON()
    except:
        abort(500)


@app.route("/get_user_data_by_email", methods=["POST"]) #TODO: Name changed, remember to change it on lab3
def get_user_data_by_email():
    data = request.get_json(silent = True)
    valid, response = checker.check_token_and_email(data)
    if not valid:
        return response
    try:
        myUserId = db.get_userId_by_token(data["token"])
        if myUserId  == None:
            return ReturnedData(False, "You are not logged in (Invalid token)").createJSON()
        else:
            userId = db.get_userId_by_email(data["email"])
            if userId == None:
                return ReturnedData(False, "Invalid email").createJSON()
            else:
                user = db.get_user_by_id(userId)
                return ReturnedData(True, "User found", user.createJSON()).createJSON()
    except:
        abort(500)

@app.route("/get_user_messages_by_token", methods=["POST"])
def get_user_messages_by_token():
    data = request.get_json(silent = True)
    valid, response = checker.check_token(data)
    if not valid:
        return response
    try:
        userId = db.get_userId_by_token(data["token"])

        if userId == None:
            return ReturnedData(False, "You are not logged in (Invalid token)").createJSON()
        else:
            messages = db.get_messages_by_user(userId)
            return ReturnedData(True, "Messages found", messages.createJSON()).createJSON()
    except:
        abort(500)


@app.route("/get_user_messages_by_email", methods=["POST"])
def get_user_messages_by_email():
    data = request.get_json(silent = True)
    valid, response = checker.check_token_and_email(data)
    if not valid:
        return response
    try:
        if db.get_userId_by_token(data["token"]) == None:
            return ReturnedData(False, "You are not logged in (Invalid token)").createJSON()
        else:
            userId = db.get_userId_by_email(data["email"])
            if userId == None:
                return ReturnedData(False, "Invalid email").createJSON()
            else:
                messages = db.get_messages_by_user(userId)
                return ReturnedData(True, "Messages found", messages.createJSON()).createJSON()
    except:
        abort(500)

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json(silent = True)
    valid, response = checker.check_send_message_data(data)
    if not valid:
        return response
    try:
        writerId = db.get_userId_by_token(data["token"])
        if writerId == None:
            return ReturnedData(False, "You are not logged in (You are not logged in (Invalid token))").createJSON()

        writer = db.get_user_by_id(writerId)

        msg = Message(writer.email, data["reader"], data["msg"])
        toId = db.get_userId_by_email(msg.reader)
        if toId == None:
            return ReturnedData(False, "Invalid reader").createJSON()

        fromId = db.get_userId_by_email(msg.writer)
        if fromId == None:
            return ReturnedData(False, "Invalid writer").createJSON()
        else:
            db.insert_message(msg)
            return ReturnedData(True, "Message sent").createJSON()
    except:
        abort(500)

if __name__ == "__main__":
    print "Starting server at "+LADDR+":"+str(LPORT)
    http_server = pywsgi.WSGIServer((LADDR, LPORT), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
