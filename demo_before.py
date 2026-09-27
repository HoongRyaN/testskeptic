import unittest

from shipping import shipping_fee


#Intentionally incomplete test suite for the before demo.
class TestShippingFee(unittest.TestCase):
    def test_small_order(self):
        self.assertEqual(shipping_fee(50), 10)

    def test_large_order(self):
        self.assertEqual(shipping_fee(150), 0)

    def test_exact_threshold(self):
        self.assertEqual(shipping_fee(100), 0)
