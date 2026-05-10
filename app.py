import streamlit as st
import pandas as pd

from calculations import (
    calculate_pump,
    PumpInputs,
    FittingItem,
    PipeSectionInput,
)

st.set_page_config(page_title="Pump Sizing App", layout="wide")

st.title(" Pump Sizing Dashboard")

fitting_types = [
    "Tee Run",
    "Tee Branch",
    "90° Ellbow",
    "45° Ellbow",
    "Swing Check Valve",
    "Angle Valve",
    "Globe Valve",
    "Gate Valve",
]

pipe_sizes = ['12"', '10"', '8"', '6"', '4"']


def fitting_rows(section_key):
    fittings = []

    for i in range(4):
        col1, col2 = st.columns([2, 3])

        with col1:
            fitting_type = st.selectbox(
                f"Fitting {i + 1} Type",
                fitting_types,
                key=f"{section_key}_type_{i}"
            )

        with col2:
            quantity = st.slider(
                f"Quantity {i + 1}",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                key=f"{section_key}_qty_{i}"
            )

        if quantity > 0:
            fittings.append(
                FittingItem(
                    fitting_type=fitting_type,
                    quantity=quantity
                )
            )

    return fittings


def section_input(title, section_key):
    st.subheader(title)

    pipe_size = st.selectbox(
        "Pipe Size",
        pipe_sizes,
        key=f"{section_key}_pipe"
    )

    straight_length = st.number_input(
        "Straight Length (ft)",
        value=0.0,
        key=f"{section_key}_length"
    )

    with st.expander("Fittings", expanded=False):
        fittings = fitting_rows(section_key)

    return PipeSectionInput(
        pipe_size=pipe_size,
        straight_length_ft=straight_length,
        fittings=fittings
    )


tab1, tab2, tab3 = st.tabs([
    "1. Suction Inputs",
    "2. Discharge Inputs",
    "3. Pump Outputs"
])


with tab1:
    st.header("🟦 Suction Inputs")

    col1, col2 = st.columns(2)

    with col1:
        flow = st.number_input("Flow Rate (USGPM)", value=960.0)
        specific_gravity = st.number_input("Specific Gravity", value=0.88)
        viscosity = st.number_input("Viscosity (cP)", value=1.0)

        roughness = st.number_input(
            "Pipe Roughness (inch)",
            value=0.0018,
            step=0.0001,
            format="%.4f"
        )

    with col2:
        source_pressure_min = st.number_input("Source Min Pressure (psig)", value=0.0)
        source_pressure_max = st.number_input("Source Max Pressure (psig)", value=0.0)
        absolute_pressure = st.number_input("Absolute Pressure (psia)", value=13.7)
        vapor_pressure = st.number_input("Vapor Pressure (psia)", value=10.8)
        suction_strainer_dp = st.number_input("Strainer Pressure Loss (psi)", value=1.0)
        suction_elevation = st.number_input("Suction Elevation (ft)", value=8.0)

    st.markdown("---")
    st.header("Suction Pipe Sections")

    suction_sections = []

    for i in range(1, 4):
        suction_sections.append(
            section_input(
                f"Suction Section {i}",
                f"suction_{i}"
            )
        )
        st.markdown("---")


with tab2:
    st.header("🟥 Discharge Inputs")

    discharge_elevation = st.number_input(
        "Discharge Elevation (ft)",
        value=0.0
    )

    required_discharge_pressure = st.number_input(
        "Required Discharge Pressure (psig)",
        value=80.0
    )

    st.markdown("---")
    st.header("Discharge Pipe Sections")

    discharge_sections = []

    for i in range(1, 4):
        discharge_sections.append(
            section_input(
                f"Discharge Section {i}",
                f"discharge_{i}"
            )
        )
        st.markdown("---")


