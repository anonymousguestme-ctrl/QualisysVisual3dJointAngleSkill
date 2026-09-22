# Troubleshooting and stop conditions

## `Right Ankle Angles` exports with zero frames

Do not immediately switch to `_CGM`.

1. Check whether the exact signal exists under `ORIGINAL`, `PROCESSED`, or another folder in the active dynamic file.
2. Confirm the correct file is active and tagged/selected by the pipeline.
3. Check whether `Right Foot Normalized` or `RMF` has a valid pose across the range.
4. Confirm `RSK` is valid and driven by the intended `R_SK1`-`R_SK4` plate.
5. Inspect the executed `model_used` and `right_foot_normalized` values.
6. Locate the first model-build or recalc warning.
7. Recalculate one trial from a clean pipeline state and inspect the signal before batch export.

An exact name with zero frames is evidence of an upstream failure or wrong folder, not permission to substitute a different definition.

## `_CGM` contains data while the final CAST angle is empty

Treat this as a diagnostic clue. Many analysis pipelines have explicit `_CGM` copy logic for the CGM branch, while CAST computes its own `Right Ankle Angles`. Verify the active CAST segment poses and recalc branch. Keep `_CGM` only as a separately named comparison curve if the user requests it.

## The curve has a large constant offset

Check, in order:

- Whether the exported signal is raw/non-normalized or a different model branch.
- Whether the correct static trial was used.
- Whether the static pose was actually neutral for the research question.
- Foot/shank marker identity and left/right assignment.
- Lab/floor coordinate orientation and model axes.
- Degrees versus radians and any component reorder.

Do not remove the offset numerically until its cause and intended reference are defined. A blind zero subtraction can hide a wrong segment definition.

## The inversion/eversion sign looks reversed

Do not flip the CSV column first. Play a known inversion/eversion motion, show segment axes, and determine whether the problem is convention, side-specific sign, marker identity, or an incorrectly oriented foot/shank segment. Record any deliberate sign transformation as a new derived signal with formula and provenance.

## The skeleton twists or jumps although all markers are present

Suspect identity before interpolation. Inspect TH/SK plate topology, pairwise distances, trajectory part boundaries, and marker labels on both sides of the jump. A complete 28-marker frame can still be biomechanically wrong.

## Visual3D asks Replace or Append

- Choose **Replace** when loading a complete standalone pipeline prepared for the current recalc/export and the previous pipeline has been saved or is disposable.
- Choose **Append** only when the loaded commands are intentionally the next stage of the current pipeline and the full combined order has been reviewed.
- Cancel if the existing pipeline may contain unsaved work whose role is unknown.

After either choice, inspect the pipeline list before executing. The dialog does not validate the biomechanical definition.

## No force plates were used

Angles remain solvable. Use the no-force/kinematic path and disable force-dependent event or inverse-dynamics stages. Do not export ankle moment, ankle power, GRF, or COP as valid results. If session metadata says `Multiple forceplates`, verify actual C3D force/analog content rather than trusting the metadata.

## Static-foot normalization produces no pose

Confirm the required static foot targets and floor/lab landmarks build correctly, then confirm the four dynamic foot markers track the segment. If the segment remains invalid, stop. Report raw `RMF` relative to `RSK` only when the user explicitly accepts a different definition, and name it distinctly such as `Right Ankle Angles Raw CAST`.

## Angle, velocity, and acceleration lengths differ

Find the generating command for each signal. Boundary loss may be legitimate for centered derivatives, but length alone cannot prove the time offset or that velocity/acceleration were derived from the exported angle. Do not combine signals in one analysis table until their definitions and time alignment are confirmed.

## A report opens but results differ between runs

Compare hashes and paths for the static C3D, dynamic C3Ds, `.mdh`, recalc pipeline, and CMZ. Also compare active-file selection, file tags, foot-normalization flags, filters, event mode, and pipeline Replace/Append history. Save the validated pipeline and report under versioned names.

## Stop conditions

Stop and report `not validated` when any of these remain:

- The static trial is unknown or belongs to another subject/session.
- Marker identity or rigid-cluster topology is ambiguous.
- The requested segment has no valid pose.
- Only an alternate signal is populated and its equivalence is unproven.
- Axis/sign cannot be established for the requested clinical interpretation.
- A kinematic-only session is being used to request kinetics.
- Raw file preservation or provenance cannot be demonstrated.
