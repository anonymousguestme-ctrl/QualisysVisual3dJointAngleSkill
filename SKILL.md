---
name: qualisys-visual3d-joint-angles
description: Build, recalculate, export, and validate lower-body joint-angle results from labeled Qualisys QTM/C3D trials in Visual3D, especially CAST workflows with static calibration and rigid tracking clusters. Use when the user asks to solve angles, explain the calculation basis, choose foot normalization, export trial CSVs, or diagnose missing/incorrect Visual3D joint-angle signals. Do not use a populated alternate signal as a substitute for the requested clinical signal without proving its model definition.
---

# Qualisys Visual3D Joint Angles

Produce joint-angle results whose source trials, static calibration, segment definitions, relative rotation, signal identity, units, frames, and timebase are all traceable. A curve is not valid merely because it is non-empty or smooth.

## Non-negotiable rules

1. Preserve every raw `.qtm`, acquisition `.c3d`, `.qpr`, PAF file, settings file, and user-completed static trial. Inventory paths, sizes, modification times, and SHA-256 hashes before any operation that could save or overwrite data.
2. Work in a new output directory and save a new `.cmz`. Never overwrite a raw QTM/C3D or the only report. Re-hash protected inputs afterward.
3. QTM supplies measured marker trajectories and labels; Visual3D constructs segments and calculates relative rotations. Never create an anatomical marker just because a model expects one.
4. Prefer correctly identified `Measured` marker samples. If labeling or gaps are uncertain, use `$qualisys-cast-gap-repair` first and do not solve until marker identity and cluster topology pass review.
5. Confirm the exact static trial and the user-confirmed dynamic trial order. Do not infer order from filenames, creation order, or consecutive trial numbers.
6. Joint angles are kinematics and do not require force plates. Joint moments, joint powers, GRF, and COP do require valid force/analog data and appropriate dynamics; do not report them from a marker-only session.
7. For a CAST report, `Right Ankle Angles_CGM` is not an automatic fallback for `Right Ankle Angles`. A non-empty `_CGM` curve does not prove that it is the requested CAST/static-normalized ankle angle.
8. Do not call an angle "static-normalized" until the actual computed segment/reference pair and signal path have been verified in the active report.
9. Never assign clinical meanings or positive directions to X/Y/Z solely from the signal name. Verify the active model convention and sign with a known movement or direct segment-axis inspection.
10. Export data only after inspecting the exact signal in Visual3D's Data Tree and confirming that X, Y, and Z contain frame-by-frame data for every requested trial.

## Route the work

- Read [references/workflow.md](references/workflow.md) for the end-to-end QTM to C3D to Visual3D procedure.
- Read [references/cast-model.md](references/cast-model.md) when the model is CAST, a foot-normalization choice is involved, or ankle-angle definitions/signs are in question.
- Read [references/export-validation.md](references/export-validation.md) before exporting JSON/CSV or adding a time column.
- Read [references/troubleshooting.md](references/troubleshooting.md) for empty signals, `_CGM` ambiguity, wrong static pose, wrong trial selection, pipeline dialogs, or implausible curves.
- Run [scripts/audit_visual3d_joint_angles.py](scripts/audit_visual3d_joint_angles.py) on Visual3D JSON exports before converting them to a final CSV.

## Required execution sequence

1. **Freeze provenance.** Record protected inputs and hashes; identify software/template versions and whether Visual3D/QTM has unsaved state.
2. **Audit QTM labels.** Confirm left/right identity, CAST bone topology, rigid-cluster identity, measured-versus-filled provenance, and required tracking-marker coverage. Resolve identity errors before gap filling.
3. **Export C3D safely.** Export the static and selected dynamic trials with full labels and Visual3D-compatible event settings. Confirm the selected frame range, axes, units, point rate, analog rate, and force-platform metadata.
4. **Create the Visual3D model.** Load the static C3D as the calibration file, apply the intended CAST model template, build it without unresolved required landmarks, and inspect segment axes and tracking targets.
5. **Assign dynamic files.** Open only the user-confirmed dynamics, associate the same calibrated model, and verify that the intended tracking targets drive each segment.
6. **Choose the ankle definition explicitly.** In a common CAST gait template, static-foot normalization selects `Right Foot Normalized` relative to `RSK`; otherwise it may select `RMF` relative to `RSK`. Verify the active `.mdh` and recalculation pipeline rather than assuming this mapping.
7. **Recalculate.** Use a fresh, known pipeline state and run the report's CAST recalculation on all selected dynamic files. Treat warnings as evidence to investigate, not messages to dismiss.
8. **Verify in Visual3D.** Inspect `Right Ankle Angles` or the requested left/other joint signal in its actual folder. Check all three components, all trials, frame counts, discontinuities, offsets, and a known motion.
9. **Export exact signals.** Use explicit type, folder, and signal names. Export empty signals during diagnostic runs so missing data cannot disappear silently.
10. **Audit and convert.** Validate the Visual3D JSON first, then create ordered per-trial CSVs with frame/time metadata. Preserve raw export and conversion code beside final CSVs.
11. **Reopen and report.** Reopen the output `.cmz` or re-run a read-only export, recheck hashes, and document the model branch, signal path, axes/sign evidence, filters, frame/time mapping, warnings, and exclusions.

## Acceptance gate

Do not describe the result as final unless all are true:

- The static and dynamic source files are explicitly listed and protected.
- Required marker identities and rigid tracking clusters are valid.
- The static model builds and the requested segments have valid poses across the analysis range.
- The exact joint-angle definition is recorded as distal segment relative to proximal/reference segment.
- The requested final signal, not a name-similar substitute, has numeric X/Y/Z data in every requested trial.
- Axis meaning and positive direction are supported by the active model or a known-motion check.
- Trial order, point rate, source frame, and time calculation are documented.
- Kinematic-only sessions contain no claimed kinetics.
- Any dropped boundary samples, filtering, interpolation, gap filling, or normalization are disclosed.
- Final exports pass the included audit script and a visual curve review.

## Deliverable record

For each run, leave a concise manifest containing source hashes, static trial, ordered dynamic trials, model/template path and hash, normalization choice, pipeline/recalc path and hash, final signal type/folder/name, component convention, sampling rate, export paths, validation result, and unresolved limitations. State "not validated" rather than substituting a convenient signal.
