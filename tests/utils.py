import unittest

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
