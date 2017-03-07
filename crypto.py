import hmac
import base64
import hashlib
import string
import random


def create_salt(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_hash(password, salt):
    pwsalt = password+salt

    for i in range(1000): # 1000 iterations to make it stronger
        pwsalt =  hashlib.sha256(pwsalt).hexdigest()

    return pwsalt


def get_hmac(data, key):
    try:
        b64data = base64.b64encode(data); # first encode to base64
        shmac = hmac.HMAC(str(key), b64data, hashlib.sha256).hexdigest() # then get hmac
        return shmac
    except: # the hmac.HMAC() function is not perfect, some characters are not accepted
        return None
