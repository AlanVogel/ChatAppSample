from unittest import TestCase
from cas.database import (
    Session,
    Base,
    engine,
    User,
    Conversation,
    ConversationUser,
    Message,
)
from cas.utils import (
    now,
    random_string,
)


class BaseUnittest(TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        Base.metadata.drop_all(engine)


def create_user(session: Session, name="Pero", email="pero.peric@gmail.com",
                password="secret", key_word=random_string(64)):
    user = User(nick_name=name, email=email, password=password,
                key_word=key_word)
    session.add(user)
    session.flush()
    return user


def create_conversation(session: Session, conv_name="Science"):
    conv = Conversation(conversation_name=conv_name)
    session.add(conv)
    session.flush()
    return conv


def create_conv_user(session: Session, user_id=1, conv_id=1):
    conv_user = ConversationUser(user_id=user_id, conversation_id=conv_id)
    session.add(conv_user)
    session.flush()
    return conv_user


def create_message(session: Session, msg='Testing', time= now(), sender_id=1):
    msg = Message(msg=msg, created_at=time, sender_id=sender_id)
    session.add(msg)
    session.flush()
    return msg
