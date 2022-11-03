# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import array
import unittest

from price import *
from clock import Clock


class TestHourlyPricesMethods(unittest.TestCase):

    def test_should_update_price(self):
        prices_0 = ()
        prices_24 = [0 for i in range(24)]
        prices_48 = [0 for i in range(48)]

        self.assertEqual(should_update(prices_0, Clock(0)), True)
        self.assertEqual(should_update(prices_0, Clock(13)), True)
        self.assertEqual(should_update(prices_24, Clock(0)), False)
        self.assertEqual(should_update(prices_24, Clock(13)), True)
        self.assertEqual(should_update(prices_48, Clock(0)), True)
        self.assertEqual(should_update(prices_48, Clock(13)), False)

    def test_appliance_cost(self):
        prices = array.array('f', [1, 2, 3])
        self.assertEqual(appliance_cost(prices, Clock(0), [1, 2]), 5)
        self.assertEqual(appliance_cost(prices, Clock(1), [1, 2]), 8)

    def test_cheapest_hour_and_cost(self):
        prices = (2, 1, 2, 2)
        self.assertEqual(cheapest_hour_and_cost(prices, Clock(0), [10]),
                         (Clock(1), 10))
        self.assertEqual(cheapest_hour_and_cost(prices, Clock(1), [10]),
                         (Clock(2), 20))
        self.assertEqual(cheapest_hour_and_cost(prices, Clock(0), [10, 10]),
                         (Clock(1), 30))


if __name__ == '__main__':
    unittest.main()
