import hmac
import base64
import hashlib
import string
import random

def create_salt(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_hash(password, salt):
    return hashlib.sha256(password+salt).hexdigest()


def get_hmac(data, key):
    try:
        b64data = base64.b64encode(data);
        shmac = hmac.HMAC(str(key), b64data, hashlib.sha256).hexdigest()
        print shmac
        return shmac
    except:
        return False
