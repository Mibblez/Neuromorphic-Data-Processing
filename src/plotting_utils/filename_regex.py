import re


def parse_frequency(input_str: str, append_if_found: str = "") -> str:
    frequency = re.search("[0-9]{1,} ?hz", input_str, re.IGNORECASE)

    if frequency:
        return frequency.group().strip(" hzHZ") + append_if_found
    else:
        return ""


def parse_voltage(input_str: str, append_if_found: str = "") -> str:
    voltage_match = re.search("[0-9]{1,} ?m?v", input_str, re.IGNORECASE)

    if voltage_match:
        voltage_str = voltage_match.group().lower()
        multiplier = 0.001 if "mv" in voltage_str else 1

        voltage_str = str(int(voltage_str.strip(" mv")) * multiplier)

        return voltage_str + append_if_found
    else:
        return ""


def parse_waveform(input_str: str, append_if_found: str = "") -> str:
    waveform = re.search("(burst|sine|square|triangle|noise)", input_str, re.IGNORECASE)
    return waveform.group() + append_if_found if waveform else ""


def parse_degrees(input_str: str, append_if_found: str = "") -> str:
    degrees = re.search("[0-9]{1,} ?deg", input_str, re.IGNORECASE)

    if degrees:
        return degrees.group().strip(" degDEG") + append_if_found
    else:
        return ""


def parse_slots(input_str: str, append_if_found: str = "") -> str:
    slots = re.search("[0-9]{1,}sl", input_str, re.IGNORECASE)

    if slots:
        return slots.group().strip(" slSL") + append_if_found
    else:
        return ""


def parse_threshold(input_str: str, append_if_found: str = "") -> str:
    threshold_match = re.search("m?[0-9]{1,}t(hreshold)?", input_str, re.IGNORECASE)

    if threshold_match:
        threshold_str = threshold_match.group().lower().replace("m", "-").strip("threshold")
        return threshold_str + append_if_found
    else:
        return ""
