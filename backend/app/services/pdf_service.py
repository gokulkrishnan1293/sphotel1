"""Generate PDF report documents using reportlab."""
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


def _inr(paise: int) -> str:
    return f"\u20b9{paise / 100:,.0f}"


def _table(rows: list[list[str]]) -> Table:
    col_w = [(A4[0] - 40 * mm) / len(rows[0])] * len(rows[0])
    t = Table(rows, colWidths=col_w, hAlign='LEFT')
    t.setStyle(_TBL)
    return t


def generate_eod_pdf(summary: dict, tenant_name: str,
                     waiter_rows: list[dict] | None = None,
                     template_flags: dict | None = None) -> bytes:
    flags = template_flags or {}
    show_payment = flags.get("eod_show_payment", True)
    show_items = flags.get("eod_show_items", True)
    show_waiters = flags.get("eod_show_waiters", True)

    buf = io.BytesIO()
    doc = _doc(buf)
    now_ist = datetime.now(_IST).strftime('%d %b %Y, %I:%M %p IST')
    story = [
        Paragraph(f"EOD Report \u2014 {tenant_name}", _STYLES['Title']),
        Paragraph(f"{summary['date']}  \u00b7  Generated {now_ist}", _STYLES['Normal']),
        Spacer(1, 10),
        _table([['Bills', 'Revenue', 'Avg Bill', 'Discounts', 'Voids'],
                [str(summary['bill_count']), _inr(summary['total_paise']),
                 _inr(summary['avg_paise']), _inr(summary['discount_paise']),
                 str(summary['void_count'])]]),
        Spacer(1, 10),
    ]
    if show_payment and summary.get('payment_breakdown'):
        pb = summary['payment_breakdown']
        total = sum(pb.values())
        rows = [['Method', 'Amount', '%']]
        for m, a in pb.items():
            pct = f"{a / total * 100:.0f}%" if total else '-'
            rows.append([m.capitalize(), _inr(a), pct])
        rows.append(['Total', _inr(total), '100%'])
        story += [Paragraph('Payment Breakdown', _STYLES['Heading2']),
                  Spacer(1, 4), _table(rows), Spacer(1, 10)]
    if show_items and summary.get('top_items'):
        rows = [['Item', 'Qty']] + [[i['name'], str(i['qty'])] for i in summary['top_items']]
        story += [Paragraph('Items Sold', _STYLES['Heading2']),
                  Spacer(1, 4), _table(rows), Spacer(1, 10)]
    if show_waiters and waiter_rows:
        rows = [['Waiter', 'Bills', 'Revenue']] + \
               [[w['waiter_name'], str(w['bill_count']), _inr(w['revenue_paise'])]
                for w in waiter_rows]
        story += [Paragraph('Waiter Performance', _STYLES['Heading2']),
                  Spacer(1, 4), _table(rows)]
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
        Paragraph(f"{dimension} \u00b7 {metric} \u00b7 {period}  \u00b7  Generated {now_ist}", _STYLES['Normal']),
        Spacer(1, 10),
        _table(data_rows),
    ]
    doc.build(story)
    return buf.getvalue()
