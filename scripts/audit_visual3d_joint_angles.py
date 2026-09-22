#!/usr/bin/env python3
"""Read-only structural audit for Visual3D JSON joint-angle exports."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON file or directory")
    parser.add_argument("--signal", default="Right Ankle Angles", help="Exact final signal name")
    parser.add_argument("--expected-frames", type=int, help="Required frame count, if fixed")
    parser.add_argument("--sample-rate", type=float, help="Point rate used only for duration reporting")
    parser.add_argument(
        "--folder",
        action="append",
        help="Allowed signal folder; repeat for multiple folders. Default: any folder.",
    )
    return parser.parse_args()


def json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.glob("*.json") if p.is_file())
    raise FileNotFoundError(path)


def finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def audit_file(path: Path, args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    try:
        root = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot read JSON: {exc}"]

    signals = root.get("Visual3D")
    if not isinstance(signals, list):
        return ["missing Visual3D signal list"]

    exact = [s for s in signals if isinstance(s, dict) and s.get("name") == args.signal]
    if args.folder:
        exact = [s for s in exact if s.get("folder") in args.folder]

    if len(exact) != 1:
        alternatives = sorted(
            {
                str(s.get("name"))
                for s in signals
                if isinstance(s, dict) and str(s.get("name", "")).startswith(args.signal)
            }
        )
        if alternatives:
            errors.append(
                f"expected exactly one {args.signal!r}, found {len(exact)}; "
                f"name-similar signals present: {alternatives}. Do not substitute automatically."
            )
        else:
            errors.append(f"expected exactly one {args.signal!r}, found {len(exact)}")
        return errors

    signal = exact[0]
    try:
        declared_frames = int(signal.get("frames"))
    except (TypeError, ValueError):
        return ["signal has invalid frames value"]

    if declared_frames <= 0:
        errors.append(f"signal is empty: frames={declared_frames}")
    if args.expected_frames is not None and declared_frames != args.expected_frames:
        errors.append(f"frames={declared_frames}, expected={args.expected_frames}")

    components = signal.get("signal")
    if not isinstance(components, list):
        return errors + ["signal has no component list"]

    by_axis = {c.get("component"): c for c in components if isinstance(c, dict)}
    if set(by_axis) != {"X", "Y", "Z"}:
        errors.append(f"component set is {sorted(str(k) for k in by_axis)}, expected X/Y/Z")

    for axis in ("X", "Y", "Z"):
        component = by_axis.get(axis)
        if component is None:
            continue
        data = component.get("data")
        if not isinstance(data, list):
            errors.append(f"{axis}: data is not a list")
            continue
        if len(data) != declared_frames:
            errors.append(f"{axis}: samples={len(data)}, declared frames={declared_frames}")
        invalid = [i + 1 for i, value in enumerate(data) if not finite_number(value)]
        if invalid:
            preview = invalid[:10]
            suffix = "..." if len(invalid) > len(preview) else ""
            errors.append(f"{axis}: {len(invalid)} non-finite/non-numeric samples at {preview}{suffix}")

    if not errors:
        duration = ""
        if args.sample_rate:
            if args.sample_rate <= 0:
                errors.append("sample rate must be positive")
            else:
                duration = f", sample_span={(declared_frames - 1) / args.sample_rate:.6f}s"
        if not errors:
            print(
                f"PASS {path}: {signal.get('type')}::{signal.get('folder')}::{args.signal}, "
                f"frames={declared_frames}{duration}"
            )
    return errors


def main() -> int:
    args = parse_args()
    try:
        files = json_files(args.input)
    except FileNotFoundError:
        print(f"ERROR input not found: {args.input}", file=sys.stderr)
        return 2

    if not files:
        print(f"ERROR no JSON files found: {args.input}", file=sys.stderr)
        return 2

    failed = 0
    for path in files:
        errors = audit_file(path, args)
        if errors:
            failed += 1
            for error in errors:
                print(f"FAIL {path}: {error}", file=sys.stderr)

    print(f"AUDIT files={len(files)} passed={len(files) - failed} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
