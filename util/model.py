from boto.dynamodb2.fields import HashKey, RangeKey, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
import logging
from passlib.apps import custom_app_context as pwd_context
import boto
from boto.exception import JSONResponseError
from boto.dynamodb2.layer1 import DynamoDBConnection
import time

def log_boto_error(e):
    logging.warn('Got exception: ' + e.__class__.__name__)
    logging.warn('\tStatus: ' + str(e.status))
    logging.warn('\tReason: ' + e.reason)
    logging.warn('\tMessage: ' + str(e.body))


class DBConnection(object):
    def __init__(self, env):
        if env == 'development':
            self.conn = DynamoDBConnection(
                host='localhost',
                port=8000,
                aws_access_key_id='development',
                aws_secret_access_key='development',
                is_secure=False)
        elif env == 'test':
            self.conn = DynamoDBConnection(
                host='localhost',
                port=8000,
                aws_access_key_id='test',
                aws_secret_access_key='test',
                is_secure=False)
        elif env == 'production':
            self.conn = boto.connect_dynamodb()
        else:
            logging.error("Invalid environment")
            self.conn = None


class DBTable(object):
    item_class = None
    simple_schema = [HashKey('_id')]

    def __init__(self, table_name, schema, global_indexes, dbconn):
        self.table_name = table_name
        self._table = Table(table_name, connection=dbconn.conn)
        self.schema = schema
        self.global_indexes = global_indexes
        self.dbconn = dbconn.conn
        return self

    def get_table(self):
        return self._table

    def exists(self):
        return self._table.table_name in self.dbconn.list_tables()['TableNames']

    def create(self):
        try:
            # print self.schema
            # print self.table_name
            self._table = Table.create(
                self.table_name,
                schema=self.schema,
                global_indexes=self.global_indexes,
                connection=self.dbconn)
        except JSONResponseError as e:
            logging.warn("Error creating table " + self.table_name)
            log_boto_error(e)
            if 'message' in e.body and e.body['message'].startswith('Table already exists'):
                self._table = Table(self.table_name, connection=self.dbconn)
            elif 'Message' in e.body and e.body['Message'].startswith("Cannot create preexisting"):
                self._table = Table(self.table_name, connection=self.dbconn)
            else:
                raise e
        return self

    def delete(self):
        try:
            self._table.delete()
        except JSONResponseError as e:
            logging.warn("Error deleting table " + self.table_name)
            log_boto_error(e)
            if e.body['Message'].startswith('Cannot do operations on a non-existent tabl'):
                return
            else:
                raise e
        return

    def insert(self, data):
        self._table.put_item(data=data, overwrite=True)
        return

    def get_item(self, **kwargs):
        item = self._table.get_item(**kwargs)
        # TODO return item or class??
        # new_item = self.item_class(self)
        # new_item.__dict__ = item._data
        # return new_item
        return item

    def query_2(self, **kwargs):
        return self._table.query_2(**kwargs)

    def scan(self, **kwargs):
        return self._table.scan(**kwargs)

    def remove(self):
        return self._table.remove()


class DBItem(object):
    def __init__(self, table):
        self._table = table
        self._item = Item(table.get_table(), data=self.get_attrs())

    def get_attrs(self):
        item_list = {}
        for key, value in self.__dict__.iteritems():
            if not key.startswith('_'):
                item_list[key] = value
        return item_list

    def save(self, **kwargs):
        self._item.save(**kwargs)

    def insert(self, **kwargs):
        return self._table.put_item(data=self._item._data)

    def delete(self):
        return self._item.delete()

class User(DBItem):
    def __init__(
            self, table, email=None, password=None,
            first_name=None, last_name=None, password_hash=None):

        if password is not None:
            self.password_hash = User.hash_password(password)
        else:
            self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self._table = table
        super(User, self).__init__(self._table)

    @staticmethod
    def hash_password(password):
        return pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class UserCollection(DBTable):
    table_name = 'users'
    item_class = User
    schema = [HashKey('email')]

    def __init__(self, dbconn):
        super(UserCollection, self).__init__(
            UserCollection.table_name, UserCollection.schema, None, dbconn)


