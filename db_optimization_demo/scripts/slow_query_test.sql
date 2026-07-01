-- 慢查询调优真实测试（修正版）
USE shop_demo;

SELECT '========== 调优前：只有 idx_user 单列索引 ==========' AS info;

SELECT '--- 调优前 EXPLAIN 结果 ---' AS info;
EXPLAIN
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

SELECT '--- user_id=12345 的订单数（评估回表扫描量）---' AS info;
SELECT COUNT(*) AS user_total_orders, SUM(status=1) AS paid_orders FROM t_order WHERE user_id = 12345;

SELECT '========== 建立复合索引 (user_id, status, created_at) ==========' AS info;
ALTER TABLE t_order
  ADD INDEX idx_user_status_created (user_id, status, created_at),
  ALGORITHM=INPLACE, LOCK=NONE;

SELECT '--- 调优后 EXPLAIN 结果 ---' AS info;
EXPLAIN
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

SELECT '--- t_order 索引列表 ---' AS info;
SELECT index_name, GROUP_CONCAT(column_name ORDER BY seq_in_index) AS cols, cardinality
FROM information_schema.statistics
WHERE table_schema='shop_demo' AND table_name='t_order'
GROUP BY index_name, cardinality ORDER BY index_name;
