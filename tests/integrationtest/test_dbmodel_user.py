from unittest import TestCase

from boto.dynamodb2.table import Table

from util import model


class TestModel(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = model.DBConnection("test")
        cls.user_collection = model.UserCollection(cls.conn)

    def test_table_exists(self):
        tables = self.conn.conn.list_tables()
        self.assertIn(model.UserCollection.table_name, tables['TableNames'])

    def test_table_exists_model(self):
        self.assertTrue(self.user_collection.exists())

# unit
    def test_user_good_password(self):
        user = model.User(
                self.user_collection,
                email='email',
                password='thisismypassword',
                first_name='first',
                last_name='last')
        self.assertTrue(user.verify_password("thisismypassword"))

        # unit
    def test_user_bad_password(self):
        user = model.User(
            self.user_collection,
            email='email',
            password='thisismypassword',
            first_name='first',
            last_name='last')
        self.assertFalse(user.verify_password("thisisNOTmypassword"))


    def test_scan_model(self):
        self.assertGreater(map(lambda x: x._data, self.user_collection.scan()), 1)

    def test_scan(self):
        t = Table('users', connection=self.conn.conn)
        x = t.scan()
        self.assertGreater(map(lambda x: x._data, x),1)

    # intgr
    def test_create_add_user(self):
        user = model.User(
            self.user_collection,
            email='george.washington@whitehouse.gov',
            password='cherryTr33',
            first_name='George',
            last_name='Washington')
        user.save(overwrite=True)
        gw = self.user_collection.get_item(
            email='george.washington@whitehouse.gov')
        self.assertEqual(user.first_name, gw['first_name'])
#        self.assertEqual(user['first_name'], gw['first_name'])
        user.delete()
