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
    User,
    Message,
    Conversation,
    ConversationUser,
    ConversationMessage,
    Session,
    update_user,
)
from cas.utils import (
    token_required,
    app,
    random_string,
    encode_security_token,
    decode_security_token,
    ok_response,
    error_response,
)
from validation import (
    RegisterUserCheck,
)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key'
db = SQLAlchemy(app)
recreate_database()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if RegisterUserCheck(**data):
        with Session.begin() as session:
            session.add(
                User(nick_name=data.get('nick_name'),
                     password=data.get('password'), email=data.get('email')))
            session.commit()
        return ok_response(message='User created!', **data)
    return jsonify({'error': 'wrong email, try again!'}), 400


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        with Session.begin() as session:
            user = session.query(User).filter(
                User.email == data.get('email')).first()
            if not user:
                return error_response(message='user does no exist!',
                                      status_code=404)
            user_id = user.id
            user_name = user.nick_name
            key_word = random_string(64)
            update_user(session, user, key_word=key_word)
            token = encode_security_token(user_id, user_name, key_word)
            session.commit()
    except BaseException as ex:
        print(ex)
        return error_response(message='something went wrong!', status_code=500)
    return ok_response(message='Success!', **{
        'data': {'Authorization': token, 'user_id': user_id}})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    # request.headers.get()
    date = datetime.datetime.utcnow()
    with Session.begin() as session:
        user = session.query(User).filter(
            User.nick_name == data.get('nick_name')).first()
        session.add(Message(msg=data.get('msg'), created_at=date,
                            sender_id=user.id))
        session.add(
            Conversation(conversation_name=data.get('conversation_name')))
        conversation_user = session.query(Conversation).filter(
            Conversation.conversation_name == data.get(
                'conversation_name')).first()
        session.add(ConversationUser(user_id=user.id,
                                     conversation_id=conversation_user.id))
        message = session.query(Message).filter(
            Message.msg == data.get('msg')).first()
        session.add(ConversationMessage(conversation_id=conversation_user.id,
                                        message_id=message.id))
        session.commit()
    return jsonify({'success': 'Chat created!'}), 200


@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    with Session.begin() as session:
        user = session.query(User).filter(User.id == id).first()
        user_id = user.id
        user_name = user.nick_name
        user_pass = user.password
        user_email = user.email
        user_key = user.key_word
    return ok_response(message='Success!', **{
        'data': {'id': user_id, 'nick_name': user_name, 'password': user_pass,
                 'email': user_email, 'key_word': user_key}})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
