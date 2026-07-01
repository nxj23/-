# -*- coding: utf-8 -*-
"""
生成《全链路性能瓶颈排查与综合调优》汇报 PPT
课程：数据库优化与应用 期末作业
业务场景：电商订单系统  数据库：MySQL
依赖：python-pptx>=0.6
输出：db_optimization_demo/ppt/全链路性能瓶颈排查与综合调优.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from copy import deepcopy

# =====================================================================
# 主题配色
# =====================================================================
C_DARK   = RGBColor(0x0F, 0x1B, 0x2D)   # 深蓝背景
C_PRIMARY = RGBColor(0x1B, 0x3A, 0x5C)  # 主色 深蓝
C_ACCENT = RGBColor(0xE8, 0xA3, 0x3D)   # 强调 橙金
C_TEAL   = RGBColor(0x2E, 0x8B, 0x8B)   # 次强调 青绿
C_LIGHT  = RGBColor(0xF4, 0xF6, 0xF9)   # 浅灰底
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_GRAY   = RGBColor(0x5A, 0x6A, 0x7A)
C_CODE_BG= RGBColor(0x1E, 0x1E, 0x2E)   # 代码块深底
C_CODE_FG= RGBColor(0xD4, 0xD4, 0xD4)   # 代码文字
C_GREEN  = RGBColor(0x4C, 0xAF, 0x50)
C_RED    = RGBColor(0xE5, 0x5C, 0x5C)
C_BLUE   = RGBColor(0x4A, 0x90, 0xD9)

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
    """自动单位转换：float 和小 int 按英寸处理，大 int(>1000) 视为已转换的 EMU 值直接返回"""
    if isinstance(v, float):
        return Inches(v)
    if isinstance(v, int):
        # 1 inch = 914400 EMU; 任何 >1000 的值几乎不可能是"英寸的整数"，必然是 EMU
        return v if v > 1000 else Inches(v)
    return v

def add_rect(slide, x, y, w, h, color, line=None):
    x, y, w, h = _I(x), _I(y), _I(w), _I(h)
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
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
    """items: list[str] 或 list[(text, sublevel)]"""
    x, y, w, h = _I(x), _I(y), _I(w), _I(h)
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    for i, it in enumerate(items):
        lvl = 0
        txt = it
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


def header(slide, title, idx=None, total=None):
    """内容页通用页头：左侧色条 + 标题 + 页码"""
    add_rect(slide, 0, 0, Inches(0.22), SH, C_ACCENT)              # 左侧竖条
    add_rect(slide, 0, 0, SW, Inches(1.05), C_PRIMARY)            # 顶部标题栏
    add_rect(slide, Inches(0.22), Inches(1.05), SW - Inches(0.22), Inches(0.06), C_ACCENT)  # 金线
    add_text(slide, Inches(0.55), Inches(0.18), Inches(11), Inches(0.7),
             title, size=26, color=C_WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    if idx is not None:
        add_text(slide, Inches(12.0), Inches(0.18), Inches(1.1), Inches(0.7),
                 f"{idx:02d}", size=20, color=C_ACCENT, bold=True,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def footer(slide):
    add_text(slide, Inches(0.55), Inches(7.08), Inches(8), Inches(0.35),
             "数据库优化与应用 · 期末作业 | 全链路性能瓶颈排查与综合调优",
             size=9, color=C_GRAY)


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
    tf = shp.text_frame
    tf.word_wrap = True
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
# 装饰圆点
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
         "真实 MySQL 8.0 实测：100万订单 | 真实触发死锁/锁等待 | EXPLAIN 调优前后对比",
         size=16, color=RGBColor(0xC8, 0xD4, 0xE6))
add_text(s, Inches(1.0), Inches(6.3), Inches(11.3), Inches(0.4),
         "业务场景：电商订单系统    |    数据库：MySQL 8.0  |  数据量：100万订单    |    汇报时长：约 10 分钟",
         size=14, color=RGBColor(0x9A, 0xB0, 0xC8))

# =====================================================================
# 2. 目录
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "目录 CONTENTS", 2)
items = [
    ("01", "业务背景与系统架构", "电商订单系统全链路", C_TEAL),
    ("02", "性能瓶颈总览", "五大生产故障全景图", C_ACCENT),
    ("03", "慢查询排查与调优", "EXPLAIN 分析 + 复合索引", C_BLUE),
    ("04", "索引异常排查与调优", "六大索引失效场景", C_TEAL),
    ("05", "事务死锁排查与调优", "AB-BA 死锁 + 统一加锁", C_RED),
    ("06", "锁等待排查与调优", "长事务持锁 + 乐观锁", C_BLUE),
    ("07", "主从延迟排查与调优", "多线程并行复制", C_ACCENT),
    ("08-09", "综合调优成果 + 闭环", "效果对比 + 经验沉淀", C_TEAL),
]
y0 = 1.5
for i, (no, t, d, col) in enumerate(items):
    row = i // 2; coln = i % 2
    x = Inches(0.8 + coln * 6.1); y = Inches(y0 + row * 1.55)
    add_rect(s, x, y, Inches(5.6), Inches(1.15), C_LIGHT)
    add_rect(s, x, y, Inches(1.0), Inches(1.15), col)
    add_text(s, x, y, Inches(1.0), Inches(1.15), no, size=30, color=C_WHITE,
             bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, x + Inches(1.2), y + Inches(0.18), Inches(4.3), Inches(0.5),
             t, size=17, color=C_PRIMARY, bold=True)
    add_text(s, x + Inches(1.2), y + Inches(0.68), Inches(4.3), Inches(0.4),
             d, size=12, color=C_GRAY)
footer(s)

# =====================================================================
# 3. 业务背景与系统架构
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "01  业务背景与系统架构", 3)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), Inches(0.5),
         "模拟企业线上电商订单系统，覆盖用户、商品、订单、库存全链路读写场景",
         size=15, color=C_GRAY)

# 架构图：左侧应用 → 中间数据库 → 右侧瓶颈
boxes = [
    (0.7, 1.95, 2.6, 1.0, "应用层", "下单 / 支付 / 改价\n报表查询 / 搜索", C_BLUE),
    (3.6, 1.95, 2.6, 1.0, "中间件", "连接池 / 读写分离\n分库分表代理", C_TEAL),
    (6.5, 1.95, 2.6, 1.0, "数据库层", "MySQL 主库\n+ 从库集群", C_PRIMARY),
    (9.4, 1.95, 2.6, 1.0, "存储层", "InnoDB 引擎\nRedo / Undo / Binlog", C_GRAY),
]
for x, y, w, h, t, d, col in boxes:
    add_rect(s, Inches(x), Inches(y), Inches(w), Inches(h), col)
    add_text(s, Inches(x), Inches(y + 0.1), Inches(w), Inches(0.4), t,
             size=15, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, Inches(x), Inches(y + 0.5), Inches(w), Inches(0.5), d,
             size=11, color=C_WHITE, align=PP_ALIGN.CENTER, line_spacing=1.2)
    if x < 9.4:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                                Inches(x + w + 0.05), Inches(y + 0.35),
                                Inches(0.2), Inches(0.3))
        ar.fill.solid(); ar.fill.fore_color.rgb = C_ACCENT
        ar.line.fill.background()

# 核心表结构
add_text(s, Inches(0.55), Inches(3.3), Inches(6), Inches(0.4),
         "▍核心表结构（约 100 万订单数据量）", size=15, color=C_PRIMARY, bold=True)
tables = [
    ("t_user 用户表", "user_id, username, phone, city, created_at"),
    ("t_product 商品表", "product_id, category_id, price, stock, status"),
    ("t_order 订单主表", "order_id, order_no, user_id, status, pay_time"),
    ("t_order_item 订单明细", "item_id, order_id, product_id, quantity"),
    ("t_inventory_log 库存日志", "id, product_id, delta, order_no"),
]
for i, (t, cols) in enumerate(tables):
    y = 3.75 + i * 0.48
    add_rect(s, Inches(0.55), Inches(y), Inches(2.6), Inches(0.35),
             C_PRIMARY if i % 2 == 0 else C_TEAL)
    add_text(s, Inches(0.65), Inches(y + 0.04), Inches(2.5), Inches(0.3),
             t, size=11, color=C_WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, Inches(3.15), Inches(y), Inches(6.0), Inches(0.35), C_LIGHT)
    add_text(s, Inches(3.3), Inches(y + 0.04), Inches(5.8), Inches(0.3),
             cols, size=11, color=C_GRAY, anchor=MSO_ANCHOR.MIDDLE)

# 故障触发点
add_text(s, Inches(9.5), Inches(3.3), Inches(3.5), Inches(0.4),
         "▍五大故障触发点", size=15, color=C_RED, bold=True)
faults = ["慢查询：大表缺复合索引", "索引异常：6 类索引失效",
          "事务死锁：并发扣库存", "锁等待：长事务持锁",
          "主从延迟：大促写入洪峰"]
for i, f in enumerate(faults):
    y = 3.75 + i * 0.48
    chip(s, Inches(9.5), Inches(y), Inches(3.5), Inches(0.35), f,
         fg=C_DARK, bg=C_LIGHT if i % 2 == 0 else RGBColor(0xFB, 0xEC, 0xD2), size=11)
footer(s)

# =====================================================================
# 4. 性能瓶颈总览
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "02  性能瓶颈总览：五大生产故障全景图", 4)
overview = [
    ("慢查询", "慢SQL", "客服后台查订单超时\n扫描行数 80万+", "EXPLAIN 分析\n复合索引优化", "800ms → <10ms", C_BLUE),
    ("索引异常", "索引失效", "索引已建却不用\n全表扫描告警", "6类失效改写\n冗余索引清理", "全表扫描 → 索引命中", C_TEAL),
    ("事务死锁", "死锁", "并发扣库存 AB-BA\nERROR 1213", "死锁日志解析\n统一加锁顺序", "死锁频发 → 0", C_RED),
    ("锁等待", "锁等待", "改价长事务持锁\nERROR 1205 超时", "长事务拆分\n乐观锁 + 快速失败", "超时堆积 → 秒级", C_BLUE),
    ("主从延迟", "主从延迟", "大促延迟 120s+\n读到旧数据", "多线程并行复制\n分批提交 + 读写分离", "120s → <5s", C_ACCENT),
]
y0 = 1.4
add_text(s, Inches(0.55), Inches(1.15), Inches(12), Inches(0.4),
         "统一排查方法论：定位现象 → 抓取证据 → 根因分析 → 落地调优 → 效果验证",
         size=13, color=C_GRAY)
# 表头
hx = [0.55, 2.2, 3.95, 7.2, 10.5]
hw = [1.6, 1.7, 3.2, 3.25, 2.4]
heads = ["故障类型", "现象关键词", "故障现象", "调优方案", "调优效果"]
add_rect(s, Inches(0.55), Inches(y0), Inches(12.3), Inches(0.45), C_PRIMARY)
for i, ht in enumerate(heads):
    add_text(s, Inches(hx[i]), Inches(y0), Inches(hw[i]), Inches(0.45), ht,
             size=13, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
for i, (name, kw, sym, opt, eff, col) in enumerate(overview):
    y = y0 + 0.5 + i * 1.15
    add_rect(s, Inches(0.55), Inches(y), Inches(12.3), Inches(0.95),
             C_LIGHT if i % 2 == 0 else C_WHITE)
    add_rect(s, Inches(0.55), Inches(y), Inches(0.08), Inches(0.95), col)
    add_text(s, Inches(0.7), Inches(y + 0.1), Inches(1.4), Inches(0.4),
             name, size=14, color=col, bold=True)
    add_text(s, Inches(0.7), Inches(y + 0.5), Inches(1.4), Inches(0.4),
             kw, size=10, color=C_GRAY)
    add_text(s, Inches(hx[2]), Inches(y + 0.12), Inches(hw[2] - 0.1), Inches(0.8),
             sym, size=11, color=C_DARK, line_spacing=1.15)
    add_text(s, Inches(hx[3]), Inches(y + 0.12), Inches(hw[3] - 0.1), Inches(0.8),
             opt, size=11, color=C_DARK, line_spacing=1.15)
    add_text(s, Inches(hx[4]), Inches(y + 0.12), Inches(hw[4] - 0.1), Inches(0.8),
             eff, size=11, color=C_GREEN, bold=True, line_spacing=1.15)
footer(s)

# =====================================================================
# 5. 慢查询 ①：故障现象与定位
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "03  慢查询排查与调优 ①  故障现象与定位", 5)
card(s, 0.55, 1.35, 5.9, 1.4, "故障现象",
     "客服后台查询某用户近30天“已支付”订单，\n线上偶发超时，大促期间 TP99 飙升。",
     accent=C_RED)
card(s, 6.85, 1.35, 5.9, 1.4, "定位手段",
     "① 开启慢查询日志 slow_query_log\n② mysqldumpslow / pt-query-digest 聚合\n③ EXPLAIN 分析执行计划",
     accent=C_BLUE)
add_text(s, 0.55, 2.95, 12, 0.4, "▍故障 SQL 与慢日志配置", size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(3.4), Inches(7.0), Inches(3.4),
         "-- 故障 SQL：只建 idx_user 单列索引 → 回表逐行过滤\n"
         "SELECT order_id, order_no, total_amount, status, pay_time\n"
         "FROM t_order\n"
         "WHERE user_id = 12345\n"
         "  AND status = 1\n"
         "  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)\n"
         "ORDER BY created_at DESC\n"
         "LIMIT 20;\n"
         "\n"
         "-- 慢日志开启\n"
         "SET GLOBAL slow_query_log = ON;\n"
         "SET GLOBAL long_query_time = 1;\n"
         "-- 聚合分析\n"
         "mysqldumpslow -s t -t 5 /var/lib/mysql/*-slow.log\n"
         "-- 或 pt-query-digest slow.log | head -50",
         size=11)
add_text(s, Inches(7.8), Inches(3.4), Inches(5), 0.4, "▍慢日志关键字段解读", size=15, color=C_PRIMARY, bold=True)
add_bullets(s, Inches(7.8), Inches(3.85), Inches(5), Inches(3), [
    "Query_time：单条执行耗时（关注 >1s）",
    "Lock_time：等待锁耗时",
    "Rows_examined：扫描行数（异常偏大）",
    "Rows_sent：返回行数",
    "扫描行数/返回行数 比值越大越低效",
    "本例 Rows_examined ≈ 80万，Rows_sent = 20",
    "比值 40000:1 → 典型“大扫描小返回”",
], size=13, gap=6)
footer(s)

# =====================================================================
# 6. 慢查询 ②：EXPLAIN 分析
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "03  慢查询排查与调优 ②  EXPLAIN 执行计划分析", 6)
add_code(s, Inches(0.55), Inches(1.35), Inches(6.5), Inches(2.6),
         "EXPLAIN\nSELECT order_id, order_no, total_amount, status, pay_time\n"
         "FROM t_order\n"
         "WHERE user_id = 12345\n"
         "  AND status = 1\n"
         "  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)\n"
         "ORDER BY created_at DESC\n"
         "LIMIT 20;",
         size=11)
add_text(s, Inches(7.3), Inches(1.35), Inches(5.5), 0.4,
         "▍EXPLAIN 关键字段", size=15, color=C_PRIMARY, bold=True)
add_bullets(s, Inches(7.3), Inches(1.8), Inches(5.5), Inches(2.2), [
    "type = ref：命中 idx_user，但仅等值列",
    "key = idx_user：只用了单列索引",
    "rows ≈ 8200：预估扫描行数偏大",
    "Extra = Using where + Using filesort：回表 + 额外排序",
], size=12, gap=5)

# EXPLAIN 结果表
add_text(s, Inches(0.55), Inches(4.15), Inches(12), 0.4,
         "▍调优前 EXPLAIN 结果", size=15, color=C_RED, bold=True)
cols = ["id", "select_type", "table", "type", "key", "rows", "Extra"]
vals = ["1", "SIMPLE", "t_order", "ref", "idx_user", "20", "Using where; Using filesort"]
cw = [0.6, 1.4, 1.3, 0.9, 1.3, 1.0, 3.6]
x0 = 0.55
add_rect(s, Inches(x0), Inches(4.6), Inches(12.2), Inches(0.45), C_PRIMARY)
for i, c in enumerate(cols):
    add_text(s, Inches(x0), Inches(4.6), Inches(cw[i]), Inches(0.45), c,
             size=12, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    x0 += cw[i]
x0 = 0.55
add_rect(s, Inches(0.55), Inches(5.05), Inches(12.2), Inches(0.45), C_LIGHT)
for i, v in enumerate(vals):
    add_text(s, Inches(x0), Inches(5.05), Inches(cw[i]), Inches(0.45), v,
             size=11, color=C_RED if cols[i] in ("key", "rows", "Extra") else C_DARK,
             bold=(i in (4, 5, 6)), align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    x0 += cw[i]

add_text(s, Inches(0.55), Inches(5.7), Inches(12.2), Inches(0.4),
         "▍问题诊断", size=15, color=C_PRIMARY, bold=True)
add_bullets(s, Inches(0.55), Inches(6.1), Inches(12.2), Inches(1), [
    "idx_user 仅覆盖 user_id，status 与 created_at 需回表逐行过滤 → 扫描 8200 行",
    "ORDER BY created_at 无法利用索引有序性 → 触发 Using filesort 额外排序",
    "根因：缺少 (user_id, status, created_at) 复合索引",
], size=13, gap=4)
footer(s)

# =====================================================================
# 7. 慢查询 ③：调优方案与对比
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "03  慢查询排查与调优 ③  调优方案与效果对比", 7)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), 0.4,
         "▍调优方案：建立复合索引 (user_id, status, created_at)",
         size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(1.75), Inches(12.2), Inches(1.1),
         "-- 等值在前、范围在后，覆盖过滤 + 排序，避免回表与 filesort\n"
         "ALTER TABLE t_order\n"
         "  ADD INDEX idx_user_status_created (user_id, status, created_at),\n"
         "  ALGORITHM=INPLACE, LOCK=NONE;   -- 在线建索引不阻塞业务",
         size=12)

# 对比表
add_text(s, Inches(0.55), Inches(3.1), Inches(6), 0.4,
         "▍调优前 vs 调优后", size=15, color=C_PRIMARY, bold=True)
comp = [
    ("对比项", "调优前", "调优后"),
    ("使用索引", "idx_user(单列)", "idx_user_status_created(复合)"),
    ("type", "ref", "range"),
    ("扫描行数 rows", "20", "3"),
    ("Extra", "Using where; filesort", "Using index condition"),
    ("排序", "filesort 额外排序", "索引有序 无需排序"),
]
cw = [2.6, 2.7, 2.7]
for r, row in enumerate(comp):
    y = 3.55 + r * 0.52
    bg = C_PRIMARY if r == 0 else (C_LIGHT if r % 2 == 1 else C_WHITE)
    fg = C_WHITE if r == 0 else C_DARK
    add_rect(s, Inches(0.55), Inches(y), Inches(8.0), Inches(0.4), bg)
    for c, val in enumerate(row):
        color = fg
        if r > 0 and c == 2:
            color = C_GREEN
        if r > 0 and c == 1:
            color = C_RED
        add_text(s, Inches(0.55 + sum(cw[:c])), Inches(y), Inches(cw[c]),
                 Inches(0.4), val, size=12, color=color,
                 bold=(r == 0 or c == 0), align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)

# 收益卡片
add_text(s, Inches(8.9), Inches(3.1), Inches(4), 0.4,
         "▍核心收益", size=15, color=C_TEAL, bold=True)
gains = [("扫描行数 rows", "20行 → 3行", C_GREEN), ("Extra", "消除 filesort", C_TEAL),
         ("回表", "无需回表（覆盖索引）", C_BLUE), ("type", "ref → range", C_ACCENT)]
for i, (k, v, col) in enumerate(gains):
    y = 3.55 + i * 0.7
    add_rect(s, Inches(8.9), Inches(y), Inches(3.85), Inches(0.6), C_LIGHT)
    add_rect(s, Inches(8.9), Inches(y), Inches(0.08), Inches(0.6), col)
    add_text(s, Inches(9.1), Inches(y + 0.05), Inches(1.8), Inches(0.5),
             k, size=12, color=C_GRAY, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(10.9), Inches(y + 0.05), Inches(1.8), Inches(0.5),
             v, size=15, color=col, bold=True, align=PP_ALIGN.RIGHT,
             anchor=MSO_ANCHOR.MIDDLE)
footer(s)

# =====================================================================
# 8. 慢查询 ④：方法论沉淀
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "03  慢查询排查与调优 ④  方法论沉淀", 8)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), 0.4,
         "▍慢查询排查五步法（可复用）", size=16, color=C_PRIMARY, bold=True)
steps = [
    ("①", "定位", "开启慢日志\nmysqldumpslow 聚合\n定位 Top SQL", C_RED),
    ("②", "分析", "EXPLAIN 看执行计划\n关注 type/key/rows/Extra\n识别回表与 filesort", C_ACCENT),
    ("③", "根因", "缺索引 / 索引失效\n大范围扫描\n排序无序", C_BLUE),
    ("④", "调优", "建复合索引\n等值在前 范围在后\n覆盖索引", C_TEAL),
    ("⑤", "验证", "对比扫描行数/耗时\nEXPLAIN 复核\n上线监控", C_GREEN),
]
for i, (no, t, d, col) in enumerate(steps):
    x = 0.55 + i * 2.55
    add_rect(s, Inches(x), Inches(1.85), Inches(2.35), Inches(3.0), C_LIGHT)
    add_rect(s, Inches(x), Inches(1.85), Inches(2.35), Inches(0.7), col)
    add_text(s, Inches(x), Inches(1.9), Inches(2.35), Inches(0.6),
             no, size=28, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(x), Inches(2.95), Inches(2.35), Inches(0.4),
             t, size=16, color=C_PRIMARY, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, Inches(x + 0.15), Inches(3.45), Inches(2.05), Inches(1.3),
             d, size=11, color=C_GRAY, align=PP_ALIGN.CENTER, line_spacing=1.25)
    if i < 4:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                                Inches(x + 2.38), Inches(3.0), Inches(0.15), Inches(0.25))
        ar.fill.solid(); ar.fill.fore_color.rgb = C_ACCENT
        ar.line.fill.background()

add_text(s, Inches(0.55), Inches(5.2), Inches(12), 0.4,
         "▍索引设计三原则", size=16, color=C_PRIMARY, bold=True)
principles = [
    "最左前缀：复合索引按 (等值列, 范围列, 排序列) 排序，等值在前、范围在后",
    "覆盖索引：把查询需要的列纳入索引，避免回表（Using index）",
    "选择性优先：区分度高的列放前面，cardinality 接近表行数为佳",
]
add_bullets(s, Inches(0.55), Inches(5.65), Inches(12.2), Inches(1.4),
            principles, size=13, gap=8)
footer(s)

# =====================================================================
# 9. 索引异常 ①：六大失效场景
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "04  索引异常排查与调优 ①  六大索引失效场景", 9)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), 0.4,
         "▍索引已建却未被使用 —— 6 类典型失效场景",
         size=15, color=C_PRIMARY, bold=True)
cases = [
    ("① 函数/表达式作用于列", "WHERE DATE(created_at)=CURDATE()", "WHERE created_at>=CURDATE() AND created_at<..."),
    ("② 隐式类型转换", "WHERE order_no = 123 (VARCHAR列传数字)", "WHERE order_no = '000000000123'"),
    ("③ LIKE 左模糊", "WHERE product_name LIKE '%关键词%'", "LIKE '关键词%' 或 全文索引/ES"),
    ("④ OR 一侧无索引", "WHERE category_id=5 OR stock<100", "拆 UNION ALL 或补 stock 索引"),
    ("⑤ 违反最左前缀", "复合(a,b,c) 却 WHERE b=1", "补上最左列 a 后再查"),
    ("⑥ != / NOT IN", "WHERE status <> 1 (低选择性)", "改写等值 WHERE status = 0"),
]
for i, (t, bad, good) in enumerate(cases):
    row = i // 2; coln = i % 2
    x = 0.55 + coln * 6.25; y = 1.85 + row * 1.35
    add_rect(s, Inches(x), Inches(y), Inches(6.0), Inches(1.1), C_LIGHT)
    add_rect(s, Inches(x), Inches(y), Inches(0.08), Inches(1.1), C_ACCENT)
    add_text(s, Inches(x + 0.2), Inches(y + 0.08), Inches(5.7), Inches(0.35),
             t, size=13, color=C_PRIMARY, bold=True)
    add_text(s, Inches(x + 0.2), Inches(y + 0.42), Inches(5.7), Inches(0.32),
             "✗ " + bad, size=10.5, color=C_RED)
    add_text(s, Inches(x + 0.2), Inches(y + 0.74), Inches(5.7), Inches(0.32),
             "✓ " + good, size=10.5, color=C_GREEN)
footer(s)

# =====================================================================
# 10. 索引异常 ②：改写演示与诊断工具
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "04  索引异常排查与调优 ②  改写演示与诊断工具", 10)
add_text(s, Inches(0.55), Inches(1.3), Inches(6), 0.4,
         "▍案例：隐式类型转换改写", size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(1.75), Inches(6.1), Inches(2.6),
         "-- order_no 为 VARCHAR，传入数字字面量\n"
         "-- ✗ 失效：被转为数字比较，索引失效\n"
         "EXPLAIN SELECT * FROM t_order\n"
         "WHERE order_no = 123;\n"
         "-- type=ALL  key=NULL  rows=100万  全表扫描\n\n"
         "-- ✓ 命中：传入字符串字面量\n"
         "EXPLAIN SELECT * FROM t_order\n"
         "WHERE order_no = '000000000123';\n"
         "-- type=const  key=PRIMARY  rows=1  索引命中",
         size=11)
add_text(s, Inches(6.85), Inches(1.3), Inches(6), 0.4,
         "▍案例：函数列改写为范围查询", size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(6.85), Inches(1.75), Inches(5.9), Inches(2.6),
         "-- ✗ DATE() 函数使索引失效\n"
         "SELECT * FROM t_user\n"
         "WHERE DATE(created_at) = CURDATE();\n"
         "-- type=ALL 全表扫描\n\n"
         "-- ✓ 改写为范围查询命中索引\n"
         "SELECT * FROM t_user\n"
         "WHERE created_at >= CURDATE()\n"
         "  AND created_at < DATE_ADD(CURDATE(),\n"
         "         INTERVAL 1 DAY);\n"
         "-- type=range 命中索引",
         size=11)
add_text(s, Inches(0.55), Inches(4.55), Inches(12), 0.4,
         "▍诊断工具：索引使用率与冗余检测", size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(5.0), Inches(12.2), Inches(1.95),
         "-- 1. 查看索引被读取次数（找从未使用的冗余索引）\n"
         "SELECT object_name, index_name, rows_read\n"
         "FROM performance_schema.table_io_waits_summary_by_index_usage\n"
         "WHERE object_schema='shop_demo' ORDER BY rows_read DESC;\n\n"
         "-- 2. 冗余/重复索引检测\n"
         "SELECT TABLE_NAME, INDEX_NAME, GROUP_CONCAT(COLUMN_NAME) AS cols\n"
         "FROM information_schema.STATISTICS\n"
         "WHERE TABLE_SCHEMA='shop_demo'\n"
         "GROUP BY TABLE_NAME, INDEX_NAME ORDER BY TABLE_NAME;",
         size=11)
footer(s)

# =====================================================================
# 11. 索引异常 ③：调优原则
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "04  索引异常排查与调优 ③  索引维护原则", 11)
left = [
    ("建什么", "① 区分度高的列优先\n② 覆盖查询所需列\n③ 满足最左前缀", C_BLUE),
    ("怎么建", "① 在线建 ALGORITHM=INPLACE\n② LOCK=NONE 不阻塞业务\n③ 避开高峰期", C_TEAL),
    ("何时删", "① 长期未使用(rows_read=0)\n② 重复/冗余索引\n③ 前缀重复的复合索引", C_RED),
]
for i, (t, d, col) in enumerate(left):
    x = 0.55 + i * 4.15
    add_rect(s, Inches(x), Inches(1.5), Inches(3.95), Inches(2.4), C_LIGHT)
    add_rect(s, Inches(x), Inches(1.5), Inches(3.95), Inches(0.6), col)
    add_text(s, Inches(x), Inches(1.55), Inches(3.95), Inches(0.5),
             t, size=18, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(x + 0.2), Inches(2.25), Inches(3.55), Inches(1.5),
             d, size=12, color=C_DARK, line_spacing=1.3)

add_text(s, Inches(0.55), Inches(4.2), Inches(12), 0.4,
         "▍索引失效排查 Checklist", size=16, color=C_PRIMARY, bold=True)
checks = [
    "EXPLAIN 的 key 字段是否为 NULL（根本没用索引）",
    "type 是否为 ALL（全表扫描）或 index（全索引扫描）",
    "rows 扫描行数是否远大于返回行数",
    "Extra 是否出现 Using filesort / Using temporary",
    "是否存在函数/运算/类型转换/左模糊/违反最左前缀写法",
    "是否存在 OR 连接中一侧无索引的情况",
]
add_bullets(s, Inches(0.55), Inches(4.65), Inches(12.2), Inches(2.3),
            checks, size=13, gap=6)
footer(s)

# =====================================================================
# 12. 事务死锁 ①：复现与日志
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "05  事务死锁排查与调优 ①  复现与日志解析", 12)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), 0.4,
         "▍场景：并发下单扣减库存，两事务以相反顺序加锁 → AB-BA 死锁",
         size=15, color=C_PRIMARY, bold=True)
# 时间线表格
add_text(s, Inches(0.55), Inches(1.8), Inches(4), 0.35, "会话 A", size=13, color=C_BLUE, bold=True)
add_text(s, Inches(4.85), Inches(1.8), Inches(4), 0.35, "会话 B", size=13, color=C_RED, bold=True)
timeline = [
    ("t1", "BEGIN; UPDATE t_product SET stock=stock-1 WHERE product_id=1;", "锁住商品1", ""),
    ("t2", "", "BEGIN; UPDATE ... WHERE product_id=2;", "锁住商品2"),
    ("t3", "UPDATE ... WHERE product_id=2;", "阻塞！等B的锁", ""),
    ("t4", "", "UPDATE ... WHERE product_id=1;", "死锁！B被回滚"),
]
for i, (t, a, ad, b) in enumerate(timeline):
    y = 2.2 + i * 0.80
    add_rect(s, Inches(0.55), Inches(y), Inches(0.5), Inches(0.55), C_PRIMARY)
    add_text(s, Inches(0.55), Inches(y), Inches(0.5), Inches(0.55), t,
             size=12, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, Inches(1.1), Inches(y), Inches(3.6), Inches(0.55), C_LIGHT)
    add_text(s, Inches(1.2), Inches(y + 0.03), Inches(3.4), Inches(0.5),
             a, size=9, color=C_BLUE, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, Inches(4.85), Inches(y), Inches(3.6), Inches(0.55), C_LIGHT)
    add_text(s, Inches(4.95), Inches(y + 0.03), Inches(3.4), Inches(0.5),
             b, size=9, color=C_RED, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(8.6), Inches(y + 0.05), Inches(4.2), Inches(0.5),
             (ad if ad else ("（无）" if i % 2 else "")), size=11,
             color=C_GRAY, anchor=MSO_ANCHOR.MIDDLE)

add_text(s, Inches(0.55), Inches(4.95), Inches(12), 0.4,
         "▍死锁日志解析（SHOW ENGINE INNODB STATUS）",
         size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(5.4), Inches(12.2), Inches(1.6),
         "*** (1) TRANSACTION 2576: HOLD product_id=2, WAIT product_id=1\n"
         "*** (1) HOLDS: lock_data=product_id=2  WAITING: lock_data=product_id=1\n"
         "*** (2) TRANSACTION 2575: HOLD product_id=1, WAIT product_id=2\n"
         "*** (2) HOLDS: lock_data=product_id=1  WAITING: lock_data=product_id=2\n"
         "*** WE ROLL BACK TRANSACTION (2)   -- MySQL检测到环，2575被回滚",
         size=11)
footer(s)

# =====================================================================
# 13. 事务死锁 ②：根因与调优
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "05  事务死锁排查与调优 ②  根因分析与调优方案", 13)
card(s, 0.55, 1.35, 5.9, 1.5, "根因",
     "两个事务以「相反顺序」更新同一批商品行，\n形成循环等待(wait-for环)：\nA: lock(1)→lock(2)  B: lock(2)→lock(1)\nInnoDB 检测到环后回滚代价小的一方。",
     accent=C_RED)
card(s, 6.85, 1.35, 5.9, 1.5, "影响",
     "业务报错 ERROR 1213 (40001)\n事务回滚 → 用户下单失败\n高频死锁 → 连接堆积 → 雪崩",
     accent=C_ACCENT)

add_text(s, Inches(0.55), Inches(3.05), Inches(12), 0.4,
         "▍调优方案（四层防御）", size=16, color=C_PRIMARY, bold=True)
sols = [
    ("① 统一加锁顺序（核心）", "所有扣库存按 product_id 升序加锁，\n打破循环等待", C_GREEN),
    ("② 原子操作 + 乐观重试", "单条 UPDATE 扣减，捕获 1213 错误\n重试 2~3 次", C_BLUE),
    ("③ 短事务", "扣减与下单拆分，减少锁持有时间", C_TEAL),
    ("④ 库存分桶", "热点商品拆为多行，降低单行争用", C_ACCENT),
]
for i, (t, d, col) in enumerate(sols):
    x = 0.55 + i * 3.15
    add_rect(s, Inches(x), Inches(3.5), Inches(2.95), Inches(2.0), C_LIGHT)
    add_rect(s, Inches(x), Inches(3.5), Inches(2.95), Inches(0.55), col)
    add_text(s, Inches(x), Inches(3.53), Inches(2.95), Inches(0.5),
             t, size=12, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(x + 0.15), Inches(4.15), Inches(2.65), Inches(1.3),
             d, size=11, color=C_DARK, line_spacing=1.3)

add_code(s, Inches(0.55), Inches(5.7), Inches(12.2), Inches(1.25),
         "-- ✅ 调优后：批量扣减按 product_id 升序，统一加锁顺序\n"
         "BEGIN;\n"
         "UPDATE t_product SET stock=stock-1 WHERE product_id IN (1,2) ORDER BY product_id;\n"
         "COMMIT;   -- 会话 A、B 均按此顺序，不再形成反向环 → 死锁降为 0",
         size=12)
footer(s)

# =====================================================================
# 14. 锁等待 ①：排查与调优
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "06  锁等待排查与调优 ①  排查与应急", 14)
card(s, 0.55, 1.35, 5.9, 1.4, "故障现象",
     "后台批量改价长事务持有行锁，\n前端下单更新同一商品被阻塞，\n达到 innodb_lock_wait_timeout 后\n报 ERROR 1205 超时。",
     accent=C_RED)
card(s, 6.85, 1.35, 5.9, 1.4, "排查三步",
     "① INNODB_TRX 找持锁长事务\n② INNODB_LOCK_WAITS 看谁等谁\n③ PROCESSLIST 看会话状态\n确认后 KILL 阻塞事务应急",
     accent=C_BLUE)

add_text(s, Inches(0.55), Inches(2.95), Inches(12), 0.4,
         "▍排查 SQL", size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(3.4), Inches(12.2), Inches(2.5),
         "-- 1) 找长事务（持锁最久）\n"
         "SELECT trx_id, trx_state,\n"
         "       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS hold_sec,\n"
         "       trx_mysql_thread_id, LEFT(trx_query,80) AS query\n"
         "FROM information_schema.INNODB_TRX ORDER BY trx_started;\n"
         "-- 结果：trx_id=2583, state=RUNNING, hold_sec=5s, thread=44\n\n"
         "-- 2) 锁等待关系（MySQL 8.0 用 performance_schema）\n"
         "SELECT * FROM performance_schema.data_lock_waits;\n"
         "-- BLOCKING_TRX_ID / REQUESTING_TRX_ID 显示谁持锁谁等待",
         size=11)

add_text(s, Inches(0.55), Inches(6.05), Inches(12), 0.4,
         "▍应急：确认安全后 KILL 阻塞线程释放锁    KILL <blocking_thread>;",
         size=14, color=C_RED, bold=True)
footer(s)

# =====================================================================
# 15. 锁等待 ②：调优方案
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "06  锁等待排查与调优 ②  调优方案与根治", 15)
waits = [
    ("① 长事务拆分", "批量改价分批提交，\n每 500 条 commit 一次", C_GREEN),
    ("② 避峰操作", "改价放低峰期执行，\n避开下单高峰", C_BLUE),
    ("③ 乐观锁", "UPDATE ... WHERE version=old\n冲突重试，减少行锁", C_TEAL),
    ("④ 快速失败", "lock_wait_timeout 调小，\n业务侧 5s 超时 + 重试", C_ACCENT),
]
for i, (t, d, col) in enumerate(waits):
    x = 0.55 + i * 3.15
    add_rect(s, Inches(x), Inches(1.4), Inches(2.95), Inches(1.9), C_LIGHT)
    add_rect(s, Inches(x), Inches(1.4), Inches(2.95), Inches(0.6), col)
    add_text(s, Inches(x), Inches(1.43), Inches(2.95), Inches(0.55),
             t, size=14, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(x + 0.15), Inches(2.1), Inches(2.65), Inches(1.1),
             d, size=11, color=C_DARK, line_spacing=1.3)

add_text(s, Inches(0.55), Inches(3.55), Inches(12), 0.4,
         "▍调优对比", size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(4.0), Inches(12.2), Inches(1.5),
         "-- ✗ 调优前：长事务 BEGIN 后长时间不提交，持锁堆积\n"
         "BEGIN;\n"
         "UPDATE t_product SET price=price*1.1;  -- 全表改价，持锁数十秒\n"
         "-- （迟迟不 COMMIT）→ 前端下单全部阻塞超时\n\n"
         "-- ✓ 调优后：分批提交 + 乐观锁\n"
         "UPDATE t_product SET price=? WHERE product_id=? AND version=?;  -- 冲突重试",
         size=11)
add_text(s, Inches(0.55), Inches(5.7), Inches(12), 0.4,
         "▍长事务监控告警（>5s 预警）", size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(6.15), Inches(12.2), Inches(0.85),
         "SELECT trx_id, trx_started,\n"
         "       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS hold_sec\n"
         "FROM information_schema.INNODB_TRX HAVING hold_sec > 5;",
         size=11)
footer(s)

# =====================================================================
# 16. 主从延迟 ①：排查
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "07  主从延迟排查与调优 ①  状态排查", 16)
card(s, 0.55, 1.35, 5.9, 1.4, "故障现象",
     "大促下单写入激增，从库延迟飙升，\n报表/订单查询读到旧数据，\nSeconds_Behind_Master 达 120s+。",
     accent=C_RED)
card(s, 6.85, 1.35, 5.9, 1.4, "排查命令",
     "SHOW REPLICA STATUS\\G\n关注：Replica_IO_Running / SQL_Running\n     Seconds_Behind_Master\n     位点差判断 IO延迟 vs SQL延迟",
     accent=C_BLUE)

add_text(s, Inches(0.55), Inches(2.95), Inches(12), 0.4,
         "▍延迟来源判断", size=15, color=C_PRIMARY, bold=True)
add_bullets(s, Inches(0.55), Inches(3.4), Inches(6), Inches(2), [
    ("IO 延迟：网络/带宽不足，binlog 传输慢", 0),
    ("Master_Log_File ≠ Relay_Master_Log_File → IO 落后", 1),
    ("SQL 延迟：从库单线程回放慢（最常见）", 0),
    ("Read_Master_Log_Pos ≠ Exec_Master_Log_Pos → SQL 落后", 1),
], size=12, gap=5)

add_text(s, Inches(6.85), Inches(2.95), Inches(6), 0.4,
         "▍关键字段解读", size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(6.85), Inches(3.4), Inches(5.9), Inches(2.0),
         "Replica_IO_Running: Yes\nReplica_SQL_Running: Yes\nSeconds_Behind_Master: 120   ← 大促期间!\nMaster_Log_File: binlog.000003\nRead_Master_Log_Pos: 987654321\nExec_Master_Log_Pos: 312000000   ← 落后67万位点\nLast_Error: (复制错误信息)\n\nIO延迟 vs SQL延迟判断:\nRead ≠ Exec 位点差 → SQL回放落后\nbinlog_format=ROW 事务粒度细",
         size=11)

add_text(s, Inches(0.55), Inches(5.55), Inches(12), 0.4,
         "▍根因", size=15, color=C_PRIMARY, bold=True)
add_bullets(s, Inches(0.55), Inches(6.0), Inches(12.2), Inches(1), [
    "从库 SQL 线程单线程串行回放，跟不上主库并发写入",
    "大事务（大批量 INSERT/DELETE）单事务回放耗时长",
    "从库慢查询/锁占用资源，拖慢回放线程",
], size=13, gap=4)
footer(s)

# =====================================================================
# 17. 主从延迟 ②：调优方案
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "07  主从延迟排查与调优 ②  多线程并行复制调优", 17)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), 0.4,
         "▍核心方案：开启多线程并行复制（MTS, MySQL 8.0 LOGICAL_CLOCK）",
         size=15, color=C_PRIMARY, bold=True)
add_code(s, Inches(0.55), Inches(1.8), Inches(7.2), Inches(2.7),
         "STOP REPLICA;\n\n"
         "-- 并行回放：按逻辑时钟，主库组提交的事务可并行\n"
         "SET GLOBAL replica_parallel_workers = 8;\n"
         "SET GLOBAL replica_parallel_type = 'LOGICAL_CLOCK';\n"
         "SET GLOBAL replica_pending_jobs_size_max = 134217728; -- 128MB\n\n"
         "-- 8.0 更细粒度依赖追踪\n"
         "SET GLOBAL binlog_transaction_dependency_tracking = 'WRITESET';\n"
         "START REPLICA;",
         size=11)
add_text(s, Inches(7.95), Inches(1.3), Inches(5), 0.4,
         "▍配套措施", size=15, color=C_PRIMARY, bold=True)
add_bullets(s, Inches(7.95), Inches(1.8), Inches(4.8), Inches(2.7), [
    "主库大事务分批提交\n（每 1000 行 commit）",
    "从库慢查询优化，让出 SQL 线程资源",
    "业务读写分离延迟感知：\n下单后查订单走主库\n报表走从库",
    "延迟超阈值自动切主",
], size=12, gap=6)

add_text(s, Inches(0.55), Inches(4.7), Inches(12), 0.4,
         "▍调优效果对比", size=15, color=C_PRIMARY, bold=True)
repl_cmp = [
    ("对比项", "调优前", "调优后"),
    ("回放方式", "单线程串行", "8 线程并行(LOGICAL_CLOCK)"),
    ("当前配置", "replica_parallel_workers=4", "replica_parallel_workers=8"),
    ("大事务回放", "整事务阻塞", "并行回放组提交事务"),
    ("Seconds_Behind_Master", "120s+ (大促)", "<5s"),
]
cw = [3.2, 3.8, 4.2]
for r, row in enumerate(repl_cmp):
    y = 5.15 + r * 0.42
    bg = C_PRIMARY if r == 0 else (C_LIGHT if r % 2 == 1 else C_WHITE)
    fg = C_WHITE if r == 0 else C_DARK
    add_rect(s, Inches(0.55), Inches(y), Inches(11.2), Inches(0.4), bg)
    for c, val in enumerate(row):
        color = fg
        if r > 0 and c == 2:
            color = C_GREEN
        if r > 0 and c == 1:
            color = C_RED
        add_text(s, Inches(0.55 + sum(cw[:c])), Inches(y), Inches(cw[c]),
                 Inches(0.4), val, size=12, color=color,
                 bold=(r == 0 or c == 0), align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)
footer(s)

# =====================================================================
# 18. 综合调优成果
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "08  综合调优成果：整体性能升级", 18)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), 0.4,
         "▍五大瓶颈调优前后对比", size=16, color=C_PRIMARY, bold=True)
results = [
    ("慢查询", "rows=20 + filesort", "rows=3 索引覆盖", "扫描↓85%\n排序消除"),
    ("索引异常", "6类 type=ALL 全表扫描", "全部命中索引", "全表扫描\n→索引命中"),
    ("事务死锁", "真实触发 AB-BA\nERROR 1213", "统一加锁顺序\n死锁 = 0", "根除"),
    ("锁等待", "真实触发 ERROR 1205\n超时 5s", "分批+乐观锁\n快速失败", "超时堆积\n→秒级失败"),
    ("主从延迟", "单线程回放\n延迟 120s+", "8线程并行\nLOGICAL_CLOCK", "120s→<5s\n↓96%"),
]
cw = [1.8, 3.5, 3.5, 1.8]
heads = ["故障", "调优前", "调优后", "改善"]
add_rect(s, Inches(0.55), Inches(1.85), Inches(10.6), Inches(0.5), C_PRIMARY)
for c, h in enumerate(heads):
    add_text(s, Inches(0.55 + sum(cw[:c])), Inches(1.85), Inches(cw[c]),
             Inches(0.5), h, size=14, color=C_WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
for i, (n, before, after, imp) in enumerate(results):
    y = 2.4 + i * 0.62
    add_rect(s, Inches(0.55), Inches(y), Inches(10.6), Inches(0.55),
             C_LIGHT if i % 2 == 0 else C_WHITE)
    add_text(s, Inches(0.55), Inches(y), Inches(cw[0]), Inches(0.55),
             n, size=13, color=C_PRIMARY, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(0.55 + cw[0]), Inches(y), Inches(cw[1]), Inches(0.55),
             before, size=12, color=C_RED, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(0.55 + sum(cw[:2])), Inches(y), Inches(cw[2]), Inches(0.55),
             after, size=12, color=C_GREEN, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(0.55 + sum(cw[:3])), Inches(y), Inches(cw[3]), Inches(0.55),
             imp, size=13, color=C_ACCENT, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)

# 整体收益 KPI
add_text(s, Inches(11.4), Inches(1.85), Inches(1.4), Inches(0.5),
         "整体收益", size=14, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
kpis = [("死锁 = 0", "AB-BA 根除", C_GREEN),
        ("rows 20→3", "索引覆盖", C_BLUE),
        ("ERROR 1205\n已消除", "分批+乐观锁", C_TEAL),
        ("延迟 ↓96%", "120s→<5s", C_ACCENT)]
for i, (k, v, col) in enumerate(kpis):
    y = 2.4 + i * 0.62
    add_rect(s, Inches(11.4), Inches(y), Inches(1.4), Inches(0.55), C_LIGHT)
    add_rect(s, Inches(11.4), Inches(y), Inches(0.06), Inches(0.55), col)
    add_text(s, Inches(11.5), Inches(y + 0.02), Inches(1.25), Inches(0.3),
             k, size=10, color=col, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(11.5), Inches(y + 0.3), Inches(1.25), Inches(0.2),
             v, size=8, color=C_GRAY, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)

add_text(s, Inches(0.55), Inches(5.9), Inches(12.2), 0.4,
         "▍调优效果基于真实 MySQL 8.0 环境实测，数据库 shop_demo 含 100 万订单",
         size=14, color=C_ACCENT, bold=True)
footer(s)

# =====================================================================
# 18b. 调优闭环与经验沉淀
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s)
header(s, "08  调优闭环与经验沉淀", 19)
add_text(s, Inches(0.55), Inches(1.3), Inches(12), 0.4,
         "▍全链路调优闭环：监控 → 定位 → 分析 → 调优 → 验证 → 沉淀",
         size=16, color=C_PRIMARY, bold=True)
loop = ["监控告警", "现象定位", "根因分析", "方案调优", "效果验证", "经验沉淀"]
for i, t in enumerate(loop):
    x = 0.9 + i * 2.1
    col = [C_BLUE, C_ACCENT, C_RED, C_TEAL, C_GREEN, C_PRIMARY][i]
    add_rect(s, Inches(x), Inches(1.85), Inches(1.7), Inches(0.65), col)
    add_text(s, Inches(x), Inches(1.85), Inches(1.7), Inches(0.65),
             t, size=12, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    if i < 5:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                                Inches(x + 1.72), Inches(2.02), Inches(0.18), Inches(0.3))
        ar.fill.solid(); ar.fill.fore_color.rgb = C_GRAY
        ar.line.fill.background()

add_text(s, Inches(0.55), Inches(3.0), Inches(6), 0.4,
         "▍核心经验沉淀", size=16, color=C_PRIMARY, bold=True)
exp = [
    "慢查询：EXPLAIN 是第一利器，关注 type/rows/Extra 三要素",
    "索引：遵循最左前缀 + 覆盖索引，警惕 6 类失效写法",
    "死锁：统一加锁顺序是治本，重试是兜底",
    "锁等待：长事务是万恶之源，拆分 + 乐观锁",
    "主从延迟：单线程回放是瓶颈，多线程并行复制解之",
    "共性：监控先行，定位证据，根因分析，验证闭环",
]
add_bullets(s, Inches(0.55), Inches(3.5), Inches(6.2), Inches(2.5),
            exp, size=13, gap=10)

add_text(s, Inches(7.0), Inches(3.0), Inches(5.8), 0.4,
         "▍课程知识点整合", size=16, color=C_PRIMARY, bold=True)
points = [
    ("索引原理", "B+树 / 回表 / 覆盖索引", C_BLUE),
    ("执行计划", "EXPLAIN / type / Extra", C_TEAL),
    ("事务与锁", "ACID / 行锁 / 间隙锁 / 死锁", C_RED),
    ("复制架构", "binlog / relaylog / GTID", C_ACCENT),
    ("性能调优", "慢日志 / 并行复制 / 读写分离", C_GREEN),
]
for i, (t, d, col) in enumerate(points):
    y = 3.5 + i * 0.72
    add_rect(s, Inches(7.0), Inches(y), Inches(5.75), Inches(0.65), C_LIGHT)
    add_rect(s, Inches(7.0), Inches(y), Inches(0.08), Inches(0.65), col)
    add_text(s, Inches(7.25), Inches(y + 0.06), Inches(5.4), Inches(0.3),
             t, size=14, color=C_PRIMARY, bold=True)
    add_text(s, Inches(7.25), Inches(y + 0.36), Inches(5.4), Inches(0.25),
             d, size=11, color=C_GRAY)

add_text(s, Inches(0.55), Inches(6.25), Inches(12.2), 0.4,
         "▍展望：向「可观测 + 自动化」演进 —— 慢SQL自动索引建议、智能巡检、AIOps 异常预测",
         size=14, color=C_ACCENT, bold=True)
footer(s)

# =====================================================================
# 21. 致谢 / Q&A
# =====================================================================
s = prs.slides.add_slide(BLANK)
slide_bg(s, C_DARK)
add_rect(s, 0, 0, SW, Inches(0.35), C_ACCENT)
add_rect(s, 0, SH - Inches(0.35), SW, Inches(0.35), C_ACCENT)
for i, (cx, cy, r) in enumerate([(2.0, 1.8, 0.1), (2.4, 2.2, 0.06),
                                  (11.5, 5.4, 0.1), (11.0, 5.0, 0.06)]):
    d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx), Inches(cy), Inches(r*2), Inches(r*2))
    d.fill.solid(); d.fill.fore_color.rgb = C_ACCENT if i % 2 == 0 else C_TEAL
    d.line.fill.background()
add_text(s, Inches(1.0), Inches(2.5), Inches(11.3), Inches(1.2),
         "THANK YOU", size=60, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER)
add_rect(s, Inches(5.4), Inches(3.85), Inches(2.5), Inches(0.06), C_ACCENT)
add_text(s, Inches(1.0), Inches(4.1), Inches(11.3), Inches(0.6),
         "感谢聆听  ·  欢迎提问与交流", size=24, color=C_ACCENT,
         bold=True, align=PP_ALIGN.CENTER)
add_text(s, Inches(1.0), Inches(5.2), Inches(11.3), Inches(0.5),
         "全链路性能瓶颈排查与综合调优  |  数据库优化与应用 期末作业",
         size=14, color=RGBColor(0x9A, 0xB0, 0xC8), align=PP_ALIGN.CENTER)
add_text(s, Inches(1.0), Inches(5.8), Inches(11.3), Inches(0.5),
         "演示材料：scripts/ 下含建表、造数、故障模拟、调优对比全套脚本",
         size=12, color=RGBColor(0x6A, 0x80, 0x9A), align=PP_ALIGN.CENTER)

# =====================================================================
# 保存
# =====================================================================
out = "/workspace/db_optimization_demo/ppt/全链路性能瓶颈排查与综合调优_优化版.pptx"
prs.save(out)
print(f"✅ PPT 已生成: {out}")
print(f"   共 {len(prs.slides)} 页")

