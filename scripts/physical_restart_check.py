"""Run short unattended process-level reconnect cycles against a CommandMic."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real-radio-disconnected", action="store_true", required=True)
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--cycle-duration", type=float, default=25.0)
    parser.add_argument("--connect-timeout", type=float, default=20.0)
    parser.add_argument("--pause", type=float, default=5.0)
    parser.add_argument("--local-ip", default="192.168.0.1")
    parser.add_argument("--mic-ip", default="192.168.0.2")
    parser.add_argument("--output", type=Path, default=Path("artifacts/physical-restarts.json"))
    args = parser.parse_args()
    if not 2 <= args.cycles <= 10:
        parser.error("--cycles must be between 2 and 10")
    if not 15 <= args.cycle_duration <= 120:
        parser.error("--cycle-duration must be between 15 and 120 seconds")
    if not 2 <= args.connect_timeout <= 60:
        parser.error("--connect-timeout must be between 2 and 60 seconds")
    if args.cycle_duration < args.connect_timeout + 5:
        parser.error("--cycle-duration must allow at least 5 seconds after --connect-timeout")
    if not 0 <= args.pause <= 15:
        parser.error("--pause must be between 0 and 15 seconds")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    checker = Path(__file__).with_name("physical_health_check.py")
    cycle_reports: list[dict[str, object]] = []
    started = time.monotonic()
    for cycle in range(1, args.cycles + 1):
        cycle_output = args.output.with_name(f"{args.output.stem}-cycle-{cycle}.json")
        command = [
            sys.executable,
            str(checker),
            "--real-radio-disconnected",
            "--duration",
            str(args.cycle_duration),
            "--connect-timeout",
            str(args.connect_timeout),
            "--local-ip",
            args.local_ip,
            "--mic-ip",
            args.mic_ip,
            "--output",
            str(cycle_output),
        ]
        completed = subprocess.run(command, check=False)
        if cycle_output.exists():
            report = json.loads(cycle_output.read_text(encoding="utf-8"))
        else:
            report = {"passed": False, "error": "cycle produced no report"}
        report["cycle"] = cycle
        report["exit_code"] = completed.returncode
        cycle_reports.append(report)
        if completed.returncode != 0:
            break
        if cycle < args.cycles:
            time.sleep(args.pause)

    summary = {
        "passed": len(cycle_reports) == args.cycles
        and all(bool(report.get("passed")) for report in cycle_reports),
        "requested_cycles": args.cycles,
        "completed_cycles": len(cycle_reports),
        "duration_seconds": round(time.monotonic() - started, 3),
        "cycles": cycle_reports,
    }
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
