# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import gc
import micropython

from eltim import Eltim
from kernel import Kernel
import config

gc.collect()
micropython.mem_info()

kernel = Kernel(config)

kernel.wlan_connect()
kernel.install_any_updates('rtitmuss', 'eltim')

gc.collect()
micropython.mem_info()

kernel.run(Eltim(kernel, config))
