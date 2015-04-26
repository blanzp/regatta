from unittest import TestCase
import time

from util import model


class TestModel(TestCase):

    def setUp(self):
        self.conn = model.DBConnection('test')

    def test_create_table_valid(self):
        collection = model.UserCollection(self.conn).create()
        time.sleep(10)
        self.assertIsInstance(collection, model.DBTable)

