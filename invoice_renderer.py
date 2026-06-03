from pathlib import Path

from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from amount_to_words import amount_to_words

DARK_BLUE = HexColor('#1F497D')
HEADER_BG = HexColor('#BDD7EE')
AMOUNT_PAYABLE_BG = HexColor('#DEEAF1')

PAGE_W = A4[0]
L_MARGIN = R_MARGIN = 20 * mm
USABLE_W = PAGE_W - L_MARGIN - R_MARGIN  # ≈ 170 mm


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def _style(name, **kwargs):
    defaults = dict(fontName='Helvetica', fontSize=10, leading=14)
    defaults.update(kwargs)
    return ParagraphStyle(name, **defaults)


S = {
    'payee_name': _style('payee_name', fontName='Helvetica-Bold', fontSize=16,
                         textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=2),
    'payee_sub': _style('payee_sub', alignment=TA_CENTER, spaceAfter=2),
    'payee_pan': _style('payee_pan', fontName='Helvetica-Oblique',
                        alignment=TA_CENTER, spaceAfter=4),
    'inv_title': _style('inv_title', fontName='Helvetica-Bold', fontSize=13,
                        textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=6),
    'normal': _style('normal'),
    'bold': _style('bold', fontName='Helvetica-Bold'),
    'bill_name': _style('bill_name', fontName='Helvetica-Bold', fontSize=11, spaceAfter=1),
    'bill_line': _style('bill_line', spaceAfter=1),
    'tbl_hdr': _style('tbl_hdr', fontName='Helvetica-Bold', alignment=TA_CENTER),
    'tbl_hdr_r': _style('tbl_hdr_r', fontName='Helvetica-Bold', alignment=TA_RIGHT),
    'tbl_r': _style('tbl_r', alignment=TA_RIGHT),
    'total_lbl': _style('total_lbl', fontName='Helvetica-Bold', alignment=TA_RIGHT),
    'ap_lbl': _style('ap_lbl', fontName='Helvetica-Bold', alignment=TA_RIGHT, textColor=DARK_BLUE),
    'ap_val': _style('ap_val', fontName='Helvetica-Bold', alignment=TA_RIGHT, textColor=DARK_BLUE),
    'words_label': _style('words_label', fontName='Helvetica-Bold'),
    'words_italic': _style('words_italic', fontName='Helvetica-Oblique'),
    'note': _style('note', fontName='Helvetica-Oblique', fontSize=8, textColor=HexColor('#555555')),
    'section': _style('section', fontName='Helvetica-Bold', spaceAfter=4),
    'bank_key': _style('bank_key', fontName='Helvetica-Bold'),
    'bank_val': _style('bank_val'),
    'sig_name': _style('sig_name', fontName='Helvetica-Bold', fontSize=11,
                       textColor=DARK_BLUE, alignment=TA_RIGHT, spaceAfter=1),
    'sig_auth': _style('sig_auth', fontName='Helvetica-Oblique', alignment=TA_RIGHT, spaceAfter=2),
    'footer': _style('footer', fontName='Helvetica-Oblique', fontSize=8,
                     textColor=HexColor('#444444'), alignment=TA_CENTER),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(value, decimals=2):
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value or '')


def _fmt_date(value):
    if hasattr(value, 'strftime'):
        return value.strftime('%d-%b-%Y')
    return str(value or '')


def _p(text, style):
    return Paragraph(str(text or ''), style)


