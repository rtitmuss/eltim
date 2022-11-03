# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import math
import network
import ntptime
import random
import time

from clock import Clock

wlan = network.WLAN(network.STA_IF)


def _retry(name, f):
    backoff_time_ms = 1000

    for attempt in range(10):
        try:
            if f() != False:
                print('{} success after {} attempts'.format(name, attempt))
                return
        except Exception as e:
            print('{} error: {} {}'.format(name, type(e), e))

        delay_ms = min(backoff_time_ms + random.randrange(1000), 10000)
        time.sleep_ms(delay_ms)

        backoff_time_ms *= 2


def connect(ssid, password, timezone):
    wlan.active(True)
    wlan.connect(ssid, password)

    _retry('wifi', lambda: wlan.isconnected() or wlan.status() < 0)

    if not wlan.isconnected():
        display.show_status(now, 'error', 'wifi ...')
        return False

    print('wifi connected {}'.format(wlan.ifconfig()))

    _retry('ntp', ntptime.settime)
    _retry('timezone', lambda: Clock.set_timezone(timezone))

    return True


def disconnect():
    wlan.disconnect()
    wlan.active(False)
