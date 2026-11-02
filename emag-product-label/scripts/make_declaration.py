#!/usr/bin/env python3
"""Generate an EU Declaration of Conformity (8-point template) as PDF.

Usage:
    python3 make_declaration.py --product product.json --out declaration.pdf

Reads product/manufacturer/eu_rep/declaration sections from product.json
(see product.example.json). The declaration follows the official EU
8-point DoC model.
"""
import argparse
import json
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--product', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--font', default='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    ap.add_argument('--font-bold', default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    args = ap.parse_args()

    pdfmetrics.registerFont(TTFont('DVS', args.font))
    pdfmetrics.registerFont(TTFont('DVSB', args.font_bold))
    st = ParagraphStyle('n', fontName='DVS', fontSize=10.5, leading=15)
    sth = ParagraphStyle('h', fontName='DVSB', fontSize=15, leading=20, alignment=1)

    with open(args.product, encoding='utf-8') as f:
        cfg = json.load(f)
    p, mfr, er, d = cfg['product'], cfg['manufacturer'], cfg['eu_rep'], cfg['declaration']

    ids = " — ".join(
        f"No. <b>{v['ean']}</b> ({v['color']['ro']} / {v['color']['en']}, seller ref. {v['seller_ref']})"
        for v in cfg['variants'])

    story = [
        Paragraph("EU DECLARATION OF CONFORMITY", sth),
        Spacer(1, 8 * mm),
        Paragraph(f"1.&nbsp;&nbsp;&nbsp;&nbsp;{ids} — unique identification of the product.", st),
        Spacer(1, 4 * mm),
        Paragraph(f"2.&nbsp;&nbsp;&nbsp;&nbsp;Name and address of the manufacturer:<br/>"
                  f"<b>{mfr['name']}</b><br/>{mfr['address']}<br/>E-mail: {mfr['email']}", st),
        Spacer(1, 4 * mm),
        Paragraph(f"3.&nbsp;&nbsp;&nbsp;&nbsp;This declaration of conformity is issued under the sole "
                  f"responsibility of the manufacturer:<br/><b>{mfr['name']}</b>", st),
        Spacer(1, 4 * mm),
        Paragraph(f"4.&nbsp;&nbsp;&nbsp;&nbsp;Object of the declaration (identification of product allowing "
                  f"traceability):<br/>{p['declaration_desc']}", st),
        Spacer(1, 4 * mm),
        Paragraph(f"5.&nbsp;&nbsp;&nbsp;&nbsp;The object of the declaration described in point 4 is in "
                  f"conformity with the relevant Union harmonisation legislation:<br/>{d['legislation']}", st),
        Spacer(1, 4 * mm),
        Paragraph(f"6.&nbsp;&nbsp;&nbsp;&nbsp;References to the relevant harmonised standards used, or "
                  f"references to the specifications in relation to which conformity is declared:<br/>{d['standards']}", st),
        Spacer(1, 4 * mm),
        Paragraph(f"7.&nbsp;&nbsp;&nbsp;&nbsp;Where applicable: the notified body … performed … and issued "
                  f"the certificate:<br/>{d.get('notified_body', 'Not applicable.')}", st),
        Spacer(1, 4 * mm),
        Paragraph(f"8.&nbsp;&nbsp;&nbsp;&nbsp;Additional information:<br/>"
                  f"EU Responsible Person (Art. 16 GPSR): <b>{er['name']}</b>, {er['address']} — "
                  f"E-mail: {er['email']}, Tel: {er['tel']}.", st),
        Spacer(1, 10 * mm),
        Paragraph(f"Signed for and on behalf of:<br/><b>{mfr['name']}</b>", st),
        Spacer(1, 5 * mm),
        Paragraph(f"(place and date of issue)<br/><b>{d['place_date']}</b>", st),
        Spacer(1, 5 * mm),
        Paragraph(f"(name, function)(signature)<br/><b>{d['signatory_name']}, {d['signatory_function']}</b>", st),
    ]
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    SimpleDocTemplate(args.out, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                      topMargin=22 * mm, bottomMargin=22 * mm).build(story)
    print(f"written: {args.out}")


if __name__ == '__main__':
    main()
