from ip_commandmic_lab.effects import CHORD3UP, CHORD3UP_LEVEL_DBFS, startup_frames


def test_startup_ping_pongs_zero_and_finishes_with_exact_test_state() -> None:
    frames = startup_frames()
    moving = frames[:-1]
    assert [frame.display.primary_raw.index(ord("0")) for frame in moving] == [
        *range(7, -1, -1), *range(1, 8), *range(6, -1, -1), *range(1, 8)
    ]
    assert all(frame.display.primary_raw.count(ord("0")) == 1 for frame in moving)
    assert [frame.led for frame in moving] == [
        "green" if index % 2 == 0 else "red" for index in range(len(moving))
    ]
    assert frames[-1].display.raw == b"--TEST--" + bytes(60)
    assert frames[-1].led == "off"


def test_chord3up_is_quiet_and_matches_requested_score() -> None:
    assert CHORD3UP == (
        (250, 100, (330.0, 440.0)),
        (0, 100, (440.0, 660.0)),
        (0, 100, (660.0, 880.0)),
    )
    assert abs(CHORD3UP_LEVEL_DBFS - (-31.9794)) < 0.0001
