# apps/finance/invoice_pdf.py
import io
from decimal import Decimal
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT


BRAND_BLUE  = colors.HexColor('#1e40af')
BRAND_LIGHT = colors.HexColor('#eff6ff')
GRAY        = colors.HexColor('#64748b')
DARK        = colors.HexColor('#0f172a')
GREEN       = colors.HexColor('#16a34a')


def generate_invoice_pdf(invoice) -> bytes:
    """Generate a KRA-compliant PDF invoice. Returns bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Header ────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph('<b><font size=20 color="#1e40af">TeralinkX</font></b><br/>'
                  '<font size=9 color="#64748b">ISP Management Platform</font><br/>'
                  '<font size=8 color="#64748b">Nairobi, Kenya | info@teralinkxwaves.uk</font>', styles['Normal']),
        Paragraph(
            f'<b><font size=22 color="#0f172a">TAX INVOICE</font></b><br/>'
            f'<font size=10 color="#64748b">{invoice.invoice_number}</font>',
            ParagraphStyle('right', parent=styles['Normal'], alignment=TA_RIGHT)
        )
    ]]
    header_table = Table(header_data, colWidths=[95*mm, 85*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width='100%', thickness=2, color=BRAND_BLUE, spaceAfter=6))

    # ── Invoice meta + Bill To ─────────────────────────────────────────────────
    customer = invoice.customer
    name = customer.display_name or customer.user.get_full_name() or customer.account

    meta_data = [[
        Paragraph(
            f'<b>Bill To:</b><br/>'
            f'<b>{name}</b><br/>'
            f'Account: {customer.account}<br/>'
            f'Phone: {customer.phone_number or "—"}<br/>'
            f'Email: {customer.user.email or "—"}',
            styles['Normal']
        ),
        Paragraph(
            f'<b>Invoice Date:</b> {invoice.issue_date.strftime("%d %b %Y")}<br/>'
            f'<b>Due Date:</b> {invoice.due_date.strftime("%d %b %Y") if invoice.due_date else "Immediate"}<br/>'
            f'<b>Status:</b> <font color="#16a34a"><b>{invoice.status.upper()}</b></font><br/>'
            f'<b>Payment Ref:</b> {invoice.transaction_id_ref or "—"}',
            ParagraphStyle('right', parent=styles['Normal'], alignment=TA_RIGHT)
        )
    ]]
    meta_table = Table(meta_data, colWidths=[95*mm, 85*mm])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)

    # ── Line Items Table ───────────────────────────────────────────────────────
    col_headers = ['Description', 'Qty', 'Unit Price (KES)', 'VAT (16%)', 'Total (KES)']
    rows = [col_headers]

    for item in invoice.line_items:
        rows.append([
            item.get('description', 'Internet Service'),
            str(item.get('quantity', 1)),
            f"{item.get('unit_price', 0):,.2f}",
            f"{item.get('vat_amount', 0):,.2f}",
            f"{item.get('total', 0):,.2f}",
        ])

    items_table = Table(rows, colWidths=[75*mm, 15*mm, 35*mm, 30*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), BRAND_BLUE),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,0), 9),
        ('ALIGN',        (1,0), (-1,-1), 'RIGHT'),
        ('ALIGN',        (0,0), (0,-1), 'LEFT'),
        ('FONTSIZE',     (0,1), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BRAND_LIGHT]),
        ('GRID',         (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 6))

    # ── Totals ─────────────────────────────────────────────────────────────────
    totals_data = [
        ['', 'Subtotal (excl. VAT):', f'KES {invoice.subtotal:,.2f}'],
        ['', f'VAT ({invoice.vat_rate}%):', f'KES {invoice.vat_amount:,.2f}'],
        ['', 'TOTAL DUE:', f'KES {invoice.total:,.2f}'],
    ]
    totals_table = Table(totals_data, colWidths=[95*mm, 50*mm, 40*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN',        (1,0), (-1,-1), 'RIGHT'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('FONTNAME',     (1,2), (-1,2), 'Helvetica-Bold'),
        ('FONTSIZE',     (1,2), (-1,2), 11),
        ('TEXTCOLOR',    (1,2), (-1,2), BRAND_BLUE),
        ('LINEABOVE',    (1,2), (-1,2), 1, BRAND_BLUE),
        ('TOPPADDING',   (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0), (-1,-1), 3),
    ]))
    story.append(totals_table)
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e8f0'), spaceBefore=8, spaceAfter=8))

    # ── Footer ─────────────────────────────────────────────────────────────────
    footer_style = ParagraphStyle('footer', parent=styles['Normal'],
                                  fontSize=8, textColor=GRAY, alignment=TA_CENTER)
    story.append(Paragraph(
        'This is a computer-generated tax invoice. No signature required.<br/>'
        'TeralinkX Waves Ltd | PIN: P000000000X | VAT Reg: V000000000X<br/>'
        'For queries: billing@teralinkxwaves.uk | +254 700 000 000',
        footer_style
    ))

    doc.build(story)
    return buffer.getvalue()
