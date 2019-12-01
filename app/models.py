import hashlib
from datetime import datetime
from random import seed, randint
from typing import Tuple, Dict, Union, Optional, List

import forgery_py
from flask_sqlalchemy import BaseQuery
from markdown import markdown
from sqlalchemy.exc import IntegrityError
from flask import current_app, Flask, request
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import BadSignature, TimedJSONWebSignatureSerializer as Serializer

from . import db, login_manager

current_app: Flask


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE = 0x04
    MODERATE = 0x08
    ADMIN = 0xff


class PostsCallback:

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        extensions = [
            'extra',
            'codehilite',
        ]
        target.body_html = markdown(value, extensions=extensions)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def insert_roles(new_roles: Dict[str, Tuple[bytes, bool]] = None):
        """Insert Roles to DB.
        :param new_roles: Dict[Role, Tuple[permissions, default for new user]]
        """
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE |
                          Permission.MODERATE, False),
            'Administrator': (0xff, False)
        }

        if new_roles:
            roles.update(new_roles)

        for role_name, permission_default in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(role_name)
            role.permissions, role.default = permission_default
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f' |{self.__tablename__} {self.name}| '


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, follower, followed):
        self.follower = follower
        self.followed = followed


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    query: BaseQuery

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, username: str, email: str, password: str,
                 role: Role = None, avatar_hash=None, confirmed: bool = False, name: str = None,
                 location: str = None, about_me: str = None, member_since: str = None):
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.avatar_hash = avatar_hash
        self.confirmed = confirmed
        self.location = location
        self.about_me = about_me
        self.member_since = member_since
        self.name = name

        if not self.role:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=Permission.ADMIN).first()
            else:
                self.role = Role.query.filter_by(default=True).first()

        if self.email and not self.avatar_hash:
            self.make_email_hash()

        self.follow(self)

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')

    @password.setter
    def password(self, new_password):
        self.password_hash = generate_password_hash(new_password)

    def gravatar(self, size: int = 100, default='retro', rating='g') -> str:
        url = 'https://secure.gravatar.com/avatar' if request.is_secure else 'http://gravatar.com/avatar'
        hash_request = self.avatar_hash or self.make_email_hash()
        return f'{url}/{hash_request}?s={size}&d={default}&r={rating}'

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration: int = 3600) -> str:
        serializer = Serializer(current_app.config['SECRET_KEY'], expiration)
        return serializer.dumps({'confirm': self.id})

    def generate_reset_token(self, expiration: int = 3600) -> str:
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    def generate_email_change_token(self, new_email: str, expiration: int = 3600) -> str:
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def generate_auth_token(self, expiration: int) -> bytes:
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token: str) -> Optional['User']:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadSignature:
            return None
        return User.query.get(data['id'])

    def confirm(self, token: bytes) -> bool:
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            data: dict = serializer.loads(token)
        except BadSignature:
            return False

        if data.get('confirm') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    @staticmethod
    def reset_password(token: Union[bytes, str, bytearray], new_password) -> bool:
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            data: dict = serializer.loads(token)
        except BadSignature:
            return False
        user = User.query.get(data.get('reset'))
        if user:
            user.password = new_password
            db.session.add(user)
            db.session.commit()
            return True
        else:
            return False

    def change_email(self, token) -> bool:
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            data: dict = serializer.loads(token)
        except BadSignature:
            return False

        new_email = data.get('new_email')
        if data.get('change_email') != self.id or not new_email or self.query.filter_by(email=new_email).first():
            return False

        self.email = new_email
        self.avatar_hash = self.make_email_hash()
        db.session.add(self)
        return True

    def can(self, permission) -> bool:
        return self.role and self.role.permissions & permission == permission

    def is_admin(self) -> bool:
        return self.can(Permission.ADMIN)

    def __repr__(self):
        return f' |{self.__tablename__} {self.name}| '

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def make_email_hash(self):
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return self.avatar_hash

    @staticmethod
    def generate_fake(count: int = 100):
        seed()
        for _ in range(count):
            user = User(username=forgery_py.internet.user_name(True),
                        email=forgery_py.internet.email_address(),
                        password=forgery_py.lorem_ipsum.word(),
                        confirmed=True,
                        name=forgery_py.name.full_name(),
                        location=forgery_py.address.city(),
                        about_me=forgery_py.lorem_ipsum.sentence(),
                        member_since=forgery_py.date.date(True))
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def is_following(self, user) -> bool:
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user) -> bool:
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(self, user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.followed.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    @classmethod
    def get_user_by_name(cls, username: str, rise_404: bool = False) -> 'User':
        """Return obj of User from DataBase by username"""
        if rise_404:
            return cls.query.filter_by(username=username).first_or_404()
        else:
            return cls.query.filter_by(username=username).first()

    @property
    def followed_posts(self) -> List['Post']:
        """Return posts of authors that follow user"""
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    @classmethod
    def add_self_follows(cls):
        for user in cls.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions) -> bool:
        return False

    def is_admin(self) -> bool:
        return False


login_manager.anonymous_user = AnonymousUser


class Post(db.Model, PostsCallback):
    __tablename__ = 'posts'
    query: BaseQuery

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __init__(self, body: str, author: User, timestamp: str = None):
        self.body = body
        self.author = author
        self.timestamp = timestamp

    @staticmethod
    def generate_fake(count=100):
        seed()
        user_count = User.query.count()
        for _ in range(count):
            user = User.query.offset(randint(0, user_count - 1)).first()
            post = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        timestamp=forgery_py.date.date(True),
                        author=user)
            db.session.add(post)
            db.session.commit()


class Comment(db.Model, PostsCallback):
    __tablename__ = 'comments'
    query: BaseQuery

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __init__(self, body: str, author: User, post: Post, disabled=False):
        self.body = body
        self.disabled = disabled
        self.author = author
        self.post = post


db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)
