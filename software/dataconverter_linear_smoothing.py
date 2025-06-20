#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 02:05:27 2025

@author: benjaminokoronkwo
"""

import csv
import numpy as np
import os

"""
BUDDY ‑ X‑Frame Motion Profile Generator
---------------------------------------
Reads X‑axis translation data (in metres) exported from Blender, converts it to
stepper‑motor step/delay arrays for an X‑axis driven by a 20‑tooth GT2 pulley
(40 mm circumference) with a 1 / 16‑micro‑stepped NEMA‑17 (1600 steps/rev).
The script outputs Arduino‑ready arrays: `deltaSteps[]` and `delayTimes[]`.
"""

# === USER CONFIGURATION ===

# Path to CSV exported from Blender (must contain an "X (m)" column)
filepath = "/Users/benjaminokoronkwo/BUDDY/data/motion/xtestgantry_data.csv"

# Folder + filename for the Arduino arrays
output_folder = "/Users/benjaminokoronkwo/BUDDY/data/processed"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "xframe_testgantry.txt")

# Mechanical parameters for Zeelo GT2 pulley system
pulley_teeth = 20                     # Number of teeth on GT2 pulley
belt_pitch_mm = 2                    # GT2 5M = 5mm pitch (NOT 2mm)
circumference = pulley_teeth * belt_pitch_mm / 1000  # metres/rev → 0.1 m/rev
steps_per_rev = 1600                 # 1/16 micro-stepping on 200-step NEMA 17

# === 1. LOAD CSV (TIME + X) ===
times_s: list[float] = []
positions_m: list[float] = []

with open(filepath, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        times_s.append(float(row["Time (s)"]))
        positions_m.append(float(row["X (m)"]))

if len(times_s) < 2:
    raise ValueError("CSV does not contain enough rows of data.")

# === 2. OPTIONAL SINE EASING IN METRES ===
start_x, end_x = positions_m[0], positions_m[-1]
displacement   = end_x - start_x

if abs(displacement) < 1e-4:
    eased_m = positions_m  # essentially no travel
else:
    ease = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, len(positions_m)))
    eased_m = [start_x + displacement * e for e in ease]

# === 3. CONVERT METRES → STEPS ===
def m_to_steps(x_m: float, steps_rev: int = steps_per_rev, circ: float = circumference) -> int:
    return int(round((x_m / circ) * steps_rev))

steps = [m_to_steps(x) for x in eased_m]

# === 4. DELTA STEPS + PER‑STEP DELAYS (μs) ===
delta_steps: list[int] = []
delay_times_us: list[int] = []

for i in range(1, len(steps)):
    d_steps = steps[i] - steps[i - 1]
    delta_steps.append(d_steps)

    dt_s = times_s[i] - times_s[i - 1]
    if d_steps != 0 and dt_s > 0:
        velocity_sps = abs(d_steps) / dt_s          # steps per second
        delay_us = int(1_000_000 / velocity_sps)   # μs per individual step
    else:
        delay_us = 0
    delay_times_us.append(delay_us)

# === 5. EXPORT ARDUINO ARRAYS ===
with open(output_path, "w") as f:
    f.write(f"const int dataLength = {len(delta_steps)};\n")
    f.write("int deltaSteps[dataLength] = {\n  " + ", ".join(map(str, delta_steps)) + "\n};\n")
    f.write("unsigned int delayTimes[dataLength] = {\n  " + ", ".join(map(str, delay_times_us)) + "\n};\n")

print(f"Export complete → {output_path}\nΔsteps range: {min(delta_steps)} .. {max(delta_steps)}")
