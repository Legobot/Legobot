import unittest
from legoCron import *


class test_f_is_num(unittest.TestCase):
    def test_integers(self):
        assert is_integer(3)
        assert is_integer(-285789)
        assert is_integer(0)

    def test_int_strings(self):
        assert is_integer('3')
        assert is_integer('-285789')
        assert is_integer('0')

    def test_floats(self):
        assert not is_integer(7.81)
        assert not is_integer(-23.59)

    def test_int_castable_floats(self):
        assert is_integer(7.00)
        assert is_integer(-23.00)
        assert is_integer(0.0)

    def test_float_strings(self):
        assert not is_integer('7.81')
        assert not is_integer('-23.59')

    def test_int_castable_float_strings(self):
        assert is_integer('7.00')
        assert is_integer('-23.00')
        assert is_integer('0.0')
