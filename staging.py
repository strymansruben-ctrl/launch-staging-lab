"""Calculate ideal delta-v for a serial stack of expendable stages."""

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

G0 = 9.80665  # m/s²


def number(value, name, *, allow_zero=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if value < 0 or (value == 0 and not allow_zero):
        limit = "nonnegative" if allow_zero else "positive"
        raise ValueError(f"{name} must be {limit}")
    return float(value)


@dataclass(frozen=True)
class Stage:
    name: str
    dry_kg: float
    propellant_kg: float
    isp_s: float

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("each stage needs a nonempty name")
        number(self.dry_kg, "dry_kg")
        number(self.propellant_kg, "propellant_kg", allow_zero=True)
        number(self.isp_s, "isp_s")


@dataclass(frozen=True)
class Burn:
    name: str
    start_kg: float
    burnout_kg: float
    delta_v_m_s: float


def calculate(stages, payload_kg):
    """Return burns in flight order. Burnout mass is measured before separation."""
    carried_kg = number(payload_kg, "payload_kg", allow_zero=True)
    burns = []
    for stage in reversed(stages):
        burnout_kg = carried_kg + stage.dry_kg
        start_kg = burnout_kg + stage.propellant_kg
        delta_v = G0 * stage.isp_s * math.log1p(stage.propellant_kg / burnout_kg)
        if not all(map(math.isfinite, (start_kg, delta_v))):
            raise ValueError("stage mass or delta-v exceeds numeric range")
        burns.append(Burn(stage.name, start_kg, burnout_kg, delta_v))
        carried_kg = start_kg
    return list(reversed(burns))


def load_vehicle(path):
    vehicle = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(vehicle, dict) or not isinstance(vehicle.get("stages"), list):
        raise ValueError("vehicle must contain a 'stages' array")
    if not vehicle["stages"]:
        raise ValueError("vehicle needs at least one stage")
    return [Stage(**row) for row in vehicle["stages"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vehicle", type=Path)
    parser.add_argument("--payload-kg", type=float, nargs="+", required=True)
    args = parser.parse_args()
    try:
        stages = load_vehicle(args.vehicle)
        results = [(payload, calculate(stages, payload)) for payload in args.payload_kg]
        rows = []
        for payload, burns in results:
            for index, burn in enumerate(burns, 1):
                rows.append((payload, index, burn.name, f"{burn.start_kg:.3f}",
                             f"{burn.burnout_kg:.3f}", f"{burn.delta_v_m_s:.3f}"))
            total = math.fsum(burn.delta_v_m_s for burn in burns)
            rows.append((payload, "", "TOTAL", "", "", f"{total:.3f}"))
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        parser.error(str(exc))

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("payload_kg", "stage_index", "stage", "start_kg",
                     "burnout_kg", "ideal_delta_v_m_s"))
    writer.writerows(rows)


if __name__ == "__main__":
    main()
