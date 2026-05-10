# Pump Sizing Calculation Engine

This is the first Python conversion step from the Excel pump sizing workbook.

It includes:
- Unit conversion helpers
- Actual pipe internal diameter lookup data from `Backup Calc`
- Actual fitting equivalent length lookup data from `Backup Calc`
- Colebrook-White friction factor calculation
- Suction/discharge hydraulics
- NPSHa
- Pump differential head and pressure

Run the sample test:

```bash
python test_cases.py
```

Next step is to compare the printed values against Excel and then build the Streamlit app.
