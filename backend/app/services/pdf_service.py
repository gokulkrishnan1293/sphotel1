"""Generate PDF report documents using reportlab."""
from __future__ import annotations

import io
from datetime import datetime, timezone, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_IST = timezone(timedelta(hours=5, minutes=30))
_STYLES = getSampleStyleSheet()

_TBL = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
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


def _inr(paise: int) -> str:
    return f"\u20b9{paise / 100:,.0f}"


def _table(rows: list[list[str]]) -> Table:
    col_w = [(A4[0] - 40 * mm) / len(rows[0])] * len(rows[0])
    t = Table(rows, colWidths=col_w, hAlign='LEFT')
    t.setStyle(_TBL)
    return t


def generate_eod_pdf(summary: dict, tenant_name: str) -> bytes:
    buf = io.BytesIO()
    doc = _doc(buf)
    now_ist = datetime.now(_IST).strftime('%d %b %Y, %I:%M %p IST')
    story = [
        Paragraph(f"EOD Report — {tenant_name}", _STYLES['Title']),
        Paragraph(f"{summary['date']}  ·  Generated {now_ist}", _STYLES['Normal']),
        Spacer(1, 10),
        _table([['Bills', 'Revenue', 'Avg Bill'],
                [str(summary['bill_count']), _inr(summary['total_paise']), _inr(summary['avg_paise'])]]),
        Spacer(1, 10),
    ]
    if summary.get('payment_breakdown'):
        pb = summary['payment_breakdown']
        total = sum(pb.values())
        rows = [['Method', 'Amount', '%']]
        for m, a in pb.items():
            rows.append([m.capitalize(), _inr(a), f"{a / total * 100:.0f}%" if total else '-'])
        rows.append(['Total', _inr(total), '100%'])
        story += [Paragraph('Payment Breakdown', _STYLES['Heading2']), Spacer(1, 4), _table(rows), Spacer(1, 10)]
    if summary.get('top_items'):
        rows = [['Item', 'Qty']] + [[i['name'], str(i['qty'])] for i in summary['top_items']]
        story += [Paragraph('Top Items', _STYLES['Heading2']), Spacer(1, 4), _table(rows)]
    doc.build(story)
    return buf.getvalue()


def generate_custom_report_pdf(name: str, period: str, dimension: str, metric: str,
                                rows: list[dict]) -> bytes:
    buf = io.BytesIO()
    doc = _doc(buf)
    now_ist = datetime.now(_IST).strftime('%d %b %Y, %I:%M %p IST')
    data_rows = [['Label', 'Value']] + [[r['label'], str(r['value'])] for r in rows]
    story = [
        Paragraph(name, _STYLES['Title']),
        Paragraph(f"{dimension} · {metric} · {period}  ·  Generated {now_ist}", _STYLES['Normal']),
        Spacer(1, 10),
        _table(data_rows),
    ]
    doc.build(story)
    return buf.getvalue()
