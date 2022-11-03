# Add your wifi configuration
WIFI_SSID = 'ssid'
WIFI_PASSWORD = 'password'

# Your tibber access token from https://developer.tibber.com/settings/access-token
TIBBER_TOKEN = 'token'

# Rotate display
ROTATE = False

# Timezone from http://worldtimeapi.org/timezones
TIMEZONE = 'Europe/Stockholm'

# Currency code
CURRENCY = 'sek'

# Elecric grid price (for example Ellevio) this is added to the hourly price
GRID_PRICE = 0.27 + 0.45 + 0.0596

# Appliances and approximate kWh consumed per hour
APPLIANCE = [{
    'name': 'dishwasher',
    'kwhPerHour': (0.6, 0.02, 0.28)
}, {
    'name': 'washer',
    'kwhPerHour': (0.9, 0.1)
}, {
    'name': 'dryer',
    'kwhPerHour': (1.5, 0.7)
}]
