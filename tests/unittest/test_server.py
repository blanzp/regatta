from unittest import TestCase

import application


class TestServer(TestCase):
    def test_middle_out_8(self):
        lanes = application.middle_out(8, 8)
        self.assertEqual([4, 5, 3, 6, 2, 7, 1, 8], lanes)

    def test_middle_out_8_3(self):
        lanes = application.middle_out(8, 3)
        self.assertEqual([4, 5, 3], lanes)

    def test_middle_out_12(self):
        lanes = application.middle_out(12, 12)
        self.assertEqual([6, 7, 5, 8, 4, 9, 3, 10, 2, 11, 1, 12], lanes)
