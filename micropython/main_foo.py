# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import gc
import machine
import math
import micropython
import time

from pimoroni import Button

from clock import Clock
from display import Display
import finger
import price
import tibber
import wlan

from config import *

MAX_TIME_OFFSET = 10

tasks = {}


def add_task(name, delay_ms, callback):
    global tasks
    tasks[name] = {
        'time': time.ticks_add(time.ticks_ms(), delay_ms),
        'callback': callback
    }


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


def render(now, pressed):
    global appliance_idx, time_offset

    if pressed[0]:
        appliance_idx = (appliance_idx + 1) % len(APPLIANCE)

    if pressed[1]:
        time_offset = (time_offset + 1) % MAX_TIME_OFFSET
        add_task('reset_time_offset', 5000, reset_time_offset)

        #next_tick = time.ticks_add(time.ticks_ms(), 5000)

    if pressed[2]:
        finger.press_button(0)

    if pressed[3]:
        finger.press_button(1)

    if len(pricePerHour) > 0:
        display_appliance(now, pricePerHour, levelPerHour)


def gc_tick():
    gc.collect()
    print('\nInitial free: {} allocated: {}'.format(gc.mem_free(),
                                                    gc.mem_alloc()))
    micropython.mem_info()


def wlan_connect(now):
    display.show_status(now, 'connecting', 'wifi ...')
    if not wlan.connect(WIFI_SSID, WIFI_PASSWORD, TIMEZONE):
        display.show_status(now, 'error', 'wifi ...')
        return False

    return True


def init_button(pin):
    machine.Pin(pin).irq(lambda pin: None),
    return Button(pin)


def call_tick(now):
    print('tick...')
    ok = tick(now)
    gc_tick()

    if ok:
        add_task('tick', Clock.now().round_up(1) * 1000, call_tick)
    else:
        add_task('tick', 10000, call_tick)


buttons = list(
    map(init_button, (12, 13, 14, 15) if not ROTATE else (14, 15, 13, 12)))

# button_a = Button(12 if not ROTATE else 15)
# button_b = Button(13 if not ROTATE else 14)
# button_x = Button(14 if not ROTATE else 13)
# button_y = Button(15 if not ROTATE else 12)
#
# machine.Pin(12).irq(handler=lambda x: print('foo'))
# machine.Pin(13).irq(handler=lambda x: print('foo'))
# machine.Pin(14).irq(handler=lambda x: print('foo'))
# machine.Pin(15).irq(handler=lambda x: print('foo'))

display = Display(ROTATE)

appliance_idx = 0
time_offset = 0

pricePerHour = ()
levelPerHour = ()

wlan_connect(Clock.now())
call_tick(Clock.now())

#next_tick = time.ticks_add(time.ticks_ms(), 0)

add_task('one', 10000, lambda now: print('one {}'.format(Clock.now())))
add_task('two', 15000, lambda now: print('two {}'.format(Clock.now())))
add_task('three', 20000, lambda now: print('three {}'.format(Clock.now())))


def reset_time_offset(now):
    global time_offset
    time_offset = 0


while True:
    now = Clock.now()

    now_ms = time.ticks_ms()

    ready = dict((k, v) for k, v in tasks.items()
                 if time.ticks_diff(v['time'], now_ms) < 0)
    #    tasks = dict((k, v) for k, v in tasks.items() if time.ticks_diff(v['time'], now_ms) >= 0)

    #    ready = list(filter(lambda task: time.ticks_diff(task['time'], now_ms) < 0, tasks))
    #    tasks = list(filter(lambda task: time.ticks_diff(task['time'], now_ms) >= 0, tasks))

    for key, task in ready.items():
        del tasks[key]
        task['callback'](now)

#     if time.ticks_diff(next_tick, time.ticks_ms()) < 0:
#         #time_offset = 0
#         ok = tick(now)
#         gc_tick()
#
#         delay_ms = 10000 if not ok else Clock.now().round_up(15) * 1000
#         next_tick = time.ticks_add(time.ticks_ms(), delay_ms)

    pressed = list(map(lambda button: button.read(), buttons))

    if any(pressed) or len(ready) > 0:
        render(now, pressed)

#    time.sleep_ms(100)

#     delay_ms = 1000 #time.ticks_diff(next_tick, time.ticks_ms())
#     if delay_ms > 0:
#         print('sleeping for {} ms'.format(delay_ms))
# #        time.sleep_ms(time.ticks_diff(next_tick, time.ticks_ms()))
#         machine.lightsleep(delay_ms)
#         print('exited sleep')
