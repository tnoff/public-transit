import random
import string
import unittest

def random_string(length=10, prefix='', suffix=''):
    chars = string.ascii_lowercase + string.digits
    s = ''.join(random.choice(chars) for _ in range(length))
    return prefix + s + suffix

class BaseTestClient(unittest.TestCase): #pylint: disable=too-many-public-methods

    def assert_dictionary(self, obj, skip=[]): #pylint: disable=dangerous-default-value
        if not isinstance(obj, list):
            obj_list = [obj]
        else:
            obj_list = obj
        for item in obj_list:
            for key, value in item.items():
                if key in skip:
                    continue
                self.assertNotEqual(value, None)

    def assertLength(self, item, length):
        self.assertEqual(len(item), length)
