# -*- coding: utf-8 -*-
"""
PPT 优化脚本：对原 PPT 做精准外科手术式优化
- P7:  修正对比表数据一致性，加箭头视觉
- P12: 修复死锁时间线布局错位（会话A/B列对齐）
- P18: 修正综合成果数据与实测一致
- 全局: 代码块加行号，对比表强化视觉层次
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from copy import deepcopy

SRC = "/workspace/.uploads/ea772e47-aaee-4d06-9ab1-afbb8b107777_全链路性能瓶颈排查与综合调优.pptx"
DST = "/workspace/db_optimization_demo/ppt/全链路性能瓶颈排查与综合调优_优化版.pptx"

C_RED    = RGBColor(0xE5, 0x5C, 0x5C)
C_GREEN  = RGBColor(0x4C, 0xAF, 0x50)
C_ACCENT = RGBColor(0xE8, 0xA3, 0x3D)
C_PRIMARY= RGBColor(0x1B, 0x3A, 0x5C)
C_GRAY   = RGBColor(0x5A, 0x6A, 0x7A)

prs = Presentation(SRC)

def set_text(shp, text, size=None, color=None, bold=None):
    """直接替换文本框内容，保留首段首run样式"""
    if not shp.has_text_frame: return
    tf = shp.text_frame
    # 保留第一个 run 的样式作为模板
    first_p = tf.paragraphs[0]
    template_run = first_p.runs[0] if first_p.runs else None
    # 清空所有段落
    tf.clear()
    p = tf.paragraphs[0]
    lines = text.split("\n") if isinstance(text, str) else [text]
    for i, line in enumerate(lines):
        if i > 0:
            p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = line
        # 复用模板样式
        if template_run:
            r.font.name = template_run.font.name or "微软雅黑"
            r.font.size = template_run.font.size or Pt(12)
            r.font.bold = template_run.font.bold
            try:
                if template_run.font.color and template_run.font.color.type:
                    r.font.color.rgb = template_run.font.color.rgb
            except: pass
        # 应用新样式
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
        if bold is not None: r.font.bold = bold

def set_cell(cell, text, size=11, color=None, bold=False, fill=None, align=PP_ALIGN.CENTER):
    """设置表格单元格"""
    cell.text = ""
    tf = cell.text_frame
    tf.margin_left = Inches(0.08); tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04); tf.margin_bottom = Inches(0.04)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.name = "微软雅黑"
    r.font.bold = bold
    r.font.color.rgb = color if color else RGBColor(0x33,0x33,0x33)
    if fill:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill

def del_shape(slide, idx):
    """删除指定索引的形状"""
    sp = slide.shapes[idx]
    sp._element.getparent().remove(sp._element)

# =====================================================================
# P7 慢查询调优对比页优化
# =====================================================================
print("优化 P7 慢查询对比页...")
s7 = prs.slides[6]

# 问题1: 对比表数据已正确(rows 20→3)，但"调优前"列描述需更准确
# 修正: 第16号 "idx_user(单列)" → 保持; 第24号 "20" → "20 (回表后)"
# 实际上 P7 数据是对的(rows 20→3)，主要问题是 P18 综合页写"80万行"
# P7 保持原样，仅强化"调优前/后"列的视觉对比

# 修正第28号 Extra 调优前: 加上 filesort 强调
# 已是 "Using where; filesort" - 正确，无需改

# 强化: 把"调优前"列文字改红色，"调优后"列改绿色
for idx in [16, 20, 24, 28, 32, 36]:  # 调优前列
    shp = s7.shapes[idx]
    if shp.has_text_frame:
        for p in shp.text_frame.paragraphs:
            for r in p.runs:
                r.font.color.rgb = C_RED
                r.font.bold = True

for idx in [17, 21, 25, 29, 33, 37]:  # 调优后列
    shp = s7.shapes[idx]
    if shp.has_text_frame:
        for p in shp.text_frame.paragraphs:
            for r in p.runs:
                r.font.color.rgb = C_GREEN
                r.font.bold = True

print("  ✓ 调优前/后列颜色强化(红/绿)")

# =====================================================================
# P12 死锁时间线布局修复
# =====================================================================
print("优化 P12 死锁时间线布局...")
s12 = prs.slides[11]

# 原布局问题: 时间线表格列宽不合理，会话B的SQL文本位置错位
# 重新设计: 3列布局 - 时间 | 会话A | 会话B | 说明
# 原列宽: t(0.5) A_SQL(3.6@1.10) B_SQL(3.6@4.85) 说明(4.2@8.60)
# 问题: A列SQL文本被截断(3.4宽不够放完整SQL)

# 修复: 缩短SQL文本，使其适配列宽
fixes_p12 = {
    12: "BEGIN;\nUPDATE t_product\nSET stock=stock-1\nWHERE product_id=1;",  # t1 会话A
    14: "",  # t1 会话B(空)
    15: "① A锁定商品1",  # t1 说明
    19: "BEGIN;\nUPDATE t_product\nSET stock=stock-1\nWHERE product_id=2;",  # t2 会话B
    21: "② B锁定商品2",  # t2 说明
    22: "",  # t2 会话A(空) - 原来错位放在说明列
    26: "UPDATE t_product\nSET stock=stock-1\nWHERE product_id=2;",  # t3 会话A
    29: "③ A等B的锁\n（阻塞）",  # t3 说明
    35: "UPDATE t_product\nSET stock=stock-1\nWHERE product_id=1;",  # t4 会话B
    36: "④ 死锁!\nB被回滚",  # t4 说明
}

# 先修正文本内容
for idx, txt in fixes_p12.items():
    try:
        shp = s12.shapes[idx]
        if shp.has_text_frame:
            set_text(shp, txt, size=9)
    except Exception as e:
        print(f"  ⚠ P12[{idx}] 修改失败: {e}")

# 修正会话A/会话B标题位置，让两列对齐
# 会话A标题[7] 在 0.55,1.80 宽4.0  → 保持
# 会话B标题[8] 在 4.85,1.80 宽4.0  → 保持

# 加宽说明列，让死锁说明更醒目
# 说明列原在 8.60，宽4.2 → 调整为 8.40 宽4.4
for idx in [15, 21, 29, 36]:
    try:
        shp = s12.shapes[idx]
        shp.left = Inches(8.40)
        shp.width = Inches(4.45)
        # 说明列加粗强调
        if shp.has_text_frame:
            for p in shp.text_frame.paragraphs:
                for r in p.runs:
                    r.font.bold = True
                    if "死锁" in r.text or "阻塞" in r.text:
                        r.font.color.rgb = C_RED
                    elif "锁定" in r.text:
                        r.font.color.rgb = C_PRIMARY
    except: pass

print("  ✓ 时间线文本与布局修复")

# =====================================================================
# P18 综合成果页数据修正（关键！与实测对齐）
# =====================================================================
print("优化 P18 综合成果数据...")
s18 = prs.slides[17]

# 修正对比表数据，与真实 MySQL 实测一致
# 原: 慢查询 调优前"扫描80万行/800ms" 调优后"20行/<10ms"
# 实测: EXPLAIN rows 调优前=20(走idx_user) 调优后=3(复合索引)
#       但慢日志 Rows_examined 可达数十万(回表)
# 统一表述: 调优前"rows=20+回表扫描 filesort" 调优后"rows=3 索引覆盖"

p18_fixes = {
    # 慢查询行
    14: "rows=20 + 回表过滤\nfilesort 额外排序",     # 调优前
    15: "rows=3 索引覆盖\n无回表无排序",              # 调优后
    16: "扫描↓85%\n排序消除",                          # 改善
    # 索引异常行
    19: "6类失效\ntype=ALL 全表扫描",                  # 调优前
    20: "全部命中索引\ntype=ref/range",                # 调优后
    21: "全表扫描→\n索引命中",                          # 改善
    # 事务死锁行（实测真实触发）
    24: "真实触发 AB-BA\nERROR 1213",                  # 调优前
    25: "统一加锁顺序\n死锁 = 0",                      # 调优后
    26: "根除",                                        # 改善
    # 锁等待行（实测真实触发）
    29: "真实触发\nERROR 1205 超时5s",                  # 调优前
    30: "分批提交+乐观锁\n快速失败+重试",                # 调优后
    31: "超时堆积→\n秒级失败",                          # 改善
    # 主从延迟行
    34: "单线程回放\n大促延迟120s+",                    # 调优前
    35: "8线程并行复制\nLOGICAL_CLOCK",                # 调优后
    36: "120s→<5s\n↓96%",                              # 改善
}

for idx, txt in p18_fixes.items():
    try:
        shp = s18.shapes[idx]
        if shp.has_text_frame:
            # 根据列位置设置颜色
            col_pos = (idx - 8) % 4  # 0=故障 1=调优前 2=调优后 3=改善
            if col_pos == 1:
                set_text(shp, txt, size=10, color=C_RED, bold=True)
            elif col_pos == 2:
                set_text(shp, txt, size=10, color=C_GREEN, bold=True)
            elif col_pos == 3:
                set_text(shp, txt, size=11, color=C_ACCENT, bold=True)
            else:
                set_text(shp, txt, size=11, color=C_PRIMARY, bold=True)
    except Exception as e:
        print(f"  ⚠ P18[{idx}] 修改失败: {e}")

# 修正整体收益KPI数据（与实测对齐）
# 原: 99.95%→99.99% / 350ms→28ms / 高频→0 / 减少90%
# 优化为更贴合实测的表述
kpi_fixes = {
    40: "死锁=0",        # 原 99.95%→99.99%
    43: "rows 20→3",     # 原 350ms→28ms
    46: "ERROR 1205\n已消除",  # 原 高频→0
    49: "延迟↓96%",      # 原 减少90%
}
for idx, txt in kpi_fixes.items():
    try:
        shp = s18.shapes[idx]
        if shp.has_text_frame:
            set_text(shp, txt, size=9, color=C_GREEN, bold=True)
    except: pass

print("  ✓ 综合成果数据修正(与实测一致)")

# =====================================================================
# P1 封面优化：突出"真实实测"
# =====================================================================
print("优化 P1 封面...")
s1 = prs.slides[0]
# 找到副标题文本框并强化"真实实测"卖点
for shp in s1.shapes:
    if shp.has_text_frame:
        t = shp.text_frame.text
        if "真实 MySQL" in t:
            set_text(shp,
                "✓ 真实 MySQL 8.0 实测环境    ✓ 100万订单数据量\n"
                "✓ 真实触发死锁/锁等待/慢查询    ✓ EXPLAIN 调优前后对比",
                size=14, color=RGBColor(0xE8, 0xA3, 0x3D), bold=True)
            break
print("  ✓ 封面卖点强化")

# =====================================================================
# 保存
# =====================================================================
import os
os.makedirs(os.path.dirname(DST), exist_ok=True)
prs.save(DST)
print(f"\n✅ 优化版 PPT 已生成: {DST}")
print(f"   共 {len(prs.slides)} 页")
