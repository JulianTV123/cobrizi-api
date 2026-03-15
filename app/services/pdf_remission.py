from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_remission_pdf(remission, user, associate) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
    )
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    # Header
    elements.append(Paragraph(f"REMISIÓN N° {remission.consecutive}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Customer and date info
    elements.append(Paragraph(f"<b>Cliente:</b> {associate.name}", styles["Normal"]))
    elements.append(
        Paragraph(f"<b>NIT/CC:</b> {associate.id_number or ''}", styles["Normal"])
    )
    elements.append(
        Paragraph(f"<b>Dirección:</b> {associate.address or ''}", styles["Normal"])
    )
    elements.append(
        Paragraph(
            f"<b>Fecha:</b> {remission.date.strftime('%d/%m/%Y')}", styles["Normal"]
        )
    )
    elements.append(Spacer(1, 0.3 * inch))

    # Items
    for rem_item in remission.items:
        item = rem_item.item

        # Item header
        elements.append(Paragraph(f"<b>Referencia:</b> {item.name}", styles["Normal"]))
        elements.append(
            Paragraph(f"<b>Descripción:</b> {item.description or ''}", styles["Normal"])
        )
        elements.append(Spacer(1, 0.1 * inch))

        # If there are properties, show them in a table
        if rem_item.property_quantities:
            headers = ["Propiedad", "Cantidad"]
            data = [headers]

            for prop_qty in rem_item.property_quantities:
                data.append([prop_qty.item_property.name, str(prop_qty.quantity)])

            data.append(["TOTAL", f"{rem_item.total_quantity}"])

            table = Table(data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
                        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
                    ]
                )
            )
            elements.append(table)
        else:
            # Without properties, just show total quantity
            elements.append(
                Paragraph(
                    f"<b>Cantidad Total:</b> {rem_item.total_quantity}",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 0.3 * inch))

    # Signature section
    elements.append(Spacer(1, 0.5 * inch))
    signature_data = [
        ["Entregó:", "Recibió:"],
        ["", ""],
        ["", ""],
        [f"{user.name}", f"{associate.name}"],
        [f"CC: {user.id_number}", f"CC: {associate.id_number or ''}"],
    ]

    sig_table = Table(signature_data, colWidths=[3 * inch, 3 * inch])
    sig_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("LINEABOVE", (0, 2), (-1, 2), 1, colors.black),
                ("TOPPADDING", (0, 2), (-1, 2), 20),
            ]
        )
    )
    elements.append(sig_table)

    # Emmiter info
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(f"{user.name}", styles["Normal"]))
    elements.append(Paragraph(f"CC: {user.id_number}", styles["Normal"]))
    elements.append(Paragraph(f"{user.address or ''}", styles["Normal"]))
    elements.append(Paragraph(f"Teléfono: {user.phone or ''}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer
