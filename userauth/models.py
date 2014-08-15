from passlib.hash import bcrypt

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    synonym
    )

from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.security import Allow, Everyone

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def hash_password(password):
    return bcrypt.encrypt(password, rounds=12)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    password = Column(Text)
    firstname = Column(Text)
    lastname = Column(Text)
    email = Column(Text)
    credentials = Column(Text)

    def __init__(self, id, username, password, firstname, lastname, email, credentials):
        self.id = id
        self.username = username
        self.password = hash_password(password)
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.credentials = credentials

    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.username == username).first() 

    @classmethod
    def check_password(cls, username, password):
        user = cls.get_by_username(username)
        if not user:
            return False
        return bcrypt.verify(password, user.password)

    def __repr__(self):
        return "<User(id='%s', username='%s', password='%s,', firstname='%s', lastname='%s', email='%s')>" % (
                                str(self.id), self.username, self.password, self.firstname, self.lastname, self.email )

Index('username_index', User.username, unique=True, mysql_length=255)

class RootFactory(object):
    __acl__ = [
        (Allow, 'group:fool', 'fool'),
        (Allow, 'group:king', 'king'),
        (Allow, 'group:god', 'god')
    ]
    
    def __init__(self, request):
        pass