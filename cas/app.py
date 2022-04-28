import os
from flask import (
    request,
)
from flask_sqlalchemy import SQLAlchemy
from cas.database import (
    recreate_database,
    ConversationUser,
    ConversationMessage,
    Session,
    add_user,
    add_conversation,
    add_message,
    update_user,
    get_user_by_email,
    get_user_by_id,
    get_conv_user_by_ids,
    get_all_conv_user_by_user_id,
    get_message_by_msg,
    get_message_by_user_id,
    get_conversation_by_id,
    get_conversation_by_room_name,
    delete_conversation_by_id,
    join_user_msg,
    delete_msg_by_msg_id,
)
from cas.utils import (
    authorization,
    app,
    random_string,
    encode_security_token,
    ok_response,
    error_response,
    now,
    refresh_security_token,
)
from cas.validation import (
    RegisterUserCheck,
    RoomCheck,
    RoomJoinLeave,
    MessageCheck,
    validation_check,
)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key'
db = SQLAlchemy(app)
recreate_database()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    val = validation_check(data, RegisterUserCheck)
    if not val:
        with Session.begin() as session:
            user = get_user_by_email(session, data.get('email'))
            if user:
                return error_response(message='Email already exist!',
                                      status_code=400)
            else:
                add_user(session, data)
        return ok_response(message='User created!', **{
            'User_info': {'Nick_name': data.get('nick_name'),
                          'User_email': data.get('email')}})
    return error_response(message=val, status_code=400)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    with Session.begin() as session:
        user = get_user_by_email(session, data.get('email'))
        if not user:
            return error_response(message='User does no exist!',
                                  status_code=404)
        user_id = user.id
        key_word = random_string(64)
        try:
            update_user(session, user, key_word=key_word)
            token = encode_security_token(user_id, user.nick_name, key_word)
        except BaseException as ex:
            return error_response(message=f'Error: {ex}', status_code=500)
    return ok_response(message='Success!', **{
        'User_info': {'User_id': user_id, 'Authorization': token}})


@app.route('/create_room', methods=['POST'])
@authorization
def create_room():
    data = request.get_json()
    val = validation_check(data, RoomCheck)
    ref_token = refresh_security_token().json
    new_token = ref_token.get('info', {}).get('data')
    if not val:
        with Session.begin() as session:
            user = get_user_by_id(session, id_=data.get('user_id'))
            if not user:
                return error_response(message='User nickname does not exist!',
                                      status_code=404)
            user_id = user.id
            user_name = user.nick_name
            user_email = user.email
            conv = get_conversation_by_room_name(session, room_name=data.get(
                'room_name'))
            if conv:
                return error_response(
                    message='Conversation room already exist!',
                    status_code=400)
            else:
                add_conversation(session, data)
                conv = get_conversation_by_room_name(session,
                                                     room_name=data.get(
                                                         'room_name'))
            if not conv:
                return error_response(
                    message='Conversation room does not exist!',
                    status_code=404)
            room_id = conv.id
            room_name = conv.conversation_name
            conv_user = get_conv_user_by_ids(session, user_id, room_id)
            if conv_user:
                return error_response(message='You are already joined!',
                                      status_code=400)
            else:
                session.add(ConversationUser(
                    user_id=user.id, conversation_id=conv.id))
        return ok_response(message='Room created!', **{'Info': {
            'User': {'ID': user_id,
                     'Authorization': new_token.get('Authorization'),
                     'Name': user_name, 'Email': user_email},
            'Room': {'ID': room_id, 'Name': room_name}}})
    return error_response(message=val, status_code=400)


@app.route('/join_room', methods=['POST'])
@authorization
def join_room():
    data = request.get_json()
    val = validation_check(data, RoomJoinLeave)
    ref_token = refresh_security_token().json
    new_token = ref_token.get('info', {}).get('data')
    if not val:
        with Session.begin() as session:
            user = get_user_by_id(session, data.get('user_id'))
            if not user:
                return error_response(message='User does not exist!',
                                      status_code=404)
            user_id = user.id
            user_name = user.nick_name
            conv = get_conversation_by_id(session, data.get('room_id'))
            if not conv:
                return error_response(message='Room does not exist!',
                                      status_code=404)
            room_id = conv.id
            conv_user = get_conv_user_by_ids(session, user_id, room_id)
            if conv_user:
                return error_response(message='You are already joined!',
                                      status_code=400)
            else:
                session.add(ConversationUser(user_id=user_id,
                                             conversation_id=conv.id))
                conv_user = get_conv_user_by_ids(session, user_id, room_id)
            if not conv_user:
                return error_response(
                    message=f'Room for the user {user.nick_name} does not '
                            f'exist!',
                    status_code=404)
            session.commit()
        return ok_response(
            message=f'You joined the room: {data.get("room_id")}',
            **{'User': {'ID': user_id, 'Name': user_name,
                        'Authorization': new_token.get('Authorization')},
               'Room': data.get('room_id')})
    return error_response(message=val, status_code=400)


