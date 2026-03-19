export interface PreviewRow { label: string; value: string }
export interface PreviewSection { title: string; rows: PreviewRow[] }

export function openPdfPreview(reportTitle: string, period: string, sections: PreviewSection[]) {
  const now = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
  const sectionHtml = sections.map((s) => `
    <div class="section">
      <div class="section-title">${s.title}</div>
      <table>
        ${s.rows.map((r) => `<tr class="${r.label.toLowerCase() === 'total' ? 'total-row' : ''}">
          <td>${r.label}</td><td>${r.value}</td>
        </tr>`).join('')}
      </table>
    </div>`).join('')

  const html = `<!DOCTYPE html><html><head>
<meta charset="utf-8"><title>${reportTitle}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 32px 40px; color: #111; font-size: 13px; line-height: 1.5; }
  .header { border-bottom: 3px solid #111; padding-bottom: 12px; margin-bottom: 20px; }
  h1 { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }
  .meta { color: #555; font-size: 12px; margin-top: 4px; }
  .section { margin-bottom: 18px; }
  .section-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #555; margin-bottom: 6px; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: 6px 10px; border-bottom: 1px solid #eee; }
  td:first-child { color: #333; }
  td:last-child { text-align: right; font-weight: 600; }
  .total-row td { font-weight: 800; background: #f5f5f5; border-top: 2px solid #ccc; }
  .footer { margin-top: 24px; color: #aaa; font-size: 11px; border-top: 1px solid #eee; padding-top: 10px; }
  @media print { body { padding: 20px; } button { display: none !important; } }
</style>
</head><body>
<div class="header">
  <h1>${reportTitle}</h1>
  <div class="meta">Period: ${period} &nbsp;·&nbsp; Generated: ${now} IST</div>
</div>
${sectionHtml}
<div class="footer">sphotel &nbsp;·&nbsp; Automated report</div>
<br>
<button onclick="window.print()" style="background:#111;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-size:13px;cursor:pointer;">Print / Save as PDF</button>
</body></html>`

  const w = window.open('', '_blank', 'width=720,height=900')
  if (!w) return
  w.document.write(html)
  w.document.close()
}
