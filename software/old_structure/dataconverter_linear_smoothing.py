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

# === INPUT FILE: CSV exported from Blender ===
# (must contain a column labeled "X (m)")
filepath = "/Users/benjaminokoronkwo/BUDDY/data/motion/tilt_x-axis_test7.csv"

# === OUTPUT FILE: Auto-generated .txt in /processed ===
output_folder = "/Users/benjaminokoronkwo/BUDDY/data/processed"
os.makedirs(output_folder, exist_ok=True)

# Strip .csv extension and optional '_data' suffix
base_filename = os.path.splitext(os.path.basename(filepath))[0]
if base_filename.endswith('_data'):
    base_filename = base_filename[:-5]

output_path = os.path.join(output_folder, f"{base_filename}.txt")



# Mechanical parameters for Zeelo GT2 pulley system
pulley_teeth = 36                     # Number of teeth on GT2 pulley
belt_pitch_mm = 2                    # GT2 pulley gear pitch
circumference = pulley_teeth * belt_pitch_mm / 1000  # in meters
steps_per_rev = 1600                 # 1/8 micro-stepping on 200-step NEMA 17

# === 1. LOAD CSV (TIME + X) ===
times_s: list[float] = []
positions_m: list[float] = []

with open(filepath, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        times_s.append(float(row["Time (s)"]))
        positions_m.append(float(row["X (m)"]))
        
#error check
if len(times_s) < 2:
    raise ValueError("CSV does not contain enough rows of data.")

# === 2. SINE EASING IN METRES ===
#this makes the motion curves similar to Blender's
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
