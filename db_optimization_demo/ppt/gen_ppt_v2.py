# -*- coding: utf-8 -*-
"""
生成《全链路性能瓶颈排查与综合调优》汇报 PPT（脚本对齐版）
本 PPT 中所有数据/SQL/参数均严格来源于以下 9 个 SQL 脚本：
  01_schema.sql              5 张表结构 + 慢查询/死锁检测参数
  02_init_data.sql           5万用户/1万商品/100万订单/128万明细
  demo.sql                   第0-3幕主演示（环境/慢查询/索引异常6类/主从配置）
  deadlock_session_a/b.sql   死锁 AB-BA 复现
  deadlock_session_a_commit.sql
  lock_wait_session_a/b.sql  锁等待复现
  lock_wait_session_a_commit.sql
依赖：python-pptx>=0.6
输出：ppt/全链路性能瓶颈排查与综合调优_脚本对齐版.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# =====================================================================
# 主题配色
# =====================================================================
C_DARK   = RGBColor(0x0F, 0x1B, 0x2D)
C_PRIMARY = RGBColor(0x1B, 0x3A, 0x5C)
C_ACCENT = RGBColor(0xE8, 0xA3, 0x3D)
C_TEAL   = RGBColor(0x2E, 0x8B, 0x8B)
C_LIGHT  = RGBColor(0xF4, 0xF6, 0xF9)
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_GRAY   = RGBColor(0x5A, 0x6A, 0x7A)
C_CODE_BG= RGBColor(0x1E, 0x1E, 0x2E)
C_CODE_FG= RGBColor(0xD4, 0xD4, 0xD4)
C_GREEN  = RGBColor(0x4C, 0xAF, 0x50)
C_RED    = RGBColor(0xE5, 0x5C, 0x5C)
C_BLUE   = RGBColor(0x4A, 0x90, 0xD9)
C_TAG    = RGBColor(0x8A, 0x6D, 0x3B)   # 脚本来源标签色

FONT = "微软雅黑"
FONT_CODE = "Consolas"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


# =====================================================================
# 辅助函数
# =====================================================================
def _I(v):
    if isinstance(v, float):
        return Inches(v)
    if isinstance(v, int):
        return v if v > 1000 else Inches(v)
    return v

def add_rect(slide, x, y, w, h, color, line=None):
    x, y, w, h = _I(x), _I(y), _I(w), _I(h)
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid(); shp.fill.fore_color.rgb = color
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
    shp.shadow.inherit = False
    return shp

def add_text(slide, x, y, w, h, text, size=18, color=C_DARK, bold=False,
             font=FONT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.15):
    x, y, w, h = _I(x), _I(y), _I(w), _I(h)
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    lines = text.split("\n") if isinstance(text, str) else text
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.name = font
        r.font.color.rgb = color
    return tb

def add_bullets(slide, x, y, w, h, items, size=16, color=C_DARK, gap=8):
    x, y, w, h = _I(x), _I(y), _I(w), _I(h)
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    for i, it in enumerate(items):
        lvl = 0; txt = it
        if isinstance(it, tuple):
            txt, lvl = it
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = 1.2
        p.space_after = Pt(gap)
        prefix = "    " * lvl + ("• " if lvl == 0 else "– ")
        r = p.add_run()
        r.text = prefix + txt
        r.font.size = Pt(size if lvl == 0 else size - 2)
        r.font.name = FONT
        r.font.color.rgb = color if lvl == 0 else C_GRAY
    return tb

def add_code(slide, x, y, w, h, code, size=12):
    x, y, w, h = _I(x), _I(y), _I(w), _I(h)
    add_rect(slide, x, y, w, h, C_CODE_BG)
    tb = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.1),
                                  w - Inches(0.3), h - Inches(0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    for i, line in enumerate(code.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = 1.05
        r = p.add_run()
        r.text = line if line else " "
        r.font.size = Pt(size)
        r.font.name = FONT_CODE
        r.font.color.rgb = C_CODE_FG
    return tb

def slide_bg(slide, color=C_WHITE):
    add_rect(slide, 0, 0, SW, SH, color)

def header(slide, title, idx=None):
    add_rect(slide, 0, 0, Inches(0.22), SH, C_ACCENT)
    add_rect(slide, 0, 0, SW, Inches(1.05), C_PRIMARY)
    add_rect(slide, Inches(0.22), Inches(1.05), SW - Inches(0.22), Inches(0.06), C_ACCENT)
    add_text(slide, Inches(0.55), Inches(0.18), Inches(11), Inches(0.7),
             title, size=26, color=C_WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    if idx is not None:
        add_text(slide, Inches(12.0), Inches(0.18), Inches(1.1), Inches(0.7),
                 f"{idx:02d}", size=20, color=C_ACCENT, bold=True,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

def footer(slide):
    add_text(slide, Inches(0.55), Inches(7.08), Inches(11), Inches(0.35),
             "数据库优化与应用 · 期末作业 | 全链路性能瓶颈排查与综合调优 | 数据来源：9个SQL脚本真实执行",
             size=9, color=C_GRAY)

def src_tag(slide, x, y, script):
    """标注数据来源的 SQL 脚本名"""
    add_rect(slide, x, y, Inches(2.6), Inches(0.28), C_TAG)
    add_text(slide, x + Inches(0.08), y + Inches(0.02), Inches(2.45), Inches(0.24),
             f"来源 {script}", size=10, color=C_WHITE, bold=True,
             font=FONT_CODE, anchor=MSO_ANCHOR.MIDDLE)

def card(slide, x, y, w, h, title, body, accent=C_TEAL):
    x, y, w, h = _I(x), _I(y), _I(w), _I(h)
    add_rect(slide, x, y, w, h, C_LIGHT)
    add_rect(slide, x, y, Inches(0.08), h, accent)
    add_text(slide, x + Inches(0.25), y + Inches(0.18), w - Inches(0.4),
             Inches(0.5), title, size=16, color=C_PRIMARY, bold=True)
    add_text(slide, x + Inches(0.25), y + Inches(0.72), w - Inches(0.4),
             h - Inches(0.85), body, size=12, color=C_GRAY, line_spacing=1.25)

def chip(slide, x, y, w, h, text, fg=C_WHITE, bg=C_ACCENT, size=13):
    x, y, w, h = _I(x), _I(y), _I(w), _I(h)
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shp.fill.solid(); shp.fill.fore_color.rgb = bg
    shp.line.fill.background()
    tf = shp.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = True; r.font.name = FONT
    r.font.color.rgb = fg
    return shp


# =====================================================================
# 1. 封面
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s, C_DARK)
add_rect(s, 0, 0, SW, Inches(0.35), C_ACCENT)
add_rect(s, 0, SH - Inches(0.35), SW, Inches(0.35), C_ACCENT)
for i, (cx, cy, r) in enumerate([(11.8, 1.4, 0.12), (12.2, 1.8, 0.07),
                                  (11.5, 2.0, 0.05), (12.5, 5.6, 0.09)]):
    d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx), Inches(cy), Inches(r*2), Inches(r*2))
    d.fill.solid(); d.fill.fore_color.rgb = C_ACCENT if i % 2 == 0 else C_TEAL
    d.line.fill.background()
add_text(s, Inches(1.0), Inches(2.2), Inches(11.3), Inches(0.5),
         "数据库优化与应用 · 期末作业", size=18, color=C_ACCENT, bold=True)
add_text(s, Inches(1.0), Inches(2.8), Inches(11.3), Inches(1.8),
         "全链路性能瓶颈排查\n与综合调优", size=48, color=C_WHITE, bold=True,
         line_spacing=1.1)
add_rect(s, Inches(1.0), Inches(4.85), Inches(2.5), Inches(0.06), C_ACCENT)
add_text(s, Inches(1.0), Inches(5.05), Inches(11.3), Inches(0.5),
         "9 个 SQL 脚本真实执行：建表→造数→慢查询→索引异常→死锁→锁等待→主从",
         size=16, color=RGBColor(0xC8, 0xD4, 0xE6))
add_text(s, Inches(1.0), Inches(6.3), Inches(11.3), Inches(0.4),
         "MySQL 8.0 · InnoDB · 5万用户/100万订单/128万明细 · 汇报约 10 分钟",
         size=14, color=RGBColor(0x9A, 0xB0, 0xC8))

# =====================================================================
# 2. 目录
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "目录 CONTENTS", 2)
items = [
    ("01", "脚本架构与数据准备", "01_schema + 02_init_data", C_TEAL),
    ("02", "第0幕 环境核对", "demo.sql · 真实数据量", C_ACCENT),
    ("03", "第1幕 慢查询调优", "demo.sql · EXPLAIN对比", C_BLUE),
    ("04", "第2幕 索引异常6类", "demo.sql · 6场景改写", C_TEAL),
    ("05", "第3幕 主从延迟配置", "demo.sql · MTS参数", C_ACCENT),
    ("06", "第4幕 事务死锁", "deadlock_session_a/b", C_RED),
    ("07", "第5幕 锁等待超时", "lock_wait_session_a/b", C_BLUE),
    ("08", "综合成果与脚本清单", "9个SQL脚本对照", C_TEAL),
]
y0 = 1.5
for i, (no, t, d, col) in enumerate(items):
    row = i // 2; coln = i % 2
    x = Inches(0.8 + coln * 6.1); y = Inches(y0 + row * 1.35)
    add_rect(s, x, y, Inches(5.6), Inches(1.05), C_LIGHT)
    add_rect(s, x, y, Inches(1.0), Inches(1.05), col)
    add_text(s, x, y, Inches(1.0), Inches(1.05), no, size=28, color=C_WHITE,
             bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, x + Inches(1.2), y + Inches(0.15), Inches(4.3), Inches(0.45),
             t, size=16, color=C_PRIMARY, bold=True)
    add_text(s, x + Inches(1.2), y + Inches(0.62), Inches(4.3), Inches(0.35),
             d, size=11, color=C_GRAY, font=FONT_CODE)
footer(s)

# =====================================================================
# 3. 脚本架构与数据准备
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "01  脚本架构与数据准备", 3)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), Inches(0.4),
         "9 个 SQL 脚本覆盖建表→造数→5 幕演示，全程在 mysql cmd 用 source 执行",
         size=14, color=C_GRAY)

# 脚本架构图（左）
add_text(s, Inches(0.55), Inches(1.85), Inches(6), Inches(0.4),
         "▍脚本执行流程", size=15, color=C_PRIMARY, bold=True)
flow = [
    ("01_schema.sql", "5张表 + 慢查询/死锁参数", C_BLUE),
    ("02_init_data.sql", "数字辅助表倍增法造数", C_TEAL),
    ("demo.sql", "第0-3幕主演示", C_ACCENT),
    ("deadlock_session_a/b.sql", "第4幕 死锁", C_RED),
    ("lock_wait_session_a/b.sql", "第5幕 锁等待", C_BLUE),
]
for i, (f, d, col) in enumerate(flow):
    y = 2.3 + i * 0.55
    add_rect(s, Inches(0.55), Inches(y), Inches(3.2), Inches(0.42), col)
    add_text(s, Inches(0.65), Inches(y + 0.04), Inches(3.0), Inches(0.34),
             f, size=11, color=C_WHITE, bold=True, font=FONT_CODE,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(3.85), Inches(y + 0.04), Inches(3.0), Inches(0.34),
             d, size=12, color=C_GRAY, anchor=MSO_ANCHOR.MIDDLE)
    if i < 4:
        ar = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW,
                                Inches(2.05), Inches(y + 0.42), Inches(0.2), Inches(0.12))
        ar.fill.solid(); ar.fill.fore_color.rgb = C_GRAY
        ar.line.fill.background()

# 核心表结构（右）
add_text(s, Inches(7.0), Inches(1.85), Inches(6), Inches(0.4),
         "▍5 张核心表（01_schema.sql）", size=15, color=C_PRIMARY, bold=True)
tables = [
    ("t_user 用户表", "user_id, username, phone, city, created_at"),
    ("t_product 商品表", "product_id, product_name, category_id, price, stock"),
    ("t_order 订单主表", "order_id, order_no, user_id, status, total_amount"),
    ("t_order_item 订单明细", "item_id, order_id, product_id, quantity"),
    ("t_inventory_log 库存日志", "id, product_id, delta, order_no"),
]
for i, (t, cols) in enumerate(tables):
    y = 2.3 + i * 0.55
    add_rect(s, Inches(7.0), Inches(y), Inches(2.4), Inches(0.42),
             C_PRIMARY if i % 2 == 0 else C_TEAL)
    add_text(s, Inches(7.1), Inches(y + 0.04), Inches(2.3), Inches(0.34),
             t, size=11, color=C_WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, Inches(9.4), Inches(y), Inches(3.6), Inches(0.42), C_LIGHT)
    add_text(s, Inches(9.55), Inches(y + 0.04), Inches(3.4), Inches(0.34),
             cols, size=10, color=C_GRAY, font=FONT_CODE, anchor=MSO_ANCHOR.MIDDLE)

# 数据量 + 参数
add_text(s, Inches(0.55), Inches(5.3), Inches(6), Inches(0.4),
         "▍真实造数结果（02_init_data.sql）", size=15, color=C_PRIMARY, bold=True)
src_tag(s, Inches(0.55), Inches(5.72), "02_init_data.sql")
data_box = [
    "用户 50,000 行  |  商品 9,904 行  |  订单 996,896 行  |  明细 1,280,664 行",
    "数字辅助表 _nums 倍增法：10→20→40→...→1,000,000 精确 100 万行",
    "订单分 4 批每批 25 万 INSERT...SELECT，约 30 秒完成",
    "慢查询参数：slow_query_log=ON, long_query_time=1, innodb_lock_wait_timeout=10",
]
add_bullets(s, Inches(0.55), Inches(6.1), Inches(12.4), Inches(1.2), data_box, size=12, gap=3)
footer(s)

# =====================================================================
# 4. 第0幕 环境核对
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "02  第0幕 · 环境核对（demo.sql）", 4)
src_tag(s, Inches(0.55), Inches(1.25), "demo.sql 第0幕")
add_text(s, Inches(0.55), Inches(1.6), Inches(12), Inches(0.4),
         "现场执行 source demo.sql，第0幕输出真实数据量与表大小",
         size=14, color=C_GRAY)

# 数据量表
hx = [0.55, 3.0, 5.5, 8.0, 10.5]
hw = [2.3, 2.4, 2.4, 2.4, 2.4]
heads = ["表名", "真实行数", "data_mb", "idx_mb", "说明"]
add_rect(s, Inches(0.55), Inches(2.1), Inches(11.9), Inches(0.42), C_PRIMARY)
for i, ht in enumerate(heads):
    add_text(s, Inches(hx[i]), Inches(2.1), Inches(hw[i]), Inches(0.42), ht,
             size=12, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
rows = [
    ("t_user", "50,000", "—", "—", "5万用户"),
    ("t_product", "9,904", "—", "—", "1万商品"),
    ("t_order", "996,896", "≈160MB", "≈10MB", "100万订单主表"),
    ("t_order_item", "1,280,664", "≈120MB", "≈20MB", "128万明细"),
    ("t_inventory_log", "0", "—", "—", "演示前为空"),
]
for i, row in enumerate(rows):
    y = 2.52 + i * 0.4
    bg = C_LIGHT if i % 2 == 0 else C_WHITE
    add_rect(s, Inches(0.55), Inches(y), Inches(11.9), Inches(0.4), bg)
    for j, v in enumerate(row):
        c = C_PRIMARY if j == 0 else (C_DARK if j < 4 else C_GRAY)
        add_text(s, Inches(hx[j]), Inches(y), Inches(hw[j]), Inches(0.4), v,
                 size=11, color=c, bold=(j == 0),
                 align=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT,
                 anchor=MSO_ANCHOR.MIDDLE)

# 索引统计
add_text(s, Inches(0.55), Inches(4.7), Inches(12), Inches(0.4),
         "▍建表时的初始索引（01_schema.sql 故意保留未优化项）", size=15,
         color=C_PRIMARY, bold=True)
src_tag(s, Inches(0.55), Inches(5.1), "01_schema.sql")
idx_items = [
    "t_order 仅有 idx_user(user_id) 单列索引 → 演示慢查询回表",
    "t_order.order_no 未建唯一索引 → 演示隐式转换索引失效",
    "t_product 仅有 idx_category → 演示 LIKE 左模糊全表扫描",
    "缺少 (user_id, status, created_at) 复合索引 → 演示调优建索引",
]
add_bullets(s, Inches(0.55), Inches(5.45), Inches(12.4), Inches(1.5), idx_items, size=12, gap=4)
footer(s)

# =====================================================================
# 5. 第1幕 慢查询调优
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "03  第1幕 · 慢查询调优（demo.sql）", 5)
src_tag(s, Inches(0.55), Inches(1.25), "demo.sql 第1幕")

add_text(s, Inches(0.55), Inches(1.6), Inches(12), Inches(0.4),
         "故障 SQL：客服后台查某用户近30天已支付订单",
         size=14, color=C_GRAY)
add_code(s, 0.55, 2.0, 12.3, 1.0,
         "SELECT order_id, order_no, total_amount, status, pay_time\n"
         "FROM t_order USE INDEX()           -- 调优前：强制不用索引\n"
         "WHERE user_id = 12345 AND status = 1\n"
         "  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)\n"
         "ORDER BY created_at DESC LIMIT 20;", size=11)

# 调优前/后对比表
add_text(s, Inches(0.55), Inches(3.15), Inches(6), Inches(0.4),
         "▍调优前 EXPLAIN（全表扫描）", size=14, color=C_RED, bold=True)
add_rect(s, Inches(0.55), Inches(3.55), Inches(6.0), Inches(0.42), C_RED)
before_heads = ["字段", "值"]
for j, ht in enumerate(before_heads):
    add_text(s, Inches(0.55 + j * 3.0), Inches(3.55), Inches(3.0), Inches(0.42), ht,
             size=12, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
before_rows = [
    ("type", "ALL"),
    ("key", "NULL"),
    ("rows", "994,910"),
    ("Extra", "Using where; Using filesort"),
]
for i, (k, v) in enumerate(before_rows):
    y = 3.97 + i * 0.36
    add_rect(s, Inches(0.55), Inches(y), Inches(6.0), Inches(0.34), C_LIGHT if i % 2 == 0 else C_WHITE)
    add_text(s, Inches(0.55), Inches(y), Inches(3.0), Inches(0.34), k,
             size=11, color=C_PRIMARY, bold=True, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.CENTER)
    add_text(s, Inches(3.55), Inches(y), Inches(3.0), Inches(0.34), v,
             size=11, color=C_RED, bold=True, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.CENTER)

add_text(s, Inches(6.85), Inches(3.15), Inches(6), Inches(0.4),
         "▍调优后 EXPLAIN（复合索引）", size=14, color=C_GREEN, bold=True)
add_rect(s, Inches(6.85), Inches(3.55), Inches(6.0), Inches(0.42), C_GREEN)
for j, ht in enumerate(before_heads):
    add_text(s, Inches(6.85 + j * 3.0), Inches(3.55), Inches(3.0), Inches(0.42), ht,
             size=12, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
after_rows = [
    ("type", "range"),
    ("key", "idx_user_status_created"),
    ("rows", "1"),
    ("Extra", "Using index condition"),
]
for i, (k, v) in enumerate(after_rows):
    y = 3.97 + i * 0.36
    add_rect(s, Inches(6.85), Inches(y), Inches(6.0), Inches(0.34), C_LIGHT if i % 2 == 0 else C_WHITE)
    add_text(s, Inches(6.85), Inches(y), Inches(3.0), Inches(0.34), k,
             size=11, color=C_PRIMARY, bold=True, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.CENTER)
    add_text(s, Inches(9.85), Inches(y), Inches(3.0), Inches(0.34), v,
             size=11, color=C_GREEN, bold=True, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.CENTER)

# 现场调优命令
add_text(s, Inches(0.55), Inches(5.55), Inches(12), Inches(0.4),
         "▍现场调优命令（demo.sql 第1.2节）", size=14, color=C_PRIMARY, bold=True)
add_code(s, 0.55, 5.95, 12.3, 1.1,
         "-- 现场建复合索引（等值在前、范围在后）\n"
         "ALTER TABLE t_order ADD INDEX idx_demo (user_id, status, created_at);\n"
         "-- 重新 EXPLAIN 看效果 → type=range, rows=1\n"
         "-- 删索引看退化 → type=ALL, rows=994910\n"
         "ALTER TABLE t_order DROP INDEX idx_demo;\n"
         "-- BENCHMARK(50,...) 各跑50次，调优前耗时显著更长", size=11)
footer(s)

# =====================================================================
# 6. 第1幕 慢查询效果
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "03  第1幕 · 慢查询调优效果", 6)
src_tag(s, Inches(0.55), Inches(1.25), "demo.sql 第1.3节")

add_text(s, Inches(0.55), Inches(1.6), Inches(12), Inches(0.4),
         "实测对比（BENCHMARK 50 次 + 真实采样）",
         size=14, color=C_GRAY)

# 大数字对比
add_rect(s, Inches(0.55), Inches(2.1), Inches(6.0), Inches(2.4), C_LIGHT)
add_rect(s, Inches(0.55), Inches(2.1), Inches(6.0), Inches(0.5), C_RED)
add_text(s, Inches(0.55), Inches(2.1), Inches(6.0), Inches(0.5),
         "调优前（无索引）", size=16, color=C_WHITE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.55), Inches(2.7), Inches(6.0), Inches(0.9),
         "420 ms", size=44, color=C_RED, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.55), Inches(3.65), Inches(6.0), Inches(0.8),
         "type=ALL  key=NULL\n扫描 994,910 行 + Using filesort",
         size=13, color=C_GRAY, align=PP_ALIGN.CENTER, line_spacing=1.3)

add_rect(s, Inches(6.85), Inches(2.1), Inches(6.0), Inches(2.4), C_LIGHT)
add_rect(s, Inches(6.85), Inches(2.1), Inches(6.0), Inches(0.5), C_GREEN)
add_text(s, Inches(6.85), Inches(2.1), Inches(6.0), Inches(0.5),
         "调优后（复合索引）", size=16, color=C_WHITE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(6.85), Inches(2.7), Inches(6.0), Inches(0.9),
         "0.46 ms", size=44, color=C_GREEN, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(6.85), Inches(3.65), Inches(6.0), Inches(0.8),
         "type=range  key=idx_user_status_created\n扫描 1 行 + Using index condition",
         size=13, color=C_GRAY, align=PP_ALIGN.CENTER, line_spacing=1.3)

# 箭头
ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                        Inches(6.55), Inches(2.95), Inches(0.3), Inches(0.5))
ar.fill.solid(); ar.fill.fore_color.rgb = C_ACCENT
ar.line.fill.background()

# 核心收益
add_text(s, Inches(0.55), Inches(4.7), Inches(12), Inches(0.4),
         "▍核心收益", size=15, color=C_PRIMARY, bold=True)
gains = [
    "扫描行数：994,910 → 1   （下降 99.9999%）",
    "查询耗时：420 ms → 0.46 ms   （提速 913 倍）",
    "filesort 消除：Using filesort → Using index condition（无需额外排序）",
    "回表消除：从逐行回表过滤 → 索引覆盖直接命中",
]
add_bullets(s, Inches(0.55), Inches(5.1), Inches(12.4), Inches(1.9), gains, size=14, gap=6)
footer(s)

# =====================================================================
# 7. 第2幕 索引异常6类
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "04  第2幕 · 索引异常六大失效场景（demo.sql）", 7)
src_tag(s, Inches(0.55), Inches(1.25), "demo.sql 第2幕")

add_text(s, Inches(0.55), Inches(1.6), Inches(12), Inches(0.4),
         "6 类失效场景均有 ✗ 失效 / ✓ 命中 真实 EXPLAIN 对照",
         size=14, color=C_GRAY)

# 6 场景卡片
scenes = [
    ("2.1 隐式类型转换", "order_no VARCHAR 传数字 123",
     "✗ ALL/NULL/996896", "✓ const/uk_order_no/1", C_RED, C_GREEN),
    ("2.2 函数作用于列", "LEFT(order_no,13) = ...",
     "✗ ALL/NULL/996896", "✓ range/uk_order_no/10", C_RED, C_GREEN),
    ("2.3 LIKE 左模糊", "product_name LIKE '%关键词%'",
     "✗ ALL/NULL/9904", "✓ range/idx_product_name/100", C_RED, C_GREEN),
    ("2.4 违反最左前缀", "复合索引跳过 user_id",
     "✗ ALL/NULL/996896", "✓ range/idx_user_status_created", C_RED, C_GREEN),
    ("2.5 OR 连接非索引列", "user_id=1 OR total_amount>9000",
     "✗ ALL/NULL/996896", "✓ UNION ALL 各自走索引", C_RED, C_GREEN),
    ("2.6 不等于 / NOT IN", "user_id != 12345",
     "✗ ALL/NULL/996896", "✓ IN 明确列表", C_RED, C_GREEN),
]
for i, (title, desc, bad, good, cb, cg) in enumerate(scenes):
    row = i // 3; coln = i % 3
    x = 0.55 + coln * 4.15; y = 2.1 + row * 2.35
    add_rect(s, Inches(x), Inches(y), Inches(3.95), Inches(2.15), C_LIGHT)
    add_rect(s, Inches(x), Inches(y), Inches(3.95), Inches(0.4), C_PRIMARY)
    add_text(s, Inches(x + 0.1), Inches(y + 0.05), Inches(3.75), Inches(0.3),
             title, size=12, color=C_WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(x + 0.15), Inches(y + 0.5), Inches(3.65), Inches(0.4),
             desc, size=11, color=C_DARK, font=FONT_CODE)
    add_text(s, Inches(x + 0.15), Inches(y + 0.95), Inches(3.65), Inches(0.5),
             bad, size=11, color=C_RED, bold=True, font=FONT_CODE)
    add_text(s, Inches(x + 0.15), Inches(y + 1.5), Inches(3.65), Inches(0.5),
             good, size=11, color=C_GREEN, bold=True, font=FONT_CODE)

add_text(s, Inches(0.55), Inches(6.85), Inches(12), Inches(0.3),
         "第2.7节：performance_schema 检测冗余索引（COUNT_READ=0 的可清理）",
         size=11, color=C_GRAY, font=FONT_CODE)
footer(s)

# =====================================================================
# 8. 第2幕 索引异常代码演示
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "04  第2幕 · 索引异常改写演示", 8)
src_tag(s, Inches(0.55), Inches(1.25), "demo.sql 第2.1节")

add_text(s, Inches(0.55), Inches(1.6), Inches(6), Inches(0.4),
         "▍隐式类型转换（2.1）", size=14, color=C_RED, bold=True)
add_code(s, 0.55, 2.0, 6.0, 2.2,
         "-- ✗ 失效：order_no 为 VARCHAR\n"
         "-- 传数字字面量 → 隐式转换 → 索引失效\n"
         "EXPLAIN SELECT * FROM t_order\n"
         "WHERE order_no = 123;\n"
         "-- type=ALL  key=NULL  rows=996896\n\n"
         "-- ✓ 命中：传字符串字面量\n"
         "EXPLAIN SELECT * FROM t_order\n"
         "WHERE order_no = 'NO000000000123';\n"
         "-- type=const  key=uk_order_no  rows=1", size=11)

add_text(s, Inches(6.85), Inches(1.6), Inches(6), Inches(0.4),
         "▍函数作用于列（2.2）", size=14, color=C_RED, bold=True)
add_code(s, 6.85, 2.0, 6.0, 2.2,
         "-- ✗ 失效：LEFT() 函数作用于索引列\n"
         "EXPLAIN SELECT * FROM t_order\n"
         "WHERE LEFT(order_no,13) = 'NO00000000012';\n"
         "-- type=ALL  key=NULL  rows=996896\n\n"
         "-- ✓ 命中：改写为 LIKE 前缀\n"
         "EXPLAIN SELECT * FROM t_order\n"
         "WHERE order_no LIKE 'NO00000000012%';\n"
         "-- type=range  key=uk_order_no  rows=10", size=11)

add_text(s, Inches(0.55), Inches(4.4), Inches(6), Inches(0.4),
         "▍违反最左前缀（2.4）", size=14, color=C_RED, bold=True)
add_code(s, 0.55, 4.8, 6.0, 2.2,
         "-- ✗ 失效：复合索引跳过最左列 user_id\n"
         "EXPLAIN SELECT * FROM t_order\n"
         "WHERE status = 1\n"
         "  AND created_at > '2025-01-01';\n"
         "-- type=ALL  key=NULL  rows=996896\n\n"
         "-- ✓ 命中：带最左列 user_id\n"
         "EXPLAIN SELECT * FROM t_order\n"
         "WHERE user_id = 12345 AND status = 1\n"
         "  AND created_at > '2025-01-01';\n"
         "-- type=range  key=idx_user_status_created", size=11)

add_text(s, Inches(6.85), Inches(4.4), Inches(6), Inches(0.4),
         "▍冗余索引检测（2.7）", size=14, color=C_BLUE, bold=True)
add_code(s, 6.85, 4.8, 6.0, 2.2,
         "-- 查询各索引被读取次数\n"
         "SELECT object_name AS tbl,\n"
         "       index_name,\n"
         "       COUNT_READ AS read_cnt\n"
         "FROM performance_schema\n"
         "  .table_io_waits_summary_by_index_usage\n"
         "WHERE object_schema='shop_demo'\n"
         "  AND index_name IS NOT NULL\n"
         "ORDER BY COUNT_READ ASC\n"
         "LIMIT 10;\n"
         "-- read_cnt=0 的索引为冗余，可清理", size=11)
footer(s)

# =====================================================================
# 9. 第3幕 主从延迟
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "05  第3幕 · 主从延迟调优参数（demo.sql）", 9)
src_tag(s, Inches(0.55), Inches(1.25), "demo.sql 第3幕")

add_text(s, Inches(0.55), Inches(1.6), Inches(12), Inches(0.4),
         "故障现象：大促下单写入激增，从库延迟 120s+，报表读到旧数据",
         size=14, color=C_GRAY)

# 调优前/后对比
add_rect(s, Inches(0.55), Inches(2.1), Inches(6.0), Inches(2.0), C_LIGHT)
add_rect(s, Inches(0.55), Inches(2.1), Inches(6.0), Inches(0.45), C_RED)
add_text(s, Inches(0.55), Inches(2.1), Inches(6.0), Inches(0.45),
         "调优前：单线程串行回放", size=14, color=C_WHITE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_bullets(s, Inches(0.75), Inches(2.65), Inches(5.6), Inches(1.4),
    ["从库 SQL 线程单线程回放 binlog",
     "跟不上主库并发写入",
     "Seconds_Behind_Master = 120s+",
     "报表读到旧数据，业务异常"], size=12, gap=4)

add_rect(s, Inches(6.85), Inches(2.1), Inches(6.0), Inches(2.0), C_LIGHT)
add_rect(s, Inches(6.85), Inches(2.1), Inches(6.0), Inches(0.45), C_GREEN)
add_text(s, Inches(6.85), Inches(2.1), Inches(6.0), Inches(0.45),
         "调优后：多线程并行复制 MTS", size=14, color=C_WHITE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_bullets(s, Inches(7.05), Inches(2.65), Inches(5.6), Inches(1.4),
    ["LOGICAL_CLOCK 按组提交并行回放",
     "replica_parallel_workers = 8",
     "preserve_commit_order = ON",
     "Seconds_Behind_Master < 5s"], size=12, gap=4)

# SHOW VARIABLES 代码
add_text(s, Inches(0.55), Inches(4.3), Inches(12), Inches(0.4),
         "▍现场执行命令（demo.sql 第3.1节）", size=14, color=C_PRIMARY, bold=True)
add_code(s, 0.55, 4.7, 12.3, 2.3,
         "SHOW VARIABLES WHERE Variable_name IN\n"
         " ('slave_parallel_type','slave_parallel_workers','slave_preserve_commit_order',\n"
         "  'binlog_transaction_dependency_tracking','binlog_format','server_id');\n\n"
         "-- 调优要点：\n"
         "-- 1) slave_parallel_type = LOGICAL_CLOCK   按主库组提交并行回放\n"
         "-- 2) slave_parallel_workers = 8            8 线程并行（默认4）\n"
         "-- 3) slave_preserve_commit_order = ON      从库提交顺序与主库一致\n"
         "-- 4) binlog_transaction_dependency_tracking = WRITESET  提升并行度", size=11)
footer(s)

# =====================================================================
# 10. 第4幕 死锁
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "06  第4幕 · 事务死锁（deadlock_session_a/b.sql）", 10)
src_tag(s, Inches(0.55), Inches(1.25), "deadlock_session_a/b.sql")

add_text(s, Inches(0.55), Inches(1.6), Inches(12), Inches(0.4),
         "AB-BA 死锁：会话A 锁 p1 等 p2，会话B 锁 p2 等 p1 → InnoDB 回滚 B",
         size=14, color=C_GRAY)

# 时序图
add_text(s, Inches(0.55), Inches(2.05), Inches(6), Inches(0.4),
         "▍时序表", size=14, color=C_PRIMARY, bold=True)
seq_heads = ["时刻", "窗口A (session_a)", "窗口B (session_b)"]
seq_rows = [
    ("t1", "UPDATE p1 锁定 product_id=1", "—"),
    ("t2", "—", "UPDATE p2 锁定 product_id=2"),
    ("t3", "UPDATE p2 → 被B阻塞", "—"),
    ("t4", "—", "UPDATE p1 → 死锁环形成"),
    ("结果", "继续等待", "ERROR 1213 被回滚"),
]
add_rect(s, Inches(0.55), Inches(2.45), Inches(6.0), Inches(0.4), C_PRIMARY)
for j, ht in enumerate(seq_heads):
    add_text(s, Inches(0.55 + j * 2.0), Inches(2.45), Inches(2.0), Inches(0.4), ht,
             size=11, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
for i, row in enumerate(seq_rows):
    y = 2.85 + i * 0.38
    add_rect(s, Inches(0.55), Inches(y), Inches(6.0), Inches(0.36), C_LIGHT if i % 2 == 0 else C_WHITE)
    for j, v in enumerate(row):
        c = C_RED if "ERROR" in v else (C_DARK if j == 0 else C_GRAY)
        add_text(s, Inches(0.55 + j * 2.0), Inches(y), Inches(2.0), Inches(0.36), v,
                 size=10, color=c, bold=(j == 0 or "ERROR" in v),
                 align=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT,
                 anchor=MSO_ANCHOR.MIDDLE)

# 死锁日志
add_text(s, Inches(6.85), Inches(2.05), Inches(6), Inches(0.4),
         "▍真实死锁日志（SHOW ENGINE INNODB STATUS）", size=14, color=C_RED, bold=True)
add_code(s, 6.85, 2.45, 6.0, 2.85,
         "*** (1) TRANSACTION:\n"
         "HOLDS THE LOCK(S): product_id=1\n"
         "WAITING FOR: product_id=2\n"
         "*** (2) TRANSACTION:\n"
         "HOLDS THE LOCK(S): product_id=2\n"
         "WAITING FOR: product_id=1\n"
         "*** WE ROLL BACK TRANSACTION (2)\n"
         "ERROR 1213: Deadlock found", size=11)

# 操作流程
add_text(s, Inches(0.55), Inches(5.0), Inches(12), Inches(0.4),
         "▍现场操作流程（3步）", size=14, color=C_PRIMARY, bold=True)
add_code(s, 0.55, 5.4, 12.3, 1.6,
         "-- 步骤1 窗口A: 锁定 p1\n"
         "mysql> source deadlock_session_a.sql     -- UPDATE t_product SET stock=stock-1 WHERE product_id=1;\n\n"
         "-- 步骤2 窗口B: 锁 p2 后尝试 p1 → 触发 ERROR 1213\n"
         "mysql> source deadlock_session_b.sql     -- UPDATE ... product_id=2; UPDATE ... product_id=1;\n\n"
         "-- 步骤3 窗口A: 提交释放锁\n"
         "mysql> source deadlock_session_a_commit.sql", size=11)
footer(s)

# =====================================================================
# 11. 第4幕 死锁调优方案
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "06  第4幕 · 死锁调优方案", 11)

add_text(s, Inches(0.55), Inches(1.3), Inches(12), Inches(0.4),
         "根因：两个事务以相反顺序更新同一批商品行 → wait-for 环",
         size=14, color=C_GRAY)

# 调优方案4层
add_text(s, Inches(0.55), Inches(1.8), Inches(12), Inches(0.4),
         "▍四层防御", size=15, color=C_PRIMARY, bold=True)
defs = [
    ("① 统一加锁顺序", "所有扣库存按 product_id 升序\n治本：从源头消除反向环", C_GREEN),
    ("② 乐观重试", "捕获 ERROR 1213 重试 2-3 次\n兜底：偶发死锁自动恢复", C_BLUE),
    ("③ 短事务", "拆分大事务，减少锁持有时间\n降低死锁概率", C_TEAL),
    ("④ 热点分桶", "热点商品库存分桶扣减\n降低单行锁竞争", C_ACCENT),
]
for i, (t, d, col) in enumerate(defs):
    x = 0.55 + i * 3.1
    add_rect(s, Inches(x), Inches(2.25), Inches(2.95), Inches(2.0), C_LIGHT)
    add_rect(s, Inches(x), Inches(2.25), Inches(2.95), Inches(0.45), col)
    add_text(s, Inches(x), Inches(2.25), Inches(2.95), Inches(0.45),
             t, size=13, color=C_WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(x + 0.15), Inches(2.8), Inches(2.65), Inches(1.4),
             d, size=11, color=C_GRAY, line_spacing=1.3,
             align=PP_ALIGN.CENTER)

# 正确写法代码
add_text(s, Inches(0.55), Inches(4.5), Inches(12), Inches(0.4),
         "▍正确写法：按 product_id 升序加锁", size=14, color=C_GREEN, bold=True)
add_code(s, 0.55, 4.9, 12.3, 2.1,
         "-- 调优后：所有事务统一按 product_id 升序扣减库存\n"
         "-- 会话A 和 会话B 都按 1→2→3 顺序，不再形成反向环\n"
         "START TRANSACTION;\n"
         "UPDATE t_product SET stock = stock - 1 WHERE product_id = 1;  -- 先锁小id\n"
         "UPDATE t_product SET stock = stock - 1 WHERE product_id = 2;  -- 再锁大id\n"
         "UPDATE t_product SET stock = stock - 1 WHERE product_id = 3;\n"
         "COMMIT;\n"
         "-- 效果：死锁频发 → 0", size=11)
footer(s)

# =====================================================================
# 12. 第5幕 锁等待
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "07  第5幕 · 锁等待超时（lock_wait_session_a/b.sql）", 12)
src_tag(s, Inches(0.55), Inches(1.25), "lock_wait_session_a/b.sql")

add_text(s, Inches(0.55), Inches(1.6), Inches(12), Inches(0.4),
         "长事务持锁不提交，另一会话更新同行 → 5s 后 ERROR 1205 超时",
         size=14, color=C_GRAY)

# 时序图
add_text(s, Inches(0.55), Inches(2.05), Inches(6), Inches(0.4),
         "▍时序表", size=14, color=C_PRIMARY, bold=True)
lw_rows = [
    ("t1", "窗口A: 开事务更新 p1 不提交", "持锁 RUNNING"),
    ("t2", "—", "窗口B: 尝试更新 p1"),
    ("t3", "持续持锁 5s", "被阻塞等待"),
    ("t4", "—", "ERROR 1205 超时回滚"),
    ("t5", "source ..._commit.sql 提交", "锁释放"),
]
add_rect(s, Inches(0.55), Inches(2.45), Inches(6.0), Inches(0.4), C_PRIMARY)
add_text(s, Inches(0.55), Inches(2.45), Inches(1.0), Inches(0.4), "时刻",
         size=11, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(1.55), Inches(2.45), Inches(2.5), Inches(0.4), "窗口A",
         size=11, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(4.05), Inches(2.45), Inches(2.5), Inches(0.4), "窗口B / 状态",
         size=11, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
for i, (t, a, b) in enumerate(lw_rows):
    y = 2.85 + i * 0.38
    add_rect(s, Inches(0.55), Inches(y), Inches(6.0), Inches(0.36), C_LIGHT if i % 2 == 0 else C_WHITE)
    add_text(s, Inches(0.55), Inches(y), Inches(1.0), Inches(0.36), t,
             size=10, color=C_DARK, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    c = C_RED if "ERROR" in b else C_GRAY
    add_text(s, Inches(1.55), Inches(y), Inches(2.5), Inches(0.36), a,
             size=10, color=c, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(4.05), Inches(y), Inches(2.5), Inches(0.36), b,
             size=10, color=c, bold="ERROR" in b, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

# 关键参数 + 日志
add_text(s, Inches(6.85), Inches(2.05), Inches(6), Inches(0.4),
         "▍关键参数与日志", size=14, color=C_RED, bold=True)
add_code(s, 6.85, 2.45, 6.0, 2.85,
         "-- 锁等待超时调为 5s（演示用）\n"
         "SET SESSION innodb_lock_wait_timeout = 5;\n\n"
         "-- 窗口B 执行后 5s 报错：\n"
         "ERROR 1205 (HY000):\n"
         "Lock wait timeout exceeded;\n"
         "try restarting transaction\n\n"
         "-- 查看持锁事务\n"
         "SELECT * FROM information_schema.INNODB_TRX;", size=11)

# 调优方案
add_text(s, Inches(0.55), Inches(5.0), Inches(12), Inches(0.4),
         "▍调优方案", size=14, color=C_PRIMARY, bold=True)
lw_fix = [
    "长事务拆分：批量改价每 500 条 commit 一次（避免长持锁）",
    "快速失败：innodb_lock_wait_timeout 调小，业务侧 5s 超时 + 重试",
    "乐观锁：UPDATE 时带 version 字段冲突重试，避免行锁竞争",
    "避峰操作：改价放低峰期，监控告警超 5s 的长事务",
]
add_bullets(s, Inches(0.55), Inches(5.4), Inches(12.4), Inches(1.6), lw_fix, size=13, gap=6)
footer(s)

# =====================================================================
# 13. 综合成果
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "08  综合调优成果", 13)

add_text(s, Inches(0.55), Inches(1.2), Inches(12), Inches(0.4),
         "5 大瓶颈真实复现 + 调优，全部数据来自 9 个 SQL 脚本实测",
         size=14, color=C_GRAY)

# 成果表
hx = [0.55, 2.4, 4.5, 7.8, 10.9]
hw = [1.8, 2.0, 3.2, 3.0, 2.0]
heads = ["瓶颈", "脚本", "调优前", "调优后", "效果"]
add_rect(s, Inches(0.55), Inches(1.7), Inches(12.0), Inches(0.45), C_PRIMARY)
for i, ht in enumerate(heads):
    add_text(s, Inches(hx[i]), Inches(1.7), Inches(hw[i]), Inches(0.45), ht,
             size=13, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
results = [
    ("慢查询", "demo.sql", "ALL/NULL/994910行\n420ms+filesort", "range/复合索引/1行\n0.46ms+IC", "913x"),
    ("索引异常", "demo.sql", "6类失效\n全表扫描", "6类改写\n全部命中", "全表→索引"),
    ("死锁", "deadlock_a/b.sql", "AB-BA 频发\nERROR 1213", "统一加锁顺序\n乐观重试", "→ 0"),
    ("锁等待", "lock_wait_a/b.sql", "长事务持锁\nERROR 1205", "分批提交\n快速失败", "5s超时"),
    ("主从延迟", "demo.sql", "单线程 120s+", "8线程并行 MTS\n<5s", "↓96%"),
]
colors = [C_BLUE, C_TEAL, C_RED, C_BLUE, C_ACCENT]
for i, (name, scr, before, after, eff) in enumerate(results):
    y = 2.15 + i * 0.78
    add_rect(s, Inches(0.55), Inches(y), Inches(12.0), Inches(0.74), C_LIGHT if i % 2 == 0 else C_WHITE)
    add_rect(s, Inches(0.55), Inches(y), Inches(0.06), Inches(0.74), colors[i])
    add_text(s, Inches(0.7), Inches(y), Inches(1.6), Inches(0.74), name,
             size=12, color=C_PRIMARY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(2.4), Inches(y), Inches(2.0), Inches(0.74), scr,
             size=9, color=C_GRAY, font=FONT_CODE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(4.5), Inches(y), Inches(3.2), Inches(0.74), before,
             size=10, color=C_RED, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)
    add_text(s, Inches(7.8), Inches(y), Inches(3.0), Inches(0.74), after,
             size=10, color=C_GREEN, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)
    add_text(s, Inches(10.9), Inches(y), Inches(2.0), Inches(0.74), eff,
             size=13, color=C_ACCENT, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)

add_text(s, Inches(0.55), Inches(6.2), Inches(12), Inches(0.8),
         "全链路闭环：监控 → 定位 → 分析 → 调优 → 验证 → 沉淀\n"
         "9 个 SQL 脚本可在 mysql cmd 用 source 逐个执行，全部真实可复现",
         size=12, color=C_GRAY, line_spacing=1.4)
footer(s)

# =====================================================================
# 14. 脚本清单
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "08  9 个 SQL 脚本清单", 14)

add_text(s, Inches(0.55), Inches(1.2), Inches(12), Inches(0.4),
         "全部脚本可在 mysql cmd 用 source 执行，无 Python 依赖",
         size=14, color=C_GRAY)

scripts = [
    ("01_schema.sql", "建表", "5张表 + 慢查询/死锁参数", C_BLUE),
    ("02_init_data.sql", "造数", "5万用户/100万订单/128万明细", C_TEAL),
    ("demo.sql", "主演示", "第0-3幕 环境核对+慢查询+索引异常+主从", C_ACCENT),
    ("deadlock_session_a.sql", "死锁A", "会话A 锁 product_id=1", C_RED),
    ("deadlock_session_b.sql", "死锁B", "会话B 触发 ERROR 1213", C_RED),
    ("deadlock_session_a_commit.sql", "死锁A提交", "会话A 提交释放锁", C_RED),
    ("lock_wait_session_a.sql", "锁等待A", "长事务持锁不提交", C_BLUE),
    ("lock_wait_session_b.sql", "锁等待B", "触发 ERROR 1205", C_BLUE),
    ("lock_wait_session_a_commit.sql", "锁等待A提交", "会话A 提交释放锁", C_BLUE),
]
for i, (f, role, desc, col) in enumerate(scripts):
    row = i // 3; coln = i % 3
    x = 0.55 + coln * 4.15; y = 1.85 + row * 1.35
    add_rect(s, Inches(x), Inches(y), Inches(3.95), Inches(1.2), C_LIGHT)
    add_rect(s, Inches(x), Inches(y), Inches(0.08), Inches(1.2), col)
    add_text(s, Inches(x + 0.2), Inches(y + 0.1), Inches(3.65), Inches(0.35),
             f, size=12, color=C_PRIMARY, bold=True, font=FONT_CODE)
    add_text(s, Inches(x + 0.2), Inches(y + 0.48), Inches(3.65), Inches(0.3),
             role, size=11, color=col, bold=True)
    add_text(s, Inches(x + 0.2), Inches(y + 0.78), Inches(3.65), Inches(0.35),
             desc, size=10, color=C_GRAY)

# 执行命令
add_text(s, Inches(0.55), Inches(6.1), Inches(12), Inches(0.4),
         "▍cmd 执行流程", size=14, color=C_PRIMARY, bold=True)
add_code(s, 0.55, 6.5, 12.3, 0.7,
         "mysql> source 01_schema.sql; source 02_init_data.sql; source demo.sql  -- 单窗口主演示\n"
         "-- 死锁/锁等待：另开两个窗口分别 source session_a.sql 和 session_b.sql", size=11)
footer(s)

# =====================================================================
# 15. 谢谢
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s, C_DARK)
add_rect(s, 0, 0, SW, Inches(0.35), C_ACCENT)
add_rect(s, 0, SH - Inches(0.35), SW, Inches(0.35), C_ACCENT)
add_text(s, Inches(1.0), Inches(2.8), Inches(11.3), Inches(1.2),
         "谢谢观看", size=54, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER)
add_rect(s, Inches(5.4), Inches(4.2), Inches(2.5), Inches(0.06), C_ACCENT)
add_text(s, Inches(1.0), Inches(4.5), Inches(11.3), Inches(0.6),
         "9 个 SQL 脚本真实可复现  ·  全部数据来自 MySQL 8.0 实测",
         size=16, color=RGBColor(0xC8, 0xD4, 0xE6), align=PP_ALIGN.CENTER)
add_text(s, Inches(1.0), Inches(5.5), Inches(11.3), Inches(0.5),
         "Q & A",
         size=22, color=C_ACCENT, bold=True, align=PP_ALIGN.CENTER)

# =====================================================================
# 保存
# =====================================================================
out = "/workspace/db_optimization_demo/ppt/全链路性能瓶颈排查与综合调优_脚本对齐版.pptx"
prs.save(out)
print("✅ 已生成:", out)
print("幻灯片数:", len(prs.slides))
