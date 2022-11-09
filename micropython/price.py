# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

from clock import Clock


def _appliance_cost(hourly_prices, kwh_per_hour):
    return sum([x * y for x, y in zip(hourly_prices, kwh_per_hour)])


def should_update(hourly_prices, time):
    if time.hour < 13:
        return len(hourly_prices) != 24
    else:
        return len(hourly_prices) != 48


def appliance_cost(hourly_prices, time, kwh_per_hour):
    return _appliance_cost(hourly_prices[time.hour:], kwh_per_hour)


def cheapest_hour_and_cost(hourly_prices, time, kwh_per_hour):
    next_hour = time.hour + 1

    cost_per_hour = list(map(lambda i: _appliance_cost(hourly_prices[i:], kwh_per_hour), \
                             range(next_hour, len(hourly_prices) - len(kwh_per_hour))))

    min_cost = min(cost_per_hour[:12])
    min_hour = cost_per_hour.index(min_cost)

    return Clock(next_hour + min_hour), cost_per_hour[min_hour]
