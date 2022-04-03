import re
import jwt
from flask import (
    Flask,
    request,
    jsonify,
)
from functools import wraps

app = Flask(__name__)


def email_validator(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True
    else:
        return False


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
