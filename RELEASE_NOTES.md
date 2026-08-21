# 0.1.0-alpha.32

- Replaces the competing connection-status writers with one stable state model,
  eliminating heartbeat-time text flicker and capitalization changes.
- Restyles connection health as a compact two-line status pill. Only the green
  link dot emits a subtle heartbeat ring; the text remains still.

# 0.1.0-alpha.31

- Consolidates connection/session/control/heartbeat information into the
  existing top-right connection indicator; it pulses only while recent real
  heartbeat replies are being received.
- Makes audio-file playback a Play/Stop toggle and prevents overlapping
  playback operations through the shared library.
- Records physical confirmation that microphone gain 1–5 changes take effect
  during an already-connected session.
- Updates the Lab dependency to `ip-commandmic 1.0.0rc2`.

# 0.1.0-alpha.30

- Moves microphone gain and immediate backlight controls out of the connection
  strip and into the main CommandMic workspace.
- Adds explicit connection, verified-session, control-readiness, and real
  received-heartbeat status. Pulses the audio-file button for the full bounded
  playback operation.
- Records physical acceptance of connection stability, audio/meters, recording,
  Parrot, volume, display and LED behavior. Runtime microphone-gain acoustic
  effect remains unresolved and is not claimed as verified.
- Updates the Lab dependency to the public `ip-commandmic 1.0.0rc1` line.

# 0.1.0-alpha.29

- Adds a live microphone-gain selector backed by the shared library's typed
  observed 1–5 two-frame transaction and exposes the selected value in endpoint
  state. Stable-session physical acceptance remains open.
- Completes a public-candidate audit: ignored build/evidence trees stay outside
  Git, no capture/audio/codeplug/credential files are publication candidates,
  and release/API documentation states the remaining hardware boundary.

# 0.1.0-alpha.28

- Replaces arbitrary peak/RMS percentages with standard dBFS values and
  absolute signed-16-bit sample magnitudes.
- Reports exact received and actively recorded packet durations from the
  verified 20 ms RTP packet cadence. Percentage values remain only as the
  visual fill position of the two level meters.

# 0.1.0-alpha.27

- Corrects the disconnected Lab snapshot to volume 22 so startup no longer
  inherits the shared endpoint's generic level-32 default.
- Prevents state polling from moving the volume slider while it is being
  dragged, then commits the selected level on release.
- Renames display-builder `Steady` columns to `Enable` and moves connection
  result text into the connection controls' normal layout.

# 0.1.0-alpha.26

- Changes the Lab speaker-volume default to 22 while retaining the verified
  0–32 range, mute boundary and unity boundary.
- Replaces separate Record and Stop & save controls with one Record/Save
  toggle that pulses while recording is active.
- Pulses the Parrot control distinctly while it is recording and playing.
- Updates the microphone FFT only when the microphone packet counter advances,
  preventing a stale captured frame from being re-fed by idle or speaker-
  playback state changes.

# 0.1.0-alpha.25

- Fixes the packaged Windows startup failure from alpha.24. Pywebview imports
  and validates its `win-arm64`, `win-x64` and `win-x86` loader directories even
  in an x64 process, so all maintained Windows runtime assets are retained.
- Adds a frozen-EXE native-backend initialization smoke test to the build. A
  package can no longer be produced if pywebview cannot initialize before any
  window, network session or hardware interaction begins.

# 0.1.0-alpha.24

- Moves common WAV/MP3/FLAC/OGG/AIFF decoding, resampling, endian conversion,
  packetization and bounded playback into `ip-commandmic 0.2.0a12`.
- Sources display dimensions, LED choices and supplied-SVG Dot 1–8 path mapping
  from shared library metadata rather than duplicating protocol knowledge.
- Aligns its dark visual tokens with the Desktop app and moves default audit output
  to a writable per-user application-data directory.
- Keeps the fast portable onedir build while pruning non-x64 and Android webview
  artifacts; adds an explicit release-readiness and missing-function inventory.

# 0.1.0-alpha.23

- Makes display dots fully bidirectional: typed periods select the matching
  steady-dot checkbox, and checking a steady dot inserts the period after its
  corresponding display character in Primary text.
- Enforces the physical eight-character display limit while excluding dot
  modifiers from the count and removes excess typed characters immediately.
- Changes the Lab app's default speaker volume from 32 to 25.

