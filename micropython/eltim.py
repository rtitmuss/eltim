# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import gc
import math
import micropython

from clock import Clock
import price
import tibber

MAX_TIME_OFFSET = 10


def _highest_level(level):
    if 'VERY_EXPENSIVE' in level:
        return 'VERY_EXPENSIVE'
    if 'EXPENSIVE' in level:
        return 'EXPENSIVE'
    if 'NORMAL' in level:
        return 'NORMAL'
    if 'CHEAP' in level:
        return 'CHEAP'
    return 'VERY_CHEAP'


class Eltim:

    def __init__(self, kernel, config):
        self.kernel = kernel
        self.config = config

        self.appliance_idx = 0
        self.time_offset = 0

        self.pricePerHour = ()
        self.levelPerHour = ()

        self.kernel.add_task('check_prices', 0,
                             lambda now: self._check_prices(now))

    def render(self, now, pressed):
        if pressed[0]:
            self.appliance_idx = (self.appliance_idx + 1) % len(
                self.config.APPLIANCE)

        if pressed[1]:
            self.time_offset = (self.time_offset + 1) % MAX_TIME_OFFSET
            self.kernel.add_task('time_offset', 5000,
                                 lambda now: self._reset_time_offset())

        if len(self.pricePerHour) > 0:
            self._display_appliance(now)

    def _check_prices(self, now):
        print('\n{}'.format(now))

        if price.should_update(self.pricePerHour, now):
            if not self._load_prices(now):
                return 60 * 1000  # retry in 1 minute

        gc.collect()
        micropython.mem_info()

        print('level: {} {:.2f} {}'.format(self.levelPerHour[now.hour],
                                           self.pricePerHour[now.hour],
                                           self.config.CURRENCY))
        for appliance in self.config.APPLIANCE:
            self._print_appliance(now, appliance)

        return Clock.now().round_up(15) * 1000  # on every quarter hour

    def _load_prices(self, now):
        self.pricePerHour = ()
        self.levelPerHour = ()

        if not self.kernel.wlan_connect(now):
            return False

        print('loading tibber prices')
        self.kernel.display.show_status(now, 'loading', 'tibber ...')
        self.pricePerHour, self.levelPerHour = tibber.fetch_price_info(
            self.config.TIBBER_TOKEN)

        for i in range(len(self.pricePerHour)):
            self.pricePerHour[i] += self.config.GRID_PRICE

        self.kernel.wlan_disconnect()

        return len(self.pricePerHour) != 0

    def _print_appliance(self, now, appliance):
        cost = price.appliance_cost(self.pricePerHour, now,
                                    appliance['kwhPerHour'])
        cheapestTime, cheapestCost = price.cheapest_hour_and_cost(
            self.pricePerHour, now, appliance['kwhPerHour'])

        print('{}: now {:.2f} {}. cheapest {:.2f} {} saving {:.2f} {} at {} in {} is {}'.format( \
            appliance['name'], \
            cost, self.config.CURRENCY, \
            cheapestCost, self.config.CURRENCY, \
            cost - cheapestCost, self.config.CURRENCY, \
            cheapestTime, \
            now.diff(cheapestTime), \
            self.levelPerHour[cheapestTime.hour]))

    def _display_appliance(self, now):
        time = now if self.time_offset == 0 else Clock(now.hour +
                                                       self.time_offset)

        appliance = self.config.APPLIANCE[self.appliance_idx]

        cost = price.appliance_cost(self.pricePerHour, time,
                                    appliance['kwhPerHour'])
        level = list(
            map(
                lambda i: _highest_level(self.levelPerHour[
                    now.hour + i:now.hour + i + len(appliance['kwhPerHour'])]),
                range(MAX_TIME_OFFSET)))

        cheapestTime, cheapestCost = price.cheapest_hour_and_cost(
            self.pricePerHour, now, appliance['kwhPerHour'])
        cheapestLevel = _highest_level(
            self.levelPerHour[cheapestTime.hour:cheapestTime.hour +
                              len(appliance['kwhPerHour'])])

        self.kernel.display.show_appliance(appliance['name'],
                                           self.config.CURRENCY,
                                           self.appliance_idx,
                                           len(self.config.APPLIANCE), now,
                                           time, cost, level, cheapestTime,
                                           cheapestCost, cheapestLevel)

    def _reset_time_offset(self):
        self.time_offset = 0
