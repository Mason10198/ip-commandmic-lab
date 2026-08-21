import inspect
import importlib
from pathlib import Path

import ip_commandmic_lab
from ip_commandmic_lab import app
from ip_commandmic_lab.app import CommandMicLabService, build_lab_html


def test_lab_packages_full_control_surface() -> None:
    assert ip_commandmic_lab.__version__ == "0.1.0a29"
    page = build_lab_html()
    assert "__DISPLAY_SVG__" not in page
    assert "__CAPABILITIES_JSON__" not in page
    assert "__INITIAL_DISPLAY_JSON__" not in page
    assert 'id="displayText"' in page
    assert 'id="sendRaw"' in page
    assert 'id="spectrum"' in page
    assert 'id="recordToggle"' in page
    assert 'id="startup"' in page
    assert 'id="characterBlink"' in page
    assert 'id="visualMode"' in page
    assert 'data-tab="audio"' not in page
    assert 'data-tab="protocol"' in page
    assert 'id="advancedDisplay"' in page
    assert 'class="commandmic-layout"' in page
    assert 'class="dashboard-column controls-column"' in page
    assert 'class="dashboard-column audio-column"' in page
    assert ".send-bar{display:flex" in page
    assert ".send-bar{position:sticky" not in page
    assert "details.advanced{grid-column" not in page
    assert 'id="backlightButtons"' in page
    assert 'id="automatic_key_responses"' not in page
    assert 'id="automatic_ptt_responses"' not in page
    assert "Optional automatic responses" not in page
    assert 'id="animationSelect"' not in page
    assert 'id="playAnimation"' not in page
    assert 'id="browseAudio"' in page
    assert 'id="browseRecordingFolder"' in page
    assert 'id="parrotMode"' in page
    assert 'id="speakerVolume"' in page
    assert "set_parrot" in page
    assert "set_speaker_volume" in page
    assert "set_mic_gain" in page
    assert "Microphone gain (live)" in page
    assert "browse_audio_file" in page
    assert "browse_recording_folder" in page
    assert "WAV, MP3, FLAC, OGG or AIFF" in page
    assert "periods attach to the preceding character" in page
    assert "Math.floor(Date.now()/500)" in page
    assert "startup_animation" not in page
    assert 'value="--TEST--"' in page
    assert "QTH NODE" not in page
    assert "setup();syncBlinkClock();requestAnimationFrame(animateSpectrum);waitForBridge()" in page
    assert "verified_offset64_pattern" in page
    assert "pattern.segments_by_position" in page
    assert "segments(pos,['e','m','d']" not in page
    assert "active?40:400" in page
    assert "pollEvents" in page
    assert "function updateSpectrum" in page
    assert "function animateSpectrum" in page
    assert "SPECTRUM_BARS=40" in page
    assert "requestAnimationFrame(animateSpectrum)" in page


def test_capabilities_come_from_library_mapping() -> None:
    capabilities = CommandMicLabService.capabilities()
    controls = {item["key"] for item in capabilities["display_bits"]}
    assert {"low_power", "rssi", "bluetooth", "dealer_p1", "decimal_8"} <= controls
    assert controls == {item["key"] for item in capabilities["display_blink_bits"]}
    assert [item["position"] for item in capabilities["character_blink"]] == list(range(1, 9))
    assert {item["key"] for item in capabilities["display_visual_modes"]} >= {
        "normal_composed_display",
        "full_segment_pattern",
        "lower_segment_pattern",
        "u_segment_pattern",
        "blank_display",
    }
    assert "startup_animations" not in capabilities


def test_gui_contains_no_wire_frame_literals() -> None:
    page = build_lab_html().lower()
    assert all(value not in page for value in ("f3417105", "807d", "b1947ef9"))


def test_bridge_service_does_not_publish_recursive_implementation_objects(tmp_path) -> None:
    service = CommandMicLabService(tmp_path)
    assert [name for name in vars(service) if not name.startswith("_")] == []


def test_bridge_exposes_typed_realtime_backlight_operation() -> None:
    assert hasattr(CommandMicLabService, "send_backlight")
    assert hasattr(CommandMicLabService, "set_parrot")
    assert hasattr(CommandMicLabService, "set_speaker_volume")
    assert hasattr(CommandMicLabService, "set_mic_gain")


def test_recording_folder_picker_preserves_wav_filename(tmp_path) -> None:
    class Window:
        def create_file_dialog(self, *_args, **_kwargs):
            return (str(tmp_path),)

    service = CommandMicLabService(tmp_path)
    service._bind_window(Window())
    result = service.browse_recording_folder("my recording.wav")
    assert result == {"ok": True, "result": str(tmp_path / "my recording.wav")}