with tab3:
    st.header("🟩 Pump Outputs")

    if st.button("Calculate Pump"):

        inputs = PumpInputs(
            flow_usgpm=flow,
            specific_gravity=specific_gravity,
            viscosity_cp=viscosity,
            pipe_roughness_in=roughness,

            source_pressure_min_psi=source_pressure_min,
            source_pressure_max_psi=source_pressure_max,
            absolute_pressure_psi=absolute_pressure,
            vapor_pressure_psi=vapor_pressure,
            suction_strainer_dp_psi=suction_strainer_dp,

            suction_elevation_ft=suction_elevation,
            discharge_elevation_ft=discharge_elevation,
            required_discharge_pressure_psi=required_discharge_pressure,

            suction_sections=suction_sections,
            discharge_sections=discharge_sections
        )

        results = calculate_pump(inputs)

        st.markdown("---")

        st.subheader("🟦 Suction Section Results")

        suction_data = []

        for i, section in enumerate(results.suction_sections):

            dp_100ft = (
                section.line_pressure_drop_psi / section.total_length_ft
            ) * 100 if section.total_length_ft > 0 else 0

            line_length = (
                section.total_length_ft - section.total_equivalent_length_ft
            )

            suction_data.append({
                "Section": i + 1,
                "Pipe Size": section.pipe_size,
                "Velocity (fps)": round(section.velocity_fps, 2),
                "Line DP (psi)": round(section.line_pressure_drop_psi, 2),
                "DP psi/100ft": round(dp_100ft, 2),
                "Line Length (ft)": round(line_length, 2),
                "Equivalent Length (ft)": round(section.total_equivalent_length_ft, 2),
                "Total Length (ft)": round(section.total_length_ft, 2),
            })

        st.dataframe(
            pd.DataFrame(suction_data),
            use_container_width=True
        )

        st.subheader("🟥 Discharge Section Results")

        discharge_data = []

        for i, section in enumerate(results.discharge_sections):

            dp_100ft = (
                section.line_pressure_drop_psi / section.total_length_ft
            ) * 100 if section.total_length_ft > 0 else 0

            line_length = (
                section.total_length_ft - section.total_equivalent_length_ft
            )

            discharge_data.append({
                "Section": i + 1,
                "Pipe Size": section.pipe_size,
                "Velocity (fps)": round(section.velocity_fps, 2),
                "Line DP (psi)": round(section.line_pressure_drop_psi, 2),
                "DP psi/100ft": round(dp_100ft, 2),
                "Line Length (ft)": round(line_length, 2),
                "Equivalent Length (ft)": round(section.total_equivalent_length_ft, 2),
                "Total Length (ft)": round(section.total_length_ft, 2),
            })

        st.dataframe(
            pd.DataFrame(discharge_data),
            use_container_width=True
        )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Suction Results")

            st.metric(
                "Total Suction Line DP",
                f"{results.suction_line_pressure_drop_psi:.2f} psi"
            )

            st.metric(
                "Total Suction DP",
                f"{results.total_suction_pressure_drop_psi:.2f} psi"
            )

            st.metric(
                "NPSHa",
                f"{results.npsha_ft:.2f} ft"
            )

            st.metric(
                "Suction Pressure Min",
                f"{results.suction_pressure_min_psi:.2f} psig"
            )

            st.metric(
                "Suction Pressure Max",
                f"{results.suction_pressure_max_psi:.2f} psig"
            )

            st.metric(
                "Suction Head",
                f"{results.suction_head_ft:.2f} ft"
            )

        with col2:
            st.subheader("Discharge / Pump Results")

            st.metric(
                "Total Discharge Line DP",
                f"{results.discharge_line_pressure_drop_psi:.2f} psi"
            )

            st.metric(
                "Discharge Pressure",
                f"{results.discharge_pressure_psi:.2f} psig"
            )

            st.metric(
                "Discharge Head",
                f"{results.discharge_head_ft:.2f} ft"
            )

            st.metric(
                "Differential Head",
                f"{results.differential_head_ft:.2f} ft"
            )

            st.metric(
                "Differential Pressure",
                f"{results.differential_pressure_psi:.2f} psig"
            )