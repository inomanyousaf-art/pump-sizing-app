"""
conversions.py

Unit conversions for the pump sizing engine.

The Excel formulas use these internal units:
- Flow: USGPM
- Pressure: psi
- Length / elevation: ft
- Pipe roughness: inch
- Viscosity: cP
"""

FLOW_TO_USGPM = {
    "USGPM": 1.0,
    "UKGPM": 1.2,
    "m3/hr": 4.4028656,
    "L/min": 0.264172,
    "Liter/min": 0.264172,
    "ft3/hr": 0.1246753,
    "Barrels/Day": 0.0291667,
}

PRESSURE_TO_PSI = {
    "psi": 1.0,
    "psig": 1.0,
    "psia": 1.0,
    "bar": 14.5037738,
    "kPa": 0.145037738,
    "kg/cm2": 14.2233433,
    "kg/cm²": 14.2233433,
}

LENGTH_TO_FT = {
    "ft": 1.0,
    "m": 3.280839895,
    "inch": 1.0 / 12.0,
    "in": 1.0 / 12.0,
    "mm": 0.003280839895,
}

ROUGHNESS_TO_IN = {
    "in": 1.0,
    "inch": 1.0,
    "mm": 0.03937007874,
    "m": 39.37007874,
}

VISCOSITY_TO_CP = {
    "cP": 1.0,
    "cp": 1.0,
    "mPa.s": 1.0,
    "mPa·s": 1.0,
    "Pa.s": 1000.0,
    "Pa·s": 1000.0,
}


def convert(value: float, unit: str, factors: dict[str, float], quantity_name: str) -> float:
    """Generic conversion helper."""
    if unit not in factors:
        options = ", ".join(factors)
        raise ValueError(f"Unknown {quantity_name} unit {unit!r}. Choose one of: {options}")
    return float(value) * factors[unit]


def flow_to_usgpm(value: float, unit: str) -> float:
    return convert(value, unit, FLOW_TO_USGPM, "flow")


def pressure_to_psi(value: float, unit: str) -> float:
    return convert(value, unit, PRESSURE_TO_PSI, "pressure")


def length_to_ft(value: float, unit: str) -> float:
    return convert(value, unit, LENGTH_TO_FT, "length")


def roughness_to_in(value: float, unit: str) -> float:
    return convert(value, unit, ROUGHNESS_TO_IN, "roughness")


def viscosity_to_cp(value: float, unit: str) -> float:
    return convert(value, unit, VISCOSITY_TO_CP, "viscosity")
