"""
test_cases.py

First test case based on the current visible Excel example.

Run this file from the same folder:

    python test_cases.py

Because we are using standard Colebrook-White instead of Excel Goal Seek's exact formula,
small differences from Excel are expected.
"""

from calculations import PumpInputs, FittingItem, calculate_pump


def run_excel_sample_case():
    inputs = PumpInputs(
        flow_usgpm=800 * 1.2,  # Excel E8=800 UKGPM, conversion to USGPM
        specific_gravity=0.88,
        viscosity_cp=13.2,
        pipe_roughness_in=0.0018,
        source_pressure_min_psi=0,
        source_pressure_max_psi=0,
        absolute_pressure_psi=13.6,
        vapor_pressure_psi=70.18 / 6.4987,
        suction_strainer_dp_psi=1,
        suction_elevation_ft=8,
        suction_line_length_ft=150 * 3.28,
        discharge_line_length_ft=100 * 3.28,
        discharge_elevation_ft=0,  # Excel E22 is blank in the uploaded workbook
        required_discharge_pressure_psi=82.32128,
        suction_pipe_size='12"',
        discharge_pipe_size='10"',
        suction_fittings=[
            FittingItem("90° Ellbow", 5),
            FittingItem("Gate Valve", 3),
        ],
        discharge_fittings=[
            FittingItem("90° Ellbow", 10),
            FittingItem("Gate Valve", 5),
        ],
    )

    results = calculate_pump(inputs)

    print("=== Excel sample case: suction 12 in, discharge 10 in ===")
    print(f"Flow: {inputs.flow_usgpm:.3f} USGPM")
    print(f"Density: {results.density_lb_ft3:.3f} lb/ft3")
    print()
    print("Suction")
    print(f"  ID: {results.suction.pipe_id_in:.4f} in")
    print(f"  Velocity: {results.suction.velocity_fps:.4f} fps")
    print(f"  Reynolds: {results.suction.reynolds_number:.0f}")
    print(f"  Friction factor: {results.suction.friction_factor:.6f}")
    print(f"  Line pressure drop: {results.suction.line_pressure_drop_psi:.4f} psi")
    print(f"  Total suction DP: {results.total_suction_pressure_drop_psi:.4f} psi")
    print(f"  NPSHa: {results.npsha_ft:.4f} ft")
    print(f"  Suction head: {results.suction_head_ft:.4f} ft")
    print()
    print("Discharge")
    print(f"  ID: {results.discharge.pipe_id_in:.4f} in")
    print(f"  Velocity: {results.discharge.velocity_fps:.4f} fps")
    print(f"  Reynolds: {results.discharge.reynolds_number:.0f}")
    print(f"  Friction factor: {results.discharge.friction_factor:.6f}")
    print(f"  Line pressure drop: {results.discharge.line_pressure_drop_psi:.4f} psi")
    print(f"  Discharge pressure: {results.discharge_pressure_psi:.4f} psi")
    print(f"  Discharge head: {results.discharge_head_ft:.4f} ft")
    print()
    print("Pump")
    print(f"  Differential head: {results.differential_head_ft:.4f} ft")
    print(f"  Differential pressure: {results.differential_pressure_psi:.4f} psi")


if __name__ == "__main__":
    run_excel_sample_case()
