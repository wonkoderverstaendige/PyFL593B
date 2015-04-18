#!/usr/bin/env python
# coding=utf-8

import unittest

from PyFL593FL.core.util import encode_command, decode_command


class Test(unittest.TestCase):
    """Unit tests for utils.fn()"""

    def test_encode_command(self):
        """Test command string encoding"""
        self.assertEqual(["TEST", "STRING"], encode_command("test string"))

    def test_decode_command(self):
        """Test command string decoding"""
        self.assertEqual(["TEST", "STRING"], encode_command("test string"))
        
    # def test_doctest(self):
        # import doctest
        # import my_program.utils
        # doctest.testmod(my_program.utils)


if __name__ == "__main__":
    unittest.main()
