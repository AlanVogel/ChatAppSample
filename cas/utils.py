import jwt
import json
import random
import string
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    request,
    jsonify,
)
from cas.database import (
    User,
    Session,
    update_user,
)

app = Flask(__name__)


def now() -> datetime:
    return datetime.now()


def random_string(size):
    return ''.join(
        [random.choice(string.ascii_letters + string.digits) for n in
         range(size)])


def encode_security_token(user_id: int, nick_name: str, key_word: str):
    """
    The function will encode the security token.
    :param user_id:
    :param nick_name:
    :param key_word:
    :return: False or hash (str)
    """
    return jwt.encode(
        {"user_id": user_id,
         "nick_name": nick_name,
         }, key_word, algorithm='HS256')


def decode_security_token(token: str, key_word: str):
    """
    The function will decode the security token.
    :param token:
    :param key_word:
    :return: False or user data (dict)
    """
    try:
        return jwt.decode(token, key_word, algorithms='HS256')
    except jwt.ExpiredSignatureError:
        return jwt.ExpiredSignatureError("Signature has expired.")
    except Exception as ex:
        return Exception(f"Something is wrong with security-token. {str(ex)}")


def ok_response(message, status_code=200, **additional_data):
    """
    The function will create https ok response
    :param message:
    :param status_code:
    :param additional_data:
    :return: response object: dict
    """
    data = {
        'status': 'OK',
        'code': status_code,
        'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
        'message': message,
    }
    for k, v in additional_data.items():
        data['{0}'.format(k)] = v
    return jsonify({"info": {'data': data}, "status_code": status_code})


def error_response(message, status_code):
    """
    The function will create https error response
    :param message:
    :param status_code:
    :return: response object: dict
    """
    data = {
        'status': 'ERROR',
        'code': status_code,
        'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
        'message': message
    }

    return jsonify({"info": {'data': data}, "status_code": status_code})


def authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get('user_id')
        with Session.begin() as session:
            user = session.query(User).filter(
                User.id == header).first()
            if not user:
                return error_response(message='user does no exist!',
                                      status_code=404)
            user_id = user.id
            user_name = user.nick_name
            key_word = user.key_word
            if not key_word:
                key_word = random_string(64)
                update_user(session, user, key_word=key_word)
            token = encode_security_token(user_id, user_name, key_word)
            if not token:
                return error_response(message='Token does not exist!',
                                      status_code=404)
            session.commit()
        try:
            dec_token = decode_security_token(token, key_word)
            return f(*args, **kwargs)
        except:
            return error_response(message='Authorization failed!',
                                  status_code=404)
    return decorated
