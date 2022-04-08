import jwt
import json
import random
import string
from datetime import datetime
from flask import (
    Flask,
    request,
    jsonify,
)
from functools import wraps

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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 400
        try:
            header_data = jwt.get_unverified_header(token)
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=header_data['alg'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 400
        return f(*args, **kwargs)

    return decorated
