# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import array
import urequests as requests

_QUERY = const(
    """{ viewer { homes { currentSubscription { priceInfo { current { startsAt } } priceRating { hourly { entries { total time level } } } } } } }"""
)


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

        today_tomorrow_rating = list(
            filter(lambda e: e['time'] >= today, price_rating))

        return array.array('f', map(lambda e: e['total'], today_tomorrow_rating)), \
               list(map(lambda e: e['level'], today_tomorrow_rating))

    except Exception as e:
        print('tibber error: {} {}'.format(type(e), e))
        return (), ()
