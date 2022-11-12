# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import os
import sys

# repair failed ota
if not 'app' in os.listdir('/'):
    os.rename('old', 'app')

sys.path.append("app")
import app.main
