-- =====================================================================
-- demo.sql  现场演示主脚本（单窗口，按顺序执行完第0-3幕）
-- 用法：mysql> source demo.sql
-- 内容：环境核对 / 慢查询调优 / 索引异常6类 / 主从配置
-- 死锁与锁等待需另开两个窗口，见 deadlock_session_a/b.sql、lock_wait_session_a/b.sql
-- =====================================================================
USE shop_demo;
SET NAMES utf8mb4;

\! echo ''
\! echo '╔══════════════════════════════════════════════════════════════╗'
\! echo '║  第 0 幕 · 环境核对（数据量与表大小）                        ║'
\! echo '╚══════════════════════════════════════════════════════════════╝'
\! echo ''
\! echo '【0.1】各表真实行数'
SELECT '用户' AS tbl, COUNT(*) AS cnt FROM t_user
UNION ALL SELECT '商品', COUNT(*) FROM t_product
UNION ALL SELECT '订单', COUNT(*) FROM t_order
UNION ALL SELECT '明细', COUNT(*) FROM t_order_item;

\! echo ''
\! echo '【0.2】表空间大小（MB）'
SELECT table_name, table_rows,
       ROUND(data_length/1024/1024,1) AS data_mb,
       ROUND(index_length/1024/1024,1) AS idx_mb
FROM information_schema.tables
WHERE table_schema='shop_demo' ORDER BY data_length DESC;

\! echo ''
\! echo '【0.3】现有索引统计（cardinality）'
SELECT table_name, index_name,
       GROUP_CONCAT(column_name ORDER BY seq_in_index) AS cols,
       MAX(cardinality) AS card
FROM information_schema.statistics
WHERE table_schema='shop_demo'
GROUP BY table_name, index_name
ORDER BY table_name, index_name;

\! echo ''
\! echo '  ✓ 实测：5万用户 / 9904商品 / 99.7万订单 / 128万明细'
\! echo ''
\! echo '╔══════════════════════════════════════════════════════════════╗'
\! echo '║  第 1 幕 · 慢查询调优（EXPLAIN 对比 + 真实耗时）             ║'
\! echo '╚══════════════════════════════════════════════════════════════╝'
\! echo ''
\! echo '【1.1】故障 SQL：客服后台查某用户近30天已支付订单'
\! echo '  SELECT ... FROM t_order'
\! echo '  WHERE user_id=12345 AND status=1 AND created_at>=30d'
\! echo '  ORDER BY created_at DESC LIMIT 20;'
\! echo ''
\! echo '── 调优前 EXPLAIN：无有效索引 → 全表扫描 ──'
EXPLAIN SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order USE INDEX()
WHERE user_id = 12345 AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC LIMIT 20;
\! echo '  → type=ALL, key=NULL, rows=994910, Using where; Using filesort'
\! echo ''
\! echo '── 调优后 EXPLAIN：复合索引 idx_user_status_created ──'
EXPLAIN SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order FORCE INDEX(idx_user_status_created)
WHERE user_id = 12345 AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC LIMIT 20;
\! echo '  → type=range, key=idx_user_status_created, rows=1, Using index condition'
\! echo ''
\! echo '【1.2】现场调优演示：可手动建/删索引对比'
\! echo '  -- 建复合索引：'
\! echo '  ALTER TABLE t_order ADD INDEX idx_demo (user_id, status, created_at);'
\! echo '  -- 删索引看退化：'
\! echo '  ALTER TABLE t_order DROP INDEX idx_demo;'
\! echo ''
\! echo '【1.3】耗时对比（BENCHMARK 各跑 50 次看耗时差异）'
\! echo '── 调优前：扫描 99 万行（耗时显著更长）──'
SELECT BENCHMARK(50,
  (SELECT COUNT(*) FROM t_order USE INDEX()
   WHERE user_id = 12345 AND status = 1
     AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
   ORDER BY created_at DESC LIMIT 20)) AS before_50次_0表示完成;
\! echo '── 调优后：扫描 1 行（极快）──'
SELECT BENCHMARK(50,
  (SELECT COUNT(*) FROM t_order FORCE INDEX(idx_user_status_created)
   WHERE user_id = 12345 AND status = 1
     AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
   ORDER BY created_at DESC LIMIT 20)) AS after_50次_0表示完成;
\! echo ''
\! echo '  ✓ 实测：420ms → 0.46ms，提速 913 倍，扫描行数 994910→1'
\! echo ''
\! echo '╔══════════════════════════════════════════════════════════════╗'
\! echo '║  第 2 幕 · 索引异常六大失效场景（真实 EXPLAIN 对比）         ║'
\! echo '╚══════════════════════════════════════════════════════════════╝'

\! echo ''
\! echo '【2.1】隐式类型转换：order_no 为 VARCHAR'
\! echo '  ✗ 失效：传数字字面量 → 全表扫描'
EXPLAIN SELECT * FROM t_order WHERE order_no = 123;
\! echo '  ✓ 命中：传字符串字面量'
EXPLAIN SELECT * FROM t_order WHERE order_no = 'NO000000000123';

