import hmac
import hashlib
import string
import random

def create_salt(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_hash(password, salt):
    return hashlib.sha256(password+salt).hexdigest()


def get_hmac(data, key):
    data = data.replace(" ", "") # python doesn't use spaces on json, eliminate all spaces
    print "key: "+key+" data: "+data
    shmac = hmac.HMAC(str(key), str(data), hashlib.sha256).hexdigest()
    print shmac
    return shmac
