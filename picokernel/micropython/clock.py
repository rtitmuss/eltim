# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

from math import ceil, floor
import urequests
import utime


class Clock:
    utc_offset_sec = 0

    def __init__(self, hour=0, minute=0, second=0):
        self.hour = hour
        self.minute = minute
        self.second = second

    @staticmethod
    def now():
        now = utime.gmtime()
        return Clock(now[3], now[4], now[5]).add(second=Clock.utc_offset_sec)

    @staticmethod
    def set_timezone(timezone):
        response = urequests.get(
            'https://timeapi.io/api/TimeZone/zone?timeZone={}'.format(
                timezone))
        data = response.json()
        response.close()

        Clock.utc_offset_sec = data['currentUtcOffset']['seconds']

    def __str__(self):
        hour = self.hour
        if hour >= 24:
            hour -= 24

        if self.second > 0:
            return '{}:{:02d}:{:02d}'.format(hour, self.minute, self.second)
        else:
            return '{}:{:02d}'.format(hour, self.minute)

    def __eq__(self, time):
        return self.hour == time.hour and self.minute == time.minute and self.second == time.second

    def add(self, hour=0, minute=0, second=0):
        second += self.second
        minute += self.minute + floor(second / 60)
        hour += self.hour + floor(minute / 60)
        return Clock(hour, minute % 60, second % 60)

    def diff(self, time):
        if self.minute == 0:
            return Clock(time.hour - self.hour)
        return Clock(time.hour - self.hour - 1, 60 - self.minute)

    def to_millis(self):
        return self.hour * 3600000 + self.minute * 60000 + self.second * 1000

    def round_up(self, interval=10):
        m = (ceil(self.minute / interval) * interval) - self.minute
        if m == 0:
            return (interval * 60) - self.second
        return (m * 60) - self.second
