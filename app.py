import streamlit as st
import pandas as pd

from calculations import (
    calculate_pump,
    PumpInputs,
    FittingItem,
    PipeSectionInput,
)

from conversions import (
    convert_flow,
    convert_pressure,
    convert_length,
    convert_viscosity,
    convert_roughness,
)

from report_generator import generate_pump_report

st.set_page_config(page_title="Pump Sizing App", layout="wide")

st.title("Pump Sizing")

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


# =========================================================
# FITTINGS INPUT
# =========================================================

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


# =========================================================
# PIPE SECTION INPUT
# =========================================================

def section_input(title, section_key, length_unit):

    st.subheader(title)

    pipe_size = st.selectbox(
        "Pipe Size",
        pipe_sizes,
        key=f"{section_key}_pipe"
    )

    straight_length_input = st.number_input(
        f"Straight Length ({length_unit})",
        value=0.0,
        key=f"{section_key}_length"
    )

    straight_length_ft = convert_length(
        straight_length_input,
        length_unit
    )

    with st.expander("Fittings", expanded=False):

        fittings = fitting_rows(section_key)

    return PipeSectionInput(
        pipe_size=pipe_size,
        straight_length_ft=straight_length_ft,
        fittings=fittings
    )


# =========================================================
# RESULTS TABLE
# =========================================================

def make_section_table(sections):

    data = []

    for i, section in enumerate(sections):

        dp_100ft = (
            section.line_pressure_drop_psi
            / section.total_length_ft
        ) * 100 if section.total_length_ft > 0 else 0

        line_length = (
            section.total_length_ft
            - section.total_equivalent_length_ft
        )

        data.append({
            "Section": i + 1,
            "Pipe Size": section.pipe_size,
            "Velocity (fps)": round(section.velocity_fps, 2),
            "Line DP (psi)": round(section.line_pressure_drop_psi, 2),
            "DP psi/100ft": round(dp_100ft, 2),
            "Line Length (ft)": round(line_length, 2),
            "Equivalent Length (ft)": round(section.total_equivalent_length_ft, 2),
            "Total Length (ft)": round(section.total_length_ft, 2),
        })

    return pd.DataFrame(data)


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "1. Suction Inputs",
    "2. Discharge Inputs",
    "3. Pump Outputs"
])


# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.header("🟦 Suction Inputs")

    with st.expander("Unit Selection", expanded=True):

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            flow_unit = st.selectbox(
                "Flow Unit",
                ["USGPM", "m3/hr", "L/min"]
            )

        with col2:
            pressure_unit = st.selectbox(
                "Pressure Unit",
                ["psi", "bar", "kPa", "kg/cm2"]
            )

        with col3:
            length_unit = st.selectbox(
                "Length Unit",
                ["ft", "m"]
            )

        with col4:
            viscosity_unit = st.selectbox(
                "Viscosity Unit",
                ["cP", "mPa.s", "Pa.s"]
            )

        with col5:
            roughness_unit = st.selectbox(
                "Roughness Unit",
                ["inch", "mm"]
            )

    col1, col2 = st.columns(2)

    with col1:

        flow_input = st.number_input(
            f"Flow Rate ({flow_unit})",
            value=960.0
        )

        specific_gravity = st.number_input(
            "Specific Gravity",
            value=0.88
        )

        viscosity_input = st.number_input(
            f"Viscosity ({viscosity_unit})",
            value=1.0
        )

        roughness_input = st.number_input(
            f"Pipe Roughness ({roughness_unit})",
            value=0.0018 if roughness_unit == "inch" else 0.0457,
            step=0.0001,
            format="%.4f"
        )

    with col2:

        source_pressure_min_input = st.number_input(
            f"Source Min Pressure ({pressure_unit} g)",
            value=0.0
        )

        source_pressure_max_input = st.number_input(
            f"Source Max Pressure ({pressure_unit} g)",
            value=0.0
        )

        absolute_pressure_input = st.number_input(
            f"Absolute Pressure ({pressure_unit} abs)",
            value=13.7 if pressure_unit == "psi" else 0.9446
        )

        vapor_pressure_input = st.number_input(
            f"Vapor Pressure ({pressure_unit} abs)",
            value=10.8 if pressure_unit == "psi" else 0.7446
        )

        suction_strainer_dp_input = st.number_input(
            f"Strainer Pressure Loss ({pressure_unit})",
            value=1.0 if pressure_unit == "psi" else 0.0689
        )

        suction_elevation_input = st.number_input(
            f"Suction Elevation ({length_unit})",
            value=8.0 if length_unit == "ft" else 2.438
        )

    flow_usgpm = convert_flow(flow_input, flow_unit)

    viscosity_cp = convert_viscosity(
        viscosity_input,
        viscosity_unit
    )

    roughness_in = convert_roughness(
        roughness_input,
        roughness_unit
    )

    source_pressure_min_psi = convert_pressure(
        source_pressure_min_input,
        pressure_unit
    )

    source_pressure_max_psi = convert_pressure(
        source_pressure_max_input,
        pressure_unit
    )

    absolute_pressure_psi = convert_pressure(
        absolute_pressure_input,
        pressure_unit
    )

    vapor_pressure_psi = convert_pressure(
        vapor_pressure_input,
        pressure_unit
    )

    suction_strainer_dp_psi = convert_pressure(
        suction_strainer_dp_input,
        pressure_unit
    )

    suction_elevation_ft = convert_length(
        suction_elevation_input,
        length_unit
    )

    st.markdown("---")

    st.header("Pipe Sections")

    suction_sections = []

    for i in range(1, 4):

        suction_sections.append(
            section_input(
                f"Section {i}",
                f"suction_{i}",
                length_unit
            )
        )

        st.markdown("---")


