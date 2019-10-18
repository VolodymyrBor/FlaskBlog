import time
from unittest import TestCase

from app import create_app, db
from app.models import User, Permission, Role, AnonymousUser


class UserModelTestCase(TestCase):

    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        Role.insert_roles()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        user = User('username', 'email', 'password')
        self.assertTrue(user.password_hash is not None)

    def test_password_verification(self):
        user = User('username', 'email', 'password')
        self.assertTrue(user.verify_password('password'))
        self.assertFalse(user.verify_password('wrong password'))

    def test_password_salts_are_random(self):
        user = User('username', 'email', 'password')
        user2 = User('username', 'email', 'password')
        self.assertFalse(user.password_hash == user2.password_hash)

    def test_valid_confirmation_token(self):
        user = User('username', 'email', 'password')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        self.assertTrue(user.confirm(token))

    def test_expired_confirmation_token(self):
        user = User('username', 'email', 'password')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(user.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User('new1', 'new1', 'password')
        u2 = User('new2', 'new2', 'wrong')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_valid_reset_token(self):
        u = User('new', 'new', 'password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u = User('new', 'new', 'cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'wrong', 'horse'))
        self.assertTrue(u.verify_password('cat'))

    def test_valid_email_change_token(self):
        u = User('john', 'john@example.com', 'cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan@example.org')

    def test_invalid_email_change_token(self):
        u1 = User('john', 'john@example.com', 'cat')
        u2 = User('susan', 'susan@example.org', 'dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('david@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_duplicate_email_change_token(self):
        u1 = User('john', 'john@example.com', 'cat')
        u2 = User('susan', 'susan@example.org', 'dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_user_role(self):
        u = User('john', 'john@example.com', 'cat')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_moderator_role(self):
        r = Role.query.filter_by(name='Moderator').first()
        u = User('john', 'john@example.com', 'cat', r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User('john', 'john@example.com', 'cat', r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))
