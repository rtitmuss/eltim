# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import machine

from pimoroni import Button

from clock import Clock
from display import Display
import ota
import task
import wlan


class Kernel:

    def __init__(self, config):
        self.display = Display(config.ROTATE)
        self.buttons = list(
            map(lambda pin: Button(pin),
                (12, 13, 14, 15) if not config.ROTATE else (15, 14, 13, 12)))

        self.WIFI_SSID = config.WIFI_SSID
        self.WIFI_PASSWORD = config.WIFI_PASSWORD
        self.TIMEZONE = config.TIMEZONE

    def add_task(self, *args):
        task.add_task(*args)

    def wlan_connect(self, now=Clock.now()):
        self.display.show_status(now, 'connecting', 'wifi ...')
        if not wlan.connect(self.WIFI_SSID, self.WIFI_PASSWORD, self.TIMEZONE):
            self.display.show_status(now, 'error', 'wifi ...')
            return False

        return True

    def wlan_disconnect(self):
        wlan.disconnect()

    def install_any_updates(self, owner, repo):
        if ota.check_for_update(owner, repo):
            self.display.show_status(Clock.now(), 'firmware', 'update ...')
            ota.install_update(owner, repo)
            wlan.disconnect()
            machine.reset()

    def run(self, app):
        while True:
            now = Clock.now()

            task_run = task.exec_tasks(now)

            pressed = list(map(lambda button: button.read(), self.buttons))

            if any(pressed) or task_run:
                app.render(now, pressed)