# =========================================================
# TAB 2
# =========================================================

with tab2:

    st.header("🟥 Discharge Inputs")

    discharge_elevation_input = st.number_input(
        f"Discharge Elevation ({length_unit})",
        value=0.0
    )

    required_discharge_pressure_input = st.number_input(
        f"Required Discharge Pressure ({pressure_unit} g)",
        value=80.0 if pressure_unit == "psi" else 5.516
    )

    discharge_elevation_ft = convert_length(
        discharge_elevation_input,
        length_unit
    )

    required_discharge_pressure_psi = convert_pressure(
        required_discharge_pressure_input,
        pressure_unit
    )

    st.markdown("---")

    st.header("Pipe Sections")

    discharge_sections = []

    for i in range(1, 4):

        discharge_sections.append(
            section_input(
                f"Section {i}",
                f"discharge_{i}",
                length_unit
            )
        )

        st.markdown("---")


# =========================================================
# TAB 3
# =========================================================

with tab3:

    st.header("🟩 Pump Outputs")

    if st.button("Calculate Pump"):

        inputs = PumpInputs(

            flow_usgpm=flow_usgpm,
            specific_gravity=specific_gravity,
            viscosity_cp=viscosity_cp,
            pipe_roughness_in=roughness_in,

            source_pressure_min_psi=source_pressure_min_psi,
            source_pressure_max_psi=source_pressure_max_psi,
            absolute_pressure_psi=absolute_pressure_psi,
            vapor_pressure_psi=vapor_pressure_psi,
            suction_strainer_dp_psi=suction_strainer_dp_psi,

            suction_elevation_ft=suction_elevation_ft,
            discharge_elevation_ft=discharge_elevation_ft,
            required_discharge_pressure_psi=required_discharge_pressure_psi,

            suction_sections=suction_sections,
            discharge_sections=discharge_sections
        )

        results = calculate_pump(inputs)

        st.markdown("---")

        st.subheader("🟦 Suction Section Results")

        suction_df = make_section_table(results.suction_sections)

        st.dataframe(
            suction_df,
            use_container_width=True
        )

        st.subheader("🟥 Discharge Section Results")

        discharge_df = make_section_table(results.discharge_sections)

        st.dataframe(
            discharge_df,
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

        st.markdown("---")

        key_inputs = {
            "Flow": f"{flow_input} {flow_unit}",
            "Specific Gravity": specific_gravity,
            "Viscosity": f"{viscosity_input} {viscosity_unit}",
            "Pipe Roughness": f"{roughness_input} {roughness_unit}",
        }

        final_outputs = {
            "Total Suction DP": f"{results.total_suction_pressure_drop_psi:.2f} psi",
            "NPSHa": f"{results.npsha_ft:.2f} ft",
            "Discharge Pressure": f"{results.discharge_pressure_psi:.2f} psig",
            "Discharge Head": f"{results.discharge_head_ft:.2f} ft",
            "Differential Head": f"{results.differential_head_ft:.2f} ft",
            "Differential Pressure": f"{results.differential_pressure_psi:.2f} psig",
        }

        pdf_report = generate_pump_report(
            key_inputs,
            suction_df,
            discharge_df,
            final_outputs
        )

        st.download_button(
            label="📄 Download One-Page PDF Report",
            data=pdf_report,
            file_name="pump_sizing_report.pdf",
            mime="application/pdf"
        )