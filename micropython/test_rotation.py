from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
import time


def draw_outline(rotate):
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY,
                           pen_type=PEN_P4,
                           rotate=rotate)

    RED = display.create_pen(255, 0, 0)
    GREEN = display.create_pen(0, 255, 0)
    BLACK = display.create_pen(0, 0, 0)

    MIN_X = 0
    MAX_X = 239

    MIN_Y = 0
    MAX_Y = 134

    display.set_pen(BLACK)
    display.clear()
    display.update()

    time.sleep(1)

    display.set_pen(RED if rotate == 0 else GREEN)

    display.line(MIN_X, MIN_Y, MAX_X, MIN_Y)
    display.line(MAX_X, MIN_Y, MAX_X, MAX_Y)
    display.line(MAX_X, MAX_Y, MIN_X, MAX_Y)
    display.line(MIN_X, MAX_Y, MIN_X, MIN_Y)

    display.update()


while True:
    draw_outline(180)
    time.sleep(1)
    draw_outline(0)
    time.sleep(1)
