#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 12:25:54 2025

@author: benjaminokoronkwo and ChatGPT
"""

import bpy
import math

# === USER CONFIGURATION ===
ARM_NAME   = "Armature"      # Your armature object name
CTRL_BONE  = "CTRL_Rig"      # Bone with the target properties
TILT_BONE  = "Bone_TiltArm"  # Physical tilt bone (X rotation)
SLIDE_BONE = "Bone_XSlider"  # Physical slide bone (X location)
PAN_BONE   = "Bone_PanBase"  # Physical pan bone (Z rotation)

PROP_TILT_TARGET_DEG  = "tilt (deg)"
PROP_SLIDE_TARGET_IN  = "x_slider (in)"
PROP_PAN_TARGET_DEG   = "pan (deg)"
PROP_ARM_RADIUS_IN    = "arm_radius_in"
PROP_DEBUG            = "debug_on"

LIMITS = {
    "tilt_min_deg":  -25.0,
    "tilt_max_deg":   25.0,
    "slide_min_in":    0.0,
    "slide_max_in":   26.0,
    "pan_min_deg":  -90.0,
    "pan_max_deg":   90.0,
}

PAN_CONST_DEG_PER_S = 120.0

# Piecewise tilt profile (in/s)
def tilt_linear_speed_in_per_s(x_deg: float) -> float:
    if -25.0 <= x_deg < -15.0:
        return (x_deg / 2.0) + 13.5
    elif -15.0 <= x_deg <= 20.0:
        return 6.0
    elif 20.0 < x_deg <= 25.0:
        return (-x_deg / 4.0) + 11.0
    else:
        return tilt_linear_speed_in_per_s(-25.0 if x_deg < -25.0 else 25.0)

# Convert in/s -> deg/s
def tilt_speed_deg_per_s(x_deg: float, radius_in: float) -> float:
    v_in_s = tilt_linear_speed_in_per_s(x_deg)
    omega_rad_s = v_in_s / radius_in
    return math.degrees(omega_rad_s)

def slide_speed_in_per_s(x_in: float) -> float:
    return 6.0 if 0.0 <= x_in <= 26.0 else 0.0

def clamp(val, lo, hi):
    return lo if val < lo else hi if val > hi else val

def on_frame(scene):
    arm_obj = bpy.data.objects.get(ARM_NAME)
    if not arm_obj or arm_obj.type != 'ARMATURE':
        return
    fps = scene.render.fps / scene.render.fps_base
    if fps <= 0:
        return
    dt = 1.0 / fps
    pb = arm_obj.pose.bones
    ctrl = pb.get(CTRL_BONE)
    if not ctrl:
        return
    arm_radius_in = float(ctrl.get(PROP_ARM_RADIUS_IN, 2.0))
    debug_on = bool(ctrl.get(PROP_DEBUG, False))

    # --- Tilt ---
    if TILT_BONE in pb:
        tilt = pb[TILT_BONE]
        target_deg  = float(ctrl.get(PROP_TILT_TARGET_DEG, 0.0))
        current_deg = math.degrees(tilt.rotation_euler.x)
        max_deg_s = tilt_speed_deg_per_s(current_deg, arm_radius_in)
        max_step  = max_deg_s * dt
        delta = target_deg - current_deg
        if   delta >  max_step: new_deg = current_deg + max_step
        elif delta < -max_step: new_deg = current_deg - max_step
        else:                   new_deg = target_deg
        new_deg = clamp(new_deg, LIMITS["tilt_min_deg"], LIMITS["tilt_max_deg"])
        tilt.rotation_euler.x = math.radians(new_deg)
        if debug_on:
            print(f"TILT | {current_deg:.2f}° -> {new_deg:.2f}° @ {max_deg_s:.2f}°/s")

    # --- Slide ---
    if SLIDE_BONE in pb:
        slide = pb[SLIDE_BONE]
        target_in  = float(ctrl.get(PROP_SLIDE_TARGET_IN, 0.0))
        current_in = slide.location.x / 0.0254
        max_in_s = slide_speed_in_per_s(current_in)
        max_step = max_in_s * dt
        delta = target_in - current_in
        if   delta >  max_step: new_in = current_in + max_step
        elif delta < -max_step: new_in = current_in - max_step
        else:                   new_in = target_in
        new_in = clamp(new_in, LIMITS["slide_min_in"], LIMITS["slide_max_in"])
        slide.location.x = new_in * 0.0254
        if debug_on:
            print(f"SLIDE | {current_in:.2f}in -> {new_in:.2f}in @ {max_in_s:.2f} in/s")

    # --- Pan ---
    if PAN_BONE and PAN_BONE in pb:
        pan = pb[PAN_BONE]
        target_deg = float(ctrl.get(PROP_PAN_TARGET_DEG, 0.0))
        current_deg = math.degrees(pan.rotation_euler.z)
        max_step = PAN_CONST_DEG_PER_S * dt
        delta = target_deg - current_deg
        if   delta >  max_step: new_deg = current_deg + max_step
        elif delta < -max_step: new_deg = current_deg - max_step
        else:                   new_deg = target_deg
        new_deg = clamp(new_deg, LIMITS["pan_min_deg"], LIMITS["pan_max_deg"])
        pan.rotation_euler.z = math.radians(new_deg)
        if debug_on:
            print(f"PAN | {current_deg:.2f}° -> {new_deg:.2f}° @ {PAN_CONST_DEG_PER_S:.2f}°/s")

# Register handler
def _install_handler():
    h = bpy.app.handlers.frame_change_post
    for fn in list(h):
        if getattr(fn, "__name__", "") == "on_frame":
            h.remove(fn)
    h.append(on_frame)

_install_handler()

# --- UI Panel ---
class RIG_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Rig Controls"
    bl_idname = "RIG_PT_custom_controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig Controls'

    def draw(self, context):
        layout = self.layout
        arm_obj = bpy.data.objects.get(ARM_NAME)
        if not arm_obj or arm_obj.type != 'ARMATURE':
            layout.label(text="Armature not found")
            return
        pb = arm_obj.pose.bones
        ctrl = pb.get(CTRL_BONE)
        if not ctrl:
            layout.label(text="Control bone missing")
            return
        layout.prop(ctrl, f'["{PROP_TILT_TARGET_DEG}"]', text="Tilt (deg)")
        layout.prop(ctrl, f'["{PROP_SLIDE_TARGET_IN}"]', text="Slide (in)")
        layout.prop(ctrl, f'["{PROP_PAN_TARGET_DEG}"]', text="Pan (deg)")
        layout.prop(ctrl, f'["{PROP_ARM_RADIUS_IN}"]', text="Arm length (in)")
        layout.prop(ctrl, f'["{PROP_DEBUG}"]', text="Debug On")

classes = [RIG_PT_CustomPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
