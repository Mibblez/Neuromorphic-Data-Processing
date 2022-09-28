import pytest
from plotting_utils import filename_regex


@pytest.mark.parametrize("test_input,expected", [
    ("29Hz-2sl-20Deg-m1Threshold-BackLight-2s.csv", "20"),
    ("27Hz-2sl-50DEG-0Threshold-BackLight-2s.csv", "50"),
    ("10sl-Burst-20Hz-40deg-2s.csv", "40"),
    ("burst-400mV-1hz-15min-30deg.csv", "30"),
    ("sine-20hz-nopol-3t-backlight.csv", ""),
    ("square-65 deg-20 hz-5threshold", "65"),
])
def test_degrees_regex(test_input, expected):
    assert filename_regex.parse_degrees(test_input) == expected


def test_degrees_regex_with_append():
    assert filename_regex.parse_degrees("10hz-20deg-2sl-sine-m1T-backlight-2t.csv", "Degrees") == "20Degrees"


@pytest.mark.parametrize("test_input,expected", [
    ("29HZ-2sl-20deg-m1Threshold-BackLight-2s.csv", "29"),
    ("27hz-2sl-50deg-0Threshold-BackLight-2s.csv", "27"),
    ("10sl-Burst-20Hz-40deg-2s.csv", "20"),
    ("burst-400mV-1hz-15min-30deg.csv", "1"),
    ("whiteFoam-20T-20deg.csv", ""),
    ("square-65 deg-20 hZ-5threshold", "20"),
])
def test_frequency_regex(test_input, expected):
    assert filename_regex.parse_frequency(test_input) == expected


def test_frequency_regex_with_append():
    assert filename_regex.parse_frequency("10hz-20deg-2sl-sine-m1T-backlight-2t.csv", "Hz") == "10Hz"


@pytest.mark.parametrize("test_input,expected", [
    ("29HZ-2sl-20deg-m1Threshold-BackLight-2s.csv", ""),
    ("27hz-2sl-50deg-0Threshold-BackLight-2s.csv", ""),
    ("10sl-Burst-2V-20Hz-40deg-2s.csv", "2"),
    ("whiteFoam-3v-20T-20deg.csv", "3"),
    ("burst-400mV-1hz-15min-30deg.csv", "0.4"),
    ("square-65 deg-20 hZ-5threshold-2 v", "2"),
])
def test_voltage_regex(test_input, expected):
    assert filename_regex.parse_voltage(test_input) == expected


def test_voltage_regex_with_append():
    assert filename_regex.parse_voltage("500mv-20deg-2sl-sine-m1T-backlight-2t.csv", "V") == "0.5V"


@pytest.mark.parametrize("test_input,expected", [
    ("29HZ-2sl-20deg-triangle-m1Threshold-BackLight-2s.csv", "triangle"),
    ("10sl-Burst-20Hz-40deg-2s.csv", "Burst"),
    ("sine-400mV-1hz-15min-30deg.csv", "sine"),
    ("whiteFoam-20T-20deg-noise.csv", "noise"),
    ("square-65 deg-20 hZ-5threshold", "square"),
    ("whiteFoam-20T-20deg.csv", ""),
])
def test_waveform_regex(test_input, expected):
    assert filename_regex.parse_waveform(test_input) == expected


def test_waveform_regex_with_append():
    assert filename_regex.parse_waveform("10hz-20deg-2sl-sine-m1T-backlight-2t.csv", "Waveform") == "sineWaveform"


@pytest.mark.parametrize("test_input,expected", [
    ("29HZ-2sl-20deg-m1Threshold-BackLight-2s.csv", "2"),
    ("27hz-10Sl-50deg-0Threshold-BackLight-2s.csv", "10"),
    ("15SL-Burst-20Hz-40deg-2s.csv", "15"),
    ("burst-400mV-1hz-15min-30deg.csv", ""),
])
def test_slots_regex(test_input, expected):
    assert filename_regex.parse_slots(test_input) == expected


def test_slots_regex_with_append():
    assert filename_regex.parse_slots("10hz-20deg-2sl-sine-m1T-backlight-2t.csv", " Slots") == "2 Slots"


@pytest.mark.parametrize("test_input,expected", [
    ("29HZ-2sl-20deg-m1Threshold-BackLight-2s.csv", "-1"),
    ("27hz-10Sl-50deg-0Threshold-BackLight-2s.csv", "0"),
    ("15SL-1t-Burst-20Hz-40deg-2s.csv", "1"),
    ("burst-400mV-1hz-15min-30deg.csv", ""),
])
def test_threshold_regex(test_input, expected):
    assert filename_regex.parse_threshold(test_input) == expected


def test_threshold_regex_with_append():
    assert filename_regex.parse_threshold("10hz-20deg-2sl-sine-m1T-backlight-2t.csv", " Threshold") == "-1 Threshold"
