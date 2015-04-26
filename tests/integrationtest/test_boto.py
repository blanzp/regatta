__author__ = 'Paul'

from unittest import TestCase
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.fields import HashKey, RangeKey, GlobalAllIndex
from boto.exception import JSONResponseError
from boto.dynamodb2.exceptions import ValidationException

class TestBoto(TestCase):

    def setUp(self):
        self.conn = self.conn = DynamoDBConnection(
            host='localhost',
            port=8000,
            aws_access_key_id='test',
            aws_secret_access_key='test',
            is_secure=False)

    def create_table(self):
        try:
            table = Table.create(
                'datatype',
                schema= [HashKey('_id')],
                global_indexes=None,
                connection=self.conn)
        except JSONResponseError as j:
            print j
            table = Table('datatype',connection=self.conn)
        return table

    def test_create_table(self):
        self.assertIsInstance(self.create_table(), Table)

    def test_insert_with_spaces(self):
        table = self.create_table()
        with self.assertRaises(ValidationException):
            resp = table.put_item(data={"_id": '1234', "name": {"first": "joe", "last": "smith", "age": 20, "home": ""}},overwrite=True)

    def test_insert_with_no_spaces(self):
        table = self.create_table()
        resp = table.put_item(data={"_id": '4567', "name": {"first": "joe", "last": "smith", "age": 20, "home": "blah", "address": {"street": "main", "number": 10, "city": 'mycity'}}},overwrite=True)
        self.assertTrue(resp)


    def test_insert_with_none(self):
        table = self.create_table()
        resp = table.put_item(data={"_id": '4567', "name": {"first": "joe", "last": "smith", "age": 20, "home": None, "address": {"street": "main", "number": 10, "city": 'mycity'}}},overwrite=True)
        self.assertTrue(resp)