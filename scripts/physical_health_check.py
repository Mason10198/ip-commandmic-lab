"""Run a short unattended physical-CommandMic connection health check."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from ip_commandmic import SoftwareRadioConfig, SoftwareRadioEndpoint


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real-radio-disconnected", action="store_true", required=True)
    parser.add_argument("--duration", type=float, default=180.0)
    parser.add_argument("--local-ip", default="192.168.0.1")
    parser.add_argument("--mic-ip", default="192.168.0.2")
    parser.add_argument("--control-port", type=int, default=52001)
    parser.add_argument("--audio-port", type=int, default=50000)
    parser.add_argument("--output", type=Path, default=Path("artifacts/physical-health.json"))
    args = parser.parse_args()
    if not 15 <= args.duration <= 600:
        parser.error("--duration must be between 15 and 600 seconds")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    audit = args.output.with_suffix(".jsonl")
    endpoint = SoftwareRadioEndpoint(
        SoftwareRadioConfig(
            local_ip=args.local_ip,
            mic_ip=args.mic_ip,
            control_port=args.control_port,
            audio_port=args.audio_port,
            mic_gain=3,
            backlight="on",
            speaker_volume=22,
            automatic_key_responses=False,
            automatic_ptt_responses=True,
        ),
        audit,
    )
    started = time.monotonic()
    connected_at: float | None = None
    heartbeat_times: list[float] = []
    failures: list[dict[str, object]] = []
    transitions: list[dict[str, object]] = []
    last_connection: str | None = None
    endpoint.start()
    try:
        deadline = started + args.duration
        while time.monotonic() < deadline:
            snapshot = endpoint.state.snapshot()
            connection = str(snapshot["connection"])
            if connection != last_connection:
                transitions.append(
                    {"seconds": round(time.monotonic() - started, 3), "state": connection}
                )
                last_connection = connection
            if connection == "connected" and connected_at is None:
                connected_at = time.monotonic()
            for event in snapshot["events"]:
                if event["event"] == "received_heartbeat_response":
                    stamp = float(event["time"])
                    if not heartbeat_times or stamp > heartbeat_times[-1]:
                        heartbeat_times.append(stamp)
                elif event["event"] in {"connection_failed", "startup_effect_error"}:
                    if event not in failures:
                        failures.append(event)
            time.sleep(0.25)
    finally:
        endpoint.stop()

    elapsed = time.monotonic() - started
    intervals = [b - a for a, b in zip(heartbeat_times, heartbeat_times[1:])]
    passed = bool(
        connected_at is not None
        and heartbeat_times
        and not failures
        and not any(item["state"] == "reconnecting" for item in transitions)
    )
    report = {
        "passed": passed,
        "duration_seconds": round(elapsed, 3),
        "connected_after_seconds": (
            round(connected_at - started, 3) if connected_at is not None else None
        ),
        "heartbeat_replies": len(heartbeat_times),
        "maximum_heartbeat_interval_seconds": round(max(intervals), 3) if intervals else None,
        "connection_transitions": transitions,
        "failures": failures,
        "audit": str(audit.resolve()),
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
