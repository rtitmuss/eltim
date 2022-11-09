# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import gc
import machine
import math
import micropython

from pimoroni import Button

from clock import Clock
from display import Display
import price
import task
import tibber
import wlan

from config import *

MAX_TIME_OFFSET = 10


def print_appliance(now, pricePerHour, appliance):
    cost = price.appliance_cost(pricePerHour, now, appliance['kwhPerHour'])
    cheapestTime, cheapestCost = price.cheapest_hour_and_cost(
        pricePerHour, now, appliance['kwhPerHour'])

    print('{}: now {:.2f} {}. cheapest {:.2f} {} saving {:.2f} {} at {} in {} is {}'.format( \
        appliance['name'], \
        cost, CURRENCY, \
        cheapestCost, CURRENCY, \
        cost - cheapestCost, CURRENCY, \
        cheapestTime, \
        now.diff(cheapestTime), \
        levelPerHour[cheapestTime.hour]))


def display_appliance(now, pricePerHour, levelPerHour):
    time = now if time_offset == 0 else Clock(now.hour + time_offset)

    appliance = APPLIANCE[appliance_idx]

    cost = price.appliance_cost(pricePerHour, time, appliance['kwhPerHour'])
    level = list(
        map(
            lambda i: highest_level(levelPerHour[
                now.hour + i:now.hour + i + len(appliance['kwhPerHour'])]),
            range(MAX_TIME_OFFSET)))

    cheapestTime, cheapestCost = price.cheapest_hour_and_cost(
        pricePerHour, now, appliance['kwhPerHour'])
    cheapestLevel = highest_level(
        levelPerHour[cheapestTime.hour:cheapestTime.hour +
                     len(appliance['kwhPerHour'])])

    display.show_appliance(appliance['name'], CURRENCY, appliance_idx,
                           len(APPLIANCE), now, time, cost, level,
                           cheapestTime, cheapestCost, cheapestLevel)


def highest_level(level):
    if 'VERY_EXPENSIVE' in level:
        return 'VERY_EXPENSIVE'
    if 'EXPENSIVE' in level:
        return 'EXPENSIVE'
    if 'NORMAL' in level:
        return 'NORMAL'
    if 'CHEAP' in level:
        return 'CHEAP'
    return 'VERY_CHEAP'


def tick(now):
    global pricePerHour, levelPerHour

    print('\n{}'.format(now))

    if price.should_update(pricePerHour, now):
        pricePerHour = ()
        levelPerHour = ()

        if not wlan_connect(now):
            return False

        print('loading tibber prices')
        display.show_status(now, 'loading', 'tibber ...')
        pricePerHour, levelPerHour = tibber.fetch_price_info(TIBBER_TOKEN)

        for i in range(len(pricePerHour)):
            pricePerHour[i] += GRID_PRICE

        wlan.disconnect()

        if len(pricePerHour) == 0:
            return False

    print('level: {} {:.2f} {}'.format(levelPerHour[now.hour],
                                       pricePerHour[now.hour], CURRENCY))
    for appliance in APPLIANCE:
        print_appliance(now, pricePerHour, appliance)

    return True


def gc_tick():
    gc.collect()
    print('\nInitial free: {} allocated: {}'.format(gc.mem_free(),
                                                    gc.mem_alloc()))
    micropython.mem_info()


def load_prices(now):
    ok = tick(now)
    gc_tick()

    if ok:
        task.add_task('load_prices',
                      Clock.now().round_up(1) * 1000, load_prices)
    else:
        task.add_task('load_prices', 1000, load_prices)


def render(now):
    if len(pricePerHour) > 0:
        display_appliance(now, pricePerHour, levelPerHour)


def wlan_connect(now):
    display.show_status(now, 'connecting', 'wifi ...')
    if not wlan.connect(WIFI_SSID, WIFI_PASSWORD, TIMEZONE):
        display.show_status(now, 'error', 'wifi ...')
        return False

    return True


def reset_time_offset(now):
    global time_offset
    time_offset = 0


buttons = list(
    map(lambda pin: Button(pin), (12, 13, 14, 15) if not ROTATE else
        (14, 15, 13, 12)))

display = Display(ROTATE)

appliance_idx = 0
time_offset = 0

pricePerHour = ()
levelPerHour = ()

wlan_connect(Clock.now())
task.add_task('load_prices', 0, load_prices)

while True:
    now = Clock.now()

    task_run = task.exec_tasks(now)

    pressed = list(map(lambda button: button.read(), buttons))

    if pressed[0]:
        appliance_idx = (appliance_idx + 1) % len(APPLIANCE)

    if pressed[1]:
        time_offset = (time_offset + 1) % MAX_TIME_OFFSET
        task.add_task('time_offset', 5000, reset_time_offset)

    if any(pressed) or task_run:
        render(now)