# 0.1.0-alpha.22

- Fixes Dot 1–8 ordering in the display builder and maps each decoded dot to
  the correct physical path in the supplied display vector. Periods typed in
  Primary text now visibly synchronize the corresponding steady-dot checkbox.
- Fixes physical Parrot playback by waiting for the actual 350 ms capture-tail
  completion event. Alpha.21 audit evidence showed its fixed 225 ms timer raced
  the delayed TX-close frame, which closed the newly opened speaker path.
- Normalizes quiet Parrot speech to a bounded replay level, then applies the
  selected 0–32 speaker volume. Nonzero volume steps now span a best-effort
  perceptually uniform 48 dB range; zero remains mute and 32 remains unity.
- Sends `-PARROT-` as a text-only 68-byte display with no LOW/RSSI icons and
  restores the exact last display state when Parrot is disabled.

# 0.1.0-alpha.21

- Adds operator-controlled Parrot mode. While enabled the physical display
  reads `-PARROT-`; the current physical PTT hold is retained in memory and,
  after the verified release/close tail, immediately replayed through the
  CommandMic speaker.
- Adds a complete 0-32 application speaker-volume state with digital mute at
  zero, unity at 32, clamping at both boundaries, and consistent attenuation
  for Parrot, tone, audio-file, and startup-score playback.
- Handles physical F2/F3 Volume Up/Down presses at the application layer and
  emits the verified `VOL nn` overlay before restoring the active idle display.
  The 2 dB software attenuation steps are reference-app policy; the real
  radio's exact acoustic volume law remains unmeasured.
- Leaves the CommandMic status LED off after startup and whenever Parrot mode
  is toggled.

# 0.1.0-alpha.20

- Answers a physical PTT hold with the verified TX-active/status handshake so
  the CommandMic actually begins transmitting microphone RTP.
- Keeps ordinary key responses disabled; the required PTT handshake is sent
  only after the operator physically holds PTT.
- Corrects the prior passive-capture assumption using alpha.19 audit evidence
  showing valid PTT sessions but zero RTP packets.

# 0.1.0-alpha.19

- Fixes the live microphone spectrum and WAV recorder when automatic PTT
  responses are disabled.
- Observing a PTT hold now opens only the local RTP capture path; the Lab app
  remains passive and sends no unsolicited TX, display, LED, or audio-state
  response.

# 0.1.0-alpha.18

- Combines display, indicators, device outputs, live controls, microphone
  audio, recording and outbound audio into one three-column CommandMic
  dashboard designed to fit at 1920×1080 and larger.
- Replaces the time-domain trace with a dependency-free 40-bar FFT spectrum,
  fast attack, smooth falloff and independent falling peak markers.
- Consumes the library's complete 160-sample, 8 kHz frame for full 0–4 kHz
  coverage.

# 0.1.0-alpha.17

- Removes optional automatic key and PTT responses from the application and
  forces both behaviors off for every connection.
- Adds a native recording-folder picker that preserves the editable WAV
  filename and produces a complete output path.

# 0.1.0-alpha.16

- Keeps the indicator controls, send controls and advanced byte editor in one
  normal-flow right-column stack so they cannot slide beneath the taller left
  display/output column.
- Removes sticky positioning from the send bar and adds explicit minimum-width
  containment for the byte editor.

# 0.1.0-alpha.15

- Reproduces the two photographed offset-64 test patterns with explicit raw
  segment paths instead of approximating them with ordinary `L` and `U` glyphs.
- Includes the upper pattern's position-1-only upper-right segment.
- Includes the upper pattern's isolated third RSSI bar above the Scan icon.

# 0.1.0-alpha.14

- Uses the portable standard `0` glyph for the startup sweep.
- Opens the editor and preview on exact text `--TEST--`.
- Treats periods as decimal-point modifiers on the preceding character.
- Matches the photographed lower and U display-control patterns.
- Drives every preview blink from one synchronized 500 ms on/500 ms off clock.

# 0.1.0-alpha.13

- Uses the physical font ROM's full-segment glyph instead of the high-bit alternate glyph.
- Makes the preview decode the exact glyph byte sent over the protocol.
- Ends startup with exactly `--TEST--` and a completely cleared display tail.
- Renders primary-text periods on their corresponding decimal-point segments.

# 0.1.0-alpha.12

Simplified startup identity.

