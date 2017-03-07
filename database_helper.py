import sqlite3
from datetime import datetime
from User import User
from Message import Message, MessageList


# return dictionary instead of tuple
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# runs a query and returns a cursor with dictionaries
def run_query(query):
    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory  # override function
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    return cur


# Public functions


def insert_user(user):
    cur = run_query("INSERT INTO User (firstname, familyname, gender, city, \
                    country, email, password, salt) \
                    VALUES('%s','%s','%s','%s','%s','%s','%s', '%s')" % (user.firstname,
                                                                   user.familyname, user.gender, user.city, user.country,
                                                                   user.email, user.password, user.salt))
    if cur.rowcount == 1:
        return True
    else:
        return False


def get_user_by_id(userId):
    cur = run_query("SELECT * FROM User WHERE User.id = %s" % userId)
    result = cur.fetchone()
    if result:
        user = User(result["email"], result["password"], result["salt"], result["firstname"],
                    result["familyname"], result["gender"], result["city"], result["country"])
    else:
        user = None

    return user


def get_userId_by_email(email):
    cur = run_query("SELECT id FROM User WHERE User.email = '%s'" % email)
    result = cur.fetchone()
    if result:
        userId = result["id"]
    else:
        userId = None

    return userId


def get_userId_by_token(token):
    cur = run_query("SELECT userId FROM Session WHERE token = '%s'" % token)
    result = cur.fetchone()

    if result:
        userId = result["userId"]
    else:
        userId = None

    return userId


def change_user_password(userId, password, salt):
    cur = run_query("UPDATE User SET password = '%s', salt = '%s' \
                    WHERE id = %s" % (password, salt, userId))

    if cur.rowcount == 1:
        return True
    else:
        return False


def get_user_number():
    cur = run_query("SELECT COUNT(*) as 'count' FROM User")
    result = cur.fetchone()

    return result["count"]


def create_session(token, userId):
    cur = run_query("INSERT INTO Session (token, userId)\
                    VALUES('%s', %s)" % (token, userId))
    if cur.rowcount == 1:
        return True
    else:
        return False


def get_session_token(userId):
    cur = run_query("SELECT * FROM Session WHERE userId = %s" % userId)
    result = cur.fetchone()
    if result:
        token = result["token"]
    else:
        token = None

    return token


def get_session_token_by_email(email):
    cur = run_query("SELECT * FROM Session WHERE userId = (SELECT id\
                                                           FROM User\
                                                           WHERE email = '%s')" % email)
    result = cur.fetchone()
    if result:
        token = result["token"]
    else:
        token = None

    return token


def delete_session(token):
    cur = run_query("DELETE FROM Session WHERE token = '%s'" % token)
    if cur.rowcount == 1:
        return True
    else:
        return False


def delete_session_by_email(email):
    cur = run_query("DELETE FROM Session WHERE userId = (SELECT id \
                                                         FROM User \
                                                         WHERE email = '%s')" % email)
    if cur.rowcount > 0:
        return True
    else:
        return False


def get_session_number():
        cur = run_query("SELECT COUNT(*) as 'count' FROM Session")
        result = cur.fetchone()

        return result["count"]


def insert_message(message):
    toId = get_userId_by_email(message.reader)
    fromId = get_userId_by_email(message.writer)

    cur = run_query("INSERT INTO Message (msg, toId, fromId)\
                    VALUES ('%s',%s, %s)" % (message.content, toId, fromId))
    if cur.rowcount == 1:
        return True
    else:
        return False


def get_messages_by_user(userId):
    cur = run_query("SELECT msg, toId, fromId FROM Message WHERE toId = %s" % userId)

    result = cur.fetchall()
    msgs = MessageList()
    for msg in result:
        writer = get_user_by_id(msg["fromId"])
        reader = get_user_by_id(userId)
        msgs.append(Message(writer.email, reader.email, msg["msg"]))

    return msgs


def insert_log(userId):
        cur = run_query("INSERT INTO Log (date, userId)\
                        VALUES ('%s',%s)" % (str(datetime.now()), userId))
        if cur.rowcount == 1:
            return True
        else:
            return False


def get_logs_between(date1, date2):
    cur = run_query("SELECT COUNT(*) as 'count' from Log WHERE date > '%s' \
                    and '%s' > date" % (date1, date2))

    result = cur.fetchone()

    return result["count"]


def get_today_logs():
    today = str(datetime.now()).split(" ")[0]
    yesterday = today.split("-")[0]+"-"+today.split("-")[1]+"-"+str(int(today.split("-")[2])-1)
    logs = {}
    for i in range(24):
        if i == 0:
            now = yesterday+" 00:00"
        elif i < 10:
            now = today+" 0"+str(i)+":00"
        else:
            now = today+" "+str(i)+":00"

        if i < 9:
            afternow = today+" 0"+str(i+1)+":00"
        else:
            afternow = today+" "+str(i+1)+":00"

        logs[i] = get_logs_between(now, afternow)

    return logs
