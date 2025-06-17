#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 19:53:13 2025

@author: benjaminokoronkwo
"""
import bpy
import csv
import math

# === CONFIGURATION ===
obj_name = "Camera"  # Change to your object name exactly
filepath = "/Users/benjaminokoronkwo/BUDDY/blender/motion_data.csv"  # Use an actual path

# === SETUP ===
obj = bpy.data.objects[obj_name]
scene = bpy.context.scene
fps = scene.render.fps

with open(filepath, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Frame", "Time (s)",
        "X (m)", "Y (m)", "Z (m)",
        "RotX (deg)", "RotY (deg)", "RotZ (deg)"
    ])

    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)

        # World position
        loc = obj.matrix_world.translation

        # World rotation (Euler)
        rot = obj.matrix_world.to_euler()

        writer.writerow([
            f,
            round(f / fps, 4),
            round(loc.x, 5), round(loc.y, 5), round(loc.z, 5),
            round(math.degrees(rot.x), 2),
            round(math.degrees(rot.y), 2),
            round(math.degrees(rot.z), 2)
        ])

