"""
check_critical_values: deterministic blood-panel triage gate.

Parses free-text or JSON blood lab values, compares each against the standard
hospital panic-value table, and returns structured triage flags. No network IO
inside the tool; NIH lookups are handled by the canvas HTTP nodes wired to the
sub-agents (fetchPubmedSearch, fetchNihConditions, fetchNihLabTests).

Returns:
    {
      "critical":     [ { marker, value, unit, reference_range, reason } ],
      "abnormal":     [ ... ],
      "normal":       [ ... ],
      "unrecognized_input": "" or the raw input if parsing failed,
      "summary":      { critical_count, abnormal_count, normal_count,
                        requires_emergency_care, panel_recognized },
    }

Panic-value thresholds sourced from standard US hospital lab callback policies.
Reference ranges are adult, non-pregnant defaults; individual ranges vary by
lab, age, sex, medication, and clinical context. This tool reports values,
not diagnoses.
"""

import json
import re


PANIC = {
    "glucose":    {"crit_low": 40,   "crit_high": 600,  "ref_low": 70,   "ref_high": 100,  "unit": "mg/dL"},
    "potassium":  {"crit_low": 2.5,  "crit_high": 7.0,  "ref_low": 3.5,  "ref_high": 5.0,  "unit": "mEq/L"},
    "sodium":     {"crit_low": 120,  "crit_high": 160,  "ref_low": 135,  "ref_high": 145,  "unit": "mEq/L"},
    "hemoglobin": {"crit_low": 7.0,  "crit_high": 20.0, "ref_low": 12.0, "ref_high": 17.0, "unit": "g/dL"},
    "platelets":  {"crit_low": 20,   "crit_high": 1000, "ref_low": 150,  "ref_high": 450,  "unit": "x10^3/uL"},
    "wbc":        {"crit_low": 1.0,  "crit_high": 50.0, "ref_low": 4.0,  "ref_high": 11.0, "unit": "x10^3/uL"},
    "inr":        {"crit_low": None, "crit_high": 5.0,  "ref_low": 0.8,  "ref_high": 1.2,  "unit": "ratio"},
    "troponin":   {"crit_low": None, "crit_high": 0.04, "ref_low": 0.0,  "ref_high": 0.04, "unit": "ng/mL"},
    "creatinine": {"crit_low": None, "crit_high": 4.0,  "ref_low": 0.6,  "ref_high": 1.3,  "unit": "mg/dL"},
    "lactate":    {"crit_low": None, "crit_high": 4.0,  "ref_low": 0.5,  "ref_high": 2.2,  "unit": "mmol/L"},
    "calcium":    {"crit_low": 6.0,  "crit_high": 13.0, "ref_low": 8.5,  "ref_high": 10.5, "unit": "mg/dL"},
    "magnesium":  {"crit_low": 1.0,  "crit_high": 4.7,  "ref_low": 1.7,  "ref_high": 2.4,  "unit": "mg/dL"},
}


ALIASES = {
    "glucose":    ["glucose", "blood glucose", "blood sugar", "fasting glucose", "fpg"],
    "potassium":  ["potassium", "k+", "serum potassium"],
    "sodium":     ["sodium", "na+", "serum sodium"],
    "hemoglobin": ["hemoglobin", "hgb", "haemoglobin"],
    "platelets":  ["platelets", "platelet count", "plt"],
    "wbc":        ["wbc", "white blood cell", "white blood count", "leukocytes", "leucocytes"],
    "inr":        ["inr", "international normalized ratio"],
    "troponin":   ["troponin", "troponin i", "troponin t"],
    "creatinine": ["creatinine", "serum creatinine"],
    "lactate":    ["lactate", "lactic acid"],
    "calcium":    ["calcium", "serum calcium"],
    "magnesium":  ["magnesium", "serum magnesium"],
}


def _build_alias_index():
    pairs = []
    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            pairs.append((alias.lower().split(), canonical))
    pairs.sort(key=lambda p: -len(p[0]))
    return pairs


_ALIAS_INDEX = _build_alias_index()


def _resolve_alias_phrase(phrase):
    tokens = phrase.split()
    for alias_tokens, canonical in _ALIAS_INDEX:
        if tokens == alias_tokens:
            return canonical
    return None


def _parse_json(text):
    stripped = text.lstrip()
    if not (stripped.startswith("{") or stripped.startswith("[")):
        return None
    try:
        data = json.loads(text)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    out = {}
    for raw_key, raw_val in data.items():
        canonical = _resolve_alias_phrase(str(raw_key).lower().strip())
        if canonical is None:
            continue
        try:
            out[canonical] = float(raw_val)
        except Exception:
            continue
    return out


def _parse_free_text(text):
    tokens = re.findall(r"[a-zA-Z+]+|\d+(?:\.\d+)?", text.lower())
    extracted = {}
    current_marker = None
    i = 0
    while i < len(tokens):
        token = tokens[i]
        try:
            value = float(token)
            if current_marker and current_marker not in extracted:
                extracted[current_marker] = value
                current_marker = None
            i += 1
            continue
        except ValueError:
            pass
        matched = False
        for alias_tokens, canonical in _ALIAS_INDEX:
            window = tokens[i:i + len(alias_tokens)]
            if window == alias_tokens:
                current_marker = canonical
                i += len(alias_tokens)
                matched = True
                break
        if not matched:
            i += 1
    return extracted


def _parse(text):
    parsed = _parse_json(text)
    if parsed:
        return parsed
    return _parse_free_text(text)


def _classify(value, spec):
    if spec["crit_low"] is not None and value < spec["crit_low"]:
        return "critical", "critically low (" + str(value) + " " + spec["unit"] + ", panic threshold <" + str(spec["crit_low"]) + ")"
    if spec["crit_high"] is not None and value > spec["crit_high"]:
        return "critical", "critically high (" + str(value) + " " + spec["unit"] + ", panic threshold >" + str(spec["crit_high"]) + ")"
    if value < spec["ref_low"]:
        return "abnormal", "below reference range (" + str(value) + " " + spec["unit"] + ", normal " + str(spec["ref_low"]) + "-" + str(spec["ref_high"]) + ")"
    if value > spec["ref_high"]:
        return "abnormal", "above reference range (" + str(value) + " " + spec["unit"] + ", normal " + str(spec["ref_low"]) + "-" + str(spec["ref_high"]) + ")"
    return "normal", "within reference range (" + str(value) + " " + spec["unit"] + ", normal " + str(spec["ref_low"]) + "-" + str(spec["ref_high"]) + ")"


def check_critical_values(lab_text: str) -> dict:
    parsed = _parse(lab_text or "")
    critical = []
    abnormal = []
    normal = []
    for marker, value in parsed.items():
        spec = PANIC.get(marker)
        if spec is None:
            continue
        bucket, reason = _classify(value, spec)
        record = {
            "marker": marker,
            "value": value,
            "unit": spec["unit"],
            "reference_range": str(spec["ref_low"]) + "-" + str(spec["ref_high"]),
            "reason": reason,
        }
        if bucket == "critical":
            critical.append(record)
        elif bucket == "abnormal":
            abnormal.append(record)
        else:
            normal.append(record)
    return {
        "critical": critical,
        "abnormal": abnormal,
        "normal": normal,
        "unrecognized_input": lab_text if not parsed else "",
        "summary": {
            "critical_count": len(critical),
            "abnormal_count": len(abnormal),
            "normal_count": len(normal),
            "requires_emergency_care": len(critical) > 0,
            "panel_recognized": bool(parsed),
        },
    }
