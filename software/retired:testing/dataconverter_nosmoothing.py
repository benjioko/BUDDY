#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 19:57:35 2025

@author: benjaminokoronkwo
"""

import csv

# === CONFIGURATION ===
filepath = "/Users/benjaminokoronkwo/BUDDY/blender/motion_data.csv"  # Update if needed

# === PARAMETERS ===
steps_per_rev = 1600  # Updated for microstepping

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

# === Convert RotX to motor steps ===
def deg_to_steps(deg, steps_per_rev=1600):
    return int((deg / 360.0) * steps_per_rev)

steps = [deg_to_steps(rx, steps_per_rev) for rx in rot_x_deg]

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

# === Prepare Arduino code format ===
with open("arduino_deltas_and_delays_tilttest.txt", "w") as f:
    f.write(f"const int dataLength = {len(delta_steps)};\n")
    f.write("int deltaSteps[dataLength] = {\n  " + ", ".join(map(str, delta_steps)) + "\n};\n")
    f.write("unsigned int delayTimes[dataLength] = {\n  " + ", ".join(map(str, delay_times_us)) + "\n};\n")

print("Exported delta steps and calculated delay times (microseconds) to arduino_deltas_and_delays_us.txt")

