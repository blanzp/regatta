__author__ = 'Paul'

import model
from unittest import TestCase
import time


class TestModel(TestCase):

    def setUp(self):
        self.conn = model.DBConnection

#unit
    def test_user_good_password(self):
        user = model.User('me','thisismypassword','first','last','email')
        self.assertTrue(user.verify_password("thisismypassword"))
#unit
    def test_user_bad_password(self):
        user = model.User('me','thisismypassword','first','last','email')
        self.assertFalse(user.verify_password("thisisNOTmypassword"))
#intgr
    def test_create_table_valid(self):
        collection = self.conn.create(model.UserCollection)
        time.sleep(20)
        self.conn.delete(collection)

#unit
    def test_create_table_invalid(self):
        with self.assertRaises(model.InvalidCollectionType):
            coll = self.conn.create(55)

