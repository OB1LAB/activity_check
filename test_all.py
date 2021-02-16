import unittest
from activity_check import check_activity


class TestActivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_vanish(self):
        with open('./test_vanish.txt.txt', 'r', encoding='UTF-8') as file:
            log = file.read()
        data = check_activity(log)
        assert data == 'abc'
