#!/usr/bin/env python3
"""Build 100x100mm EU product labels with vector-drawn EAN-13 barcodes.

Usage:
    python3 build_labels.py --product product.json --qr-url <declaration-url> \\
        --ce ce-mark.png --outdir ./out

product.json schema: see product.example.json next to this script.

Dependencies: pip install reportlab qrcode pillow
A font covering Romanian/Bulgarian/Hungarian diacritics is required;
DejaVu Sans is used by default (present on most Linux systems).
"""
import argparse
import json
import os
import sys

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import qrcode

# ---------------------------------------------------------------- EAN-13 ---
L = {'0': '0001101', '1': '0011001', '2': '0010011', '3': '0111101', '4': '0100011',
     '5': '0110001', '6': '0101111', '7': '0111011', '8': '0110111', '9': '0001011'}
G = {'0': '0100111', '1': '0110011', '2': '0011011', '3': '0100001', '4': '0011101',
     '5': '0111001', '6': '0000101', '7': '0010001', '8': '0001001', '9': '0010111'}
R = {'0': '1110010', '1': '1100110', '2': '1101100', '3': '1000010', '4': '1011100',
     '5': '1001110', '6': '1010000', '7': '1000100', '8': '1001000', '9': '1110100'}
PARITY = {'0': 'LLLLLL', '1': 'LLGLGG', '2': 'LLGGLG', '3': 'LLGGGL', '4': 'LGLLGG',
          '5': 'LGGLLG', '6': 'LGGGLL', '7': 'LGLGLG', '8': 'LGLGGL', '9': 'LGGLGL'}


def ean13_modules(ean):
    if not (len(ean) == 13 and ean.isdigit()):
        raise ValueError(f"not a 13-digit EAN: {ean}")
    s = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(ean[:12]))
    if (10 - s % 10) % 10 != int(ean[12]):
        raise ValueError(f"bad EAN-13 check digit: {ean}")
    pat = '101'
    for i, d in enumerate(ean[1:7]):
        pat += (L if PARITY[ean[0]][i] == 'L' else G)[d]
    pat += '01010'
    for d in ean[7:]:
        pat += R[d]
    pat += '101'
    assert len(pat) == 95
    return pat


def draw_ean13(c, ean, x, y, width, bar_h=11 * mm, guard_extra=2.2 * mm, num_size=7):
    """Draw a vector EAN-13. x,y = bottom-left of the quiet-zone box."""
    qz = 9
    mw = width / (95 + 2 * qz)
    num_gap = num_size * 0.55 * mm + 1 * mm
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, y, width, bar_h + guard_extra + num_gap, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    pat = ean13_modules(ean)
    bx = x + qz * mw
    for i, b in enumerate(pat):
        guard = i < 3 or (43 <= i < 48) or i >= 92
        h = bar_h + (guard_extra if guard else 0)
        if b == '1':
            c.rect(bx + i * mw, y + num_gap, mw + 0.15, h, stroke=0, fill=1)
    c.setFont('DVS', num_size)
    c.drawCentredString(x + width / 2, y, ean)


def selftest(eans):
    revL = {v: k for k, v in L.items()}
    revG = {v: k for k, v in G.items()}
    revR = {v: k for k, v in R.items()}
    for ean in eans:
        pat = ean13_modules(ean)
        assert pat[:3] == '101' and pat[45:50] == '01010' and pat[-3:] == '101'
        left, right = pat[3:45], pat[50:92]
        parity, digits = '', ''
        for i in range(6):
            seg = left[i * 7:(i + 1) * 7]
            if seg in revL:
                parity += 'L'; digits += revL[seg]
            else:
                parity += 'G'; digits += revG[seg]
        first = [k for k, v in PARITY.items() if v == parity][0]
        digits = first + digits + ''.join(revR[right[i * 7:(i + 1) * 7]] for i in range(6))
        assert digits == ean, f"roundtrip failed: {digits} != {ean}"
        print(f"  {ean}: barcode encode/decode roundtrip OK", file=sys.stderr)


