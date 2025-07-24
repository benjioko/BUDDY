#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 13:55:29 2025

@author: benjaminokoronkwo, ChatGPT
"""

import csv
import os
from linMotion import linMotion
from rotMotion import rotMotion

# === 1. FILE NAMING CONFIGURATION ===
# (must contain a column labeled "X (m)")
filepath = "/Users/benjaminokoronkwo/BUDDY/data/testing/captured/increments5_20.csv"

# === OUTPUT FILE: Auto-generated .txt in /processed ===
output_folder = "/Users/benjaminokoronkwo/BUDDY/data/testing/processed"
os.makedirs(output_folder, exist_ok=True)

# Strip .csv extension and optional '_data' suffix
base_filename = os.path.splitext(os.path.basename(filepath))[0]
if base_filename.endswith('_data'):
    base_filename = base_filename[:-5]

output_path = os.path.join(output_folder, f"{base_filename}.txt")

# === 2. USER CONFIGURATION ===
#HARDWARE
pulley_teeth = 36 #example of config, not used.
belt_pitch_mm = 2 #example of config, not used.

# === 3. SORT DATA INTO LISTS===
#initialize lists here...
times_s = []
lin_x = []
rot_x = []

#...and here
with open(filepath, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        times_s.append(float(row["Time (s)"]))
        lin_x.append(float(row["X (m)"]))
        rot_x.append(float(row["RotX (deg)"]))

# === 4. RUN FUNCTIONS FOR EACH DOF ===
results_by_dof = {
    #"linX": linMotion(lin_x, times_s),
    "rotX": rotMotion(rot_x, times_s)
}

# === 5. EXPORT HELPER FUNCTION ===
def export_dof_arrays(f, name_prefix, delta_steps, delay_times_us):
    f.write(f"// --- {name_prefix} axis ---\n")
    f.write(f"int deltaSteps{name_prefix}[dataLength] = {{\n  " + ", ".join(map(str, delta_steps)) + "\n};\n")
    f.write(f"unsigned int delayTimes{name_prefix}[dataLength] = {{\n  " + ", ".join(map(str, delay_times_us)) + "\n};\n\n")

# === 6. WRITE TO TXT ===
with open(output_path, "w") as f:
    data_length = len(next(iter(results_by_dof.values()))[0])
    f.write(f"const int dataLength = {data_length};\n\n")
    for dof_name, (deltas, delays) in results_by_dof.items():
        export_dof_arrays(f, dof_name, deltas, delays)

print(f"Export complete → {output_path}")
