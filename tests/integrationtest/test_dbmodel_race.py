from unittest import TestCase
import time

from boto.dynamodb2.table import Table

from util import model


class TestRace(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = model.DBConnection("test")
        print cls.conn.conn.list_tables()

        cls.race_collection = model.RaceCollection(cls.conn).create()
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        cls.race_collection.delete()

    def test_collection(self):
        self.assertEqual(self.race_collection.table_name, model.RaceCollection.table_name)

    def test_collection_table(self):
        self.assertIsInstance(self.race_collection._table, Table)

    def test_table_exists(self):
        self.assertTrue(self.race_collection.table_name in self.conn.conn.list_tables()['TableNames'])

    def test_write_read(self):
        print self.race_collection._table
        self.race_collection.insert(data={'_id': '_G2Ql0M7-EeO6Hqy3RlUohQ', 'dummy': '5'})
        race = self.race_collection.get_item(_id='_G2Ql0M7-EeO6Hqy3RlUohQ')
        self.assertEqual(race['dummy'], '5')

    def delete(self):
        race = self.race_collection.get_item(_id='_G2Ql0M7-EeO6Hqy3RlUohQ')
        race.delete()