def test_parrot_bridge_forces_led_off_and_mode_display(tmp_path) -> None:
    observed = []

    class Runtime:
        def set_parrot_enabled(self, enabled, *, mode_display=None):
            observed.append(("parrot", enabled, mode_display.raw))
            return enabled

        def send_led(self, color):
            observed.append(("led", color))

    service = CommandMicLabService(tmp_path)
    service._runtime = Runtime()
    assert service.set_parrot(True) == {"ok": True, "result": True}
    assert observed == [
        ("parrot", True, b"-PARROT-" + bytes(60)),
        ("led", "off"),
    ]


def test_gui_uses_physical_svg_dot_path_order_and_text_syncs_dot_bits() -> None:
    page = build_lab_html()
    assert "DOT_PATHS=CAPABILITIES.display_svg_decimal_point_paths" in page
    assert "points=new Set" in page
    assert "if(chars.length<8)chars.push(ch)" in page
    assert "syncDisplayTextFromRaw" in page
    assert "control.key.startsWith('decimal_')&&control.offset<60" in page
    assert "light(DOT_PATHS[point-1]" in page


def test_lab_defaults_speaker_volume_to_22() -> None:
    page = build_lab_html()
    assert '<strong id="speakerVolumeValue">22</strong>' in page
    assert 'id="speakerVolume" type="range" value="22"' in page
    assert "raw.get(\"speaker_volume\", 22)" in inspect.getsource(app.CommandMicLabService.connect)
    assert CommandMicLabService(Path()).snapshot()["speaker_volume"] == 22


def test_volume_drag_display_headers_and_connection_result_layout() -> None:
    page = build_lab_html()
    assert "if(!volumeDragging)" in page
    assert "onpointerdown=()=>{volumeDragging=true}" in page
    assert "volumeDragging=false" in page
    assert "<span>Enable</span><span>Blink</span>" in page
    assert 'class="connection-control"' in page
    assert ".connection-result{position:absolute" not in page


def test_record_parrot_pulses_and_spectrum_only_accepts_new_audio_packets() -> None:
    page = build_lab_html()
    assert 'id="recordToggle"' in page
    assert "recording?'Save recording':'Record'" in page
    assert "classList.toggle('recording-pulse',recording)" in page
    assert "classList.toggle('parrot-recording',parrotStatus==='recording')" in page
    assert "classList.toggle('parrot-playing',parrotStatus==='playing')" in page
    assert "if(audioPackets>lastAudioPackets)updateSpectrum(s.waveform)" in page


def test_audio_statistics_use_dbfs_sample_magnitudes_and_exact_duration() -> None:
    page = build_lab_html()
    assert 'id="peakValue">−∞ dBFS · 0 samples' in page
    assert 'id="rmsValue">−∞ dBFS · 0.0 samples' in page
    assert "20*Math.log10(value)" in page
    assert "Math.round(peak*32768)" in page
    assert "(rms*32768).toFixed(1)" in page
    assert "(audioPackets*.02).toFixed(2)" in page
    assert "peak ${(s.audio_peak*100).toFixed(1)}%" not in page


def test_gui_payload_cannot_change_fixed_response_policy(tmp_path, monkeypatch) -> None:
    observed = {}

    class Config:
        def __init__(self, **values):
            observed.update(values)

    class Runtime:
        def start(self):
            pass

        def stop(self):
            pass

    monkeypatch.setattr(app, "SoftwareRadioConfig", Config)
    monkeypatch.setattr(app, "SoftwareRadioEndpoint", lambda *_args: Runtime())
    service = CommandMicLabService(tmp_path)
    monkeypatch.setattr(service, "_start_effect", lambda **_kwargs: None)
    result = service.connect(
        {"automatic_key_responses": True, "automatic_ptt_responses": True}
    )
    assert result["ok"] is True
    assert observed["automatic_key_responses"] is False
    assert observed["automatic_ptt_responses"] is True
    assert observed["handle_volume_keys"] is True
    assert observed["idle_display_text"] == "--TEST--"
    assert observed["speaker_volume"] == 22


def test_desktop_window_opens_maximized() -> None:
    assert "maximized=True" in inspect.getsource(app.main)


def test_package_smoke_path_initializes_native_backend_without_creating_window(monkeypatch) -> None:
    observed = []
    webview_guilib = importlib.import_module("webview.guilib")
    monkeypatch.setattr(webview_guilib, "initialize", lambda: observed.append("initialized"))
    monkeypatch.setattr(app, "CommandMicLabService", lambda *_args: (_ for _ in ()).throw(AssertionError("window path entered")))
    assert app.main(["--package-smoke-test"]) == 0
    assert observed == ["initialized"]


def test_common_audio_is_delegated_to_shared_endpoint(tmp_path) -> None:
    observed = []
    class Runtime:
        def send_audio_file(self, path):
            observed.append(path)
            return 5

    service = CommandMicLabService(tmp_path)
    service._runtime = Runtime()
    assert service.send_wav("voice.flac") == {"ok": True, "result": 5}
    assert observed == ["voice.flac"]
