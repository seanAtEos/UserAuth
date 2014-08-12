import cryptcular.bcrypt

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
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

crypt = cryptcular.bcryptBCRYPTPasswordManager()

def hash_password(password):
    return unicode(crypt.encode(password))

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    password = Column(Text)
    firstname = Column(Text)
    lastname = Column(Text)
    email = Column(Text)

    def __repr__(self):
        return "<User(id='%s', username='%s', password='%s,', firstname='%s', lastname='%s', email='%s',)>" % (
                                str(self.id), self.username, self.password, self.firstname, self.lastname, self.email )

Index('username_index', User.username, unique=True, mysql_length=255)
