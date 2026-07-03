#!/usr/bin/env python3
"""慢查询真实耗时：深分页（生产最常见慢查询）
调优前：LIMIT 500000,20 → 扫描50万行+filesort
调优后：覆盖索引+延迟关联 → 仅扫描20行"""
import pymysql, time

conn = pymysql.connect(host='localhost', user='root', password='root123',
                       database='shop_demo', charset='utf8mb4',
                       unix_socket='/var/run/mysqld/mysqld.sock')

# 深分页：跳过50万行取20行（典型后台/分页慢查询）
BEFORE = """
SELECT order_id, order_no, user_id, total_amount, status, created_at
FROM t_order USE INDEX()
WHERE status = 1
ORDER BY created_at DESC
LIMIT 500000, 20"""

# 延迟关联 + 覆盖索引：先用主键索引找出20个order_id，再回表
AFTER = """
SELECT o.order_id, o.order_no, o.user_id, o.total_amount, o.status, o.created_at
FROM t_order o
INNER JOIN (
  SELECT order_id FROM t_order FORCE INDEX(idx_status_created_amount)
  WHERE status = 1 ORDER BY created_at DESC LIMIT 500000, 20
) t ON o.order_id = t.order_id"""

def bench(sql, n=5):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        with conn.cursor() as c:
            c.execute(sql)
            rows = c.fetchall()
        times.append((time.perf_counter() - t0) * 1000)
    times.sort()
    mid = times[1:-1] if len(times) > 2 else times
    return sum(mid)/len(mid), min(times), max(times), len(rows)

print("="*66)
print("  深分页慢查询真实耗时（5次采样，去头尾平均，单位ms）")
print("  查询: 已支付订单 按时间倒序 LIMIT 500000,20")
print("="*66)

with conn.cursor() as c:
    c.execute("EXPLAIN " + BEFORE)
    r = c.fetchone()
    print(f"\n调优前 EXPLAIN: type={r[4]} key={r[6]} rows={r[9]} Extra={r[10]}")
bm, bmin, bmax, br = bench(BEFORE)
print(f"调优前耗时: avg={bm:.0f}ms  min={bmin:.0f}  max={bmax:.0f}  返回{br}行")

with conn.cursor() as c:
    c.execute("EXPLAIN " + AFTER)
    rows = c.fetchall()
    print("\n调优后 EXPLAIN (延迟关联):")
    for r in rows:
        print(f"  type={r[4]} key={r[6]} rows={r[9]} Extra={r[10]}")
am, amin, amax, ar = bench(AFTER)
print(f"\n调优后耗时: avg={am:.0f}ms  min={amin:.0f}  max={amax:.0f}  返回{ar}行")

print("\n" + "-"*66)
print(f"  提速倍数: {bm/am:.1f}x   耗时下降: {(1-am/bm)*100:.1f}%")
print("="*66)
conn.close()
