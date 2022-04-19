import unittest
from cas.app import (
    register,
    login,
    create_room,
    join_room,
    leave_room,
)
from cas.utils import app
from unittests.utils import (
    BaseUnittest,
    create_user,
    create_conversation,
    create_conv_user,
    create_message,
)
from cas.database import (
    Session,
)


class Endpoints(BaseUnittest):

    def test_register_pass(self):
        with app.test_client() as client_test:
            client_test.post('/create_user', json={
                "nick_name": "Pero", "email": "pero.peric@gmail.com",
                "password": "secret"
            })
            res = register()
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 5)
            self.assertEqual(info.get('message'), 'User created!')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_register_fail(self):
        with app.test_client() as client_test:
            client_test.post('/create_user', json={
                "nick_name": "Pero", "email": "pero.peric.gmail.com",
                "password": "secret"
            })
            res = register()
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             '1 validation error for RegisterUserCheck\nemail'
                             '\n  pero.peric.gmail.com is not a valid email: '
                             'The email address is not valid. It must have'
                             ' exactly one @-sign. (type=value_error)')
            self.assertEqual(info.get('code'), 400)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_register_fail_email_exists(self):
        with Session.begin() as session:
            user = create_user(session)
            email = user.email
        with app.test_client() as client_test:
            client_test.post('/create_user', json={
                "nick_name": "Bero", "email": email,
                "password": "secret2"
            })
            res = register()
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'Email already exist!')
            self.assertEqual(info.get('code'), 400)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_login_pass(self):
        with Session.begin() as session:
            user = create_user(session)
            email = user.email
            password = user.email
        with app.test_client() as client_test:
            client_test.post('/login',
                             json={"email": email, "password": password})
            res = login()
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 5)
            self.assertEqual(info.get('message'), 'Success!')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_login_fail(self):
        with Session.begin() as session:
            create_user(session, email="marko@gmail.com")
        with app.test_client() as client_test:
            client_test.post('/login', json={
                "nick_name": "Pero", "email": "pero.peric@gmail.com"})
            res = login()
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'User does no exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_get_user_pass(self):
        with Session.begin() as session:
            create_user(session)
        with app.test_client() as client_test:
            res = client_test.get('/user/1',
                                  headers={"User_id": 1,
                                           "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 5)
            self.assertEqual(info.get('message'), 'Success!')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_get_user_fail(self):
        with app.test_client() as client_test:
            res = client_test.get('/user/1',
                                  headers={"User_id": 1,
                                           "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'User does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_create_room_pass(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
        with app.test_client() as client_test:
            res = client_test.post('/create_room', json={
                "nick_name": user_name, "room_name": 'Science'},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 5)
            self.assertEqual(info.get('message'), 'Room created!')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_create_room_fail_case1(self):
        with Session.begin() as session:
            user = create_user(session)
        with app.test_client() as client_test:
            res = client_test.post('/create_room', json={
                "nick_name": 'John', "room_name": 'Science'},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             'User nickname does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_create_room_fail_case2(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            room = create_conversation(session)
            room_name = room.conversation_name
        with app.test_client() as client_test:
            res = client_test.post('/create_room', json={
                "nick_name": user_name, "room_name": room_name},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             'Conversation room name already exist!')
            self.assertEqual(info.get('code'), 400)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_create_room_fail_case3(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
        with app.test_client() as client_test:
            res = client_test.post('/create_room', json={
                "nick_name": user_name, "room_name": None},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             '1 validation error for RoomCheck\nroom_name\n  '
                             'none is not an allowed value'
                             ' (type=type_error.none.not_allowed)')
            self.assertEqual(info.get('code'), 400)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_join_room_pass(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            room = create_conversation(session)
            room_name = room.conversation_name
        with app.test_client() as client_test:
            res = client_test.post('/join_room', json={
                "nick_name": user_name, "room_name": room_name},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 6)
            self.assertEqual(info.get('message'),
                             f'You joined the room: {room_name}')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_join_room_fail_case1(self):
        with Session.begin() as session:
            create_user(session)
            room = create_conversation(session)
            room_name = room.conversation_name
        with app.test_client() as client_test:
            res = client_test.post('/join_room', json={
                "nick_name": 'Peter', "room_name": room_name},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'User does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_join_room_fail_case2(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            create_conversation(session)
        with app.test_client() as client_test:
            res = client_test.post('/join_room', json={
                "nick_name": user_name, "room_name": 'Technology'},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'Room name does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_join_room_fail_case3(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            room = create_conversation(session)
            room_name = room.conversation_name
            create_conv_user(session, user.id, room.id)
        with app.test_client() as client_test:
            res = client_test.post('/join_room', json={
                "nick_name": user_name, "room_name": room_name},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'You are already joined!')
            self.assertEqual(info.get('code'), 400)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_leave_room_pass(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            room = create_conversation(session)
            room_name = room.conversation_name
            create_conv_user(session, user.id, room.id)
        with app.test_client() as client_test:
            res = client_test.post('/leave_room', json={
                "nick_name": user_name, "room_name": room_name},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 6)
            self.assertEqual(info.get('message'),
                             f'You leaved the room: {room_name}')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_leave_room_fail_case1(self):
        with Session.begin() as session:
            create_user(session)
            room = create_conversation(session)
            room_name = room.conversation_name
        with app.test_client() as client_test:
            res = client_test.post('/leave_room', json={
                "nick_name": 'Peter', "room_name": room_name},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'User does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_leave_room_fail_case2(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            create_conversation(session)
        with app.test_client() as client_test:
            res = client_test.post('/leave_room', json={
                "nick_name": user_name, "room_name": 'Technology'},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             f'Room for the user {user_name} does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_leave_room_fail_case3(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            room = create_conversation(session)
            create_conv_user(session, user.id, room.id)
        with app.test_client() as client_test:
            res = client_test.post('/leave_room', json={
                "nick_name": user_name, "room_name": 'Technology'},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"}
                                   )
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'Room name does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_send_msg_pass(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            room = create_conversation(session)
            room_name = room.conversation_name
            message = create_message(session)
            msg = message.msg
        with app.test_client() as client_test:
            res = client_test.post('/send_msg', json={
                "nick_name": user_name, "room_name": room_name, "msg": msg},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 7)
            self.assertEqual(info.get('message'),
                             'Message is successfully send!')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_send_msg_fail_case1(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            create_conversation(session)
            message = create_message(session)
            msg = message.msg
        with app.test_client() as client_test:
            res = client_test.post('/send_msg', json={
                "nick_name": user_name, "room_name": 'Technology', "msg": msg},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             'You are not joined to the conversation!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_send_msg_fail_case2(self):
        with Session.begin() as session:
            create_user(session)
            room = create_conversation(session)
            room_name = room.conversation_name
            message = create_message(session)
            msg = message.msg
        with app.test_client() as client_test:
            res = client_test.post('/send_msg', json={
                "nick_name": 'Peter', "room_name": room_name, "msg": msg},
                                   headers={"User_id": 1,
                                            "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'User does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_lst_of_conversation_pass(self):
        with Session.begin() as session:
            user = create_user(session)
            conv = create_conversation(session)
            user_id = user.id
            conv_id = conv.id
            create_conv_user(session, user_id=user_id, conv_id=conv_id)
        with app.test_client() as client_test:
            res = client_test.get('/list_con/1',
                                  headers={"User_id": 1,
                                           "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 5)
            self.assertEqual(info.get('message'), 'Success!')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_lst_of_conversation_fail_case1(self):
        with app.test_client() as client_test:
            res = client_test.get('/list_con/1',
                                  headers={"User_id": 1,
                                           "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'User does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_lst_of_conversation_fail_case2(self):
        with Session.begin() as session:
            user = create_user(session)
            create_conversation(session)
            user_name = user.nick_name
        with app.test_client() as client_test:
            res = client_test.get('/list_con/1',
                                  headers={"User_id": 1,
                                           "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             f'Room for the user {user_name} does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_delete_conversation_pass(self):
        with Session.begin() as session:
            user = create_user(session)
            conv = create_conversation(session)
            user_id = user.id
            conv_id = conv.id
            create_conv_user(session, user_id=user_id, conv_id=conv_id)
        with app.test_client() as client_test:
            res = client_test.delete('/delete_con/1',
                                     headers={"User_id": 1,
                                              "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'Conversation deleted!')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_delete_conversation_fail_case1(self):
        with app.test_client() as client_test:
            res = client_test.delete('/delete_con/1',
                                     headers={"User_id": 1,
                                              "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'User does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_delete_conversation_fail_case2(self):
        with Session.begin() as session:
            user = create_user(session)
            room = create_conversation(session)
            user_name = user.nick_name
            conv_id = room.id
        with app.test_client() as client_test:
            res = client_test.delete('/delete_con/1',
                                     headers={"User_id": 1,
                                              "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             f'Conversation by the id: {conv_id} does not '
                             f'exist for the user: {user_name} ')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_delete_messages_pass(self):
        with Session.begin() as session:
            create_user(session)
            create_message(session)
        with app.test_client() as client_test:
            res = client_test.delete('/delete_msg/1',
                                     headers={"User_id": 1,
                                              "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'Message deleted!')
            self.assertEqual(info.get('code'), 200)
            self.assertEqual(info.get('status'), 'OK')

    def test_delete_messages_fail_case1(self):
        with app.test_client() as client_test:
            res = client_test.delete('/delete_msg/1',
                                     headers={"User_id": 1,
                                              "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'), 'User does not exist!')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')

    def test_delete_messages_fail_case2(self):
        with Session.begin() as session:
            user = create_user(session)
            user_name = user.nick_name
            create_message(session)
            header_id = 2
        with app.test_client() as client_test:
            res = client_test.delete(f'/delete_msg/{header_id}',
                                     headers={"User_id": 1,
                                              "authorization": "asj34"})
            info = res.json.get('info').get('data')
            self.assertEqual(type(info), dict)
            self.assertEqual(len(info), 4)
            self.assertEqual(info.get('message'),
                             f'Message by the id: {header_id} does not exist '
                             f'for the user: {user_name} ')
            self.assertEqual(info.get('code'), 404)
            self.assertEqual(info.get('status'), 'ERROR')


if __name__ == '__main__':
    unittest.main()
