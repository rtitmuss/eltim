import array
import urequests as requests

_QUERY = const(
    """{ viewer { homes { currentSubscription { priceInfo { today { startsAt total level } tomorrow { startsAt total level } } } } }}"""
)


def _chain(*p):
    for i in p:
        yield from i


def fetch_price_info(token):
    try:
        response = requests.post('https://api.tibber.com/v1-beta/gql', \
                                 json = { 'query': _QUERY }, \
                                 headers = {'Authorization': 'Bearer {}'.format(token)})

        data = response.json()
        response.close()

        price_info = data['data']['viewer']['homes'][0]['currentSubscription'][
            'priceInfo']

        return array.array('f', map(lambda e: e['total'], _chain(price_info['today'], price_info['tomorrow']))), \
               list(map(lambda e: e['level'], _chain(price_info['today'], price_info['tomorrow'])))

    except Exception as e:
        print('tibber error: {} {}'.format(type(e), e))
        return (), ()
