# Contributing

This repository is the physical-CommandMic reference and conformance client.
Protocol changes belong in
[`ip-commandmic`](https://github.com/Mason10198/ip-commandmic); general product
features normally belong in
[`ip-commandmic-gateway`](https://github.com/Mason10198/ip-commandmic-gateway).

Run `python -m pytest -q` and `git diff --check` before a pull request. Hardware
reports must identify the disconnected endpoint and RF-safety conditions. Never
commit captures, codeplugs, credentials, serial numbers or recorded voice.
Generated contributions must be understood, reviewed and cleaned by the
contributor.
