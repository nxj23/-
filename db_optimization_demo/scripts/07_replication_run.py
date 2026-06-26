#!/usr/bin/env python3
"""
主从延迟演示脚本（07_replication_demo.py）
单机环境：展示所有诊断命令 + 大批量写入对 binlog 的影响
"""
import pymysql
import subprocess
import time

conn_params = {
    'host': 'localhost', 'user': 'root', 'db': 'shop_demo',
    'unix_socket': '/var/run/mysqld/mysqld.sock',
    'autocommit': False, 'charset': 'utf8mb4'
}

print("=" * 65)
print("  主从延迟诊断演示")
print("=" * 65)

# 1. 查看 binlog 配置（主从延迟根因在此）
print("\n[1] Binlog 配置（主库写入→binlog→从库拉取）")
conn = pymysql.connect(**conn_params)
with conn.cursor() as c:
    c.execute("SHOW MASTER STATUS")
    row = c.fetchone()
    if row:
        print(f"  Binlog 文件: {row[0]}")
        print(f"  位置: {row[1]}")
        print(f"  Binlog_Do_DB: {row[2]}")
        print(f"  Binlog_Ignore_DB: {row[3]}")
    else:
        print("  ⚠️  Binlog 未开启（单机演示环境）")

    c.execute("SHOW VARIABLES LIKE 'log_bin'")
    for r in c.fetchall():
        print(f"  {r[0]}: {r[1]}")

    c.execute("SHOW VARIABLES LIKE 'sync_binlog'")
    for r in c.fetchall():
        print(f"  {r[0]}: {r[1]}")

    c.execute("SHOW VARIABLES LIKE 'binlog_format'")
    for r in c.fetchall():
        print(f"  {r[0]}: {r[1]}")
conn.close()

# 2. 从库状态（单机演示：展示命令 + 说明）
print("\n[2] 从库状态（SHOW REPLICA STATUS - MySQL 8.0）")
result = subprocess.run(
    ["mysql", "-u", "root", "-e", "SHOW REPLICA STATUS\\G"],
    capture_output=True, text=True
)
out = result.stdout + result.stderr
if "Replica" in out or "Slave" in out:
    for line in out.split('\n'):
        if line.strip():
            print(f"  {line.strip()}")
else:
    print("  ⚠️  当前为单机 MySQL，无从库")
    print("  在真实主从环境中执行此命令将显示：")
    print("    Replica_IO_Running: Yes/No   ← IO 线程状态")
    print("    Replica_SQL_Running: Yes/No  ← SQL 线程状态")
    print("    Seconds_Behind_Master: N     ← 延迟秒数")
    print("    Read_Master_Log_Pos vs Exec_Master_Log_Pos  ← 位点差")
    print("    Retrieved_Gtid_Set / Executed_Gtid_Set        ← GTID 位点")

# 3. 大批量写入（模拟大促洪峰，观察 binlog 增长）
print("\n[3] 批量写入测试（模拟大促库存变更洪峰）")
conn = pymysql.connect(**conn_params)
conn.begin()
with conn.cursor() as c:
    start = time.time()
    # 批量插入 10 万条库存变更日志
    print("  插入 100000 条库存变更日志...")
    c.execute("""
      INSERT INTO t_inventory_log(product_id, delta, order_no, created_at)
      SELECT
        (n % 10000) + 1,
        -1,
        CONCAT('NO', LPAD(n, 12, '0')),
        NOW()
      FROM _nums WHERE n < 100000
    """)
    conn.commit()
    elapsed = time.time() - start
    print(f"  ✅ 100000 条写入完成，耗时 {elapsed:.2f}s")

    # 检查表大小
    c.execute("SELECT COUNT(*) FROM t_inventory_log")
    cnt = c.fetchone()[0]
    print(f"  t_inventory_log 当前行数: {cnt:,}")

    # 查看 binlog 大小变化
    c.execute("SHOW MASTER STATUS")
    row = c.fetchone()
    if row:
        print(f"  Binlog 当前位置: {row[1]}")
conn.close()

# 4. 并行复制配置（MySQL 8.0 核心调优）
print("\n[4] 多线程并行复制配置（MySQL 8.0 LOGICAL_CLOCK）")
conn = pymysql.connect(**conn_params)
with conn.cursor() as c:
    # 查看当前配置
    c.execute("SHOW VARIABLES LIKE 'replica_parallel_%'")
    print("  当前并行复制配置:")
    for r in c.fetchall():
        print(f"    {r[0]}: {r[1]}")

    # 在真实从库上执行以下命令
    print("\n  📋 在从库执行以下命令开启并行复制:")
    commands = [
        "STOP REPLICA;",
        "SET GLOBAL replica_parallel_workers = 8;",
        "SET GLOBAL replica_parallel_type = 'LOGICAL_CLOCK';",
        "SET GLOBAL binlog_transaction_dependency_tracking = 'WRITESET';",
        "START REPLICA;",
    ]
    for cmd in commands:
        print(f"    mysql> {cmd}")

    print("\n  ✅ LOGICAL_CLOCK: 主库组提交的事务可并行回放，")
    print("     大促写入激增时，延迟可从 120s+ 降至 <5s")
conn.close()

# 5. 读写分离延迟感知
print("\n[5] 读写分离延迟感知（业务层方案）")
print("  方案1: 下单后立即读订单 → 走主库")
print("  方案2: 报表查询（容忍延迟） → 走从库")
print("  方案3: 延迟感知中间件（如 ShardingSphere-proxy）")
print("         → 延迟超阈值自动切主库")
print("  方案4: 业务侧 5s 快速失败 + 重试，避免用户感知")

print("\n" + "=" * 65)
print("  主从延迟演示完成")
print("=" * 65)
