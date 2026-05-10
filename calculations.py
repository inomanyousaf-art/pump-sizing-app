"""
calculations.py

Pump sizing calculations converted from Excel.

Internal units:
- Flow: USGPM
- Pressure: psi
- Length: ft
- Pipe ID: inch
- Viscosity: cP
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

from pipe_data import get_pipe_id_in, get_fitting_equivalent_length_ft


@dataclass
class FittingItem:
    fitting_type: str
    quantity: float = 0.0


@dataclass
class PipeSectionInput:
    pipe_size: str
    straight_length_ft: float
    fittings: list[FittingItem] = field(default_factory=list)


@dataclass
class PumpInputs:
    flow_usgpm: float
    specific_gravity: float
    viscosity_cp: float
    pipe_roughness_in: float

    source_pressure_min_psi: float
    source_pressure_max_psi: float
    absolute_pressure_psi: float
    vapor_pressure_psi: float
    suction_strainer_dp_psi: float

    suction_elevation_ft: float
    discharge_elevation_ft: float
    required_discharge_pressure_psi: float

    suction_sections: list[PipeSectionInput] = field(default_factory=list)
    discharge_sections: list[PipeSectionInput] = field(default_factory=list)


@dataclass
class SideHydraulics:
    pipe_size: str
    pipe_id_in: float
    velocity_fps: float
    total_equivalent_length_ft: float
    total_length_ft: float
    reynolds_number: float
    flow_type: str
    relative_roughness: float
    friction_factor: float
    line_pressure_drop_psi: float


@dataclass
class PumpResults:
    suction_sections: list[SideHydraulics]
    discharge_sections: list[SideHydraulics]

    density_lb_ft3: float

    suction_line_pressure_drop_psi: float
    total_suction_pressure_drop_psi: float

    discharge_line_pressure_drop_psi: float

    npsha_ft: float
    suction_pressure_min_psi: float
    suction_pressure_max_psi: float
    suction_head_ft: float

    discharge_pressure_psi: float
    discharge_head_ft: float
    differential_head_ft: float
    differential_pressure_psi: float


def density_lb_ft3(specific_gravity: float) -> float:
    return 62.341 * specific_gravity


def velocity_fps(flow_usgpm: float, pipe_id_in: float) -> float:
    return 0.408 * flow_usgpm / (pipe_id_in ** 2)


def reynolds_number(
    flow_usgpm: float,
    density: float,
    pipe_id_in: float,
    viscosity_cp: float
) -> float:
    return 50.6 * flow_usgpm * density / (pipe_id_in * viscosity_cp)


def classify_flow(reynolds: float) -> str:
    if reynolds > 4000:
        return "Turbulent"
    if reynolds < 2100:
        return "Laminar"
    return "Transition"


def colebrook_white_friction_factor(
    reynolds: float,
    relative_roughness: float,
    tolerance: float = 1e-10,
    max_iterations: int = 100,
) -> float:

    if reynolds <= 0:
        raise ValueError("Reynolds number must be positive.")

    if reynolds < 2100:
        return 64.0 / reynolds

    f = 1.0 / (
        -1.8 * math.log10((relative_roughness / 3.7) ** 1.11 + 6.9 / reynolds)
    ) ** 2

    for _ in range(max_iterations):
        right_side = -2.0 * math.log10(
            (relative_roughness / 3.7)
            + (2.51 / (reynolds * math.sqrt(f)))
        )

        new_f = 1.0 / (right_side ** 2)

        if abs(new_f - f) < tolerance:
            return new_f

        f = new_f

    raise RuntimeError("Colebrook-White friction factor did not converge.")


def total_equivalent_length_ft(
    fittings: list[FittingItem],
    pipe_size: str
) -> float:

    total = 0.0

    for item in fittings:
        total += (
            get_fitting_equivalent_length_ft(item.fitting_type, pipe_size)
            * item.quantity
        )

    return total


def line_pressure_drop_psi(
    friction_factor: float,
    density: float,
    flow_usgpm: float,
    pipe_id_in: float,
    total_length_ft: float,
) -> float:

    return (
        ((0.0216 * friction_factor * density * (flow_usgpm ** 2))
         / (pipe_id_in ** 5))
        / 100.0
    ) * total_length_ft


def calculate_section(
    flow_usgpm: float,
    density: float,
    viscosity_cp: float,
    roughness_in: float,
    section: PipeSectionInput,
) -> SideHydraulics:

    pipe_id = get_pipe_id_in(section.pipe_size)

    velocity = velocity_fps(flow_usgpm, pipe_id)

    equivalent_length = total_equivalent_length_ft(
        section.fittings,
        section.pipe_size
    )

    total_length = section.straight_length_ft + equivalent_length

    reynolds = reynolds_number(
        flow_usgpm,
        density,
        pipe_id,
        viscosity_cp
    )

    flow_type = classify_flow(reynolds)

    relative_roughness = roughness_in / pipe_id

    friction_factor = colebrook_white_friction_factor(
        reynolds,
        relative_roughness
    )

    pressure_drop = line_pressure_drop_psi(
        friction_factor,
        density,
        flow_usgpm,
        pipe_id,
        total_length
    )

    return SideHydraulics(
        pipe_size=section.pipe_size,
        pipe_id_in=pipe_id,
        velocity_fps=velocity,
        total_equivalent_length_ft=equivalent_length,
        total_length_ft=total_length,
        reynolds_number=reynolds,
        flow_type=flow_type,
        relative_roughness=relative_roughness,
        friction_factor=friction_factor,
        line_pressure_drop_psi=pressure_drop,
    )


def calculate_sections(
    flow_usgpm: float,
    density: float,
    viscosity_cp: float,
    roughness_in: float,
    sections: list[PipeSectionInput],
) -> list[SideHydraulics]:

    results = []

    for section in sections:
        results.append(
            calculate_section(
                flow_usgpm=flow_usgpm,
                density=density,
                viscosity_cp=viscosity_cp,
                roughness_in=roughness_in,
                section=section,
            )
        )

    return results


def calculate_pump(inputs: PumpInputs) -> PumpResults:

    density = density_lb_ft3(inputs.specific_gravity)

    suction_sections = calculate_sections(
        flow_usgpm=inputs.flow_usgpm,
        density=density,
        viscosity_cp=inputs.viscosity_cp,
        roughness_in=inputs.pipe_roughness_in,
        sections=inputs.suction_sections,
    )

    discharge_sections = calculate_sections(
        flow_usgpm=inputs.flow_usgpm,
        density=density,
        viscosity_cp=inputs.viscosity_cp,
        roughness_in=inputs.pipe_roughness_in,
        sections=inputs.discharge_sections,
    )

    suction_line_dp = sum(
        section.line_pressure_drop_psi
        for section in suction_sections
    )

    discharge_line_dp = sum(
        section.line_pressure_drop_psi
        for section in discharge_sections
    )

    total_suction_dp = suction_line_dp + inputs.suction_strainer_dp_psi

    npsha = (
        inputs.suction_elevation_ft
        + (
            inputs.source_pressure_min_psi
            + inputs.absolute_pressure_psi
            - inputs.vapor_pressure_psi
            - total_suction_dp
        )
        * 2.31
        / inputs.specific_gravity
    ) * 0.90

    suction_pressure_min = (
        inputs.source_pressure_min_psi
        - total_suction_dp
        + (inputs.suction_elevation_ft / 2.31 * inputs.specific_gravity)
    ) * 0.90

    suction_pressure_max = (
        inputs.source_pressure_max_psi
        - total_suction_dp
        + (inputs.suction_elevation_ft / 2.31 * inputs.specific_gravity)
    )

    suction_head = (
        inputs.suction_elevation_ft
        + (
            inputs.source_pressure_min_psi
            - total_suction_dp
        )
        * 2.31
        / inputs.specific_gravity
    ) * 0.90

    discharge_pressure = (
        inputs.required_discharge_pressure_psi
        + discharge_line_dp
        + (inputs.discharge_elevation_ft / 2.31 * inputs.specific_gravity)
    ) * 1.10

    discharge_head = discharge_pressure * 2.31 / inputs.specific_gravity

    differential_head = discharge_head - suction_head

    differential_pressure = differential_head * inputs.specific_gravity / 2.31

    return PumpResults(
        suction_sections=suction_sections,
        discharge_sections=discharge_sections,
        density_lb_ft3=density,
        suction_line_pressure_drop_psi=suction_line_dp,
        total_suction_pressure_drop_psi=total_suction_dp,
        discharge_line_pressure_drop_psi=discharge_line_dp,
        npsha_ft=npsha,
        suction_pressure_min_psi=suction_pressure_min,
        suction_pressure_max_psi=suction_pressure_max,
        suction_head_ft=suction_head,
        discharge_pressure_psi=discharge_pressure,
        discharge_head_ft=discharge_head,
        differential_head_ft=differential_head,
        differential_pressure_psi=differential_pressure,
    )