# Launch Staging Lab

A Python command-line tool for comparing how payload mass changes the ideal delta-v of a multistage rocket. It exports one row per burn plus a total for each payload, so you can reuse the results in a spreadsheet or plotting tool.

## Run the demo

From this repository root, with Python 3.10 or later. No packages are required. Use `python3` in place of `python` if your system uses that command.

```sh
python staging.py examples/two-stage.json --payload-kg 2000 6000
python -m unittest discover -s tests -v
```

The example vehicle is fictional. Raising payload from 2,000 to 6,000 kg reduces total ideal delta-v from approximately 12,653 to 10,987 m/s. The upper-stage contribution drops more because payload is a larger share of its burnout mass.

## Input and model

The input JSON lists stages in burn order, bottom to top. Each stage has a name, dry mass in kilograms, usable propellant mass in kilograms and constant specific impulse in seconds. Each payload argument is an independent scenario in kilograms.

For each burn, the vehicle carries the current stage, all fueled stages above it and the payload. At burnout, the current stage is still attached. Its dry mass is discarded before the next burn. Ideal delta-v is `g₀ × Isp × ln(start mass / burnout mass)`, with `g₀ = 9.80665 m/s²`. The model sums ideal delta-v across the stack. See [NASA Glenn's ideal rocket equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation/).

The model assumes serial burns, full use of each stage's stated propellant and instant separation. It omits gravity and drag losses, thrust constraints, trajectory and recovery. The results measure ideal propulsion performance and are insufficient to determine whether a vehicle can reach orbit.

## Files

- `staging.py` contains the model and CSV command-line interface.
- `examples/two-stage.json` contains the fictional input vehicle.
- `tests/test_staging.py` checks stage mass accounting, a hand calculation and invalid inputs.
