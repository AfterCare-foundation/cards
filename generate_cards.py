#!/usr/bin/env python3
"""
AfterCare card generator.

One HTML file = one A4 sheet (front page + back page).
Raw tokens are written only into the QR codes, never into a manifest
or the terminal. Delete the HTML files after printing.

SETUP:  pip3 install 'qrcode[pil]' Pillow
USAGE:  python3 generate_cards.py --count 20 --domain after-care.eu
"""

import argparse
import base64
import io
import os
import secrets

try:
    import qrcode
except ImportError:
    print("Run: pip3 install 'qrcode[pil]' Pillow")
    raise SystemExit(1)


CARDS_PER_ROW = 2
ROWS_PER_SHEET = 4
CARDS_PER_SHEET = CARDS_PER_ROW * ROWS_PER_SHEET


def generate_token():
    # 16 random bytes, URL-safe, no padding. The app hashes those raw bytes.
    return secrets.token_urlsafe(16)


def token_to_url(token, domain):
    return f"https://{domain}/connect#et={token}"


def generate_qr_b64(url):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def card_pair_html(token, domain):
    b64 = generate_qr_b64(token_to_url(token, domain))
    return f'''<div class="card-pair">
      <span class="mark tl"></span><span class="mark tr"></span>
      <span class="mark bl"></span><span class="mark br"></span>
      <div class="card-half left">
        <div class="card-content">
          <div class="logo-row"><span class="logo-icon">♥</span><span class="brand">AfterCare</span></div>
          <div class="qr-wrap"><img src="data:image/png;base64,{b64}"></div>
        </div>
      </div>
      <div class="perf"><div class="perf-line"></div></div>
      <div class="card-half right">
        <div class="card-content">
          <div class="logo-row"><span class="logo-icon">♥</span><span class="brand">AfterCare</span></div>
          <div class="qr-wrap"><img src="data:image/png;base64,{b64}"></div>
        </div>
      </div>
    </div>'''


def dark_back_pair():
    return '''<div class="card-pair">
      <span class="mark tl"></span><span class="mark tr"></span>
      <span class="mark bl"></span><span class="mark br"></span>
      <div class="card-half left"></div>
      <div class="perf"><div class="perf-line"></div></div>
      <div class="card-half right"></div>
    </div>'''


def rows_html(rows, pair_html):
    html = ""
    for row in rows:
        pairs = "".join(pair_html(token) for token in row)
        html += f'<div class="card-row">{pairs}</div>\n'
    return html


def sheet_html(rows, domain, sheet_no, sheet_count):
    """Front page, then back page mirrored vertically for a short-edge flip."""
    front = rows_html(rows, lambda token: card_pair_html(token, domain))
    back = rows_html(list(reversed(rows)), lambda _token: dark_back_pair())
    cards_here = sum(len(row) for row in rows)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AfterCare sheet {sheet_no} of {sheet_count}</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
