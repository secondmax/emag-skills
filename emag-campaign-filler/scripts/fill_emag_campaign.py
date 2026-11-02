#!/usr/bin/env python3
"""
eMAG Marketplace Campaign File Filler

从 origin.xlsx 读取折扣数据，根据活动文件类型自动填入 voucher_discount 或 sale_price。

Usage:
    python3 fill_emag_campaign.py <活动文件路径> [--origin <折扣源文件>]

默认折扣源: ~/workspace/user/files/origin.xlsx
"""

import sys
import os
import argparse
import openpyxl
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

DEFAULT_ORIGIN = Path.home() / "workspace" / "user" / "files" / "origin.xlsx"


def load_origin_discounts(origin_file):
    """从 origin.xlsx 加载折扣数据"""
    origin_file = Path(origin_file)
    if not origin_file.exists():
        print(f"❌ 错误：找不到 origin.xlsx 文件: {origin_file}")
        sys.exit(1)

    wb = openpyxl.load_workbook(origin_file)
    ws = wb['Offers']

    discount_map = {}
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 5:  # 跳过表头行
            continue
        if all(v is None for v in row):
            continue

        part_number = row[4]  # Product Code
        voucher_discount = row[12]  # voucher_discount

        if part_number:
            discount_map[part_number] = voucher_discount

    wb.close()
    print(f"📊 从 origin.xlsx 加载了 {len(discount_map)} 个商品的折扣数据")
    return discount_map


def detect_campaign_type(ws):
    """检测活动类型：折扣模式 vs 价格模式；同时按表头定位各列"""
    cols = {}
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 2:  # 第3行是字段名
            fields = {}
            for idx, v in enumerate(row):
                if v:
                    key = str(v).strip().lower()
                    fields[key] = idx
                    # 定位关键列（兼容不同活动文件的列位置差异）
                    if key == 'part_number':
                        cols['part_number'] = idx
                    elif key == 'part_number_key':
                        cols['pnk'] = idx
                    elif key == 'voucher_discount':
                        cols['voucher_discount'] = idx
                    elif key == 'sale_price':
                        cols['sale_price'] = idx
                    elif key == 'current_price':
                        cols['current_price'] = idx
                    elif key in ('max_campaign_price', 'maximum_campaign_price'):
                        cols['max_campaign_price'] = idx

            print(f"\n📋 检测到的字段:")
            for k in sorted(fields, key=lambda k: fields[k]):
                print(f"   列{fields[k]+1}: {k}")

            has_voucher_discount = 'voucher_discount' in cols
            has_sale_price = 'sale_price' in cols

            if has_sale_price:
                campaign_type = 'price'  # Discount Campaign - 填 sale_price
            elif has_voucher_discount:
                campaign_type = 'discount'  # Multi Deals 等 - 填 voucher_discount
            else:
                campaign_type = 'unknown'
            return campaign_type, cols
    return 'unknown', {}


def fill_campaign_file(file_path, discount_map):
    """填入活动数据"""
    if not os.path.exists(file_path):
        print(f"❌ 错误：找不到文件: {file_path}")
        sys.exit(1)

    wb = openpyxl.load_workbook(file_path)
    # 工作表名可能是英文 Offers 或罗马尼亚文 Oferte
    if 'Offers' in wb.sheetnames:
        ws = wb['Offers']
    elif 'Oferte' in wb.sheetnames:
        ws = wb['Oferte']
    else:
        print(f"❌ 错误：找不到 Offers/Oferte 工作表，可用表: {wb.sheetnames}")
        sys.exit(1)

    campaign_type, cols = detect_campaign_type(ws)
    print(f"\n🎯 活动类型: {campaign_type}")

    if 'part_number' not in cols:
        print("❌ 错误：活动文件中找不到 part_number 列")
        sys.exit(1)

    c_part = cols['part_number']
    c_pnk = cols.get('pnk')
    c_price = cols.get('current_price')
    c_disc = cols.get('voucher_discount')
    c_sale = cols.get('sale_price')
    c_max = cols.get('max_campaign_price')

    results = []
    updated = 0
    not_found = []
    warnings = []

    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 5:  # 跳过表头行
            continue
        if all(v is None for v in row):
            continue

        part_number = row[c_part] if c_part < len(row) else None
        pnk = row[c_pnk] if c_pnk is not None and c_pnk < len(row) else None
        current_price_raw = row[c_price] if c_price is not None and c_price < len(row) else None

        try:
            current_price = float(current_price_raw) if current_price_raw else None
        except (ValueError, TypeError):
            current_price = None

        if part_number not in discount_map:
            not_found.append((i + 1, part_number, pnk))
            continue

        discount = discount_map[part_number]

        if campaign_type == 'discount':
            if c_disc is None:
                warnings.append({'row': i + 1, 'code': part_number,
                                 'message': '文件中无 voucher_discount 列'})
                continue
            ws.cell(row=i + 1, column=c_disc + 1, value=discount)  # voucher_discount 列
            results.append({'row': i + 1, 'pnk': pnk, 'code': part_number,
                            'discount': discount, 'action': 'discount'})
            updated += 1

        elif campaign_type == 'price':
            if c_sale is None:
                warnings.append({'row': i + 1, 'code': part_number,
                                 'message': '文件中无 sale_price 列'})
                continue
            if current_price is not None and discount is not None:
                sale_price = round(current_price * (1 - discount / 100), 2)
                sale_price = float(Decimal(str(sale_price)).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP))

                ws.cell(row=i + 1, column=c_sale + 1, value=sale_price)  # sale_price 列

                max_price_raw = row[c_max] if c_max is not None and c_max < len(row) else None
                if max_price_raw:
                    try:
                        max_price = float(max_price_raw)
                        if sale_price > max_price:
                            warnings.append({'row': i + 1, 'code': part_number,
                                             'sale': sale_price, 'max': max_price,
                                             'message': '超过平台价格上限'})
                    except (ValueError, TypeError):
                        pass

                results.append({'row': i + 1, 'pnk': pnk, 'code': part_number,
                                'current': current_price, 'discount': discount,
                                'sale': sale_price, 'action': 'price'})
                updated += 1
            else:
                warnings.append({'row': i + 1, 'code': part_number,
                                 'message': '缺少价格或折扣数据'})

    base, ext = os.path.splitext(file_path)
    output_path = f"{base}_updated{ext}"
    wb.save(output_path)
    wb.close()

    print(f"\n{'=' * 70}")
    print(f"✅ 成功处理 {updated} 个商品")

    if not_found:
        print(f"\n⚠️ 未匹配到折扣的商品 ({len(not_found)}):")
        for row_num, code, pnk in not_found:
            print(f"   Row {row_num}: {code} ({pnk})")

    if warnings:
        print(f"\n⚠️ 需要注意的商品 ({len(warnings)}):")
        for w in warnings:
            if 'sale' in w:
                print(f"   Row {w['row']}: {w['code']} - Sale={w['sale']}, Max={w['max']} ({w['message']})")
            else:
                print(f"   Row {w['row']}: {w['code']} - {w['message']}")

    print(f"\n📁 输出文件: {output_path}")
    print(f"{'=' * 70}")

    return output_path, results, not_found, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign_file', help='eMAG 活动申报文件路径')
    parser.add_argument('--origin', default=str(DEFAULT_ORIGIN), help='折扣源文件路径')
    args = parser.parse_args()

    print(f"📂 正在处理: {args.campaign_file}")
    print(f"📊 数据源: {args.origin}")

    discount_map = load_origin_discounts(args.origin)
    fill_campaign_file(args.campaign_file, discount_map)


if __name__ == "__main__":
    main()
