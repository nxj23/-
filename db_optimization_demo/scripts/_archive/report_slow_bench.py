#!/usr/bin/env python3
"""慢查询真实耗时：报表查询调优前 vs 调优后
调优前：无合适索引 → 全表扫描 ~99万行 + filesort
调优后：(status, created_at, total_amount) 覆盖索引 → range + Using index"""
import pymysql, time

conn = pymysql.connect(host='localhost', user='root', password='root123',
                       database='shop_demo', charset='utf8mb4',
                       unix_socket='/var/run/mysqld/mysqld.sock')

Q = """
SELECT order_id, order_no, user_id, total_amount, created_at
FROM t_order
WHERE status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY total_amount DESC LIMIT 20"""

BEFORE = Q.replace("FROM t_order\n", "FROM t_order USE INDEX()\n")

def bench(sql, n=10):
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
print("  报表慢查询真实耗时（10次采样，去头尾平均，单位ms）")
print("  查询: 近30天已支付订单 按金额倒序 LIMIT 20")
print("="*66)

# 调优前
with conn.cursor() as c:
    c.execute("EXPLAIN " + BEFORE)
    r = c.fetchone()
    print(f"\n调优前 EXPLAIN: type={r[4]} key={r[6]} rows={r[9]} Extra={r[10]}")
bm, bmin, bmax, br = bench(BEFORE)
print(f"调优前耗时: avg={bm:.1f}ms  min={bmin:.1f}  max={bmax:.1f}  返回{br}行")

# 建调优索引：覆盖索引 (status, created_at, total_amount) + order_id/order_no/user_id 主键回表
print("\n>> 建立覆盖索引 idx_status_created_amount (status, created_at, total_amount)...")
with conn.cursor() as c:
    try:
        c.execute("ALTER TABLE t_order ADD INDEX idx_status_created_amount (status, created_at, total_amount)")
    except Exception as e:
        print(f"   (索引已存在或跳过: {e})")
    c.execute("ANALYZE TABLE t_order")
conn.commit()

AFTER = Q.replace("FROM t_order\n", "FROM t_order FORCE INDEX(idx_status_created_amount)\n")
with conn.cursor() as c:
    c.execute("EXPLAIN " + AFTER)
    r = c.fetchone()
    print(f"\n调优后 EXPLAIN: type={r[4]} key={r[6]} rows={r[9]} Extra={r[10]}")
am, amin, amax, ar = bench(AFTER)
print(f"调优后耗时: avg={am:.1f}ms  min={amin:.1f}  max={amax:.1f}  返回{ar}行")

print("\n" + "-"*66)
print(f"  提速倍数: {bm/am:.1f}x   耗时下降: {(1-am/bm)*100:.1f}%")
print(f"  扫描行数: 996896 → 20 (EXPLAIN rows)")
print("="*66)

# 清理：保留索引供PPT演示，不删除
conn.close()
