from contextlib import contextmanager
import os
import random
import string
from sqlalchemy import create_engine
import unittest

def random_string(length=10, prefix='', suffix=''):
    chars = string.ascii_lowercase + string.digits
    s = ''.join(random.choice(chars) for _ in range(length))
    return prefix + s + suffix

@contextmanager
def temp_database(db_name=None):
    db_name = db_name or random_string(prefix='db-', suffix='.sql')
    engine = create_engine('sqlite:///' + db_name, encoding='utf-8')
    try:
        yield engine
    finally:
        os.remove(db_name)

class BaseTestClient(unittest.TestCase): #pylint: disable=too-many-public-methods

    def assert_all_variables(self, obj, skip=[]): #pylint: disable=dangerous-default-value
        # assert all variables in object are not none
        keys = vars(obj).keys()
        real_keys = list(set(keys) - set(skip))
        for key in real_keys:
            self.assertNotEqual(getattr(obj, key), None)
            # if list, check not empty
            if isinstance(getattr(obj, key), list):
                self.assertTrue(getattr(obj, key))
            if isinstance(getattr(obj, key), str):
                self.assertTrue(len(getattr(obj, key)) > 0)

    def assertLength(self, item, length):
        self.assertEqual(len(item), length)