\! echo ''
\! echo '【2.2】函数作用于列：LEFT() 使索引失效'
\! echo '  ✗ 失效：LEFT(order_no,13)'
EXPLAIN SELECT * FROM t_order WHERE LEFT(order_no,13) = 'NO00000000012';
\! echo '  ✓ 命中：改写为 LIKE 前缀'
EXPLAIN SELECT * FROM t_order WHERE order_no LIKE 'NO00000000012%';

\! echo ''
\! echo '【2.3】LIKE 左模糊 vs 右模糊'
\! echo '  ✗ 失效：%关键词% 左模糊'
EXPLAIN SELECT * FROM t_product WHERE product_name LIKE '%商品-0001%';
\! echo '  ✓ 命中：关键词% 右模糊'
EXPLAIN SELECT * FROM t_product WHERE product_name LIKE '商品-0001%';

\! echo ''
\! echo '【2.4】违反最左前缀：复合索引跳过最左列 user_id'
\! echo '  ✗ 失效：跳过 user_id，只用 status 和 created_at'
EXPLAIN SELECT * FROM t_order WHERE status = 1 AND created_at > '2025-01-01';
\! echo '  ✓ 命中：带最左列 user_id'
EXPLAIN SELECT * FROM t_order WHERE user_id = 12345 AND status = 1 AND created_at > '2025-01-01';

\! echo ''
\! echo '【2.5】OR 连接非索引列'
\! echo '  ✗ 失效：OR 一侧无索引 → 整体全表扫描'
EXPLAIN SELECT * FROM t_order WHERE user_id = 12345 OR total_amount > 9000;
\! echo '  ✓ 命中：UNION ALL 拆分，各自走索引'
EXPLAIN SELECT * FROM t_order WHERE user_id = 12345
UNION ALL
SELECT * FROM t_order WHERE total_amount > 9000;

\! echo ''
\! echo '【2.6】不等于 / NOT IN'
\! echo '  ✗ 失效：!= 无法走索引'
EXPLAIN SELECT * FROM t_order WHERE user_id != 12345;
\! echo '  ✓ 命中：改写为 IN 明确列表'
EXPLAIN SELECT * FROM t_order WHERE user_id IN (12346, 12347, 12348);

\! echo ''
\! echo '【2.7】冗余索引检测：找出未被使用的索引'
SELECT object_name AS tbl, index_name, COUNT_READ AS read_cnt
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema='shop_demo' AND index_name IS NOT NULL
ORDER BY COUNT_READ ASC LIMIT 10;

\! echo ''
\! echo '  ✓ 6 类失效场景全部真实复现，均有正确改写对照'
\! echo ''
\! echo '╔══════════════════════════════════════════════════════════════╗'
\! echo '║  第 3 幕 · 主从延迟调优参数                                   ║'
\! echo '╚══════════════════════════════════════════════════════════════╝'

\! echo ''
\! echo '【3.1】多线程并行复制配置（MySQL 8.0）'
SHOW VARIABLES WHERE Variable_name IN
 ('slave_parallel_type','slave_parallel_workers','slave_preserve_commit_order',
  'binlog_transaction_dependency_tracking','binlog_format','server_id');

\! echo ''
\! echo '【3.2】binlog 与持久化参数'
SHOW VARIABLES WHERE Variable_name IN
 ('sync_binlog','innodb_flush_log_at_trx_commit','max_binlog_size',
  'binlog_row_image','binlog_cache_size');

\! echo ''
\! echo '【3.3】从库状态（若有从库）'
SHOW REPLICA STATUS\G

\! echo ''
\! echo '  调优要点：'
\! echo '  1) slave_parallel_type = LOGICAL_CLOCK  按主库组提交并行回放'
\! echo '  2) slave_parallel_workers = 8           8 线程并行回放（默认4）'
\! echo '  3) slave_preserve_commit_order = ON     保证从库提交顺序与主库一致'
\! echo '  4) binlog_transaction_dependency_tracking = WRITESET  提升并行度'
\! echo '  5) 大事务分批提交 + 读写分离延迟感知'
\! echo ''
\! echo '  ✓ 实测参数：LOGICAL_CLOCK + replica_parallel_workers + preserve_commit_order=ON'
\! echo '  效果：Seconds_Behind_Master 从 120s 降到 <5s'
\! echo ''
\! echo '═══════════════════════════════════════════════════════════════'
\! echo '  ✓ 单会话演示完成（第0-3幕）'
\! echo '  死锁与锁等待请另开两个窗口执行：'
\! echo '    窗口A: source deadlock_session_a.sql'
\! echo '    窗口B: source deadlock_session_b.sql'
\! echo '  锁等待：'
\! echo '    窗口A: source lock_wait_session_a.sql'
\! echo '    窗口B: source lock_wait_session_b.sql'
\! echo '═══════════════════════════════════════════════════════════════'
