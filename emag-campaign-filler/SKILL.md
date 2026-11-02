---
name: emag-campaign-filler
description: |
  eMAG Marketplace 活动申报文件处理技能。
  根据折扣数据源 origin.xlsx 中的折扣数据，自动填入 eMAG 活动的申报文件
  （折扣百分比 voucher_discount 或活动价格 sale_price），按 Product Code
  （part_number）匹配。

  触发场景：
  - 用户说"填 eMAG 活动"、"填写活动申报"、"填折扣"、"填价格"
  - 用户上传了 eMAG 活动文件（Offers proposal...xlsx）需要处理
  - 用户提到 Multi Deals、Discount Campaign、Genius Deals、Black Friday 等活动
---

# eMAG Marketplace 活动申报文件处理

## 功能说明

根据折扣数据源 `origin.xlsx` 中的折扣数据，自动为 eMAG 活动申报文件填入：

1. **voucher_discount（折扣百分比）**：直接使用 origin.xlsx 中的折扣值
2. **sale_price（活动价格）**：根据折扣计算：`活动价格 = 当前价格 × (1 - 折扣%)`

## 数据源文件

- **默认路径**：`~/workspace/user/files/origin.xlsx`（可用 `--origin` 指定其他文件）
- **包含内容**：
  - 每个商品的 Product Code（part_number，第5列）
  - 每个商品的 Voucher Discount（voucher_discount，第13列）
- **匹配方式**：按 Product Code（part_number）匹配
- **注意**：origin.xlsx 里的折扣是"上一次活动填好的值"。填新活动前，先跟用户确认折扣是沿用还是要更新。

## 活动文件识别

eMAG 活动申报文件通常命名为：
- `Offers proposal in Multi Deals Campaign XXX-...`
- `Offers proposal in Discount Campaign XXX-...`
- `Offers proposal in Genius Deals Campaign XXX-...`
- `Offers proposal in Black Friday Campaign XXX-...`

## 执行脚本

```bash
python3 scripts/fill_emag_campaign.py <活动文件路径> [--origin <折扣源文件>]
```

脚本会自动：
1. 从 origin.xlsx 加载折扣数据
2. 读取活动文件
3. 判断活动类型（折扣模式 or 价格模式）
4. 计算并填入对应列
5. 保存为 `原文件名_updated.xlsx`

## 活动类型判断逻辑

### 折扣模式（Multi Deals / Genius Deals / Black Friday voucher 类）
- 文件中有 `voucher_discount` 列
- 直接将 origin.xlsx 中的折扣填入该列

### 价格模式（Discount Campaign）
- 文件中有 `sale_price` 列
- 计算公式：`sale_price = current_price × (1 - discount / 100)`
- 注意：current_price 有时是字符串格式，需转换为 float；保留 2 位小数

## 注意事项

- 填完后把未匹配到的商品（origin.xlsx 里没有的）和超 max_campaign_price 的警告如实告诉用户
- 输出文件发给用户前，先打开抽查几行确认数字正确
- 上传到 eMAG 后台的动作由用户自己做，不要代传
