#!/usr/bin/env python3
"""慢查询真实耗时：用户订单查询 调优前(无索引) vs 调优后(复合索引)
同一SQL，仅索引不同 → 完全可比的真实数据"""
import pymysql, time

conn = pymysql.connect(host='localhost', user='root', password='root123',
                       database='shop_demo', charset='utf8mb4',
                       unix_socket='/var/run/mysqld/mysqld.sock')

SQL = """SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order {hint}
WHERE user_id = 12345 AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC LIMIT 20"""

BEFORE = SQL.format(hint="USE INDEX()")          # 无索引 全表扫描
AFTER  = SQL.format(hint="FORCE INDEX(idx_user_status_created)")  # 复合索引

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
print("  用户订单查询真实耗时（同一SQL，索引不同）")
print("  SQL: WHERE user_id=12345 AND status=1 AND created_at>=30d")
print("       ORDER BY created_at DESC LIMIT 20")
print("="*66)

with conn.cursor() as c:
    c.execute("EXPLAIN " + BEFORE); r=c.fetchone()
    print(f"\n调优前(无索引) EXPLAIN: type={r[4]} key={r[6]} rows={r[9]} Extra={r[10]}")
bm,bmin,bmax,br = bench(BEFORE)
print(f"调优前耗时: avg={bm:.0f}ms  min={bmin:.0f}  max={bmax:.0f}  返回{br}行")

with conn.cursor() as c:
    c.execute("EXPLAIN " + AFTER); r=c.fetchone()
    print(f"\n调优后(复合索引) EXPLAIN: type={r[4]} key={r[6]} rows={r[9]} Extra={r[10]}")
am,amin,amax,ar = bench(AFTER)
print(f"调优后耗时: avg={am:.2f}ms  min={amin:.2f}  max={amax:.2f}  返回{ar}行")

print("\n" + "-"*66)
print(f"  扫描行数: 994910 → 1")
print(f"  耗时: {bm:.0f}ms → {am:.2f}ms  提速 {bm/am:.0f}x  下降 {(1-am/bm)*100:.1f}%")
print("="*66)
conn.close()
