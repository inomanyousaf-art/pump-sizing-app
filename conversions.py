def convert_flow(value, unit):
    if unit == "USGPM":
        return value
    if unit == "m3/hr":
        return value * 4.40287
    if unit == "L/min":
        return value * 0.264172
    return value


def convert_pressure(value, unit):
    if unit == "psi":
        return value
    if unit == "bar":
        return value * 14.5038
    if unit == "kPa":
        return value * 0.145038
    if unit == "kg/cm2":
        return value * 14.2233
    return value


def convert_length(value, unit):
    if unit == "ft":
        return value
    if unit == "m":
        return value * 3.28084
    return value


def convert_viscosity(value, unit):
    if unit == "cP":
        return value
    if unit == "mPa.s":
        return value
    if unit == "Pa.s":
        return value * 1000
    return value


def convert_roughness(value, unit):
    if unit == "inch":
        return value
    if unit == "mm":
        return value * 0.0393701
    return value