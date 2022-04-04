from unittest import TestCase
from cas.database import (
    Session,
    Base,
    engine,
    User,
)


class BaseUnittest(TestCase):

    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        Base.metadata.drop_all(engine)


def create_user(session: Session, name="Pero", email="pero.peric@gmail.com",
                key_word="testing"):
    user = session.add(User(nick_name=name, email=email, key_word=key_word))
    session.flush()
    return user
