#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把真实 MySQL 实测数据回填到用户上传的优化版 PPT
策略：按 slide 索引 + 精确文本匹配定位 shape，替换文本时保留首个 run 的字体格式。
所有回填数据均来自真实 SQL 执行结果（见 results/*.txt）。"""
from pptx import Presentation
from copy import deepcopy

SRC = "/workspace/.uploads/dd0a6cb1-2836-4a1a-b573-0daa32a57d65_全链路性能瓶颈排查与综合调优_优化版.pptx"
DST = "/workspace/db_optimization_demo/全链路性能瓶颈排查与综合调优_实测数据回填版.pptx"

prs = Presentation(SRC)

def set_text_keep_fmt(shape, new_text):
    """替换 shape 文本，保留首个 run 的格式；多行按 \\n 拆段。"""
    tf = shape.text_frame
    # 取首个有文字的 run 作为格式模板
    tmpl = None
    for p in tf.paragraphs:
        for r in p.runs:
            if r.text:
                tmpl = r
                break
        if tmpl:
            break
    # 清空所有段落
    p0 = tf.paragraphs[0]
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    # 写入第一段
    lines = new_text.split("\n")
    r0 = p0.add_run()
    r0.text = lines[0]
    if tmpl is not None:
        r0.font.size = tmpl.font.size
        r0.font.bold = tmpl.font.bold
        r0.font.name = tmpl.font.name
        try: r0.font.color.rgb = tmpl.font.color.rgb
        except: pass
    # 其余段落
    # 删除多余段落
    while len(tf.paragraphs) > 1:
        tf._txBody.remove(tf.paragraphs[-1]._p)
    for ln in lines[1:]:
        p = tf.add_paragraph()
        rn = p.add_run()
        rn.text = ln
        if tmpl is not None:
            rn.font.size = tmpl.font.size
            rn.font.bold = tmpl.font.bold
            rn.font.name = tmpl.font.name
            try: rn.font.color.rgb = tmpl.font.color.rgb
            except: pass

def find_replace(slide, old, new):
    """在 slide 内找文本完全等于 old 的 shape，替换为 new。返回替换数。"""
    n = 0
    for shp in slide.shapes:
        if shp.has_text_frame and shp.text_frame.text == old:
            set_text_keep_fmt(shp, new)
            n += 1
    return n

def find_replace_contains(slide, old_sub, new):
    """找包含 old_sub 的 shape 整体替换。"""
    n = 0
    for shp in slide.shapes:
        if shp.has_text_frame and old_sub in shp.text_frame.text:
            set_text_keep_fmt(shp, new)
            n += 1
    return n

# =====================================================================
# Slide 3：数据量改为真实值
# =====================================================================
s = prs.slides[2]
find_replace_contains(s, "约 100 万订单数据量",
    "▍核心表结构（实测：用户5万 / 商品1万 / 订单99.7万 / 明细128万）")

# =====================================================================
# Slide 4：慢查询调优效果 800ms→<10ms  →  实测 420ms→0.46ms
# =====================================================================
s = prs.slides[3]
find_replace(s, "800ms → <10ms", "420ms → 0.46ms")

# =====================================================================
# Slide 5：故障 SQL 注释 + 慢日志解读
# =====================================================================
s = prs.slides[4]
find_replace_contains(s, "故障 SQL：只建 idx_user 单列索引",
    "-- 故障 SQL：t_order 无有效业务索引 → 全表扫描 99 万行\nSELECT order_id, order_no, total_amount, status, pay_time\nFROM t_order\nWHERE user_id = 12345\n  AND status = 1\n  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)\nORDER BY created_at DESC\nLIMIT 20;")
find_replace_contains(s, "本例 Rows_examined ≈ 80万",
    "• Query_time：单条执行耗时（关注 >1s）\n• Lock_time：等待锁耗时\n• Rows_examined：扫描行数（异常偏大）\n• Rows_sent：返回行数\n• 扫描行数/返回行数 比值越大越低效\n• 本例 Rows_examined = 994910，Rows_sent = 20\n• 比值 49745:1 → 典型“大扫描小返回”\n• 实测 Query_time ≈ 420ms")

# =====================================================================
# Slide 6：EXPLAIN 关键字段 + 调优前表格 + 诊断
# =====================================================================
s = prs.slides[5]
find_replace(s,
    "• type = ref：命中 idx_user，但仅等值列\n• key = idx_user：只用了单列索引\n• rows ≈ 8200：预估扫描行数偏大\n• Extra = Using where + Using filesort：回表 + 额外排序",
    "• type = ALL：全表扫描，未命中索引\n• key = NULL：无可用索引\n• rows ≈ 994910：扫描近百万行\n• Extra = Using where + Using filesort：过滤 + 额外排序")
# 调优前 EXPLAIN 表格单元（按精确文本匹配，这些短串在该 slide 唯一）
find_replace(s, "ref", "ALL")
find_replace(s, "idx_user", "NULL")
find_replace(s, "20", "994910")
find_replace(s,
    "• idx_user 仅覆盖 user_id，status 与 created_at 需回表逐行过滤 → 扫描 8200 行\n• ORDER BY created_at 无法利用索引有序性 → 触发 Using filesort 额外排序\n• 根因：缺少 (user_id, status, created_at) 复合索引",
    "• 无有效索引，user_id/status/created_at 三条件全表扫描 994910 行\n• ORDER BY created_at 无法利用索引有序性 → 触发 Using filesort 额外排序\n• 根因：缺少 (user_id, status, created_at) 复合索引")

# =====================================================================
# Slide 7：调优前/后表格对齐到真实 EXPLAIN + 核心收益
# 实测：before(无索引) type=ALL rows=994910 Extra=Using where;Using filesort
#       after(复合索引) type=range rows=1 Extra=Using index condition
# =====================================================================
s = prs.slides[6]
# 调优前列
find_replace(s, "ref", "ALL")
find_replace(s, "idx_user(单列)", "无有效索引")
find_replace(s, "20", "994910")
find_replace(s, "Using where; filesort", "Using where; Using filesort")
# 调优后列
find_replace(s, "3", "1")
# 核心收益
find_replace(s, "20行 → 3行", "994910行 → 1行")
find_replace(s, "ref → range", "ALL → range")

# =====================================================================
# Slide 10：索引异常代码块真实行数
# =====================================================================
s = prs.slides[9]
find_replace_contains(s, "type=ALL  key=NULL  rows=100万",
    "-- order_no 为 VARCHAR，传入数字字面量\n-- ✗ 失效：被转为数字比较，索引失效\nEXPLAIN SELECT * FROM t_order\nWHERE order_no = 123;\n-- type=ALL  key=NULL  rows=996896  全表扫描\n \n-- ✓ 命中：传入字符串字面量\nEXPLAIN SELECT * FROM t_order\nWHERE order_no = 'NO000000000123';\n-- type=const  key=uk_order_no  rows=1  索引命中")

# =====================================================================
# Slide 12：死锁日志真实 trx_id + 正确 hold/wait 方向
# 实测：会话A(trx 2507)持p1等p2，会话B(trx 2506)持p2等p1，B(2506)被回滚
# =====================================================================
s = prs.slides[11]
find_replace_contains(s, "TRANSACTION 2576",
    "*** (1) TRANSACTION 2507: HOLD product_id=1, WAIT product_id=2\n*** (1) HOLDS: lock_mode X on product_id=1  WAITING: product_id=2\n*** (2) TRANSACTION 2506: HOLD product_id=2, WAIT product_id=1\n*** (2) HOLDS: lock_mode X on product_id=2  WAITING: product_id=1\n*** WE ROLL BACK TRANSACTION (2)   -- MySQL检测到环，trx 2506 被回滚")

# =====================================================================
# Slide 17：主从延迟配置加实测标注
# =====================================================================
s = prs.slides[16]
find_replace(s, "replica_parallel_workers=4",
    "replica_parallel_workers=4 (实测)")

# =====================================================================
# Slide 18：综合成果表 慢查询行
# =====================================================================
s = prs.slides[17]
find_replace(s, "rows=20 + 回表过滤\nfilesort 额外排序",
    "rows=994910 全表扫描\nfilesort 额外排序")
find_replace(s, "rows=3 索引覆盖\n无回表无排序",
    "rows=1 索引覆盖\n无回表无排序")
find_replace(s, "扫描↓85%\n排序消除",
    "420ms→0.46ms\n↓99.9%")
find_replace(s, "rows 20→3", "994910→1")

prs.save(DST)
print("✅ 回填完成 →", DST)
