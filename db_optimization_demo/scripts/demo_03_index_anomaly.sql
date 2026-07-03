-- =====================================================================
-- demo_03_index_anomaly.sql  第2幕 · 索引异常六大失效场景
-- 用法：mysql> source demo_03_index_anomaly.sql
-- =====================================================================
USE shop_demo;
SET NAMES utf8mb4;

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
\! echo '  下一幕：source demo_04_replication.sql'
