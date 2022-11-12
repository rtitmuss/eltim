# eltim
A gadget to show the cheapest electric prices using tibber api

## Hardware
- [Raspberry Pi Pico W](https://www.raspberrypi.com/products/raspberry-pi-pico/)
- [Pico Display Pack](https://shop.pimoroni.com/products/pico-display-pack)

## Install

Install MicroPython with support for the Pico Display Plack from https://github.com/pimoroni/pimoroni-pico/releases/latest/

Then install eltime using:
```
mpremote connect /dev/tty.usbmodem14??? soft-reset mip install --target app github:rtitmuss/eltim
mpremote connect /dev/tty.usbmodem14??? mip install --target . github:rtitmuss/eltim/main.py
```

Any future updates are automatically installed by OTA from github.

## Development

Code format using `yapf -i *.py`