def _table(data, col_widths, style_cmds):
    t = Table(data, colWidths=[w * mm for w in col_widths])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, black),
    ] + style_cmds))
    return t


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def build_invoice_pdf(data, output_path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(_p(data['Payee Name'], S['payee_name']))
    story.append(_p(data['Payee Address'], S['payee_sub']))
    story.append(_p(f"PAN: {data['Payee PAN']}", S['payee_pan']))
    story.append(HRFlowable(width='100%', thickness=1, color=black, spaceAfter=4))

    expense = str(data['Expense Nature'] or 'Consultancy').strip().title()
    story.append(_p(f"{expense.upper()} INVOICE", S['inv_title']))

    # ── Info grid ───────────────────────────────────────────────────────────
    # colWidths: label | value | label | value  (total = 170 mm)
    info_rows = [
        [_p('<b>Invoice No.</b>', S['normal']), _p(data['Invoice No.'], S['normal']),
         _p('<b>Date</b>', S['normal']), _p(_fmt_date(data['Invoice Date']), S['normal'])],
        [_p('<b>Period</b>', S['normal']), _p(data['Period'], S['normal']),
         _p('<b>Place of Supply</b>', S['normal']), _p(data['Payor Address'], S['normal'])],
    ]
    story.append(_table(info_rows, [35, 55, 40, 40], []))
    story.append(Spacer(1, 6))

    # ── Bill To ─────────────────────────────────────────────────────────────
    story.append(_p('Bill To:', S['bill_line']))
    story.append(_p(data['Payor Name'], S['bill_name']))
    story.append(_p(data['Payor Address'], S['bill_line']))
    story.append(_p(f"PAN: {data['Payor PAN']}", S['bill_line']))
    story.append(Spacer(1, 6))

    # ── Services table ──────────────────────────────────────────────────────
    gross = float(data['Gross Amount'] or 0)
    gross_str = f"{gross:,.2f}"
    rs_gross = f"Rs. {gross_str}"

    # Description: use custom column if available, else auto-generate
    description = str(data.get('Description') or '').strip()
    if not description:
        description = f"{expense} services rendered for the period {data['Period']}"

    svc_rows = [
        # header
        [_p('<b>S.No.</b>', S['tbl_hdr']),
         _p('<b>Description of Services</b>', S['tbl_hdr']),
         _p('<b>Amount (Rs.)</b>', S['tbl_hdr_r'])],
        # data row
        [_p('1', S['normal']), _p(description, S['normal']), _p(gross_str, S['tbl_r'])],
        # Total Amount
        [_p('Total Amount', S['total_lbl']), '', _p(rs_gross, S['tbl_r'])],
        # Amount Payable
        [_p('Amount Payable', S['ap_lbl']), '', _p(rs_gross, S['ap_val'])],
    ]

    svc_table = _table(svc_rows, [20, 110, 40], [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('BACKGROUND', (0, 3), (-1, 3), AMOUNT_PAYABLE_BG),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ])
    story.append(svc_table)
    story.append(Spacer(1, 6))

    # ── Amount in words ─────────────────────────────────────────────────────
    words = amount_to_words(gross)
    story.append(Paragraph(
        f'<b>Amount in Words:</b> <i>{words}</i>',
        S['normal'],
    ))
    story.append(Paragraph(
        'Note: TDS to be deducted by the payer, if applicable, as per the relevant '
        'provisions of the Income Tax Act, 1961.',
        S['note'],
    ))
    story.append(Spacer(1, 6))

    # ── Bank Details ────────────────────────────────────────────────────────
    story.append(_p('<b>Bank Details for Payment:</b>', S['section']))
    bank_rows = [
        [_p('Account Holder', S['bank_key']), _p(data['Payee Name'], S['bank_val'])],
        [_p('Bank Name', S['bank_key']), _p(data['Payee Bank Name'], S['bank_val'])],
        [_p('Account Number', S['bank_key']), _p(data['Payee Bank A/c No.'], S['bank_val'])],
        [_p('IFSC Code', S['bank_key']), _p(data['Payee IFSC'], S['bank_val'])],
    ]
    story.append(_table(bank_rows, [50, 120], []))
    story.append(Spacer(1, 10))

    # ── Signature ────────────────────────────────────────────────────────────
    story.append(_p(f"For {data['Payee Name']}", S['sig_name']))
    story.append(_p('(Authorised Signatory)', S['sig_auth']))
    story.append(Spacer(1, 8))

    # ── Footer ───────────────────────────────────────────────────────────────
    footer_row = [[_p(
        'This is a system-generated invoice. No physical signature is required '
        'as per the Information Technology Act, 2000.',
        S['footer'],
    )]]
    footer_t = Table(footer_row, colWidths=[USABLE_W])
    footer_t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(footer_t)

    doc.build(story)
