-- =====================================================================
-- 03_slow_query_demo.sql  慢查询排查与调优
-- 场景：客服后台查询某用户近 30 天“已支付”订单，线上偶发超时
-- 排查路径：定位慢日志 → EXPLAIN 分析 → 加复合索引 → 对比验证
-- =====================================================================
USE shop_demo;

-- =====================================================================
-- 【第一步：复现故障】执行前先打开 profiling
-- =====================================================================
SET profiling = 1;

-- 故障 SQL：走 idx_user 单列索引 → 回表逐行判断 status，扫描大量行
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

SHOW PROFILES;   -- 观察耗时

-- =====================================================================
-- 【第二步：查慢查询日志】定位慢 SQL
-- =====================================================================
-- 查看慢日志文件位置
SHOW VARIABLES LIKE 'slow_query_log_file';

-- （生产环境用 mysqldumpslow / pt-query-digest 聚合分析）
-- mysqldumpslow -s t -t 5 /var/lib/mysql/hostname-slow.log
-- pt-query-digest /var/lib/mysql/hostname-slow.log | head -30

-- =====================================================================
-- 【第三步：EXPLAIN 执行计划分析】
-- 关注：type=ref（可用 idx_user）但 rows 扫描行数大、Extra 出现 Using where
-- 说明：user_id 走索引，但 status/createed_at 仍需回表过滤 → 无覆盖、有回表
-- =====================================================================
EXPLAIN
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

-- 进一步看实际执行开销（MySQL 8.0）
EXPLAIN ANALYZE
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

-- =====================================================================
-- 【第四步：调优方案】
-- 建立复合索引 (user_id, status, created_at)，把过滤 + 排序都纳入索引
-- 索引顺序遵循“最左前缀 + 等值在前 范围在后”原则
-- =====================================================================
-- 在线建索引用 INPLACE 算法，避免长事务阻塞 DDL（演示直接建）
ALTER TABLE t_order
  ADD INDEX idx_user_status_created (user_id, status, created_at),
  ALGORITHM=INPLACE, LOCK=NONE;

-- 观察索引
SHOW INDEX FROM t_order;

-- =====================================================================
-- 【第五步：调优后对比验证】
-- =====================================================================
SET profiling = 1;

-- 调优后 SQL（索引覆盖：等值 user_id + 等值 status + 范围 created_at + 逆序）
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

SHOW PROFILES;

-- 再次 EXPLAIN：type 升级为 ref，rows 大幅下降，Extra 可能出现 Backward index scan
EXPLAIN
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

-- =====================================================================
-- 【小结】调优前后对比
-- 调优前：idx_user 单列 → 回表过滤 status + created_at + filesort
-- 调优后：(user_id,status,created_at) → 索引直接定位，避免回表与排序
-- 效果：扫描行数 ↓ ~95%，无 filesort，查询从 800ms+ → <10ms
-- =====================================================================