@page{{size:A4 portrait;margin:6mm}}
body{{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;background:#e8e8e8;}}
.page{{
  background:white;width:198mm;min-height:285mm;margin:0 auto 8mm;
  padding:4mm;position:relative;page-break-after:always;
}}
.header{{font-size:7px;color:#999;text-align:center;
  padding-bottom:3mm;margin-bottom:3mm;
  border-bottom:.5px solid #ddd;line-height:1.5;}}
.card-row{{display:flex;flex-direction:row;justify-content:center;gap:6mm;margin-bottom:6mm;}}
.card-pair{{
  display:flex;flex-direction:row;align-items:stretch;
  width:91mm;height:60mm;flex-shrink:0;position:relative;
}}
.card-half{{width:44mm;height:60mm;background:#1E1035;position:relative;overflow:hidden;flex-shrink:0;}}
.card-half.left{{border-radius:3mm 0 0 3mm;}}
.card-half.right{{border-radius:0 3mm 3mm 0;}}
.card-content{{
  position:absolute;inset:3mm;display:flex;flex-direction:column;
  align-items:center;justify-content:space-between;padding:1mm;
}}
.logo-row{{display:flex;align-items:center;gap:1.5mm;width:100%;}}
.logo-icon{{font-size:9px;color:#8B3FCC;line-height:1;}}
.brand{{font-size:6.5px;font-weight:700;color:#fff;letter-spacing:.4px;}}
.qr-wrap{{
  width:28mm;height:28mm;background:white;border-radius:1.5mm;
  display:flex;align-items:center;justify-content:center;padding:.5mm;flex-shrink:0;
}}
.qr-wrap img{{width:100%;height:100%;display:block;}}
.perf{{
  width:3mm;height:60mm;background:#1E1035;
  display:flex;align-items:center;justify-content:center;position:relative;flex-shrink:0;
}}
.perf-line{{
  position:absolute;top:0;bottom:0;left:50%;
  border-left:2px dotted rgba(255,255,255,0.65);transform:translateX(-50%);
}}
.mark{{position:absolute;width:3mm;height:3mm;}}
.mark.tl{{top:-3.5mm;left:-3.5mm;border-top:.25mm solid #111;border-left:.25mm solid #111;}}
.mark.tr{{top:-3.5mm;right:-3.5mm;border-top:.25mm solid #111;border-right:.25mm solid #111;}}
.mark.bl{{bottom:-3.5mm;left:-3.5mm;border-bottom:.25mm solid #111;border-left:.25mm solid #111;}}
.mark.br{{bottom:-3.5mm;right:-3.5mm;border-bottom:.25mm solid #111;border-right:.25mm solid #111;}}
@media print{{
  body{{background:white;}}
  .page{{margin:0;page-break-after:always;}}
  .card-pair,.card-row,.page{{page-break-inside:avoid;break-inside:avoid;}}
}}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <strong>AfterCare — front</strong> &nbsp;·&nbsp;
    Sheet {sheet_no} of {sheet_count} &nbsp;·&nbsp; {cards_here} cards &nbsp;·&nbsp; {domain}<br>
    100% scale &nbsp;·&nbsp; background graphics on &nbsp;·&nbsp; crop marks show the trim
  </div>
  {front}
</div>
<div class="page">
  <div class="header">
    <strong>AfterCare — back</strong> &nbsp;·&nbsp;
    Sheet {sheet_no} of {sheet_count}<br>
    Flip this sheet on the short edge (top to bottom), then print this page
  </div>
  {back}
</div>
</body>
</html>'''


def chunk_rows(tokens):
    rows = [tokens[i:i + CARDS_PER_ROW] for i in range(0, len(tokens), CARDS_PER_ROW)]
    return [rows[i:i + ROWS_PER_SHEET] for i in range(0, len(rows), ROWS_PER_SHEET)]


def clear_previous_sheets(out_dir):
    for name in os.listdir(out_dir):
        if name.startswith("sheet-") and name.endswith(".html"):
            os.remove(os.path.join(out_dir, name))


def main():
    parser = argparse.ArgumentParser(description="AfterCare card sheets. Tokens are not saved outside the QR codes.")
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--domain", type=str, default="after-care.eu")
    parser.add_argument("--output", type=str, default="aftercare-cards")
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    tokens = [generate_token() for _ in range(args.count)]
    sheets = chunk_rows(tokens)
    out_dir = os.path.abspath(args.output)
    os.makedirs(out_dir, exist_ok=True)
    clear_previous_sheets(out_dir)

    for index, rows in enumerate(sheets, start=1):
        path = os.path.join(out_dir, f"sheet-{index:03d}.html")
        html = sheet_html(rows, args.domain, index, len(sheets))
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(html)

    print(f"Wrote {len(sheets)} sheet(s), {args.count} card(s), to {out_dir}")
    print("Tokens are only inside the QR codes. Delete this folder after printing.")
    print("""
For each sheet-NNN.html:
  1. Open in Chrome — File → Print
  2. Background graphics: ON. Scale: 100%. Paper: A4 portrait
  3. Print page 1 (front)
  4. Flip that sheet on the short edge (top to bottom)
  5. Print page 2 (back)
  6. Cut on the crop marks and score the centre perforation
""")


if __name__ == "__main__":
    main()