# ---------------------------------------------------------------- layout ---
W = H = 100 * mm
M = 3 * mm
FS = 6.5
LD = 8.0


def wrap_lines(c, text, maxw, font='DVS', size=FS):
    c.setFont(font, size)
    words, lines, cur = text.split(' '), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines


def tri(lang_dict):
    return f"{lang_dict['ro']} / {lang_dict['bg']} / {lang_dict['hu']}"


def build_one(cfg, variant, qr_path, ce_path, fc_path, out):
    ean = variant['ean']
    c = canvas.Canvas(out, pagesize=(W, H))
    lx, rx = M + 2.2 * mm, W - M - 2.2 * mm
    maxw = rx - lx
    col = variant['color']

    name = f"Product Name: {cfg['product']['name']['ro']} ({col['ro']})/{cfg['product']['name']['bg']} ({col['bg']})/{cfg['product']['name']['hu']} ({col['hu']})"
    mat = f"Product Material: {tri(cfg['product']['material'])}"
    batch = f"Batch Number: {variant.get('batch_number', ean)}"
    use = f"Product Usage: {tri(cfg['product']['usage'])}"
    prod = wrap_lines(c, name, maxw) + wrap_lines(c, mat, maxw) + wrap_lines(c, batch, maxw) + wrap_lines(c, use, maxw)

    mfr = cfg['manufacturer']
    man = (wrap_lines(c, f"Manufacturer: {mfr['name']}", maxw) +
           wrap_lines(c, f"Address: {mfr['address']}", maxw) +
           wrap_lines(c, f"E-mail: {mfr['email']}", maxw))

    safety = wrap_lines(c, tri(cfg['product']['safety']), maxw)

    eurep_h, bot_h = 14 * mm, 24 * mm
    gap = 1.2 * mm
    prod_h = len(prod) * LD + 3 * 1.0 * mm
    man_h = len(man) * LD
    safety_h = len(safety) * LD + 2 * mm
    total = prod_h + gap + man_h + gap + eurep_h + gap + safety_h + bot_h
    avail = H - 2 * M - 2 * mm
    if total > avail:
        raise RuntimeError(f"content overflow: {total/mm:.1f}mm > {avail/mm:.1f}mm — shorten texts")

    y = H - M - 1.5 * mm
    prod_top = y
    y -= prod_h + gap; man_top = y
    y -= man_h + gap; eurep_top = y
    y -= eurep_h + gap; safety_top = y
    y -= safety_h; bot_div = y

    c.setLineWidth(0.7)
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(M, M, W - 2 * M, H - 2 * M)
    for yy in [bot_div, safety_top - safety_h, eurep_top - eurep_h, man_top - man_h]:
        c.line(M, yy, W - M, yy)

    # bottom row: vector barcode | CE [+ food-contact] | QR
    fc_on = bool(fc_path and os.path.exists(fc_path))
    bc_w = 41 * mm if fc_on else 44 * mm
    draw_ean13(c, ean, lx, 5 * mm, bc_w)
    from PIL import Image as PILImage
    marks = []
    if ce_path and os.path.exists(ce_path):
        iw, ih = PILImage.open(ce_path).size
        marks.append((ce_path, iw / ih))
    if fc_on:
        iw, ih = PILImage.open(fc_path).size
        marks.append((fc_path, iw / ih))
    zone_x0, zone_x1 = lx + bc_w, rx - 18 * mm
    if marks:
        gap = 2 * mm if len(marks) > 1 else 0
        avail_w = (zone_x1 - zone_x0) - 2 * mm
        h = min(13 * mm, (avail_w - gap * (len(marks) - 1)) / sum(a for _, a in marks))
        total_w = sum(h * a for _, a in marks) + gap * (len(marks) - 1)
        x = zone_x0 + ((zone_x1 - zone_x0) - total_w) / 2
        for path, aspect in marks:
            w = h * aspect
            c.drawImage(ImageReader(path), x, 5 * mm + (18 * mm - h) / 2,
                        width=w, height=h, preserveAspectRatio=True, anchor='c', mask='auto')
            x += w + gap
    else:
        c.setFont('DVSB', 13); c.setFillColorRGB(0, 0, 0)
        c.drawCentredString((zone_x0 + zone_x1) / 2, 10.5 * mm, "CE")
    c.drawImage(ImageReader(qr_path), rx - 18 * mm, 5 * mm, width=18 * mm, height=18 * mm)

    yy = safety_top - 1.5 * mm
    for ln in safety:
        c.setFont('DVS', FS); c.drawString(lx, yy, ln); yy -= LD

    er = cfg['eu_rep']
    et = eurep_top - 2 * mm
    bx, bh = lx, et - 9 * mm
    c.setLineWidth(1.1)
    c.rect(bx, bh, 13 * mm, 9 * mm); c.rect(bx + 13 * mm, bh, 17 * mm, 9 * mm)
    c.setFont('DVSB', 10)
    c.drawCentredString(bx + 6.5 * mm, bh + 2.5 * mm, "EU")
    c.drawCentredString(bx + 21.5 * mm, bh + 2.5 * mm, "REP")
    c.setLineWidth(0.7)
    tx = bx + 32 * mm
    er_lines = ([(l, 'DVSB') for l in wrap_lines(c, er['name'], rx - tx, font='DVSB')] +
                [(l, 'DVS') for l in wrap_lines(c, f"Address: {er['address']}", rx - tx)] +
                [(l, 'DVS') for l in wrap_lines(c, f"E-mail: {er['email']}, Tel: {er['tel']}", rx - tx)])
    yy = et
    for ln, f in er_lines:
        c.setFont(f, FS); c.drawString(tx, yy, ln); yy -= LD

    yy = man_top - 1.5 * mm
    for ln in man:
        c.setFont('DVS', FS); c.drawString(lx, yy, ln); yy -= LD

    yy = prod_top
    for fl in [wrap_lines(c, name, maxw), wrap_lines(c, mat, maxw),
               wrap_lines(c, batch, maxw), wrap_lines(c, use, maxw)]:
        for ln in fl:
            c.setFont('DVS', FS); c.drawString(lx, yy, ln); yy -= LD
        yy -= 1.0 * mm

    c.showPage(); c.save()
    print(f"built: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--product', required=True, help='product.json (see product.example.json)')
    ap.add_argument('--qr-url', required=True, help='long-lasting URL of the hosted declaration')
    ap.add_argument('--ce', default='', help='official CE mark image (PNG); text fallback if missing')
    ap.add_argument('--food-contact', default='',
                    help='food-contact symbol PNG (enables the mark); when empty, product.json "food_contact": true uses the bundled assets/food-contact.png')
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--font', default='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    ap.add_argument('--font-bold', default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    args = ap.parse_args()

    pdfmetrics.registerFont(TTFont('DVS', args.font))
    pdfmetrics.registerFont(TTFont('DVSB', args.font_bold))

    with open(args.product, encoding='utf-8') as f:
        cfg = json.load(f)

    os.makedirs(args.outdir, exist_ok=True)
    qr_path = os.path.join(args.outdir, '_qr.png')
    qr = qrcode.QRCode(box_size=12, border=2)
    qr.add_data(args.qr_url); qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(qr_path)

    selftest([v['ean'] for v in cfg['variants']])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    bundled_fc = os.path.join(script_dir, '..', 'assets', 'food-contact.png')
    if args.food_contact:
        fc_path = args.food_contact
    elif cfg.get('food_contact'):
        fc_path = bundled_fc
    else:
        fc_path = None

    for v in cfg['variants']:
        build_one(cfg, v, qr_path, args.ce, fc_path, os.path.join(args.outdir, v['output']))


if __name__ == '__main__':
    main()