- Replaces the animation catalogue with one automatic full-character ping-pong sequence.
- Sweeps right-to-left-to-right-to-left-to-right while alternating the status LED green and red.
- Centers the final startup text as `  TEST  `.
- Removes animation selection and replay controls from the GUI.

# 0.1.0-alpha.11

Startup-volume correction.

- Reduces the `chord3up` startup sound to 20% of its former amplitude (approximately 14 dB lower).
- Leaves generated tones and user-selected audio-file playback unchanged.

# 0.1.0-alpha.10

Common audio-file playback release.

- Adds a native audio-file browser to Controls & Audio.
- Plays WAV, MP3, FLAC, OGG/Vorbis, and AIFF files.
- Decodes, mixes to mono, and resamples files to the verified 8 kHz protocol format inside the Lab app while keeping the shared library's audio contract strict.

# 0.1.0-alpha.9

Startup-effects release.

- Plays Segment Wave and the three-step `chord3up` score once a physical or
  software CommandMic finishes connecting.
- Adds Radio Sweep, Scanner, Signal Launch, Segment Wave, Comet, Digital
  Glitch, and Icon Parade to the Device Outputs animation picker.
- Lets the operator replay any animation with or without the startup chord.
- Keeps all named animations and sound identity in this application. The
  shared library provides only generic display/LED and polyphonic-audio
  primitives.
- Uses `ip-commandmic 0.2.0a5`.

# 0.1.0-alpha.8

Passive-by-default physical CommandMic release.

- Stops generating demo channel, zone, volume, status-carousel, or PTT/TX
  responses unless the operator explicitly enables the corresponding mode.
- Uses neutral blank startup synchronization and `TEST` only as the test
  editor's initial text.
- Adds immediate Off, Dim, and On backlight controls through the typed library
  endpoint.
- Clearly labels optional demo-key and PTT microphone-audio response modes.
- Uses `ip-commandmic 0.2.0a4`.

# 0.1.0-alpha.7

Focused workspace and complete verified display-control release.

- Replaces the cramped three-column layout with focused Display, Controls &
  Audio, and Protocol workspaces.
- Adds library-driven controls for every verified indicator blink bit, all
  eight character blink attributes, and synchronized LCD visual modes.
- Adds a complete 68-byte advanced display editor while keeping verified
  controls prominent and human-readable.
- Enlarges the live display, audio scope, physical-control monitor, and
  protocol-event workspaces.
- Defers construction of the 68-byte editor until it is opened to keep startup
  responsive.
- Uses `ip-commandmic 0.2.0a3` as the protocol source of truth.

# 0.1.0-alpha.6

Efficiency-audited Windows public-alpha build.

- Opens maximized by default while retaining the normal title bar, minimize,
  restore, and close controls.

- Uses the lazy-loading `ip-commandmic 0.2.0a2` public API.
- Separates 2 Hz protocol-event refreshes from latency-sensitive state and
  audio-meter refreshes instead of resending event history at 25 Hz.
- Removes JSON encode/decode round trips from the endpoint snapshot hot path.
- Keeps runtime and filesystem objects private from pywebview's recursive API
  discovery. This reduced measured idle working set from about 823 MB to 105 MB.
- Uses one LCD SVG glow compositor layer instead of a layer per lit segment.

- Shows a lightweight startup screen until the native bridge answers a real
  state request; the working interface is never presented prematurely.
- Reduces disconnected bridge polling from 25 calls per second to 2.5.
- Reuses an immutable disconnected snapshot instead of rebuilding it on every
  poll.

- The display editor, indicator controls, 68-byte grid, initial LCD preview,
  and live-button panel now render immediately with the page.
- Python bridge initialization and live protocol polling occur in the
  background and no longer block the editor's first paint.

- Renamed the application to **IP CommandMic Lab**.
- Replaced the self-extracting single-file executable with a self-contained
  application directory to eliminate extraction work on every launch.
- Stopped bundling unused pywebview backends.

- Uses `ip-commandmic 0.2.0a1` as its protocol implementation.
- Drives the verified display and LED controls.
- Shows button/PTT state and live microphone audio.
- Sends tones/WAV audio and records received microphone audio to WAV.
- Provides a guarded expert raw-frame interface.

Experimental software: disconnect the real radio from the CommandMic under
test before connecting this radio-side endpoint.
