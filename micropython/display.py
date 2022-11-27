# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

from math import floor
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4

LINE_1 = 16
LINE_2 = 48
LINE_3 = 80
LINE_4 = 112


def text_right_align(display, text, x, y, wordwrap, scale):
    width = display.measure_text(text, scale)
    display.text(text, x - width, y, wordwrap, scale)


class Display:

    def __init__(self, rotate=False):
        self.led = RGBLED(6, 7, 8)
        self.led.set_rgb(0, 0, 0)

        # work around for https://github.com/pimoroni/pimoroni-pico/issues/562
        if rotate:
            display = PicoGraphics(display=DISPLAY_PICO_DISPLAY,
                                   pen_type=PEN_P4,
                                   rotate=0)
            black = display.create_pen(0, 0, 0)
            display.set_pen(black)
            display.clear()

        display = PicoGraphics(display=DISPLAY_PICO_DISPLAY,
                               pen_type=PEN_P4,
                               rotate=180 if rotate else 0)

        self.display = display
        self.WHITE = display.create_pen(255, 255, 255)
        self.BLACK = display.create_pen(0, 0, 0)
        self.RED = display.create_pen(255, 0, 0)
        self.GREEN = display.create_pen(0, 255, 0)
        self.YELLOW = display.create_pen(255, 255, 0)

    def level_to_color(self, level):
        if level == 'LOW':
            return self.GREEN
        elif level == 'NORMAL':
            return self.YELLOW
        else:
            return self.RED

    def show_status(self, time, line1, line2=None):
        display = self.display

        display.set_pen(self.BLACK)
        display.clear()

        display.set_pen(self.WHITE)
        display.set_font("sans")
        display.text(line1, 10, LINE_1, 240, 1)
        if line2:
            display.text(line2, 10, LINE_2, 240, 1)

        display.set_font("bitmap8")
        text_right_align(display, str(time), 230, 114, 240, 1)

        display.update()

    def show_appliance(self, name, currency, idx, total_idx, now, time, cost,
                       level, cheapest_time, cheapest_cost, cheapest_level,
                       timer_at):
        display = self.display
        delay_time = now.diff(cheapest_time)
        time_offset = time.hour - now.hour

        now_level = level[0]
        time_level = level[time_offset]

        if now_level == 'LOW':
            self.led.set_rgb(0, 16, 0)  # green
        elif now_level == 'HIGH':
            self.led.set_rgb(16, 0, 0)  # red
        else:
            self.led.set_rgb(0, 0, 0)  # off

        display.set_pen(self.BLACK)
        display.clear()

        display.set_pen(self.WHITE)

        if total_idx > 1:
            scroll_len = floor(135 / total_idx)
            display.line(1, scroll_len * idx, 1, (scroll_len * idx) + scroll_len)

        display.set_font("bitmap8")
        text_right_align(display, str(now), 230, 114, 240, 1)

        display.set_font("sans")
        display.text(name, 10, LINE_1, 240, 1)

        if timer_at:
            display.text('timer set', 10, LINE_2, 240, 1)
            display.text(str(timer_at), 10, LINE_3, 240, 1)
        else:
            if time_offset == 0:
                display.text('now', 10, LINE_2, 240, 1)
            else:
                display.text(str(time), 10, LINE_2, 240, 1)

            display.set_pen(self.level_to_color(time_level))
            text_right_align(display, '{:.2f}{}'.format(cost, currency), 230,
                             LINE_2, 240, 1)

            if cheapest_cost < cost:
                display.set_pen(self.WHITE)

                display.text(str(cheapest_time), 10, LINE_3, 240, 1)
                display.text(
                    'in {}h {}m'.format(delay_time.hour, delay_time.minute),
                    10, LINE_4, 240, 1)

                display.set_pen(self.level_to_color(cheapest_level))
                text_right_align(display,
                                 '{:.2f}{}'.format(cheapest_cost, currency),
                                 230, LINE_3, 240, 1)

        len_level = len(level)
        total_len = floor(230 / len_level) * len_level
        bar_len = floor(total_len / len_level)
        line_len = bar_len - 3

        x = floor((240 - total_len) / 2)
        for i in range(len_level):
            display.set_pen(self.level_to_color(level[i]))

            x2 = x + line_len
            if i == time_offset:
                display.line(x, 131, x2, 131)
                display.line(x, 132, x2, 132)
            display.line(x, 133, x2, 133)

            x += bar_len

        display.update()

    def show_timer(self, name, currency, time):
        display = self.display

        display.set_pen(self.BLACK)
        display.clear()

        display.set_pen(self.WHITE)

        display.set_font("sans")
        display.text(name, 10, LINE_1, 240, 1)
        display.text('timer at', 10, LINE_2, 240, 1)
        display.text(str(time), 10, LINE_3, 240, 1)

        display.set_pen(self.RED)
        display.text('cancel', 10, LINE_4, 240, 1)

        display.set_pen(self.GREEN)
        text_right_align(display, 'ok', 230, LINE_4, 240, 1)

        display.update()
