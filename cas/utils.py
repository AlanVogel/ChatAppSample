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


def refresh_security_token():
    try:
        user_id = int(request.headers.get('user_id'))
        with Session.begin() as session:
            user = get_user_by_id(session, user_id)
            update_user(session, user, key_word=random_string(64))
            token = encode_security_token(user.id, user.nick_name,
                                          user.key_word)
            return ok_response(
                message='Security token has successfully updated!',
                **{'User_id': user.id, 'Authorization': token})
    except BaseException as ex:
        print(ex)
        return error_response(
            message='Something went wrong refreshing the security token',
            status_code=500)


def authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            data = request.get_json()
            user_id = int(request.headers.get('user_id'))
            auth_token = request.headers.get('authorization')
            with Session.begin() as session:
                user = get_user_by_id(session, data.get('user_id'))
                key_word = user.key_word
                session.commit()
            response = decode_security_token(auth_token, key_word)
            if response.get('user_id') == user_id:
                return f(*args, **kwargs)
        except Exception as ex:
            print(ex)
            return error_response(
                message=f'Authorization error: wrong security-token',
                status_code=401)

    return decorated
