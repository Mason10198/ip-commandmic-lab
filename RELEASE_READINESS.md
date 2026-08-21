# Release readiness

## Release posture

Version `0.1.0-alpha.32` is ready for a packaged **public alpha** release. Its
offline application and packaging checks pass, but it is not a final
hardware-qualified release. The real radio must remain disconnected: this app
implements the radio side of the link and is intended to operate a physical or
software CommandMic.

The application is a thin client of `ip-commandmic 1.0.0rc2`. Protocol
framing, sessions, display dimensions and metadata, LED/backlight values,
button/PTT decoding, speaker-volume state, Parrot capture/replay, RTP/audio
packetization, common-file decoding and WAV recording are library-owned. The
app owns only UI composition, startup presentation, file pickers and operator
workflow.

## Included in this alpha

- Physical and software CommandMic session support with lossless 68-byte display
  editing, every verified steady/blinking indicator, character blink attributes,
  whole-display modes, status LED and backlight controls.
- Live key/PTT monitoring, microphone spectrum, streaming WAV recording, tones,
  common audio-file playback and guarded expert raw-frame transmission.
- Library-backed live 1–5 microphone gain and 0–32 speaker volume, default
  speaker level 22, physical volume-key
  handling and bounded Parrot capture/replay with exact display restoration.
- Unified CommandMic dark theme and per-user audit storage outside the portable
  application directory.

## Pending protocol/library progress

These gaps are documented rather than hidden behind application approximations:

- Live 1–5 microphone-gain changes and their audible effect are physically
  confirmed during an already-connected session.
- Alpha.29 physical acceptance passed for stable connection, display text/dots,
  icon clearing/restoration, Parrot audio, 0–32 and startup-22 volume behavior,
  spectrum freshness, WAV recording, common audio-file playback, and status LED
  off behavior.
- Cold-start/reconnect/PoE-cycle coverage and a 30-minute physical-CommandMic
  soak with no stale audio, stuck PTT or display divergence.
- A generic continuous low-latency application-audio source and the reference
  AllStarLink-style node bridge. Bounded files, generated tones and Parrot replay
  are implemented now.
- The real radio's acoustic volume transfer curve. The verified numeric range,
  clamps, zero mute and level-32 unity match; intermediate software attenuation
  is a documented perceptual approximation until calibrated measurements exist.
- Remaining auxiliary display bytes, extended glyph/font-ROM coverage, hook,
  repeat/chord semantics, VOX, horn and accessory states.
- Individual radio meanings for advanced scan/call/set-mode/GPS/Bluetooth and
  configuration-dependent functions beyond already mapped generic controls.
- Synchronized mouth-to-speaker latency, loss/underrun and fault-injection
  acceptance metrics.
- Emergency, remote-destructive and firmware-sensitive behavior remains absent
  or explicitly gated pending dedicated Tier-3 protocol work and authorization.

## Runtime and portability

The Windows x64 release is a self-contained PyInstaller onedir package. It does
not require Python, installation or administrator rights and can be moved as a
directory. Windows must provide the Microsoft Edge WebView2 runtime. The build
keeps pywebview's complete maintained Windows loader set because its Windows
backend validates all three runtime directories during import. Every release
build executes the frozen EXE's native-backend initialization smoke path before
it can be packaged. Source execution remains cross-platform, but only Windows
x64 is packaged and verified for this alpha.
