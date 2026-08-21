from __future__ import annotations

from dataclasses import dataclass

from ip_commandmic import DISPLAY_BUFFER_SIZE, PRIMARY_TEXT_SIZE, DisplayBuffer

CHORD3UP = (
    (250, 100, (330.0, 440.0)),
    (0, 100, (440.0, 660.0)),
    (0, 100, (660.0, 880.0)),
)
CHORD3UP_LEVEL_DBFS = -31.9794


@dataclass(frozen=True, slots=True)
class AnimationFrame:
    seconds: float
    display: DisplayBuffer
    led: str


def _sweep_character(position: int) -> DisplayBuffer:
    raw = bytearray(DISPLAY_BUFFER_SIZE)
    raw[position] = ord("0")
    return DisplayBuffer(bytes(raw))


def startup_frames() -> tuple[AnimationFrame, ...]:
    """Sweep right-left-right-left-right, then settle on centered TEST."""

    positions = (*range(7, -1, -1), *range(1, 8), *range(6, -1, -1), *range(1, 8))
    frames = tuple(
        AnimationFrame(0.06, _sweep_character(position), "green" if index % 2 == 0 else "red")
        for index, position in enumerate(positions)
    )
    return frames + (
        AnimationFrame(
            0.18,
            DisplayBuffer(
                b"--TEST--" + bytes(DISPLAY_BUFFER_SIZE - PRIMARY_TEXT_SIZE)
            ),
            "off",
        ),
    )
