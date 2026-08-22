from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from importlib.resources import files
from pathlib import Path
from typing import Any, Callable

from ip_commandmic import (
    DisplayBuffer,
    DISPLAY_BUFFER_SIZE,
    EndpointState,
    PRIMARY_TEXT_SIZE,
    SoftwareRadioConfig,
    SoftwareRadioEndpoint,
    STATUS_LED_COLORS,
    verified_character_blink_controls,
    verified_display_bit_controls,
    verified_display_blink_bit_controls,
    verified_display_visual_modes,
    verified_display_svg_decimal_point_paths,
)
from .effects import CHORD3UP, CHORD3UP_LEVEL_DBFS, startup_frames


def _unblock_bundled_windows_runtime() -> bool:
    """Remove the download-zone stream from pythonnet's private assembly.

    Windows propagates Mark-of-the-Web from a downloaded ZIP to every extracted
    file. .NET Framework then refuses to resolve pythonnet's bundled runtime
    assembly. The user has already chosen to run this executable, so remove the
    marker only from this executable's private Python.Runtime.dll.
    """

    if os.name != "nt" or not getattr(sys, "frozen", False):
        return False
    runtime_dll = (
        Path(sys.executable).parent
        / "_internal"
        / "pythonnet"
        / "runtime"
        / "Python.Runtime.dll"
    )
    try:
        os.remove(f"{runtime_dll}:Zone.Identifier")
    except (FileNotFoundError, OSError):
        return False
    return True


def _asset_text(name: str) -> str:
    return files("ip_commandmic_lab").joinpath("assets", name).read_text(encoding="utf-8")


def default_audit_root() -> Path:
    """Return a writable per-user audit location for installed/portable builds."""

    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        root = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return root / "IPCommandMic" / "artifacts" / "lab"


def build_lab_html() -> str:
    display = _asset_text("mic_display_vector.svg")
    if display.startswith("<?xml"):
        display = display.split("?>", 1)[1].lstrip()
    initial = bytearray(DISPLAY_BUFFER_SIZE)
    initial[:PRIMARY_TEXT_SIZE] = b"--TEST--"
    capabilities = CommandMicLabService.capabilities()
    html = (
        _asset_text("index.html")
        .replace("__DISPLAY_SVG__", display)
        .replace("__CAPABILITIES_JSON__", json.dumps(capabilities, separators=(",", ":")))
        .replace(
            "__INITIAL_DISPLAY_JSON__",
            json.dumps(DisplayBuffer(bytes(initial)).to_dict(), separators=(",", ":")),
        )
    )
    return html


