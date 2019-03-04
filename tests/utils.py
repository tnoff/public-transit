from contextlib import contextmanager
import os
import random
import string
import unittest

def random_string(prefix='', suffix='', length=10):
    chars = string.ascii_lowercase + string.digits
    tempy = ''.join(random.choice(chars) for _ in range(length))
    return prefix + tempy + suffix

@contextmanager
def temp_file(name=None, suffix='', delete=True):
    if not name:
        name = random_string(prefix='/tmp/', suffix=suffix)
    try:
        yield name
    finally:
        if delete:
            try:
                os.remove(name)
            except OSError as exc:
                if exc.errno == os.errno.ENOENT:
                    pass
                else:
                    raise

class TestRunnerHelper(unittest.TestCase):
    '''
    Test runner class with helper methods
    '''
    def check_error_message(self, error, error_message):
        '''
        Check that error has matching error message
        '''
        self.assertEqual(str(error.exception), error_message)

    def assert_dictionary(self, actual_dictionary, expected_dictionary):
        '''
        Check dictionary objects match
        '''
        # Check for missing or extra keys
        expected_keys = set(expected_dictionary.keys())
        actual_keys = set(actual_dictionary.keys())

        missing_keys = expected_keys - actual_keys
        if len(missing_keys) > 0:
            raise AssertionError("Error: dictionary missing keys: %s" % missing_keys)

        extra_keys = actual_keys - expected_keys
        if len(extra_keys) > 0:
            raise AssertionError("Error: dictionary has extra keys: %s" % extra_keys)

        # Check values match expected
        for key, value in actual_dictionary.items():
            self.assertEqual(value, expected_dictionary[key])
