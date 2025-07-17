#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 10:55:08 2025

@author: benjaminokoronkwo
"""

import numpy as np

def linMotion(lin_data, times, pulley_teeth = 36, belt_pitch_mm = 2, steps_per_rev = 1600):
    
    """
    Generates Arduino-ready step and delay arrays for linear motion based on 
    Blender-exported X-axis translation data.

    Applies sine easing to input motion, converts to motor steps, and 
    calculates per-step delays to achieve smooth motion.

    Args:
        lin_data (list[float]): Raw X-position data in meters.
        times (list[float]): Corresponding timestamps in seconds.
        steps_per_rev (int, optional): Motor steps per full revolution. Default is 1600 (1/8 microstepping on 200-step motor).
        circumference (float, optional): Pulley circumference in meters. If None, assumes 36-tooth GT2 pulley (0.072 m).

    Returns:
        tuple:
            - delta_steps (list[int]): Step changes per timestep (can be negative).
            - delay_times_us (list[int]): Delay per step in microseconds for smooth timing.
    """
    
    circumference = pulley_teeth * belt_pitch_mm / 1000  # in meters
    
    # === 2. SINE EASING IN METRES ===
    #this makes the motion curves similar to Blender's
    start_x, end_x = lin_data[0], lin_data[-1]
    displacement   = end_x - start_x
    
    if abs(displacement) < 1e-4:
        eased_m = lin_data  # essentially no travel
    else:
        ease = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, len(lin_data)))
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
    
        dt_s = times[i] - times[i - 1]
        if d_steps != 0 and dt_s > 0:
            velocity_sps = abs(d_steps) / dt_s          # steps per second
            delay_us = int(1_000_000 / velocity_sps)   # μs per individual step
        else:
            delay_us = 0
        delay_times_us.append(delay_us)
    return delta_steps, delay_times_us