from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_invoice_pdf(invoice, user, associate) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
    )
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#000000"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    header_style = ParagraphStyle(
        "Header", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER
    )

    # Header
    elements.append(Paragraph("FORMATO CUENTA DE COBRO", title_style))
    elements.append(Paragraph(f"{invoice.date.strftime('%d %B %Y')}", header_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Account Number
    elements.append(
        Paragraph(f"<b>Cuenta de cobro {invoice.consecutive}</b>", styles["Heading2"])
    )
    elements.append(Spacer(1, 0.2 * inch))

    # Who is charging
    elements.append(Paragraph(f"<b>{associate.name}</b>", styles["Normal"]))
    elements.append(Paragraph(f"NIT/CC: {associate.id_number}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    # Who is being charged
    elements.append(Paragraph("<b>DEBE A</b>", styles["Normal"]))
    elements.append(Paragraph(f"{user.name}", styles["Normal"]))
    elements.append(Paragraph(f"CC/NIT: {user.id_number}", styles["Normal"]))
    elements.append(Paragraph(f"{user.address or ''}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    # Total
    elements.append(Paragraph("<b>LA SUMA DE</b>", styles["Normal"]))
    elements.append(Paragraph(f"{invoice.total_text}", styles["Normal"]))
    elements.append(Paragraph(f"<b>${invoice.total:,.0f}</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Items
    elements.append(Paragraph("<b>Por concepto de:</b>", styles["Normal"]))
    elements.append(Spacer(1, 0.1 * inch))

    data = [["Descripción", "Cantidad", "Precio Unit.", "Subtotal"]]
    for item in invoice.items:
        data.append(
            [
                item.item.name,
                str(item.quantity),
                f"${item.unit_price:,.0f}",
                f"${item.subtotal:,.0f}",
            ]
        )

    table = Table(data, colWidths=[3 * inch, 1 * inch, 1.2 * inch, 1.2 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # Signature
    elements.append(Paragraph("Cordialmente,", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"<b>{user.name}</b>", styles["Normal"]))
    elements.append(Paragraph(f"C.C. {user.id_number}", styles["Normal"]))
    elements.append(Paragraph(f"Teléfono: {user.phone or ''}", styles["Normal"]))
    elements.append(Paragraph(f"Dirección: {user.address or ''}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer
