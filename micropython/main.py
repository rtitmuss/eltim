# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import gc
import micropython

from display import Display
from kernel import Kernel

gc.collect()
micropython.mem_info()

kernel = Kernel(lambda *args: display.show_status(*args))
display = Display(kernel.config.ROTATE)

kernel.wlan_connect()
kernel.install_any_updates('rtitmuss', 'eltim')

gc.collect()
micropython.mem_info()

from eltim import Eltim

app = Eltim(kernel, display)
kernel.run()
