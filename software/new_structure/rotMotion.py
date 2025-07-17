#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 10:51:42 2025

@author: benjaminokoronkwo, ChatGPT
"""

import numpy as np

def rotMotion(rot_data, times, steps_per_rev = 1600):
    
    """
   Generates Arduino-ready step and delay arrays for rotational motion based on 
   Blender-exported data.
   
   Process:
   Applies sine easing to input motion, converts to motor steps, and 
   calculates per-step delays to achieve smooth motion.

   Args:
       rot_data (list[float]): Raw position data in meters.
       times (list[float]): Corresponding timestamps in seconds.
       steps_per_rev (int): Number of motor steps per full 360° rotation.
                           Default is 1600 (1/8 microstepping).

   Returns:
       tuple:
           delta_steps (list[int]): Step differences between consecutive rotation values.
           delay_times_us (list[int]): Delay per step in microseconds, suitable for Arduino step control.
   """
    
    # === Apply Sine-Based Easing to Rotation if there's motion ===
    n = len(rot_data)
    rot_start, rot_end = rot_data[0], rot_data[-1]
    
    if abs(rot_end - rot_start) < 0.01:
        print("No significant rotation detected; skipping easing.")
        eased_rot_x = rot_data
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
        
    return delta_steps, delay_times_us
