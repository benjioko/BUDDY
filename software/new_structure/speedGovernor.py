#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 01:40:08 2025

@author: benjaminokoronkwo and ChatGPT
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 01:40:08 2025

@author: benjaminokoronkwo and ChatGPT
"""

# Blender Rig Speed Governor — CUSTOM ZONES (with linear→angular conversion)
# The TILT piecewise profile below is in INCHES/SECOND (linear speed at the camera).
# We convert to DEGREES/SECOND using ARM_TILT_RADIUS_IN (pivot→camera distance).
#
#   omega[deg/s] = ( v[in/s] / R[in] ) * (180/pi)
#
# Drop this in Blender's Text Editor, edit names/arm length below, then "Run Script".
# Enable: Edit > Preferences > Save & Load > Auto Run Python Scripts (if desired).

import bpy
import math

# === USER CONFIGURATION ===
ARM_NAME   = "Armature"      # Your armature object name
CTRL_BONE  = "CTRL_Rig"      # Bone with the target properties
TILT_BONE  = "Bone_TiltArm"  # Physical tilt bone (X rotation)
SLIDE_BONE = "Bone_XSlider"  # Physical slide bone (X location)
PAN_BONE   = None             # Optional (e.g., "Bone_PanBase"). Not used here.

# Custom Property names on CTRL_BONE (Pose Mode > Bone Properties > Custom Properties)
# NOTE: These match your earlier message (with spaces and parentheses). Change only if you also edit below.
PROP_TILT_TARGET_DEG  = "tilt (deg)"
PROP_SLIDE_TARGET_IN  = "x_slider (in)"
# (Optional) PROP_PAN_TARGET_DEG = "Pan_target_deg"

# --- ARM GEOMETRY (edit this) ---
# Distance from tilt pivot to the point whose linear speed you are limiting (inches)
ARM_TILT_RADIUS_IN = 2.0  # <-- set this to your real arm length in inches

# Safety limits
LIMITS = {
    "tilt_min_deg":  -25.0,
    "tilt_max_deg":   25.0,
    "slide_min_in":    0.0,
    "slide_max_in":   26.0,
}

# ==============================
# SPEED PROFILES (YOUR ENVELOPES)
# ==============================
# NOTE: Your TILT piecewise function is given in INCHES/SECOND as a function of angle (deg).
# We'll convert that linear v(x) to angular omega(x) via the arm length above.
#
# TILT linear v(x) [in/s] with x in degrees:
#   -25 <= x < -15 :  v =  x/2 + 13.5
#   -15 <= x <= 20 :  v =  6
#    20 < x <= 25 :  v = -x/4 + 11
#
# SLIDE v(x) [in/s]:
#   0 <= x <= 26 : v = 6

def tilt_linear_speed_in_per_s(x_deg: float) -> float:
    """Piecewise linear speed (in/s) at the camera as a function of tilt angle x (deg)."""
    if -25.0 <= x_deg < -15.0:
        return (x_deg / 2.0) + 13.5
    elif -15.0 <= x_deg <= 20.0:
        return 6.0
    elif 20.0 < x_deg <= 25.0:
        return (-x_deg / 4.0) + 11.0
    else:
        # Clamp to nearest edge value for smooth behavior
        if x_deg < -25.0:
            return tilt_linear_speed_in_per_s(-25.0)
        else:
            return tilt_linear_speed_in_per_s(25.0)

def tilt_speed_deg_per_s(x_deg: float, radius_in: float) -> float:
    """Convert linear (in/s) to angular (deg/s) using arm length R (in)."""
    r = max(1e-6, abs(radius_in))  # avoid divide-by-zero
    v_in_s = tilt_linear_speed_in_per_s(x_deg)
    omega_deg_s = (v_in_s / r) * (180.0 / math.pi)
    return omega_deg_s

def slide_speed_in_per_s(x_in: float) -> float:
    """Slide speed profile (in/s) as a function of current slide position (in)."""
    if 0.0 <= x_in <= 26.0:
        return 6.0
    return 0.0

# =========================
# GOVERNOR CORE
# =========================

def clamp(val, lo, hi):
    return lo if val < lo else hi if val > hi else val


def on_frame(scene):
    """
    FRAME HANDLER (runs every frame):
      - Reads your *target* properties on CTRL_BONE (what you want).
      - Reads current physical bone state (what you have).
      - Computes the maximum allowed step this frame from your speed envelope.
      - Advances the physical bone toward the target without exceeding the speed limit.
    """
    arm_obj = bpy.data.objects.get(ARM_NAME)
    if not arm_obj or arm_obj.type != 'ARMATURE':
        return

    # dt from FPS
    fps = scene.render.fps / scene.render.fps_base
    if fps <= 0:
        return
    dt = 1.0 / fps

    pb = arm_obj.pose.bones

    # --- TILT (deg) governed by linear→angular conversion ---
    if CTRL_BONE in pb and TILT_BONE in pb:
        ctrl = pb[CTRL_BONE]
        tilt = pb[TILT_BONE]

        # The *target* angle in degrees (you keyframe this property).
        target_deg  = float(ctrl.get(PROP_TILT_TARGET_DEG, 0.0))

        # Current bone angle (radians in Blender) -> convert to degrees
        current_deg = math.degrees(tilt.rotation_euler.x)

        # Allowed angular speed (deg/s) from your linear envelope at current position
        max_deg_s = tilt_speed_deg_per_s(current_deg, ARM_TILT_RADIUS_IN)
        max_step  = max_deg_s * dt  # allowed delta this frame (deg)

        # Move toward target, clamped by max_step
        delta = target_deg - current_deg
        if   delta >  max_step: new_deg = current_deg + max_step
        elif delta < -max_step: new_deg = current_deg - max_step
        else:                   new_deg = target_deg

        # Safety clamp to travel limits
        new_deg = clamp(new_deg, LIMITS["tilt_min_deg"], LIMITS["tilt_max_deg"])

        # Apply back to the bone (convert deg -> rad)
        tilt.rotation_euler.x = math.radians(new_deg)

    # --- SLIDE (in) ---
    if CTRL_BONE in pb and SLIDE_BONE in pb:
        ctrl  = pb[CTRL_BONE]
        slide = pb[SLIDE_BONE]

        # Target slide in inches (you keyframe this)
        target_in  = float(ctrl.get(PROP_SLIDE_TARGET_IN, 0.0))

        # Current slide: bone.location.x is meters -> convert to inches
        current_in = slide.location.x / 0.0254

        # Allowed speed (in/s) from envelope at current position
        max_in_s = slide_speed_in_per_s(current_in)
        max_step = max_in_s * dt  # inches allowed this frame

        # Move toward target, clamped
        delta = target_in - current_in
        if   delta >  max_step: new_in = current_in + max_step
        elif delta < -max_step: new_in = current_in - max_step
        else:                   new_in = target_in

        # Safety clamp to travel limits
        new_in = clamp(new_in, LIMITS["slide_min_in"], LIMITS["slide_max_in"])

        # Apply back (inches -> meters)
        slide.location.x = new_in * 0.0254

# --- Install handler (avoid duplicates on re-run) ---
def _install_handler():
    h = bpy.app.handlers.frame_change_post
    for fn in list(h):
        if getattr(fn, "__name__", "") == "on_frame":
            h.remove(fn)
    h.append(on_frame)

_install_handler()

print("[Speed Governor] Installed with linear→angular conversion for TILT.")
print(f"Using ARM_TILT_RADIUS_IN = {ARM_TILT_RADIUS_IN} inches.")
print(f"Targets: Tilt in deg (CTRL_Rig['{PROP_TILT_TARGET_DEG}']), Slide in inches (CTRL_Rig['{PROP_SLIDE_TARGET_IN}']).")