@app.route('/leave_room', methods=['DELETE'])
@authorization
def leave_room():
    data = request.get_json()
    val = validation_check(data, RoomJoinLeave)
    ref_token = refresh_security_token().json
    new_token = ref_token.get('info', {}).get('data')
    if not val:
        with Session.begin() as session:
            user = get_user_by_id(session, id_=data.get('user_id'))
            if not user:
                return error_response(message='User does not exist!',
                                      status_code=404)
            conv = get_conversation_by_id(session, data.get('room_id'))
            if not conv:
                return error_response(message='Room does not exist!',
                                      status_code=404)
            room_id = conv.id
            conv_user = get_conv_user_by_ids(session, user.id, room_id)
            if not conv_user:
                return error_response(
                    message=f'Room for the user {user.nick_name} does not '
                            f'exist!',
                    status_code=404)
            conv = get_conversation_by_id(session, data.get('room_id'))
            if not conv:
                return error_response(message='Room does not exist!',
                                      status_code=404)
            room = session.query(ConversationUser).filter(
                ConversationUser.user_id == user.id,
                ConversationUser.conversation_id == conv.id).first()
            session.delete(room)
            return ok_response(
                message=f'You leaved the room: {data.get("room_id")}',
                **{'User': {'ID': user.id, 'Name': user.nick_name,
                            'Authorization': new_token.get(
                                'Authorization')},
                   'Room': data.get('room_id')})
    return error_response(message=val, status_code=400)


@app.route('/send_msg', methods=['POST'])
@authorization
def send_msg():
    data = request.get_json()
    val = validation_check(data, MessageCheck)
    ref_token = refresh_security_token().json
    new_token = ref_token.get('info', {}).get('data')
    if not val:
        with Session.begin() as session:
            user = get_user_by_id(session, data.get('user_id'))
            if not user:
                return error_response(message='User does not exist!',
                                      status_code=404)
            user_id = user.id
            user_name = user.nick_name
            conv = get_conversation_by_id(session, data.get('room_id'))
            if not conv:
                return error_response(
                    message='You are not joined to the conversation!',
                    status_code=404)
            add_message(session, data=data, created_at=now(),
                        sender_id=user_id)
            msg = get_message_by_msg(session, data.get('msg'))
            session.add(ConversationMessage(conversation_id=conv.id,
                                            message_id=msg.id))
            session.commit()
        return ok_response(message='Message is successfully send!',
                           **{'User': {'ID': user_id, 'Name': user_name,
                                       'Authorization': new_token.get(
                                           'Authorization')},
                              'Room': data.get('room_id'),
                              'Message': data.get('msg')})
    return error_response(message=val, status_code=400)


@app.route('/list_con/user_id/<int:user_id>', methods=['GET'])
@authorization
def lst_of_conversations(user_id):
    conv_data = {}
    ref_token = refresh_security_token().json
    new_token = ref_token.get('info', {}).get('data')
    with Session.begin() as session:
        user = get_user_by_id(session, user_id)
        if not user:
            return error_response(message='User does not exist!',
                                  status_code=404)
        conv_user = get_all_conv_user_by_user_id(session, user.id)
        if not conv_user:
            return error_response(
                message=f'Room for the user {user.nick_name} does not'
                        f' exist!',
                status_code=404)
        try:
            for all_con in conv_user:
                conv_data['Room {0}'.format(
                    all_con.id)] = all_con.conversation.conversation_name
            return ok_response(message='Success!',
                               **{'Conversations_info': {'rooms': conv_data},
                                  'User_id': user.id,
                                  'Authorization': new_token.get(
                                      'Authorization')})
        except BaseException as ex:
            return error_response(message=f'Error: {ex}', status_code=500)


@app.route('/delete_con/user_id/<int:user_id>/conv_id/<int:conv_id>',
           methods=['DELETE'])
@authorization
def delete_conversation(user_id, conv_id):
    ref_token = refresh_security_token().json
    new_token = ref_token.get('info', {}).get('data')
    with Session.begin() as session:
        user = get_user_by_id(session, user_id)
        if not user:
            return error_response(message='User does not exist',
                                  status_code=404)
        conv_users = get_all_conv_user_by_user_id(session, user.id)
        for conv_user_lst in conv_users:
            if conv_user_lst.conversation_id == conv_id:
                delete_conversation_by_id(session, conv_id)
                session.commit()
                return ok_response(message='Conversation deleted!', **{
                    'User_ID': user.id,
                    'Authorization': new_token.get('Authorization')})
        return error_response(
            message='Room already deleted or doesnt exist!',
            status_code=404)


@app.route('/delete_msg/user_id/<int:user_id>/msg_id/<int:msg_id>',
           methods=['DELETE'])
@authorization
def delete_message(user_id, msg_id):
    ref_token = refresh_security_token().json
    new_token = ref_token.get('info', {}).get('data')
    with Session.begin() as session:
        user = get_user_by_id(session, user_id)
        if not user:
            return error_response(message='User does not exist',
                                  status_code=404)
        join_msg = join_user_msg(session, user_id)
        msg = get_message_by_user_id(session, user_id)
        if not msg:
            return error_response(
                message=f'Message by the id: {user_id} does not exist '
                        f'for the user: {user.nick_name} ', status_code=404)
        for msg_lst in join_msg:
            if msg_lst.id == msg_id:
                delete_msg_by_msg_id(session, msg_id)
                session.commit()
                return ok_response(message='Message deleted!', **{
                    'User_ID': user.id,
                    'Authorization': new_token.get('Authorization')})
        return error_response(
            message='Message already deleted or doesnt exist!',
            status_code=404)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
