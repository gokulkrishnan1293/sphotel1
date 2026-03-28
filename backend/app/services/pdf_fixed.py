"""PDF generators for fixed report card types."""
from __future__ import annotations

import io
from datetime import datetime, timezone, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

_IST = timezone(timedelta(hours=5, minutes=30))
_STYLES = getSampleStyleSheet()
_TBL = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f7f7')]),
    ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dddddd')),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
])


def _doc(buf: io.BytesIO) -> SimpleDocTemplate:
    return SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=20 * mm, rightMargin=20 * mm,
                             topMargin=20 * mm, bottomMargin=20 * mm)


def _tbl(rows: list[list[str]]) -> Table:
    col_w = [(A4[0] - 40 * mm) / len(rows[0])] * len(rows[0])
    t = Table(rows, colWidths=col_w, hAlign='LEFT')
    t.setStyle(_TBL)
    return t


def _inr(paise: int) -> str:
    return f"\u20b9{paise / 100:,.0f}"


def _ts() -> str:
    return datetime.now(_IST).strftime('%d %b %Y, %I:%M %p IST')


def generate_top_items_pdf(items: list[dict], tenant_name: str) -> bytes:
    buf = io.BytesIO()
    doc = _doc(buf)
    rows = [['Item', 'Qty']] + [[i['name'], str(i['qty'])] for i in items]
    story = [
        Paragraph(f"Top Items — {tenant_name}", _STYLES['Title']),
        Paragraph(f"Generated {_ts()}", _STYLES['Normal']),
        Spacer(1, 10),
        _tbl(rows) if len(rows) > 1 else Paragraph("No data", _STYLES['Normal']),
    ]
    doc.build(story)
    return buf.getvalue()


def generate_payment_pdf(breakdown: dict, tenant_name: str) -> bytes:
    buf = io.BytesIO()
    doc = _doc(buf)
    total = sum(breakdown.values())
    rows = [['Method', 'Amount', '%']]
    for m, a in breakdown.items():
        rows.append([m.capitalize(), _inr(a), f"{a / total * 100:.0f}%" if total else '-'])
    rows.append(['Total', _inr(total), '100%'])
    story = [
        Paragraph(f"Payment Breakdown — {tenant_name}", _STYLES['Title']),
        Paragraph(f"Generated {_ts()}", _STYLES['Normal']),
        Spacer(1, 10),
        _tbl(rows) if len(rows) > 1 else Paragraph("No data", _STYLES['Normal']),
    ]
    doc.build(story)
    return buf.getvalue()


def generate_waiter_pdf(rows: list[dict], tenant_name: str, days: int) -> bytes:
    buf = io.BytesIO()
    doc = _doc(buf)
    data = [['Waiter', 'Bills', 'Revenue']] + [
        [r['waiter_name'], str(r['bill_count']), _inr(r['revenue_paise'])] for r in rows
    ]
    story = [
        Paragraph(f"Waiter Performance — {tenant_name}", _STYLES['Title']),
        Paragraph(f"Last {days} days  ·  Generated {_ts()}", _STYLES['Normal']),
        Spacer(1, 10),
        _tbl(data) if len(data) > 1 else Paragraph("No data", _STYLES['Normal']),
    ]
    doc.build(story)
    return buf.getvalue()
