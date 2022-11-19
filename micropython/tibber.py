# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import array
import urequests as requests

_QUERY = const(
    """{ viewer { homes { currentSubscription { priceInfo { current { startsAt } } priceRating { hourly { entries { total time } } } } } } }"""
)


def get_level(e, low_price, high_price):
    e['level'] = 'LOW' if e['total'] < low_price else 'HIGH' if e[
        'total'] > high_price else 'NORMAL'
    return e


def fetch_price_info(token):
    try:
        response = requests.post('https://api.tibber.com/v1-beta/gql', \
                                 json = { 'query': _QUERY }, \
                                 headers = {'Authorization': 'Bearer {}'.format(token)})

        data = response.json()
        response.close()

        subscription = data['data']['viewer']['homes'][0][
            'currentSubscription']

        today = subscription['priceInfo']['current']['startsAt'][:10]
        price_rating = subscription['priceRating']['hourly']['entries']

        price = list(map(lambda e: e['total'], price_rating))

        min_price = min(price)
        max_price = max(price)
        avg_price = sum(price) / len(price)

        low_price = min_price + (avg_price - min_price) / 2
        high_price = avg_price + (max_price - avg_price) / 2

        today_tomorrow_rating = list(
            map(lambda e: get_level(e, low_price, high_price),
                filter(lambda e: e['time'] >= today, price_rating)))

        return array.array('f', map(lambda e: e['total'], today_tomorrow_rating)), \
               list(map(lambda e: e['level'], today_tomorrow_rating))

    except Exception as e:
        print('tibber error: {} {}'.format(type(e), e))
        return (), ()
