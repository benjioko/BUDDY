#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 20:53:44 2025

@author: benjaminokoronkwo

"""

import csv
import numpy as np
import os

"""
BUDDY – Dual-Axis Motion Profile Generator  (X + Tilt)
---------------------------------------
Reads X‑axis translation and rotational data (in metres) exported from Blender,
converts it to stepper‑motor step/delay arrays for an X‑axis driven by a 
20‑tooth GT2 pulley (40 mm circumference) with a 1 / 16‑micro‑stepped NEMA‑17
(1600 steps/rev). The script outputs Arduino‑ready arrays: `deltaSteps[]` and `delayTimes[]`.
"""

# === USER CONFIGURATION ===

# === INPUT FILE: CSV exported from Blender ===
# (must contain a column labeled "X (m)")
filepath = "/Users/benjaminokoronkwo/BUDDY/data/motion/tilt_x-axis_test4.csv"

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

# === 1. LOAD CSV (TIME + X (trans and rot)) ===
times_s: list[float] = []
lin_x: list[float] = []
rot_x: list[float] = []

with open(filepath, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        times_s.append(float(row["Time (s)"]))
        lin_x.append(float(row["X (m)"]))
        rot_x.append(float(row["RotX (deg)"]))
        
#error check
if len(times_s) < 2:
    raise ValueError("CSV does not contain enough rows of data.")

# === 2. SINE EASING IN METRES ===
#this makes the motion curves similar to Blender's
#linear-based
lin_start, lin_end = lin_x[0], lin_x[-1]

if abs(lin_end - lin_start) < 1e-4:
    eased_m = lin_x  # essentially no travel
else:
    ease = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, len(lin_x)))
    eased_m = [lin_start +(lin_end - lin_start) * e for e in ease]

#rotation-based
rot_start, rot_end = rot_x[0], rot_x[-1]

if abs(rot_end - rot_start) < 0.01:
    print("No significant rotation detected; skipping easing.")
    eased_rot_x = rot_x
else:
    ease = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, len(rot_x)))  # Sine ease-in-out
    eased_rot_x = [rot_start + (rot_end - rot_start) * e for e in ease]

# === 3. CONVERT METRES → STEPS ===
def m_to_steps(x_m: float, steps_rev: int = steps_per_rev, circ: float = circumference) -> int:
    return int(round((x_m / circ) * steps_rev))

# === Convert eased RotX to motor steps ===
def deg_to_steps(deg, steps_per_rev=1600):
    return int((deg / 360.0) * steps_per_rev)

lin_steps = [m_to_steps(x) for x in eased_m]
rot_steps = [deg_to_steps(rx, steps_per_rev) for rx in eased_rot_x]

def deltaSteps(steps):
    # === 4. DELTA STEPS + PER‑STEP DELAYS (μs) ===
    delta_steps: list[int] = []
    delay_times_us: list[int] = []
    
    for i in range(1, len(steps)):
        d_steps = steps[i] - steps[i - 1]
        
    
        dt_s = times_s[i] - times_s[i - 1]
        if d_steps != 0 and dt_s > 0:
            velocity_sps = abs(d_steps) / dt_s          # steps per second
            delay_us = int(1_000_000 / velocity_sps)   # μs per individual step
        else:
            delay_us = 0
        
        delay_times_us.append(delay_us)
        delta_steps.append(d_steps)
    return delta_steps, delay_times_us

lin_delta_steps, lin_delay_times_us = deltaSteps(lin_steps)
rot_delta_steps, rot_delay_times_us = deltaSteps(rot_steps)

# === 5. EXPORT ARDUINO ARRAYS ===
with open(output_path, "w") as f:
    f.write(f"const int dataLength = {len(lin_delta_steps)};\n")
    f.write("int deltaStepsLin[dataLength] = {\n  " + ", ".join(map(str, lin_delta_steps)) + "\n};\n")
    f.write("unsigned int delayTimesLin[dataLength] = {\n  " + ", ".join(map(str, lin_delay_times_us)) + "\n};\n")
    f.write("int deltaStepsRot[dataLength] = {\n  " + ", ".join(map(str, rot_delta_steps)) + "\n};\n")
    f.write("unsigned int delayTimesRot[dataLength] = {\n  " + ", ".join(map(str, rot_delay_times_us)) + "\n};\n")

print(f"Export complete → {output_path}")
print(f"Linear Δsteps range: {min(lin_delta_steps)} … {max(lin_delta_steps)}")
print(f"Rotational Δsteps range: {min(rot_delta_steps)} … {max(rot_delta_steps)}")