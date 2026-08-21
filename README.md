# IP CommandMic Lab

Desktop protocol exerciser for physical and software CommandMic endpoints. It
can drive the LCD and status LED, observe held buttons and PTT, send audio,
visualize microphone audio as a smoothed 0–4 kHz spectrum, report peak/RMS in
dBFS and signed-16-bit PCM units, and record it to WAV
with a native output-folder picker. Parrot mode captures one physical PTT hold
in memory and immediately plays it back after release while displaying
`-PARROT-`. The CommandMic dashboard can also browse
for and play WAV, MP3, FLAC, OGG/Vorbis, and AIFF files through a connected
CommandMic.

The unified CommandMic dashboard exposes steady and blinking states for every
verified indicator, all eight primary-character blink attributes, verified
whole-LCD visual modes, status LED and backlight control, real-time physical
control monitoring, live 1–5 microphone gain, 0–32 speaker volume,
bidirectional audio tests, WAV
recording, and a lossless
68-byte advanced editor. At 1920×1080 and larger, all routine controls fit in a
three-column view. Protocol events and validated raw-frame transmission remain
in a dedicated second workspace.

On connection the app sweeps a standard `0` glyph right-to-left-to-right-to-
left-to-right while alternating the status LED red and green, plays the quiet
`chord3up` startup score, and settles on `--TEST--` with all non-text display
state cleared and the status LED off. This application owns the startup identity; the shared protocol
package supplies only the generic display, LED and polyphonic-audio operations.

This repository contains only the application. Protocol framing, endpoint
sessions, display models and media handling are provided by
[`ip-commandmic`](https://github.com/mason10198/ip-commandmic).

Status: public alpha. The application acts as a radio-side endpoint, so the real
radio must be disconnected from the CommandMic under test.

See [RELEASE_READINESS.md](RELEASE_READINESS.md) for the verified release scope,
runtime requirements and protocol-dependent functionality that remains open.

The endpoint remains passive for ordinary controls after the required neutral
connection handshake. Received keys are displayed and logged; only physical
F2/F3 presses update the app's speaker volume and produce the verified
`VOL nn` overlay. Other keys do not generate zone/channel or function feedback.
A physical PTT hold is
answered with the verified TX-active/status transaction because the CommandMic
will not transmit microphone RTP without it; release receives the verified
close transaction. Display, LED, backlight, and outbound speaker audio are sent
only when their corresponding UI controls are activated.

Speaker volume uses the radio's verified 0-32 range, clamps at both boundaries,
and mutes digitally at zero. Level 32 is unity; nonzero levels 1–32 span a
best-effort perceptually uniform 48 dB range. The numeric range and clamps match
the radio exactly. The gain curve remains application policy because the real
radio's acoustic transfer law has not yet been measured.

Periods typed into Primary text attach to the preceding character and update
the matching Dot 1–8 checkboxes; checking a steady dot also inserts that period
into the text field. The field accepts at most eight display characters, with
dots excluded from that limit. The builder and preview present all dots in
physical left-to-right order. Parrot's `-PARROT-` overlay clears all icons and
disabling the mode restores the exact most recently submitted 68-byte display.
The Lab app starts at speaker volume 22.

Microphone gain uses the observed two-frame mapping for values 1–5. Physical
testing confirms that changes take audible effect during an already-connected
session, and the selected value is reflected in endpoint state.

Original project code is MIT licensed. See [NOTICE.md](NOTICE.md) for Icom
trademark and third-party asset limitations.

Windows releases use a self-contained application directory for fast startup.
Extract the ZIP, keep the directory together, and run `IPCommandMicLab.exe`.
The Windows x64 build requires the Microsoft Edge WebView2 runtime. Audits are
written to the current user's application-data directory, so the extracted
release remains portable and read-only-safe.

For a short unattended physical-link check, keep the real radio disconnected
and run:

```powershell
.\.venv\Scripts\python.exe scripts\physical_health_check.py `
  --real-radio-disconnected --duration 180
```

The check requires no interaction after startup and writes a JSON summary plus
the protocol audit under `artifacts/`. Its duration is intentionally bounded to
10 minutes; it is a practical health check, not a claim of long-duration soak
qualification.

Three process-level teardown/reconnect cycles take about 85 seconds and are
also unattended:

```powershell
.\.venv\Scripts\python.exe scripts\physical_restart_check.py `
  --real-radio-disconnected --cycles 3
```

Each cycle constructs a fresh endpoint process, reaches a stable session,
observes heartbeat replies, shuts down cleanly, pauses briefly, and reconnects.

For local development before the library is published:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ..\ip-commandmic[audio]
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\ip-commandmic-lab
```
