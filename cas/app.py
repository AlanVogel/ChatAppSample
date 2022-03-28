import os
from flask import (
    Flask,
    request,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from database import (
    recreate_database,
    session,
    User,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
recreate_database()


@app.route('/create_user', methods=['POST'])
def create_user():
    body = request.get_json()
    session.add(User(nick_name=body['nick_name'], email=body['email'],
                     key_word=body['key_word']))
    session.commit()
    return "User created"


@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = session.query(User).filter(User.id == id).first()
    del user.__dict__['_sa_instance_state']
    return jsonify(user.__dict__)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
