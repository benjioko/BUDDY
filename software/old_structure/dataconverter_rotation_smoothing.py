#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 20:32:43 2025

@author: benjaminokoronkwo
"""

import csv
import numpy as np

# === CONFIGURATION ===
filepath = "/Users/benjaminokoronkwo/BUDDY/data/motion/tilt_x-axis_test1.csv"  # Update if needed
output_path = "/Users/benjaminokoronkwo/BUDDY/data/processed/arduino_deltas_and_delays_tilt_x-axis_test1.txt"
steps_per_rev = 1600  # For microstepping

# === Read CSV and extract RotX (deg) data ===
times = []
rot_x_deg = []

with open(filepath, mode='r') as file:
    reader = csv.DictReader(file)
    for i, row in enumerate(reader):
        if i > 125:
            break
        times.append(float(row["Time (s)"]))
        rot_x_deg.append(float(row["RotX (deg)"]))

# === Apply Sine-Based Easing to Rotation if there's motion ===
n = len(rot_x_deg)
rot_start, rot_end = rot_x_deg[0], rot_x_deg[-1]

if abs(rot_end - rot_start) < 0.01:
    print("No significant rotation detected; skipping easing.")
    eased_rot_x = rot_x_deg
else:
    ease = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))  # Sine ease-in-out
    eased_rot_x = [rot_start + (rot_end - rot_start) * e for e in ease]

# === Convert eased RotX to motor steps ===
def deg_to_steps(deg, steps_per_rev=1600):
    return int((deg / 360.0) * steps_per_rev)

steps = [deg_to_steps(rx, steps_per_rev) for rx in eased_rot_x]

# === Compute delta steps and delay time based on velocity ===
delta_steps = []
delay_times_us = []

for i in range(1, len(steps)):
    delta = steps[i] - steps[i - 1]
    time_diff_s = times[i] - times[i - 1]  # in seconds

    # Avoid division by zero
    if delta != 0:
        velocity = abs(delta) / time_diff_s  # steps per second
        delay_per_step = 1_000_000 / velocity  # microseconds per step
    else:
        delay_per_step = 0

    delta_steps.append(delta)
    delay_times_us.append(int(delay_per_step))

# === Export Arduino-ready arrays ===
with open(output_path, "w") as f:
    f.write(f"const int dataLength = {len(delta_steps)};\n")
    f.write("int deltaSteps[dataLength] = {\n  " + ", ".join(map(str, delta_steps)) + "\n};\n")
    f.write("unsigned int delayTimes[dataLength] = {\n  " + ", ".join(map(str, delay_times_us)) + "\n};\n")

print(f"Exported delta steps and calculated delay times (microseconds) with easing to {output_path}")
