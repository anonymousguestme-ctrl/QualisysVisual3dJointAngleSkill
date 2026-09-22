# CAST model and ankle-angle definition

This reference describes a common Qualisys CAST lower-body template pattern. Re-inspect the active `.mdh` template because vendor updates, project settings, and laboratory customizations can change definitions.

## How the calculation works

The static trial supplies anatomical targets and establishes a calibrated coordinate system for each segment. Dynamic tracking markers then estimate each segment's pose over time. A joint angle is the orientation of the distal segment relative to the proximal/reference segment, decomposed according to Visual3D's configured rotation convention.

Conceptually, with segment orientation matrices expressed in the lab frame:

```text
R_relative(t) = transpose(R_reference(t)) * R_distal(t)
joint_components(t) = decompose(R_relative(t), active Visual3D convention)
```

This is not an angle calculated directly from one pair of marker coordinates. The rigid clusters drive time-varying segment poses; the static calibration maps those tracking poses to anatomical coordinate systems.

## Tracking definitions to verify

Many CAST lower-body templates contain definitions similar to these; verify names and target order in the active model:

| Segment | Role | Dynamic tracking targets |
|---|---|---|
| `RSK` | Right shank/reference for right ankle | `R_SK1`, `R_SK2`, `R_SK3`, `R_SK4` |
| `RFT` | Right foot segment used by the CGM branch | `R_FM1`, `R_FM2`, `R_FM5`, `R_FCC` |
| `RMF` | Right foot segment for non-normalized CAST branch | `R_FCC`, `R_FM1`, `R_FM2`, `R_FM5` |
| `Right Foot Normalized` | Static-foot-orientation-normalized foot segment | `R_FCC`, `R_FM1`, `R_FM2`, `R_FM5` |

The same physical foot markers can track different modeled segments whose calibrated coordinate systems differ. Therefore a common tracking list does not make `RFT`, `RMF`, and `Right Foot Normalized` interchangeable.

## Right-ankle branch patterns

An installed CAST `recalc_gait.v3m` may define branches like these:

```text
CAST/IOR/Gait_Overlay and right_foot_normalized = TRUE
  RESULT_NAME       = Right Ankle Angles
  FUNCTION          = JOINT_ANGLE
  SEGMENT           = Right Foot Normalized
  REFERENCE_SEGMENT = RSK

CAST/IOR/Skinmarker/Gait_Overlay and right_foot_normalized != TRUE
  RESULT_NAME       = Right Ankle Angles
  FUNCTION          = JOINT_ANGLE
  SEGMENT           = RMF
  REFERENCE_SEGMENT = RSK

CGM
  RESULT_NAME       = Right Ankle Angles
  FUNCTION          = JOINT_ANGLE
  SEGMENT           = RFT
  REFERENCE_SEGMENT = RSK
```

Some analysis pipelines later copy the newly computed `LINK_MODEL_BASED::ORIGINAL::Right Ankle Angles` into a processed result of the same name, while a CGM branch may copy `Right Ankle Angles_CGM`. Inspect the active pipeline. `_CGM` must not be substituted into a CAST result merely because the final CAST signal is empty.

## What static foot normalization means

`right_foot_normalized=TRUE` does not time-normalize a gait cycle to 0-100 percent and does not scale values by body size. It chooses a foot segment whose calibrated orientation is referenced to the static trial/floor construction in the model. The template may build floor-related landmarks such as `RFCC_Floor`, `RFM2_Floor`, and `RFM5_Floor`, then track the normalized segment dynamically with four right-foot markers.

Enable it when:

- The static trial is the intended neutral/reference standing posture.
- Right-foot markers are correctly identified and stable in the static and dynamic files.
- The analysis question needs motion relative to that calibrated reference.
- The active report/model expects this branch and produces a valid segment pose.

Do not enable it blindly when:

- The static trial intentionally contains inversion, eversion, plantarflexion, or another non-neutral pose that should remain visible as an offset.
- The foot markers or floor/lab orientation are wrong.
- The normalized segment fails to build or has no valid dynamic pose.
- The study requires the unnormalized `RMF` definition for comparability with an existing protocol.

If the normalized segment is invalid, fix the model/static inputs. Do not silently fall back to `RMF` or `_CGM`; a fallback changes the biomechanical definition and requires explicit user approval and a distinct signal name.

## Axis order and signs

Some CAST pipelines leave `USE_CARDAN_SEQUENCE=FALSE` and do not explicitly negate X/Y/Z in the right-ankle commands. That fact alone does not establish the clinical positive direction in a customized report.

For many CAST workflows, X is interpreted as sagittal dorsiflexion/plantarflexion, Y as frontal inversion/eversion, and Z as transverse internal/external rotation. Treat those labels as a hypothesis until verified. Establish the actual sign by at least one of:

1. Inspecting segment axes and the joint-angle definition in Visual3D.
2. Using a trial with a known isolated movement.
3. Comparing a controlled static pose with neutral while keeping marker identity fixed.

Record conclusions in explicit form, for example `X: dorsiflexion positive, verified by trial ...`, not merely `X = ankle flexion`.

## Kinematics versus kinetics

Marker trajectories, static calibration, and valid segment tracking are sufficient for angles, angular velocities, and angular accelerations. Joint moments and powers additionally require valid force-platform assignment, force signals, subject parameters, and inverse dynamics. A marker-only inversion/eversion session can yield ankle angles but not defensible ankle moments, powers, GRF, or COP.
