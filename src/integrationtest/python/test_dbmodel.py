__author__ = 'Paul'

from boto.dynamodb2.fields import HashKey, RangeKey, GlobalAllIndex
from boto.dynamodb2.table import Table
import boto
import time
from unittest import TestCase


class TestModel(TestCase):

    def setUp(self):
        self.conn = boto.connect_dynamodb()

    def test_connection(self):
        self.assertIsInstance(self.conn ,boto.dynamodb.layer2.Layer2)

    def test_create_table(self):
        schema = [
            HashKey('username'),
            RangeKey('last_name'),
        ]

        global_indexes = [GlobalAllIndex('EverythingIndex', parts=[
            HashKey('account_type'),
        ])]
        t1 = Table.create('test', schema=[HashKey('username')])
        # wait for table creation
        time.sleep(20)

        t2 = Table('test', schema=[HashKey('username')])

        self.assertEqual(t1.table_name, t2.table_name)

        t1.delete()

    def tearDown(self):
        pass