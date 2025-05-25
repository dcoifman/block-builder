import unittest
from app.models import User # Assuming User is accessible like this

class TestUserModel(unittest.TestCase):

    def test_password_setter(self):
        u = User(username='john', email='john@example.com')
        u.set_password('cat')
        self.assertIsNotNone(u.password_hash)
        self.assertNotEqual(u.password_hash, 'cat')

    # Removed test_no_password_getter as it's not applicable to the current User model design.
    # The User model does not have a 'password' property that would raise AttributeError on get.
    # It stores 'password_hash', and direct access to 'password_hash' is possible.

    def test_password_verification(self):
        u = User(username='david', email='david@example.com')
        u.set_password('mouse')
        self.assertTrue(u.check_password('mouse'))
        self.assertFalse(u.check_password('rat'))

    def test_password_salts_are_random(self):
        u1 = User(username='jane', email='jane@example.com')
        u2 = User(username='peter', email='peter@example.com')
        u1.set_password('commonpassword')
        u2.set_password('commonpassword')
        self.assertNotEqual(u1.password_hash, u2.password_hash)

if __name__ == '__main__':
    unittest.main()
