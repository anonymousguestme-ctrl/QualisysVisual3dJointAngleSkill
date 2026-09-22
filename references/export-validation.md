# Export and validation

## Identify the exact Visual3D signal

Visual3D signals are identified by all three fields:

```text
TYPE::FOLDER::NAME
```

For example, `LINK_MODEL_BASED::ORIGINAL::Right Ankle Angles` and `LINK_MODEL_BASED::PROCESSED::Right Ankle Angles` are different objects. Exporting from the wrong folder can produce a zero-frame signal even when a same-named signal exists elsewhere.

Before scripting, inspect the Data Tree and graph the exact object. Diagnostic exports should set `EXPORT_EMPTY_SIGNALS=TRUE`; otherwise a missing requested signal may vanish from the output and look like a successful export.

## Minimal diagnostic Visual3D export

Use one known-good trial first. Adjust the file, folder, and output path only after checking the Data Tree.

```text
Select_Active_File
/FILE_NAME=<absolute dynamic C3D path>
;

Export_Data_To_Ascii_File
/FILE_NAME=<new absolute JSON output path>
/SIGNAL_TYPES=LINK_MODEL_BASED
/SIGNAL_FOLDER=ORIGINAL
/SIGNAL_NAMES=Right Ankle Angles
/NORMALIZE_DATA=FALSE
/USE_POINT_RATE=FALSE
/USE_JSON_FORMAT=TRUE
/EXPORT_EMPTY_SIGNALS=TRUE
/EXPORT_NAN=TRUE
/CREATE_FOLDER_PATH=TRUE
;
```

Do not add `_CGM` as a fallback in the final export. It may be included in a separate diagnostic export for comparison, with its definition and limitations clearly labeled.

Once the one-trial JSON passes, generate explicit `Select_Active_File` and export blocks for the user-confirmed order. Avoid broad `Gait*.c3d` discovery because it can mix raw, repaired, duplicates, and trials the user excluded.

## JSON audit

Run:

```powershell
py -3 scripts\audit_visual3d_joint_angles.py `
  --input <json-file-or-directory> `
  --signal "Right Ankle Angles" `
  --expected-frames 800 `
  --sample-rate 100
```

Omit `--expected-frames` when trials legitimately differ. The audit fails if the exact final signal is absent/empty, lacks X/Y/Z, contains non-numeric/non-finite values, or has inconsistent component lengths. If only `_CGM` is found, it reports the ambiguity and fails.

The audit is structural, not biomechanical proof. Also inspect waveforms and animation.

## CSV design

Keep the raw Visual3D JSON unchanged. Create a new CSV directory and refuse to overwrite it by default. For a long-format CSV, include at least:

```text
trial_order
trial
source_file
signal_type
signal_folder
signal
component
clinical_axis_label
positive_direction_evidence
unit
sampling_frequency_hz
sample_index
source_frame
time_seconds
value
```

Do not populate `clinical_axis_label` or `positive_direction_evidence` with guesses. Use `unverified` until the model/known-motion check is complete.

## Frame and time rules

Prefer frame/time metadata supplied by the source export. If only samples and point rate are available, document the assumption and calculate:

```text
time_seconds = (source_frame - first_source_frame) / point_rate_hz
```

Do not assume every source begins at frame 1. QTM exports may be cropped; C3D can preserve non-one first-frame indices or event offsets.

For a direct angle signal with one value per point frame, its time vector normally follows the point frames. For velocity/acceleration, do not invent offsets from array length alone. Inspect the command that generated them. A centered derivative commonly loses boundary samples, but an exported `Ang_Vel` signal might instead be a model-based angular velocity and need not be the numerical derivative of the exported angle.

QTM TSV files contain per-frame time only when `Export time data for every frame` was enabled. When absent, use the verified frequency and first-frame convention; retain both `source_frame` and calculated `time_seconds`.

## Required numeric checks

For every trial and component, report:

- Number of samples and missing/non-finite values.
- First and last source frame/time.
- Minimum, maximum, mean, and obvious discontinuities.
- Whether X/Y/Z lengths agree.
- Whether the signal covers the intended analysis range.
- Whether any boundary loss is explained by a documented operation.

Cross-check the first, middle, and last exported samples against the Visual3D graph/data view. For known movement trials, verify component and sign. If comparing angle with angular velocity, numerically differentiate only as a diagnostic and account for filtering and the actual derivative definition; do not force equality to an unrelated signal.

## Final filenames and manifest

Use names that identify the trial and definition, for example:

```text
01_CAST_9_right_ankle_angles_static_foot_normalized.csv
02_CAST_10_right_ankle_angles_static_foot_normalized.csv
right_ankle_angles_all_trials_ordered.csv
joint_angle_export_manifest.json
```

The manifest must record the exact Visual3D type/folder/name, distal/reference segments, normalization branch, units, point rate, frame/time convention, filters, gap-fill provenance, and hashes of the model and recalc pipeline.
