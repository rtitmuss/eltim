# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import gc
import math
import micropython
import time

from servo import Servo

from clock import Clock
import price
import tibber

MAX_TIME_OFFSET = 10


def _highest_level(level):
    if 'HIGH' in level:
        return 'HIGH'
    if 'NORMAL' in level:
        return 'NORMAL'
    return 'LOW'


class PriceScreen:

    def __init__(self, eltim):
        self.eltim = eltim
        self.config = eltim.config
        self.kernel = eltim.kernel

        self.appliance_idx = 0
        self.time_offset = 0

    def button(self, now, pressed):
        if pressed[0]:
            self.appliance_idx = (self.appliance_idx + 1) % len(
                self.config.APPLIANCE)

        if pressed[1]:
            self.time_offset = (self.time_offset + 1) % MAX_TIME_OFFSET
            self.kernel.add_task('time_offset', 5000,
                                 lambda now: self._reset_time_offset())

        if pressed[2]:
            appliance = self.config.APPLIANCE[self.appliance_idx]

            if 'servo' in appliance:
                cheapestTime, cheapestCost, cheapestLevel = self.eltim.cheapest_for_appliance(
                    now, appliance)

                timer_at = cheapestTime if self.time_offset == 0 else Clock(
                    now.hour + self.time_offset)

                self.kernel.set_screen(
                    TimerScreen(self.eltim, self, appliance, timer_at))

    def _reset_time_offset(self):
        self.time_offset = 0

    def render(self, now):
        pricePerHour = self.eltim.pricePerHour
        levelPerHour = self.eltim.levelPerHour

        if len(pricePerHour) == 0:
            return

        time = now if self.time_offset == 0 else Clock(now.hour +
                                                       self.time_offset)

        appliance = self.config.APPLIANCE[self.appliance_idx]

        cost = price.appliance_cost(pricePerHour, time,
                                    appliance['kwhPerHour'])
        level = list(
            map(
                lambda i: _highest_level(levelPerHour[
                    now.hour + i:now.hour + i + len(appliance['kwhPerHour'])]),
                range(MAX_TIME_OFFSET)))

        cheapestTime, cheapestCost, cheapestLevel = self.eltim.cheapest_for_appliance(
            now, appliance)

        self.eltim.display.show_appliance(appliance['name'],
                                          self.config.CURRENCY,
                                          self.appliance_idx,
                                          len(self.config.APPLIANCE), now,
                                          time, cost, level, cheapestTime,
                                          cheapestCost, cheapestLevel,
                                          self.eltim.is_timer_at(appliance))


class TimerScreen:

    def __init__(self, eltim, back_screen, appliance, timer_at):
        self.eltim = eltim
        self.config = eltim.config
        self.kernel = eltim.kernel

        self.back_screen = back_screen
        self.appliance = appliance
        self.timer_at = timer_at

        self.kernel.add_task(
            'timer_screen', 60000,
            lambda now: self.kernel.set_screen(self.back_screen))

    def _back(self):
        self.kernel.cancel_task('timer_screen')
        self.kernel.set_screen(self.back_screen)

    def button(self, now, pressed):
        if pressed[3]:
            self.eltim.set_timer(now, self.appliance, self.timer_at)
            self._back()

        if pressed[1]:
            self.eltim.cancel_timer(self.appliance)
            self._back()

    def render(self, now):
        pricePerHour = self.eltim.pricePerHour
        levelPerHour = self.eltim.levelPerHour

        cheapestTime, cheapestCost, cheapestLevel = self.eltim.cheapest_for_appliance(
            self.timer_at, self.appliance)

        self.eltim.display.show_timer(self.appliance['name'],
                                      self.config.CURRENCY, self.timer_at)


class Eltim:

    def __init__(self, kernel, display):
        self.kernel = kernel
        self.config = kernel.config
        self.display = display

        self.pricePerHour = ()
        self.levelPerHour = ()
        self.timer_at = {}

        self.servo = dict(
            map(lambda e: (e['name'], Servo(e['servo'])),
                filter(lambda e: 'servo' in e, self.config.APPLIANCE)))

        self.kernel.set_screen(PriceScreen(self))

        self.kernel.add_task('check_prices', 0,
                             lambda now: self._check_prices(now))

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
        self.display.show_status(now, 'loading', 'tibber ...')
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

    def cheapest_for_appliance(self, now, appliance):
        cheapestTime, cheapestCost = price.cheapest_hour_and_cost(
            self.pricePerHour, now, appliance['kwhPerHour'])
        cheapestLevel = _highest_level(
            self.levelPerHour[cheapestTime.hour:cheapestTime.hour +
                              len(appliance['kwhPerHour'])])

        return (cheapestTime, cheapestCost, cheapestLevel)

    def timer_fired(self, appliance):
        self.cancel_timer(appliance)
        print('timer {}'.format(appliance['name']))

        servo = self.servo[appliance['name']]
        servo.value(80)
        time.sleep(1)
        servo.to_min()
        time.sleep(1)

    def set_timer(self, now, appliance, timer_at):
        timer_millis = now.diff(timer_at).to_millis()
        print('set timer {} at {} ({} millis)'.format(appliance['name'],
                                                      timer_at, timer_millis))
        self.timer_at[appliance['name']] = timer_at
        self.kernel.add_task('timer_{}'.format(appliance['name']),
                             timer_millis,
                             lambda now: self.timer_fired(appliance))

    def cancel_timer(self, appliance):
        print('cancel timer {}'.format(appliance['name']))
        if appliance['name'] in self.timer_at:
            del self.timer_at[appliance['name']]
        self.kernel.cancel_task('timer_{}'.format(appliance['name']))

    def is_timer_at(self, appliance):
        return self.timer_at.get(appliance['name'])
