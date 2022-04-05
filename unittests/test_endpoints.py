import unittest
from cas.app import (
    register,
    login,
    get_user,
)
from cas.utils import app
from unittests.utils import (
    create_user,
    BaseUnittest,
)
from cas.database import (
    Session,
)


class Endpoints(BaseUnittest):

    def test_register_pass(self):
        with app.test_client() as client_test:
            client_test.post('/create_user', json={
                "nick_name": "Pero", "email": "pero.peric@gmail.com",
                "key_word": "testing"
            })
            res = register()
            self.assertEqual(type(res), tuple)
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0].status_code, 200)
            self.assertEqual(res[1], 200)

    def test_register_fail(self):
        with app.test_client() as client_test:
            client_test.post('/create_user', json={
                "nick_name": "Pero", "email": "pero.peric.gmail.com",
                "key_word": "testing"
            })
            res = register()
            self.assertEqual(type(res), tuple)
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0].status_code, 200)
            self.assertEqual(res[1], 400)

    def test_login_pass(self):
        with Session.begin() as session:
            user = create_user(session)
            nick_name = user.nick_name
            email = user.email
            word = user.key_word
        with app.test_client() as client_test:
            client_test.post('/login', json={
                "nick_name": nick_name, "email": email, "key_word": word})
            res = register()
            self.assertEqual(type(res), tuple)
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0].status_code, 200)

    def test_login_fail(self):
        with Session.begin() as session:
            create_user(session, email="marko@gmail.com")
        with app.test_client() as client_test:
            res = client_test.post('/login', json={
                "nick_name": "Pero", "email": "pero.peric@gmail.com"})
            self.assertEqual(res.status_code, 400)


if __name__ == '__main__':
    unittest.main()
