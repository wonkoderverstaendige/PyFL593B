#!/usr/bin/env python
# coding=utf-8

import unittest
import time

from PyFL593FL.core.util import encode_command, memoize_with_expiry
from PyFL593FL.core.constants import *


class Test(unittest.TestCase):
    """Unit tests for utils.fn()"""

    def test_encode_command(self):
        """Test command string encoding"""
        # FIXME needs assertion
        encode_command("status read model")

    def test_decode_command(self):
        """Test command string decoding"""
        encode_command("status read model")
        
    # def test_doctest(self):
        # import doctest
        # import my_program.utils
        # doctest.testmod(my_program.utils)

    def test_memoize_with_expiry(self):
        """A horribly designed test! This one can cause false alarm if the random numbers are
        identical!"""
        @memoize_with_expiry(0.1)
        def read(op_code):
            return time.time()

        first = read(CMD_IMON)
        cached = read(CMD_IMON)
        self.assertEqual(first, cached)
        time.sleep(0.1)
        expired = read(CMD_IMON)  # should be different!
        self.assertNotEqual(first, expired, msg="Cache not randomized!")

if __name__ == "__main__":
    unittest.main()
