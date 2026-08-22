# IP CommandMic Lab

IP CommandMic Lab is a Windows application for operating and testing a physical
Icom IP CommandMic without its radio. It turns your PC into the radio-side
network endpoint so you can inspect buttons and PTT, test the display and LEDs,
record microphone audio, send audio to the speaker, and experiment with the
CommandMic protocol.

> **Important:** Disconnect the real radio before using Lab. The radio and Lab
> must not both try to control the same CommandMic.

If you have a **physical CommandMic** and want to connect it to a PC, this is the
application you want. If you have a **physical radio** and want the PC to act as
its microphone, use
[`ip-commandmic-gateway`](https://github.com/Mason10198/ip-commandmic-gateway)
instead.

## Windows quick start

You need:

- A 64-bit Windows 10 or Windows 11 PC
- A physical IP CommandMic
- A PoE source appropriate for the CommandMic
- A wired Ethernet adapter connected to the CommandMic's network
- The real radio disconnected

1. Download
   [`ip-commandmic-lab-0.1.0-alpha.33-windows-x64.zip`](https://github.com/Mason10198/ip-commandmic-lab/releases/download/v0.1.0-alpha.33/ip-commandmic-lab-0.1.0-alpha.33-windows-x64.zip).
2. Right-click the ZIP, select **Extract All**, and open the extracted folder.
3. Open the `IPCommandMicLab` folder and run `IPCommandMicLab.exe`.
4. If Windows Firewall asks, allow access on **Private networks**.
5. Configure the Ethernet adapter as described below, power the CommandMic,
   and select **Connect** in Lab.

Lab is portable: it does not need to be installed and the extracted files must
remain together. Windows normally includes the required Microsoft Edge
WebView2 runtime. If the application window does not open, install the current
[WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)
and try again.

## Configure the Windows Ethernet adapter

Lab replaces the radio, so the PC's Ethernet adapter must use the IP address
that the CommandMic expects its radio to have. With the default Icom addressing,
the connection looks like this:

```text
Physical CommandMic             Windows PC running Lab
192.168.0.2        Ethernet     192.168.0.1
        |------------------------------|
              PoE switch/injector
```

Use these defaults unless the radio programming (codeplug) assigns different
addresses:

| Setting | Value |
| --- | --- |
| PC Ethernet / Local / radio IP | `192.168.0.1` |
| Physical CommandMic IP | `192.168.0.2` |
| Subnet mask | `255.255.255.0` |
| Default gateway | Leave blank |
| DNS servers | Leave blank |
| Control TCP port | `52001` |
| Audio UDP port | `50000` |

To set the PC address on Windows 10 or 11:

1. Press **Windows+R**, enter `ncpa.cpl`, and press **Enter**.
2. Right-click the wired Ethernet adapter connected to the CommandMic and
   select **Properties**.
3. Select **Internet Protocol Version 4 (TCP/IPv4)** and then **Properties**.
4. Select **Use the following IP address**.
5. Enter `192.168.0.1` for the IP address and `255.255.255.0` for the subnet
   mask. Leave gateway and DNS blank.
6. Select **OK**, then **Close**.

Do not assign `192.168.0.2` to the PC while the physical CommandMic is using
that address. Two devices with the same address cannot communicate reliably.

If your CommandMic was programmed for different addresses, use the programmed
**radio IP** for the PC adapter and the programmed **microphone IP** in Lab.
The two addresses must be unique and on the same subnet.

## Connect in Lab

At the top of the application, confirm:

- **Local / radio IP:** the static address assigned to the PC adapter
- **CommandMic IP:** the physical microphone's address
- **TCP port:** `52001`, unless reprogrammed
- **UDP audio port:** `50000`, unless reprogrammed

Select **Connect**. A successful connection shows a stable, pulsing connection
indicator in the upper-right corner. Lab then runs its short display, LED, and
audio startup sequence before settling on `--TEST--`.

## What Lab can do

- Show physical button, PTT, and connection activity in real time
- Build and send verified LCD text, icons, dots, blink states, and visual modes
- Control the status LED, backlight, microphone gain, and speaker volume
- Monitor microphone audio with peak/RMS values and a spectrum display
- Record microphone audio to WAV
- Replay the latest transmission with Parrot mode
- Play WAV, MP3, FLAC, OGG/Vorbis, and AIFF files through the CommandMic
- Inspect protocol events and send validated advanced display frames

The app is intentionally a diagnostic and development tool. It does not emulate
radio programming such as zones, channels, or every codeplug-dependent button
action.

## Troubleshooting

**Lab does not connect**

- Make sure the real radio is disconnected.
- Confirm that the CommandMic has PoE power and an Ethernet link.
- Confirm the PC adapter is using the radio-side IP, not the microphone IP.
- Check that no other device is already using either address.
- Confirm both addresses are on the same subnet.
- Allow `IPCommandMicLab.exe` through Windows Firewall on Private networks.
- If the adapter has several IPv4 addresses, temporarily remove unrelated
  addresses from that dedicated adapter.

**The window does not open**

- Extract the entire ZIP before running the executable.
- Keep `IPCommandMicLab.exe` with the other extracted files.
- Install or repair the Microsoft Edge WebView2 Runtime.

**The mic connects but a button appears to do nothing**

Some button behavior is defined by the radio codeplug. Lab reports received
controls but does not invent radio-side zone, channel, or function behavior.

## Project status

The current Windows release is
[`0.1.0-alpha.33`](https://github.com/Mason10198/ip-commandmic-lab/releases/tag/v0.1.0-alpha.33).
It has been physically tested with a real CommandMic. It is labeled alpha
because this is reverse-engineered hardware integration and some behavior is
still codeplug-dependent or not yet implemented.

See [RELEASE_READINESS.md](RELEASE_READINESS.md) for the precise verified scope
and open limitations. Protocol framing, endpoint sessions, display models, and
media handling are provided by the
[`ip-commandmic`](https://github.com/Mason10198/ip-commandmic) library.

## Development on Windows

Python 3.11 or newer is required:

```powershell
git clone https://github.com/Mason10198/ip-commandmic-lab.git
cd ip-commandmic-lab
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\ip-commandmic-lab
```

Run the automated tests with:

```powershell
.\.venv\Scripts\python -m pytest -q
```

Release packaging instructions are in
[packaging/windows/README.md](packaging/windows/README.md).

## License and trademarks

Original project code is MIT licensed. Icom and IP CommandMic are trademarks
of their respective owner; this independent project is not affiliated with or
endorsed by Icom. See [NOTICE.md](NOTICE.md) for details.
