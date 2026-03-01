"""Service for parsing and managing NTC2018 hazard profiles imported from EdiLus-MS.

This module implements the minimal data model and parser required by STEP2 of
"Spectrum Paste Service".  No numerical interpolation, web access, or spectrum
calculations are performed here; the service merely normalizes and persists
user-provided parameters.

The public API follows the specification in
`docs/MEGAPLAN/SPEC_NTC2018_HAZARD_PASTE.md`.
"""

from __future__ import annotations

import dataclasses
import datetime
import re

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class Ntc2018HazardRow:
    limit_state_label: str
    tr_years: float
    ag_g: float
    f0: float
    tc_star_s: float


@dataclasses.dataclass
class Ntc2018HazardProfile:
    source: str = "EDILUS_MS"
    class_of_use: str = ""
    vita_nominale_years: int = 0
    vr_years: int = 0
    site_label: str | None = None
    raw_paste: str = ""
    parsed_rows: list[Ntc2018HazardRow] = dataclasses.field(default_factory=list)
    timestamp_import: str = ""
    quality: str = "OK"  # OK | WARNING | ERROR
    messages: list[str] = dataclasses.field(default_factory=list)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

_LIMIT_LABELS = [
    "Operatività",
    "Danno",
    "Salvaguardia Vita",
    "Prevenzione Collasso",
]


def parse_edilus_ms_table(raw_paste: str) -> tuple[list[Ntc2018HazardRow], list[str], str]:
    """Parse the raw text copied from EdiLus-MS.

    Returns:
        rows: list of successfully parsed rows
        messages: list of warning/error messages
        quality: one of "OK","WARNING","ERROR"
    """
    text = raw_paste.replace("\r\n", "\n")
    # split and cleanup
    lines = []
    for line in text.split("\n"):
        ln = re.sub(r"\s+", " ", line).strip()
        if ln:
            lines.append(ln)

    rows: list[Ntc2018HazardRow] = []
    messages: list[str] = []
    quality = "OK"
    found_labels: set[str] = set()

    for line in lines:
        for lbl in _LIMIT_LABELS:
            if re.search(re.escape(lbl), line, flags=re.IGNORECASE):
                found_labels.add(lbl.lower())

                # normalize decimals only inside numeric tokens (digit,comma,digit)
                normalized = re.sub(r"(?<=\d),(?=\d)", ".", line)
                nums = re.findall(r"[-+]?\d+\.?\d*", normalized)
                if len(nums) < 4:
                    messages.append(f"Riga '{lbl}' manca valori: {len(nums)}")
                    quality = "ERROR"
                    # do not add row
                else:
                    if len(nums) > 4:
                        messages.append(
                            f"Riga '{lbl}' contiene {len(nums)} numeri, usati primi quattro"
                        )
                        if quality == "OK":
                            quality = "WARNING"
                    try:
                        tr = float(nums[0])
                        ag = float(nums[1])
                        f0 = float(nums[2])
                        tc = float(nums[3])
                    except ValueError:
                        messages.append(f"Riga '{lbl}' valori non numerici")
                        quality = "ERROR"
                    else:
                        # basic validations
                        if ag <= 0 or f0 <= 0 or tc <= 0:
                            messages.append(f"Riga '{lbl}' ha valori non positivi")
                            quality = "ERROR"
                        else:
                            rows.append(Ntc2018HazardRow(lbl, tr, ag, f0, tc))
                break
    # check missing labels
    for lbl in _LIMIT_LABELS:
        if lbl.lower() not in found_labels:
            messages.append(f"Etichetta '{lbl}' mancante")
            if quality == "OK":
                quality = "WARNING"
    if not rows:
        quality = "ERROR"
    return rows, messages, quality


# ---------------------------------------------------------------------------
# Profile builder / accessor
# ---------------------------------------------------------------------------


def build_profile(
    class_of_use: str,
    vita_nominale_years: int,
    vr_years: int,
    site_label: str | None,
    raw_paste: str,
) -> Ntc2018HazardProfile:
    rows, messages, quality = parse_edilus_ms_table(raw_paste)
    profile = Ntc2018HazardProfile(
        class_of_use=class_of_use,
        vita_nominale_years=vita_nominale_years,
        vr_years=vr_years,
        site_label=site_label,
        raw_paste=raw_paste,
        parsed_rows=rows,
        timestamp_import=datetime.datetime.utcnow().isoformat(),
        quality=quality,
        messages=messages,
    )
    return profile


def get_hazard_params(
    profile: Ntc2018HazardProfile, limit_state_label: str
) -> tuple[float, float, float, float] | None:
    """Return parameters for a given limit state label.

    Matching is case-insensitive and ignores extra spaces.

    Raises KeyError if not found.
    """
    normalized = limit_state_label.strip().lower()
    for row in profile.parsed_rows:
        if row.limit_state_label.strip().lower() == normalized:
            return row.tr_years, row.ag_g, row.f0, row.tc_star_s
    raise KeyError(f"Limit state '{limit_state_label}' not found")
