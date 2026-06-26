#!/usr/bin/env python3
"""
锁等待演示脚本（06_lock_wait_run.py）
会话A开长事务持锁，会话B尝试更新同一行 → 等待超时 → 捕获 ERROR 1205
"""
import pymysql
import threading
import time

conn_params = {
    'host': 'localhost', 'user': 'root', 'db': 'shop_demo',
    'autocommit': False, 'charset': 'utf8mb4',
    'unix_socket': '/var/run/mysqld/mysqld.sock'
}

# 调小锁等待超时（演示用）
def init_env():
    conn = pymysql.connect(**conn_params)
    with conn.cursor() as c:
        c.execute("SET GLOBAL innodb_lock_wait_timeout = 5")
    conn.close()
    print("  innodb_lock_wait_timeout = 5s")

def wait_for_lock():
    """会话B：尝试更新同一商品，被阻塞后超时"""
    conn = pymysql.connect(**conn_params)
    conn.begin()
    try:
        with conn.cursor() as c:
            start = time.time()
            print("  [会话B] UPDATE product_id=1 → 等待锁...")
            c.execute("UPDATE t_product SET price=price*1.1 WHERE product_id=1")
            conn.commit()
            elapsed = time.time() - start
            print(f"  [会话B] ✅ 更新成功，耗时 {elapsed:.2f}s")
    except pymysql.err.OperationalError as e:
        err = str(e)
        elapsed = time.time() - start
        if "1205" in err:
            print(f"  [会话B] 💥 ERROR 1205 Lock wait timeout! 耗时 {elapsed:.1f}s")
            print(f"         {err}")
        else:
            print(f"  [会话B] ❌ 其他错误: {err}")
    finally:
        conn.close()

print("=" * 65)
print("  锁等待演示")
print("=" * 65)
init_env()

# 重置商品 1 价格
reset = pymysql.connect(**conn_params)
with reset.cursor() as c:
    c.execute("UPDATE t_product SET price=99.0 WHERE product_id=1")
    reset.commit()
reset.close()
print("  商品1 价格重置为 99.0\n")

# 会话A：开启长事务持锁（不提交，模拟批量改价长事务）
connA = pymysql.connect(**conn_params)
connA.begin()
with connA.cursor() as c:
    print("  [会话A] BEGIN + UPDATE product_id=1 (持锁，不提交)")
    c.execute("UPDATE t_product SET price=price*1.1 WHERE product_id=1")
    print("  [会话A] 已锁定 product_id=1，模拟批量改价中...（长事务持锁）")

time.sleep(0.3)  # 等A完成锁定

# 会话B：尝试更新同一行 → 阻塞超时
print("  [会话B] BEGIN + UPDATE product_id=1...")
thread_b = threading.Thread(target=wait_for_lock)
thread_b.start()
thread_b.join(timeout=15)

# 查看 INNODB_TRX 找长事务
print("\n" + "=" * 65)
print("  排查：INNODB_TRX 找持锁长事务")
print("=" * 65)
try:
    conn3 = pymysql.connect(**conn_params)
    with conn3.cursor() as c:
        c.execute("""SELECT trx_id, trx_state, trx_started,
                           TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS hold_sec,
                           trx_mysql_thread_id, LEFT(trx_query, 80) AS query
                    FROM information_schema.INNODB_TRX""")
        print(f"  {'trx_id':>8} {'state':>10} {'hold_sec':>8} {'thread':>6}  query")
        for row in c.fetchall():
            print(f"  {row[0]:>8} {row[1]:>10} {row[3]:>8}s {row[4]:>6}  {row[5]}")
    conn3.close()
except Exception as e:
    print(f"  {e}")

# 锁等待关系
print("\n" + "=" * 65)
print("  排查：INNODB_LOCK_WAITS 谁等谁")
print("=" * 65)
try:
    conn4 = pymysql.connect(**conn_params)
    with conn4.cursor() as c:
        c.execute("""SELECT
          b.trx_mysql_thread_id AS blocking_tid,
          r.trx_mysql_thread_id AS waiting_tid,
          b.trx_query AS blocking_query,
          r.trx_query AS waiting_query
        FROM information_schema.INNODB_LOCK_WAITS w
        JOIN information_schema.INNODB_TRX b ON b.trx_id = w.blocking_trx_id
        JOIN information_schema.INNODB_TRX r ON r.trx_id = w.requesting_trx_id""")
        for row in c.fetchall():
            print(f"  阻塞线程: {row[0]}  等待线程: {row[1]}")
            print(f"  阻塞SQL: {row[2]}")
            print(f"  等待SQL: {row[3]}")
    conn4.close()
except Exception as e:
    print(f"  {e}")

# 清理
with connA.cursor() as c:
    c.execute("ROLLBACK")  # A 回滚，释放锁
connA.close()
clean = pymysql.connect(**conn_params)
with clean.cursor() as c:
    c.execute("UPDATE t_product SET price=99.0 WHERE product_id=1")
    clean.commit()
clean.close()
print("\n  ✅ 清理完成，锁已释放")
print("=" * 65)
