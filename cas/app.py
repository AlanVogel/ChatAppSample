import os
import datetime
from flask import (
    request,
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
    update_conversation,
    delete_message_by_id,
    delete_conversation_by_id,
)
from cas.utils import (
    authorization,
    app,
    random_string,
    encode_security_token,
    ok_response,
    error_response,
    now,
)
from validation import (
    RegisterUserCheck,
    RoomCheck,
    RoomJoinLeave,
    MessageCheck,
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
    return error_response(message='Wrong email', status_code=400)


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


@app.route('/user/<int:id>', methods=['GET'])
@authorization
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


@app.route('/create_room', methods=['POST'])
@authorization
def create_room():
    data = request.get_json()
    if RoomCheck(**data):
        with Session.begin() as session:
            session.add(
                Conversation(conversation_name=data.get('room_name')))
            user = session.query(User).filter(
                User.nick_name == data.get('nick_name')).first()
            conversation = session.query(Conversation).filter(
                Conversation.conversation_name == data.get(
                    'room_name')).first()
            session.add(ConversationUser(user_id=user.id,
                                         conversation_id=conversation.id))
            session.commit()
        return ok_response(message='Room created', **{
            'req': {'user': data, 'header': request.headers.get('user_id')}})


@app.route('/join_room', methods=['POST'])
@authorization
def join_room():
    data = request.get_json()
    if RoomJoinLeave(**data):
        with Session.begin() as session:
            user = session.query(User).filter(
                User.nick_name == data.get('nick_name')).first()
            conv_user = session.query(ConversationUser).filter(
                ConversationUser.user_id == user.id).first()
            if not conv_user:
                return error_response(
                    message=f'conversation for user {user.nick_name} does no '
                            f'exist!',
                    status_code=404)
            conversation = session.query(Conversation).filter(
                Conversation.conversation_name == data.get(
                    'room_name')).first()
            if conversation.joined:
                return error_response(message='You are already joined',
                                      status_code=400)
            update_conversation(session, conversation, joined=True)
            session.commit()
        return ok_response(
            message=f'You joined the room: {data.get("room_name")}', **data)


@app.route('/leave_room', methods=['POST'])
@authorization
def leave_room():
    data = request.get_json()
    if RoomJoinLeave(**data):
        with Session.begin() as session:
            user = session.query(User).filter(
                User.nick_name == data.get('nick_name')).first()
            conv_user = session.query(ConversationUser).filter(
                ConversationUser.user_id == user.id).first()
            if not conv_user:
                return error_response(
                    message=f'conversation for user {user.nick_name} does no '
                            f'exist!',
                    status_code=404)
            conversation = session.query(Conversation).filter(
                Conversation.conversation_name == data.get(
                    'room_name')).first()
            if not conversation.joined:
                return error_response(message='You are already leaved',
                                      status_code=400)
            update_conversation(session, conversation, joined=False)
            session.commit()
        return ok_response(
            message=f'You leaved the room: {data.get("room_name")}', **data)


@app.route('/send_msg', methods=['POST'])
@authorization
def send_msg():
    data = request.get_json()
    if MessageCheck(**data):
        with Session.begin() as session:
            user = session.query(User).filter(
                User.nick_name == data.get('nick_name')).first()
            conv = session.query(Conversation).filter(
                Conversation.conversation_name == data.get(
                    "room_name")).first()
            if not conv.joined:
                return error_response(
                    message='You are not joined to the conversation',
                    status_code=404)
            session.add(Message(msg=data.get('msg'), created_at=now(),
                                sender_id=user.id))
            msg = session.query(Message).filter(
                Message.msg == data.get('msg')).first()
            session.add(ConversationMessage(conversation_id=conv.id,
                                            message_id=msg.id))
            session.commit()
        return ok_response(message='message is successfully send!', **data)
    return error_response(message='something went wrong!', status_code=500)


@app.route('/list_con/<int:id>', methods=['GET'])
@authorization
def lst_of_conversations(id):
    conv_data = {}
    with Session.begin() as session:
        user = session.query(User).filter(User.id == id).first()
        user_id = user.id
        conv_user = session.query(ConversationUser).filter(
            ConversationUser.user_id == user_id).all()
        for all_con in conv_user:
            conv_data['Room {0}'.format(
                all_con.id)] = all_con.conversation.conversation_name
        return ok_response(message='Success!', **{
            'conversation_data': {'rooms': conv_data}})


@app.route('/delete_con/<int:id>', methods=['DELETE'])
@authorization
def delete_conversation(id):
    with Session.begin() as session:
        user = session.query(User).filter(User.id == id).first()
        user_id = user.id
        conv_user = session.query(ConversationUser).filter(
            ConversationUser.user_id == user_id).first()
        conv_user_id = conv_user.id
        delete_conversation_by_id(session, conv_user_id)
        session.commit()
        return ok_response(message='Conversation deleted!')


@app.route('/delete_msg/<int:id>', methods=['DELETE'])
@authorization
def delete_message(id):
    with Session.begin() as session:
        user = session.query(User).filter(User.id == id).first()
        user_id = user.id
        msg = session.query(Message).filter(
            Message.sender_id == user_id).first()
        msg_id = msg.id
        delete_message_by_id(session, msg_id)
        session.commit()
        return ok_response(message='Message deleted!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