class CommandMicLabService:
    """Thin GUI bridge over the public software-radio endpoint."""

    def __init__(self, audit_root: Path) -> None:
        # Keep implementation objects private. Pywebview recursively exposes
        # public bridge members; publishing Path/runtime objects creates a huge
        # and unnecessary JavaScript API graph.
        self._audit_root = audit_root
        self._runtime: SoftwareRadioEndpoint | None = None
        disconnected_state = EndpointState()
        disconnected_state.update(speaker_volume=22)
        self._disconnected_snapshot = disconnected_state.snapshot(include_events=False)
        self._effect_generation = 0
        self._effect_lock = threading.Lock()
        self._window: Any | None = None

    def _bind_window(self, window: Any) -> None:
        self._window = window

    @staticmethod
    def _result(operation: Callable[[], Any]) -> dict[str, Any]:
        try:
            return {"ok": True, "result": operation()}
        except Exception as exc:
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    def connect(self, raw: dict[str, Any]) -> dict[str, Any]:
        def action() -> None:
            self.disconnect()
            config = SoftwareRadioConfig(
                local_ip=str(raw.get("local_ip", "192.168.0.1")),
                mic_ip=str(raw.get("mic_ip", "192.168.0.2")),
                control_port=int(raw.get("control_port", 52001)),
                audio_port=int(raw.get("audio_port", 50000)),
                mic_gain=int(raw.get("mic_gain", 3)),
                backlight=str(raw.get("backlight", "on")),
                speaker_volume=int(raw.get("speaker_volume", 22)),
                handle_volume_keys=True,
                idle_display_text="--TEST--",
                automatic_key_responses=False,
                # The physical mic withholds RTP until an observed PTT press
                # receives the verified TX-active/status transaction.
                automatic_ptt_responses=True,
            )
            stamp = time.strftime("%Y%m%dT%H%M%S")
            self._audit_root.mkdir(parents=True, exist_ok=True)
            self._runtime = SoftwareRadioEndpoint(
                config, self._audit_root / f"{stamp}_lab.jsonl"
            )
            self._runtime.start()
            self._start_effect(sound=True, wait_for_connection=True)

        return self._result(action)

    def disconnect(self) -> dict[str, Any]:
        self._effect_generation += 1
        runtime, self._runtime = self._runtime, None
        if runtime:
            runtime.stop()
        return {"ok": True}

    def snapshot(self) -> dict[str, Any]:
        if self._runtime is None:
            return {**self._disconnected_snapshot, "heartbeat_age_seconds": None}
        state = self._runtime.state.snapshot()
        heartbeat_time = next(
            (
                float(event["time"])
                for event in reversed(state["events"])
                if event.get("event") == "received_heartbeat_response"
            ),
            None,
        )
        state.pop("events", None)
        state["heartbeat_age_seconds"] = (
            max(0.0, time.time() - heartbeat_time) if heartbeat_time is not None else None
        )
        return state

    def protocol_events(self) -> dict[str, Any]:
        if self._runtime is None:
            return {"events": []}
        return {"events": self._runtime.state.snapshot()["events"][-80:]}

    @staticmethod
    def capabilities() -> dict[str, Any]:
        # Retained for protocol clients and compatibility. The desktop page embeds
        # this immutable metadata so its first paint never waits on the JS bridge.
        return {
            "display_size": DISPLAY_BUFFER_SIZE,
            "primary_text_size": PRIMARY_TEXT_SIZE,
            "display_bits": list(verified_display_bit_controls()),
            "display_blink_bits": list(verified_display_blink_bit_controls()),
            "character_blink": list(verified_character_blink_controls()),
            "display_visual_modes": list(verified_display_visual_modes()),
            "display_svg_decimal_point_paths": list(
                verified_display_svg_decimal_point_paths()
            ),
            "status_led_colors": list(STATUS_LED_COLORS),
        }

    def send_display(self, raw_hex: str) -> dict[str, Any]:
        return self._result(lambda: self._require().send_display(bytes.fromhex(raw_hex)))

    @staticmethod
    def decode_display(raw_hex: str) -> dict[str, Any]:
        return CommandMicLabService._result(
            lambda: DisplayBuffer(bytes.fromhex(raw_hex)).to_dict()
        )

    def send_led(self, color: str) -> dict[str, Any]:
        return self._result(lambda: self._require().send_led(color))

    def send_backlight(self, state: str) -> dict[str, Any]:
        return self._result(lambda: self._require().send_backlight(state))

    def set_speaker_volume(self, level: int) -> dict[str, Any]:
        return self._result(lambda: self._require().set_speaker_volume(int(level)))

    def set_mic_gain(self, level: int) -> dict[str, Any]:
        return self._result(lambda: self._require().set_mic_gain(int(level)))

    def set_parrot(self, enabled: bool) -> dict[str, Any]:
        def action() -> bool:
            runtime = self._require()
            self._effect_generation += 1
            active = runtime.set_parrot_enabled(
                bool(enabled),
                mode_display=(
                    DisplayBuffer(
                        b"-PARROT-" + bytes(DISPLAY_BUFFER_SIZE - PRIMARY_TEXT_SIZE)
                    )
                    if enabled
                    else None
                ),
            )
            runtime.send_led("off")
            return active

        return self._result(action)

    def _start_effect(
        self, *, sound: bool, wait_for_connection: bool = False
    ) -> None:
        runtime = self._require()
        self._effect_generation += 1
        generation = self._effect_generation

        def run() -> None:
            try:
                if wait_for_connection:
                    deadline = time.monotonic() + 15.0
                    while time.monotonic() < deadline:
                        if generation != self._effect_generation or runtime is not self._runtime:
                            return
                        if runtime.state.snapshot(include_events=False)["connection"] == "connected":
                            break
                        time.sleep(0.04)
                    else:
                        raise TimeoutError("CommandMic did not become ready for startup effect")
                with self._effect_lock:
                    if generation != self._effect_generation or runtime is not self._runtime:
                        return
                    audio_thread = None
                    if sound:
                        audio_thread = threading.Thread(
                            target=lambda: runtime.send_polyphonic(
                                CHORD3UP, level_dbfs=CHORD3UP_LEVEL_DBFS
                            ),
                            daemon=True,
                        )
                        audio_thread.start()
                    for frame in startup_frames():
                        if generation != self._effect_generation or runtime is not self._runtime:
                            return
                        runtime.send_led(frame.led)
                        runtime.send_display(frame.display)
                        time.sleep(frame.seconds)
                    if audio_thread:
                        audio_thread.join(2.0)
                    runtime.send_led("off")
            except Exception as exc:
                runtime.state.event(
                    "startup_effect_error", error=f"{type(exc).__name__}: {exc}"
                )

        threading.Thread(target=run, daemon=True, name="commandmic-test-effect").start()

    def send_raw(self, raw_hex: str) -> dict[str, Any]:
        return self._result(lambda: self._require().send_raw(bytes.fromhex(raw_hex)))

    def send_tone(self, frequency: float, level: float, duration: float) -> dict[str, Any]:
        return self._result(
            lambda: self._require().send_tone(float(frequency), float(level), float(duration))
        )

    def send_wav(self, path: str) -> dict[str, Any]:
        return self._result(lambda: self._require().send_audio_file(path))

    def stop_audio_playback(self) -> dict[str, Any]:
        return self._result(lambda: self._require().stop_audio_playback())

    def browse_audio_file(self) -> dict[str, Any]:
        """Open the platform-native audio picker without exposing the window API."""

        def action() -> str | None:
            if self._window is None:
                raise RuntimeError("application window is not ready")
            import webview

            selected = self._window.create_file_dialog(
                webview.FileDialog.OPEN,
                allow_multiple=False,
                file_types=(
                    "Audio files (*.wav;*.mp3;*.flac;*.ogg;*.oga;*.aif;*.aiff)",
                    "All files (*.*)",
                ),
            )
            return str(selected[0]) if selected else None

        return self._result(action)

    def browse_recording_folder(self, current_output: str) -> dict[str, Any]:
        """Choose a directory and preserve the current recording filename."""

        def action() -> str | None:
            if self._window is None:
                raise RuntimeError("application window is not ready")
            import webview

            selected = self._window.create_file_dialog(
                webview.FileDialog.FOLDER,
                allow_multiple=False,
            )
            if not selected:
                return None
            filename = Path(current_output).name or "commandmic_recording.wav"
            if Path(filename).suffix.lower() != ".wav":
                filename += ".wav"
            return str(Path(selected[0]) / filename)

        return self._result(action)

    def start_recording(self, output: str) -> dict[str, Any]:
        return self._result(lambda: self._require().start_recording(output))

    def stop_recording(self) -> dict[str, Any]:
        return self._result(self._require().stop_recording)

    def _require(self) -> SoftwareRadioEndpoint:
        if self._runtime is None:
            raise RuntimeError("not connected")
        return self._runtime

    def shutdown(self) -> None:
        self.disconnect()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="IP CommandMic Lab")
    parser.add_argument("--audit-directory", type=Path, default=default_audit_root())
    parser.add_argument("--package-smoke-test", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    _unblock_bundled_windows_runtime()
    import webview

    if args.package_smoke_test:
        from webview.guilib import initialize

        initialize()
        return 0

    service = CommandMicLabService(args.audit_directory)
    window = webview.create_window(
        "IP CommandMic Lab",
        html=build_lab_html(),
        js_api=service,
        width=1240,
        height=820,
        min_size=(900, 620),
        maximized=True,
        background_color="#0b1016",
        text_select=False,
        zoomable=False,
    )
    service._bind_window(window)
    window.events.closed += service.shutdown
    webview.start(debug=False, http_server=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
