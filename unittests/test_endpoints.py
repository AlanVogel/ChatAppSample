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
            return_statement = res[0].json.get("success")
            self.assertEqual(type(res), tuple)
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0].json.get("success"), return_statement)
            self.assertEqual(res[0].status_code, 200)
            self.assertEqual(res[1], 200)

    def test_register_fail(self):
        with app.test_client() as client_test:
            client_test.post('/create_user', json={
                "nick_name": "Pero", "email": "pero.peric.gmail.com",
                "key_word": "testing"
            })
            res = register()
            return_statement = res[0].json.get("error")
            self.assertEqual(type(res), tuple)
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0].json.get("error"), return_statement)
            self.assertEqual(res[0].status_code, 200)
            self.assertEqual(res[1], 400)

    def test_login_pass(self):
        with app.test_client() as client_test:
            client_test.post('/login', json={
                "nick_name": "Pero", "email": "pero.peric@gmail.com"})
            with Session.begin() as session:
                create_user(session)
            res = login()
            token = res[0].json.get("token")
            self.assertEqual(type(res), tuple)
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0].json.get("token"), token)
            self.assertEqual(res[0].status_code, 200)
            self.assertEqual(res[1], 200)

    def test_login_fail(self):
        with app.test_client() as client_test:
            client_test.post('/login', json={
                "nick_name": "Pero", "email": "pero.peric@gmail.com"})
            with Session.begin() as session:
                create_user(session, email="marko@gmail.com")
            res = login()
            return_statement = res[0].json.get("error")
            self.assertEqual(type(res), tuple)
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0].json.get("error"), return_statement)
            self.assertEqual(res[0].status_code, 200)
            self.assertEqual(res[1], 400)

    # def get_user_pass(self):
    #     with app.test_client() as client_test:
    #         id = 1
    #         client_test.get(f'/user/{id}')
    #     res = get_user(id)


if __name__ == '__main__':
    unittest.main()
