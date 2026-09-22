# End-to-end workflow

## 1. Inventory without changing data

Create a manifest for every candidate `.qtm`, `.c3d`, `.qpr`, `.cmz`, `.mdh`, session/settings XML, and pipeline script. Record full path, byte size, last-write time, and SHA-256. Query open applications for unsaved state before closing or replacing anything.

Identify these inputs explicitly:

- One user-approved static CAST trial.
- The ordered dynamic trials to solve.
- The CAST marker-set/model version.
- The Visual3D model template (`.mdh`).
- The generated or installed recalculation pipeline (`.v3s`/`.v3m`) for this project.
- Subject mass and height if the broader report uses kinetics; these are not needed merely to define relative segment angles.
- Point rate and, if present, analog rate.
- Whether force plates were actually recorded, independent of what a stale `session.xml` field says.

Do not treat a file as raw solely because its filename lacks a suffix. Use acquisition timestamps, hashes, and user confirmation.

## 2. QTM preflight

Open a copy when inspection may trigger saves. Confirm the static labels against the user's completed static trial and inspect left/right colors and bones. In dynamics, verify the tracking clusters and foot markers over the entire range, especially crossings, occlusions, and the first frame after each gap.

For CAST lower body, common expectations are 36 static markers and 28 dynamic tracking markers, but treat these as configuration checks rather than permission to manufacture absent trajectories. Marker completeness does not prove identity.

Use `Measured` samples when correctly identified. A present trajectory at the wrong physical point is an identity problem, not a gap. Invoke the CAST gap-repair skill for relabeling or explicitly authorized relational repair. Re-export C3D only after the QTM result is saved to a distinct output file and reopened for validation.

## 3. Export QTM trials to C3D

For one trial in QTM, use `File > Export > To C3D`. For multiple trials, use `File > Batch Process`, select the exact static and dynamic files, and enable only the required export action.

Recommended C3D settings for Visual3D:

- Exclude unidentified trajectories after confirming they are genuinely irrelevant.
- Exclude empty trajectories.
- Use the de facto standard/full-label format so CAST labels are preserved.
- Use the C3D.org event format with original start time for modern Visual3D.
- Preserve the intended exported frame range.
- Keep length units consistent, normally millimeters from QTM.
- Do not enable Y-up conversion when force-plate data makes that option inapplicable; inspect the lab axes in Visual3D instead of applying an unexplained conversion.
- If force data exists, choose zero-force-baseline frames only while every plate is unloaded.

After export, compare label names, point rate, frame count, first/last frame, units, events, analog rate, and force-platform parameters with the QTM source. A C3D can open successfully while carrying wrong axes, cropped timing, or force baselines.

## 4. Build the static model in Visual3D

Start from a clean workspace or save the existing workspace/report first. Load the static C3D with `Model > Create (Add Static Calibration File) > Hybrid Model from C3DFile`, then apply the intended CAST `.mdh` template.

Inspect model build messages. Do not continue past an unresolved required anatomical target merely because a skeleton is visible. Verify at least:

- Pelvis, thigh, shank, and foot segments exist on the requested side.
- Anatomical/calibration targets belong to the correct side and physical landmark.
- TH1-TH4 and SK1-SK4 tracking lists agree with the labels physically attached to those rigid plates.
- Foot tracking targets agree with the model definition.
- Segment coordinate axes point in plausible anatomical directions.
- Joint centers and segment lengths are plausible and left/right are not swapped.

The static trial defines anatomical relationships and calibration geometry. It does not mean dynamic anatomical markers must all remain present; dynamics normally track segments from their tracking clusters.

Save the calibrated model/report under a new name.

## 5. Load and assign dynamic trials

Open only the confirmed dynamic C3Ds. Associate the calibrated static model with every dynamic file. Confirm the model is not accidentally built from a dynamic trial or a static trial from another session/subject.

Play each file and inspect segment pose rather than only marker trajectories. A rigid plate that was mislabeled can look spatially plausible while rotating the modeled segment incorrectly. Check the first frame, large-motion portions, known gaps, and the last frame.

If no force plates were recorded, select the no-force/kinematic processing path. Do not use `Multiple forceplates` merely because it is present in copied session metadata. This does not prevent joint-angle computation; it prevents invalid kinetic claims and avoidable force-event errors.

## 6. Configure the intended angle branch

For the selected Qualisys CAST pipeline, inspect the generated `recalc.v3s` values and the referenced `recalc_gait.v3m` branch. Do not copy settings from another laboratory or project. Record at least:

```text
model_used = CAST
right_foot_normalized = TRUE or FALSE
left_foot_normalized = TRUE or FALSE
event_mode = actual acquisition mode
```

Common right-ankle CAST branches are:

```text
TRUE:  JOINT_ANGLE, segment = Right Foot Normalized, reference = RSK
FALSE: JOINT_ANGLE, segment = RMF,                  reference = RSK
```

These are reference patterns, not a substitute for inspecting the active model and pipeline.

Do not infer which branch executed from a UI checkbox alone. Inspect the generated pipeline and then the actual signal definition in the report.

## 7. Recalculate from a controlled pipeline state

Save any pipeline the user may need. When loading a standalone replacement pipeline prepared for this run, choose **Replace** so stale commands are not executed before or after it. Choose **Append** only when the new commands are intentionally designed to follow the existing pipeline and that combined order has been reviewed. This choice affects the pipeline workspace, not permission to overwrite source data.

Run the model/recalculation pipeline on the selected dynamic files. If a command reports missing segments, missing signals, build errors, or empty results, stop and locate the first upstream failure. Do not compensate by exporting a different signal with a similar name.

## 8. Inspect before export

In the Visual3D Data Tree, select each dynamic trial and navigate to the exact signal type and folder. Inspect the requested signal graph:

- X/Y/Z all exist and are numeric.
- Frame counts agree with the trial, except documented derivative/filter boundary loss.
- No large discontinuity aligns with a label swap or marker gap.
- Static or neutral portions have a plausible offset for the selected normalization method.
- A known dorsiflexion, inversion/eversion, or rotation movement changes the expected component and establishes sign.

Also inspect the 3D animation with modeled segment axes. A plausible waveform is insufficient if the distal/proximal segments are wrong.

## 9. Save and export

Save a new solved `.cmz`; never overwrite the only report. Export diagnostic JSON with empty signals included, validate it, and only then convert to CSV. Read [export-validation.md](export-validation.md) for the exact checks.

## 10. Final handoff

Report:

- Static trial and ordered dynamic files.
- QTM/C3D provenance and hashes.
- CAST template and recalculation pipeline versions/hashes.
- Angle definition as distal segment relative to reference segment.
- Foot-normalization setting and what it means.
- Exact Visual3D type/folder/signal exported.
- Axis/sign evidence rather than an unsupported convention.
- Sampling rate, source-frame convention, and time formula.
- Filters, interpolation/gap fill, cropped ranges, and derivative boundary loss.
- Whether force data existed and which requested outputs are therefore valid.
- Any unresolved warning; do not label a partial result final.
