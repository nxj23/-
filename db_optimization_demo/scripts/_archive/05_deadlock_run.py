#!/usr/bin/env python3
"""
死锁并发演示脚本（05_deadlock_run.py）
使用 PyMySQL + threading.Barrier 确保双会话真正同时持锁 → 触发 AB-BA 死锁
"""
import pymysql
import threading
import time

conn_params = {
    'host': 'localhost', 'user': 'root', 'password': 'root123', 'db': 'shop_demo',
    'autocommit': False, 'charset': 'utf8mb4',
    'unix_socket': '/var/run/mysqld/mysqld.sock'
}

results = {}
errors = {}

# Barrier: 确保两个线程都在持锁后才尝试下一个
barrier = threading.Barrier(2)

def hold_locks_and_wait(name, p1, p2):
    """会话：先锁定 p1 → Barrier同步 → 再尝试锁定 p2（触发死锁）"""
    conn = pymysql.connect(**conn_params)
    conn.begin()
    try:
        with conn.cursor() as cur:
            # 第1步：锁定 p1
            cur.execute(f"UPDATE t_product SET stock=stock-1 WHERE product_id={p1}")
            results[f'{name}_locked_{p1}'] = f"🔒 锁定 product_id={p1}"

            # 到达屏障，等另一个会话也完成第一步
            barrier.wait()  # 双方同时越过屏障

            # 第2步：尝试锁定 p2（此时对方已锁定 p2，AB-BA 死锁！）
            try:
                cur.execute(f"UPDATE t_product SET stock=stock-1 WHERE product_id={p2}")
                results[f'{name}_locked_{p2}'] = f"🔒 锁定 product_id={p2}"
                conn.commit()
            except pymysql.err.OperationalError as e:
                err_str = str(e)
                if "1213" in err_str or "Deadlock" in err_str:
                    errors['deadlock_detected'] = f"[{name}] {err_str}"
                    results[f'{name}_step2'] = f"💥 死锁! {err_str[:80]}"
                    conn.rollback()
                else:
                    errors[name] = err_str
                    results[f'{name}_step2'] = f"❌ {err_str[:40]}"
    except Exception as e:
        errors[f'{name}_fatal'] = str(e)
        results[name] = f"ERROR: {e}"
    finally:
        try:
            conn.close()
        except:
            pass

print("=" * 65)
print("  死锁并发演示（AB-BA 循环等待）")
print("=" * 65)

# 重置库存
reset = pymysql.connect(**conn_params)
with reset.cursor() as c:
    c.execute("UPDATE t_product SET stock=1000 WHERE product_id IN (1,2)")
    reset.commit()
reset.close()
print("  库存重置: product_id=1,2 = 1000\n")

print("  时序设计:")
print("  会话A: BEGIN → UPDATE product_id=1(🔒) → [屏障] → UPDATE product_id=2(等🔒)")
print("  会话B: BEGIN → UPDATE product_id=2(🔒) → [屏障] → UPDATE product_id=1(等🔒)")
print("           ↓                    ↓")
print("         A持1等2              B持2等1")
print("           ←────────死锁环────────→\n")

# 启动两个线程
tA = threading.Thread(target=hold_locks_and_wait, args=("A", 1, 2))
tB = threading.Thread(target=hold_locks_and_wait, args=("B", 2, 1))

print("▶ 启动并发死锁模拟...")
tA.start()
tB.start()

tA.join(timeout=15)
tB.join(timeout=15)

print("\n" + "=" * 65)
print("  线程执行结果")
print("=" * 65)
for k in sorted(results):
    v = results[k]
    icon = "💥" if "死锁" in str(v) else ("🔒" if "锁定" in str(v) else "❌")
    print(f"  {icon} {k}: {v}")

# 死锁日志
print("\n" + "=" * 65)
print("  死锁日志（SHOW ENGINE INNODB STATUS）")
print("=" * 65)
conn2 = pymysql.connect(**conn_params)
with conn2.cursor() as c:
    c.execute("SHOW ENGINE INNODB STATUS")
    row = c.fetchone()
    if row:
        status = row[2] if len(row) > 2 else str(row)
        lines = status.split('\n')
        capture = False
        for line in lines:
            stripped = line.strip()
            if 'LATEST DETECTED DEADLOCK' in stripped:
                capture = True
            if capture and stripped:
                print(f"  {stripped}")
            if capture and ('WE ROLL BACK' in stripped or 'ROLL BACK TRANSACTION' in stripped):
                break
conn2.close()

# 清理
clean = pymysql.connect(**conn_params)
with clean.cursor() as c:
    try: c.execute("ROLLBACK"); clean.commit()
    except: pass
    c.execute("UPDATE t_product SET stock=1000 WHERE product_id IN (1,2)")
    clean.commit()
clean.close()

print("\n" + "=" * 65)
if "deadlock_detected" in errors:
    print("  ✅ 死锁成功触发！一方会话被回滚。")
    print(f"     错误码: {errors['deadlock_detected']}")
else:
    print("  ⚠️  未触发死锁（可重试几次，或增大 innodb_lock_wait_timeout）")
print("=" * 65)
