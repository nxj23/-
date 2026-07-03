#!/usr/bin/env python3
"""慢查询真实耗时测量（ms级），调优前 vs 调优后"""
import pymysql, time

conn = pymysql.connect(host='localhost', user='root', password='root123',
                       database='shop_demo', charset='utf8mb4',
                       unix_socket='/var/run/mysqld/mysqld.sock')

BEFORE = """
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order FORCE INDEX(idx_user)
WHERE user_id = 12345 AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC LIMIT 20"""

AFTER = """
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order FORCE INDEX(idx_user_status_created)
WHERE user_id = 12345 AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC LIMIT 20"""

def bench(sql, n=20):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        with conn.cursor() as c:
            c.execute(sql)
            rows = c.fetchall()
        times.append((time.perf_counter() - t0) * 1000)
    times.sort()
    # 去掉最大最小，取中间平均
    mid = times[2:-2] if len(times) > 4 else times
    return sum(mid)/len(mid), min(times), max(times), len(rows)

print("="*60)
print("  慢查询真实耗时（20次采样，去头尾平均，单位ms）")
print("="*60)
bm, bmin, bmax, br = bench(BEFORE)
print(f"  调优前(idx_user+filesort): avg={bm:.2f}ms min={bmin:.2f} max={bmax:.2f} rows={br}")
am, amin, amax, ar = bench(AFTER)
print(f"  调优后(复合索引):         avg={am:.2f}ms min={amin:.2f} max={amax:.2f} rows={ar}")
print("-"*60)
print(f"  提速倍数: {bm/am:.1f}x   耗时下降: {(1-am/bm)*100:.1f}%")
print("="*60)
conn.close()
