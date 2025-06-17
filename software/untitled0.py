#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converts Blender angle data to stepper motor control instructions.
Assumes: 1.8° step angle, 8 microsteps/step → 0.225° per microstep
"""

import numpy as np

# Blender angle data (deg)
blender_data = [
    (0.0, 0), (0.1, 10), (0.2, 25), (0.3, 45), (0.4, 65),
    (0.5, 80), (0.6, 90), (0.7, 90), (0.8, 90), (0.9, 90),
    (1.0, 80), (1.1, 60), (1.2, 40), (1.3, 20), (1.4, 5),
    (1.5, 0), (1.6, 0), (1.7, 0), (1.8, 0), (1.9, 0),
    (2.0, 0),
]

# Microstep conversion
deg_per_microstep = 1.8 / 8  # = 0.225
angle = np.array([tup[1] for tup in blender_data])
steps = angle / deg_per_microstep

# Get delta steps (difference between frames), round to int
delta_steps = np.round(np.diff(steps)).astype(int)

# Time between frames (seconds)
dt = 0.1
velocity = delta_steps / dt

# Delay per step (microseconds) = 1 sec / steps per sec
micro_delay = 1e6 / np.abs(velocity)

# Clamp any infinite or unreasonable values
micro_delay = np.nan_to_num(micro_delay, nan=1000.0, posinf=1000.0, neginf=1000.0)
micro_delay = np.clip(micro_delay, 200, 5000).astype(int)

# Output arrays
def PytoArd(name, array):
    c_array = ', '.join(str(int(x)) for x in array)
    print(f"{name}[] = {{{c_array}}};")

print("\nArduino arrays:\n")
PytoArd("int delta", delta_steps)
PytoArd("int offset", micro_delay)
