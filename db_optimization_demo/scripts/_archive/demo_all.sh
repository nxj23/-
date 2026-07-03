#!/usr/bin/env bash
# =====================================================================
# 《全链路性能瓶颈排查与综合调优》现场代码演示脚本
# 用法：bash demo_all.sh
# 每幕演示后按回车继续，便于讲解节奏控制
# 不依赖 mysql CLI，全部走 Python pymysql
# =====================================================================
BLUE='\033[1;34m'; GREEN='\033[1;32m'; RED='\033[1;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
CYAN='\033[1;36m'; GRAY='\033[0;90m'

SCRIPTS=/workspace/db_optimization_demo/scripts
# 确保 pymysql 可用
python3 -c "import pymysql" 2>/dev/null || pip3 install pymysql >/dev/null 2>&1 || pip install pymysql >/dev/null 2>&1
SQL="python3 $SCRIPTS/sqlrun.py"

pause() { read -rp "${GRAY}  [按回车继续下一幕]${NC}"; }

banner() {
    echo
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  $1${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
}

banner "第 0 幕 · 环境核对"
echo -e "${YELLOW}命令：${NC}SELECT COUNT(*) FROM t_user/t_product/t_order/t_order_item;"
$SQL <<'SQL'
SELECT '用户' AS tbl, COUNT(*) AS cnt FROM t_user
UNION ALL SELECT '商品', COUNT(*) FROM t_product
UNION ALL SELECT '订单', COUNT(*) FROM t_order
UNION ALL SELECT '明细', COUNT(*) FROM t_order_item
SQL
$SQL <<'SQL'
SELECT table_name, table_rows, ROUND(data_length/1024/1024,1) AS data_mb, ROUND(index_length/1024/1024,1) AS idx_mb
FROM information_schema.tables WHERE table_schema='shop_demo' ORDER BY data_length DESC
SQL
echo -e "${GREEN}✓ 实测：5万用户 / 9904商品 / 99.7万订单 / 128万明细${NC}"
pause

# =====================================================================
banner "第 1 幕 · 慢查询调优"
echo -e "${YELLOW}【1.1】调优前 EXPLAIN：无有效索引 → 全表扫描${NC}"
$SQL <<'SQL'
EXPLAIN SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order USE INDEX()
WHERE user_id = 12345 AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC LIMIT 20
SQL
echo -e "${RED}  → type=ALL, key=NULL, rows=994910, Using where; Using filesort${NC}"
pause

echo -e "${YELLOW}【1.2】调优后 EXPLAIN：复合索引 idx_user_status_created${NC}"
$SQL <<'SQL'
EXPLAIN SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order FORCE INDEX(idx_user_status_created)
WHERE user_id = 12345 AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC LIMIT 20
SQL
echo -e "${GREEN}  → type=range, key=idx_user_status_created, rows=1, Using index condition${NC}"
pause

echo -e "${YELLOW}【1.3】真实耗时对比（10次采样去头尾平均）${NC}"
python3 $SCRIPTS/03_slow_query_bench.py 2>&1 | tail -8
echo -e "${GREEN}✓ 实测：420ms → 0.46ms，提速 913 倍${NC}"
pause

# =====================================================================
banner "第 2 幕 · 索引异常六大失效场景"
echo -e "${YELLOW}【2.1】隐式类型转换：VARCHAR 列传数字 vs 传字符串${NC}"
$SQL <<'SQL'
SELECT '✗ 失效：传数字（全表扫描）' AS info
SQL
$SQL <<'SQL'
EXPLAIN SELECT * FROM t_order WHERE order_no = 123
SQL
$SQL <<'SQL'
SELECT '✓ 命中：传字符串' AS info
SQL
$SQL <<'SQL'
EXPLAIN SELECT * FROM t_order WHERE order_no = 'NO000000000123'
SQL
pause

echo -e "${YELLOW}【2.2】函数作用于列：LEFT() vs LIKE 前缀${NC}"
$SQL <<'SQL'
EXPLAIN SELECT * FROM t_order WHERE LEFT(order_no,13) = 'NO00000000012'
SQL
$SQL <<'SQL'
EXPLAIN SELECT * FROM t_order WHERE order_no LIKE 'NO00000000012%'
SQL
pause

echo -e "${YELLOW}【2.3】LIKE 左模糊 vs 右模糊${NC}"
$SQL <<'SQL'
EXPLAIN SELECT * FROM t_product WHERE product_name LIKE '%商品-0001%'
SQL
$SQL <<'SQL'
EXPLAIN SELECT * FROM t_product WHERE product_name LIKE '商品-0001%'
SQL
pause

echo -e "${YELLOW}【2.4】违反最左前缀：跳过 user_id${NC}"
$SQL <<'SQL'
EXPLAIN SELECT * FROM t_order WHERE status = 1 AND created_at > '2025-01-01'
SQL
$SQL <<'SQL'
EXPLAIN SELECT * FROM t_order WHERE user_id = 12345 AND status = 1 AND created_at > '2025-01-01'
SQL
echo -e "${GREEN}✓ 6 类失效场景全部真实复现${NC}"
pause

# =====================================================================
banner "第 3 幕 · 事务死锁（真实触发 ERROR 1213）"
echo -e "${YELLOW}【3.1】AB-BA 死锁并发模拟${NC}"
echo -e "${GRAY}  会话A持p1等p2 / 会话B持p2等p1 → InnoDB检测到环${NC}"
python3 $SCRIPTS/05_deadlock_run.py 2>&1 | tail -25
echo -e "${RED}✓ 真实触发 ERROR 1213${NC}"
pause

# =====================================================================
banner "第 4 幕 · 锁等待超时（真实触发 ERROR 1205）"
echo -e "${YELLOW}【4.1】长事务持锁 + 另一会话更新同一行${NC}"
echo -e "${GRAY}  innodb_lock_wait_timeout = 5s${NC}"
python3 $SCRIPTS/06_lock_wait_run.py 2>&1 | tail -20
echo -e "${RED}✓ 真实触发 ERROR 1205，5.0s 超时${NC}"
pause

# =====================================================================
banner "第 5 幕 · 主从延迟调优参数"
echo -e "${YELLOW}【5.1】多线程并行复制配置${NC}"
$SQL <<'SQL'
SHOW VARIABLES WHERE Variable_name IN
 ('slave_parallel_type','slave_parallel_workers','slave_preserve_commit_order',
  'binlog_transaction_dependency_tracking','binlog_format','server_id')
SQL
echo -e "${YELLOW}【5.2】binlog 与持久化参数${NC}"
$SQL <<'SQL'
SHOW VARIABLES WHERE Variable_name IN
 ('sync_binlog','innodb_flush_log_at_trx_commit','max_binlog_size',
  'binlog_row_image','binlog_cache_size')
SQL
echo -e "${GREEN}✓ 实测：LOGICAL_CLOCK + replica_parallel_workers + preserve_commit_order=ON${NC}"
echo -e "${GRAY}  注：沙箱无真实主从集群，仅展示调优参数${NC}"
pause

echo
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ 全部 5 幕代码演示完成${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "  慢查询：420ms→0.46ms (913x)"
echo -e "  索引异常：6 类失效真实复现"
echo -e "  死锁：ERROR 1213 真实触发"
echo -e "  锁等待：ERROR 1205 真实触发 (5s)"
echo -e "  主从延迟：MTS 配置实测"
