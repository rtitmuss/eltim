# eltim
A gadget to show the cheapest electric prices using tibber api

## Hardware
- [Raspberry Pi Pico W](https://www.raspberrypi.com/products/raspberry-pi-pico/)
- [Pico Display Pack](https://shop.pimoroni.com/products/pico-display-pack)

## Install

Install MicroPython with support for the Pico Display Plack from https://github.com/pimoroni/pimoroni-pico/releases/latest/

Install eltime using `mpremote connect /dev/tty.usbmodem14??? soft-reset mip install --target . github:rtitmuss/eltim`

## Development

Code format using `yapf -i *.py`
