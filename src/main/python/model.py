__author__ = 'Paul'


from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.table import Table

from passlib.apps import custom_app_context as pwd_context


class DBConnection(object):
    def __init__(self):
        pass

    @staticmethod
    def create(collection):
        return Table.create(collection._tablename, schema=collection._schema)


    @staticmethod
    def delete(collection):
        return Table.delete(collection)

class DBObject(object):
    pass


class DBCollection(object):
    _tablename = None
    _collection_of = None
    _schema = None

    def __init__(self, name):
        self._table = Table(name)

    def fetch(self):
        pass

    def put(self, db_object):
        self._table.put_item(data=db_object.__dict__)

    def get(self, **kwargs):
        return self._table.get_item(**kwargs)


class UserCollection(DBCollection):
    _tablename = 'users'
    _collection_of = User
    _schema = [HashKey('user'), RangeKey('last')]

    def get_user(self, name):
        pass


class User(DBObject):

    def __index__(self, username, password, first, last, email):
        self.username = username
        self.password = password
        self.first_name = first
        self.last_name = last
        self.email = email
        self._memberOf = UserCollection

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)