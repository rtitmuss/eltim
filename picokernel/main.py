# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import os
import sys

# repair failed ota
if not 'app' in os.listdir('/'):
    os.rename('app.old', 'app')
if not 'picokernel' in os.listdir('/'):
    os.rename('picokernel.old', 'picokernel')

sys.path.append('app')
sys.path.append('picokernel')
import app.main