class Host(DBItem):
    def __init__(self, table, host_name=None):
        self.host_name = host_name
        self._table = table
        super(Host, self).__init__(self._table)


class HostCollection(DBTable):
    TABLE_NAME = 'host'
    item_class = Host
    schema = [HashKey('id')]

    def __init__(self, table_name=TABLE_NAME):
        self.table_name = table_name
        super(HostCollection, self).__init__()


class AthleteCollection(DBTable):
    table_name = 'athletes'
    global_indexes = [GlobalAllIndex(
        'OrgIndex', parts=[HashKey('organization')])]

    def __init__(self, dbconn):
        super(AthleteCollection, self).__init__(
            AthleteCollection.table_name,
            DBTable.simple_schema,
            AthleteCollection.global_indexes,
            dbconn)


class OrganizationCollection(DBTable):
    table_name = 'organizations'
    global_indexes = [GlobalAllIndex('NameIndex', parts=[HashKey('name')])]

    def __init__(self, dbconn):
        super(OrganizationCollection, self).__init__(
            OrganizationCollection.table_name,
            DBTable.simple_schema,
            OrganizationCollection.global_indexes,
            dbconn)


class EventCollection(DBTable):
    table_name = 'events'
    global_indexes = [GlobalAllIndex('event-index', parts=[HashKey('event')])]

    def __init__(self, dbconn):
        super(EventCollection, self).__init__(
            EventCollection.table_name, DBTable.simple_schema, None, dbconn)
        self.schema = DBTable.simple_schema


class CrewCollection(DBTable):
    table_name = 'crew'
    global_indexes = [GlobalAllIndex('event-index', parts=[HashKey('event')])]

    def __init__(self, dbconn):
        super(CrewCollection, self).__init__(
            CrewCollection.table_name,
            DBTable.simple_schema,
            CrewCollection.global_indexes,
            dbconn)


class StageCollection(DBTable):
    table_name = 'stage'
    global_indexes = [GlobalAllIndex('event-index', parts=[HashKey('event')])]

    def __init__(self, dbconn):
        super(StageCollection, self).__init__(
            StageCollection.table_name,
            DBTable.simple_schema,
            StageCollection.global_indexes,
            dbconn)


class RaceCollection(DBTable):
    table_name = 'race'
    global_indexes = [GlobalAllIndex('event-index', parts=[HashKey('event')])]

    def __init__(self, dbconn):
        super(RaceCollection, self).__init__(
            RaceCollection.table_name,
            DBTable.simple_schema,
            RaceCollection.global_indexes,
            dbconn)


class Race(DBItem):
    def __init__(self, collection):
        super(Race, self).__init__(collection._table)


class RacingCrewCollection(DBTable):
    table_name = 'racing_crew'
    item_class = Race
    global_indexes = [GlobalAllIndex('race-index', parts=[HashKey('race')]),
                      GlobalAllIndex('event-index', parts=[HashKey('event')])]

    def __init__(self, dbconn):
        super(RacingCrewCollection, self).__init__(
            RacingCrewCollection.table_name,
            DBTable.simple_schema,
            RacingCrewCollection.global_indexes,
            dbconn)

class RegattaCollection(DBTable):
    table_name = 'regatta'
    #item_class = Regatta
    global_indexes = [GlobalAllIndex('name-index', parts=[HashKey('name')])]

    def __init__(self, dbconn):
        super(RegattaCollection, self).__init__(
            RegattaCollection.table_name,
            DBTable.simple_schema,
            RegattaCollection.global_indexes,
            dbconn)


class Audit(DBTable):
    table_name = 'audit'
    schema = [HashKey('timeStamp'), RangeKey('user')]
    global_indexes = [GlobalAllIndex('race-index', parts=[HashKey('user')])]

    def __init__(self, dbconn):
        self.logger = logging.getLogger('audit')

        super(Audit, self).__init__(
            Audit.table_name,
            Audit.schema,
            Audit.global_indexes, dbconn)

    def info(self, message):
        self.logger.info(message)
        self.insert(data={
                    'message': message,
                    'timestamp': time.time()})
