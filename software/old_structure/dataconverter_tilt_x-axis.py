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
# Mechanical parameters for Zeelo GT2 pulley system
pulley_teeth = 36                     # Number of teeth on GT2 pulley
belt_pitch_mm = 2                    # GT2 pulley gear pitch
circumference = pulley_teeth * belt_pitch_mm / 1000  # in meters
steps_per_rev = 1600                 # 1/8 micro-stepping on 200-step NEMA 17

#interval between Blender times → cuts big jumps into smaller ones
dt = 0.020

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
def sine_ease(data,threshold):
    data_start, data_end = data[0], data[-1]

    if abs(data_end - data_start) < 1e-4:
        eased = data  # essentially no travel
    else:
        ease = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, len(data)))
        eased = [data_start +(data_end - data_start) * e for e in ease]
    return eased

eased_lin_x = sine_ease(lin_x,1e-4)      #linear
eased_rot_x = sine_ease(rot_x, 0.01) #rotational
        
# Build uniform timeline
t_uniform = np.arange(times_s[0], times_s[-1] + dt, dt)   # +dt to hit the final time exactly

# Interpolate eased positions onto that grid
eased_lin_uniform = np.interp(t_uniform, times_s, eased_lin_x)
eased_rot_uniform = np.interp(t_uniform, times_s, eased_rot_x)


# === 3. CONVERT METRES → STEPS ===
def m_to_steps(x_m: float, steps_rev: int = steps_per_rev, circ: float = circumference) -> int:
    return int(round((x_m / circ) * steps_rev))

# === Convert eased RotX to motor steps ===
def deg_to_steps(deg, steps_per_rev=1600):
    return int((deg / 360.0) * steps_per_rev)

lin_steps = [m_to_steps(x) for x in eased_lin_uniform]
rot_steps = [deg_to_steps(rx, steps_per_rev) for rx in eased_rot_uniform]

# === 4. DELTA STEPS + PER‑STEP DELAYS (μs) ===
def deltaSteps(steps, time_array):
    delta_steps = []
    delay_times_us = []
    for i in range(1, len(steps)):
        d_steps = steps[i] - steps[i-1]
        dt_s = time_array[i] - time_array[i-1]
        if d_steps and dt_s > 0:
            delay_us = int(1_000_000 * dt_s / abs(d_steps))
        else:
            delay_us = 0
        delta_steps.append(d_steps)
        delay_times_us.append(delay_us)
    return delta_steps, delay_times_us

# call it with the uniform timeline
lin_delta_steps, lin_delay_times_us = deltaSteps(lin_steps, t_uniform)
rot_delta_steps, rot_delay_times_us = deltaSteps(rot_steps, t_uniform)

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

#visualizer (for testing)
"""
| Plot             | What “smooth” looks like             | What “jerk” looks like                          |
| ---------------- | ------------------------------------ | ----------------------------------------------- |
| **Position**     | A single clean S‑curve (ease‑in‑out) | Kinks or flat steps between frames              |
| **Velocity**     | Gradual ramp → plateau → ramp down   | Sudden vertical jumps; saw‑tooth edges          |
| **Acceleration** | One triangular/S‑shaped pulse        | Big spikes or rapid sign changes frame‑to‑frame |

"""

# --- diagnostics.py ---------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ---- 1.  PREP: choose the timeline you actually used -----------------------
# (A) If your CSV times are uniform after resampling:
t = t_uniform
dt = np.diff(t).mean()

# (B) If you still have uneven frame spacing, velocity/accel won’t be perfect,
#     but the plots still reveal large step jumps.

# ---- 2.  Convert motor steps back to physical units (optional) -------------
mm_per_step = circumference * 1000 / steps_per_rev   # ≈ 0.045 mm
lin_pos_mm  = np.array(lin_steps) * mm_per_step
rot_pos_deg = np.array(rot_steps) * 360 / steps_per_rev

# ---- 3.  Derive velocity & acceleration ------------------------------------
# central‑difference keeps vector lengths aligned with t[1:-1]
lin_vel = np.gradient(lin_pos_mm,  dt)          # mm / s
lin_acc = np.gradient(lin_vel,     dt)          # mm / s²
rot_vel = np.gradient(rot_pos_deg, dt)          # deg / s
rot_acc = np.gradient(rot_vel,     dt)          # deg / s²

# ---- 4.  Plotting ----------------------------------------------------------
fig, ax = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

# Position
ax[0].plot(t, lin_pos_mm,  label="Linear (mm)")
ax[0].plot(t, rot_pos_deg, label="Rotational (°)", ls="--")
ax[0].set_ylabel("Position")
ax[0].legend();  ax[0].grid(True)

# Velocity
ax[1].plot(t, lin_vel,     label="Linear velocity")
ax[1].plot(t, rot_vel,     label="Rot velocity", ls="--")
ax[1].set_ylabel("Velocity")
ax[1].legend();  ax[1].grid(True)

# Acceleration
ax[2].plot(t, lin_acc,     label="Linear accel")
ax[2].plot(t, rot_acc,     label="Rot accel", ls="--")
ax[2].set_ylabel("Acceleration")
ax[2].set_xlabel("Time (s)")
ax[2].legend(); ax[2].grid(True)

plt.tight_layout()
plt.show()
# ---------------------------------------------------------------------------
