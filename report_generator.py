from io import BytesIO
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _dict_table(data):
    rows = [["Item", "Value"]]

    for key, value in data.items():
        rows.append([key, str(value)])

    table = Table(rows, colWidths=[180, 220])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))

    return table


def _dataframe_table(df):
    rows = [list(df.columns)]

    for _, row in df.iterrows():
        rows.append([str(x) for x in row.tolist()])

    table = Table(rows)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
    ]))

    return table


def generate_pump_report(key_inputs, suction_df, discharge_df, final_outputs):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Pump Sizing Report", styles["Title"]))
    story.append(Paragraph(f"Date: {date.today()}", styles["Normal"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Key Inputs", styles["Heading2"]))
    story.append(_dict_table(key_inputs))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Suction Section Results", styles["Heading2"]))
    story.append(_dataframe_table(suction_df))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Discharge Section Results", styles["Heading2"]))
    story.append(_dataframe_table(discharge_df))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Final Pump Outputs", styles["Heading2"]))
    story.append(_dict_table(final_outputs))

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf