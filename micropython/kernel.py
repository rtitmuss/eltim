# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import machine
import time

from pimoroni import Button

from clock import Clock
from display import Display
import ota
import wlan

import config

class Kernel:

    def __init__(self):
        self.config = config

        self.display = Display(config.ROTATE)
        self.buttons = list(
            map(lambda pin: Button(pin),
                (12, 13, 14, 15) if not config.ROTATE else (15, 14, 13, 12)))

        self.tasks = {}

        self.WIFI_SSID = config.WIFI_SSID
        self.WIFI_PASSWORD = config.WIFI_PASSWORD
        self.TIMEZONE = config.TIMEZONE

    def add_task(self, name, delay_ms, callback):
        self.tasks[name] = {
            'time': time.ticks_add(time.ticks_ms(), delay_ms),
            'callback': callback
        }

    def exec_tasks(self, *args):
        now_ms = time.ticks_ms()
        ready = dict((k, v) for k, v in self.tasks.items()
                     if time.ticks_diff(v['time'], now_ms) < 0)

        for key, task in ready.items():
            del self.tasks[key]
            delay_ms = task['callback'](*args)
            if delay_ms != None:
                self.add_task(key, delay_ms, task['callback'])

        return len(ready) > 0

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

            task_run = self.exec_tasks(now)

            pressed = list(map(lambda button: button.read(), self.buttons))

            if any(pressed) or task_run:
                app.render(now, pressed)
