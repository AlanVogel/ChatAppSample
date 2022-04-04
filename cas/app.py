import os
import datetime
import jwt
from flask import (
    request,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from cas.database import (
    recreate_database,
    session,
    User,
    Message,
    Conversation,
    ConversationUser,
    ConversationMessage,
)
from cas.utils import (
    email_validator,
    token_required,
    app,
)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key'
db = SQLAlchemy(app)
recreate_database()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if email_validator(data['email']):
        session.add(User(nick_name=data['nick_name'], email=data['email'],
                         key_word=data['key_word']))
        session.commit()
        return jsonify({'success': 'User created!'}), 200
    return jsonify({'error': 'wrong email, try again!'}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = session.query(User).filter(User.email == data['email']).first()
    if user.email == data['email']:
        token = jwt.encode({'user': user.nick_name,
                            'exp': datetime.datetime.utcnow() + \
                                   datetime.timedelta(
                                       minutes=15)}, app.config['SECRET_KEY'])
        header_data = jwt.get_unverified_header(token)
        return jsonify({'decoded_token': jwt.decode(token,
                                                    app.config['SECRET_KEY'],
                                                    algorithms=header_data[
                                                        'alg']),
                        'token': token}), 200
    return jsonify({'error': 'could not verify!'}), 400


@app.route('/chat', methods=['POST'])
@token_required
def chat():
    data = request.get_json()
    user = session.query(User).filter(
        User.nick_name == data['nick_name']).first()
    date = datetime.datetime.utcnow()
    session.add(Message(msg=data['msg'], created_at=date,
                        sender_id=user.id))
    session.add(Conversation(conversation_name=data['conversation_name']))
    conversation_user = session.query(Conversation).filter(
        Conversation.conversation_name == data['conversation_name']).first()
    session.add(ConversationUser(user_id=user.id,
                                 conversation_id=conversation_user.id))
    message = session.query(Message).filter(Message.msg == data['msg']).first()
    session.add(ConversationMessage(conversation_id=conversation_user.id,
                                    message_id=message.id))
    session.commit()
    return jsonify({'success': 'Chat created!'}), 200


@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = session.query(User).filter(User.id == id).first()
    del user.__dict__['_sa_instance_state']
    return jsonify(user.__dict__), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
