import jwt
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
    Session,
    update_user,
    get_user_by_id,
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
        header = int(request.headers.get('user_id'))
        if not header:
            return error_response(message='Header: missing user_id!',
                                  status_code=404)
        auth_token = request.headers.get('authorization')
        if not auth_token:
            return error_response(message='Header: missing authorization!',
                                  status_code=404)
        with Session.begin() as session:
            user = get_user_by_id(session, header)
            if not user:
                return error_response(message='User does not exist!',
                                      status_code=404)
            key_word = user.key_word
            if not key_word:
                key_word = random_string(64)
                update_user(session, user, key_word=key_word)
            session.commit()
        try:
            decode_security_token(auth_token, key_word)
            return f(*args, **kwargs)
        except Exception as ex:
            return error_response(message='Authorization error',
                                  status_code=401)
    return decorated
