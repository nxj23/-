-- 慢查询真实耗时测试（ms级）
USE shop_demo;
SET SESSION profiling = 1;

SELECT '========== 调优前模拟：FORCE INDEX(idx_user) 单列索引 + filesort ==========' AS info;

-- 用 FORCE INDEX 强制走单列索引 idx_user，模拟调优前的执行路径
EXPLAIN
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order FORCE INDEX(idx_user)
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

SELECT '--- 真实执行耗时（调优前路径）---' AS info;
SELECT COUNT(*) AS result_rows FROM (
  SELECT order_id, order_no, total_amount, status, pay_time
  FROM t_order FORCE INDEX(idx_user)
  WHERE user_id = 12345
    AND status = 1
    AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
  ORDER BY created_at DESC
  LIMIT 20
) t;

SELECT '========== 调优后：复合索引 idx_user_status_created ==========' AS info;

EXPLAIN
SELECT order_id, order_no, total_amount, status, pay_time
FROM t_order FORCE INDEX(idx_user_status_created)
WHERE user_id = 12345
  AND status = 1
  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 20;

SELECT '--- 真实执行耗时（调优后路径）---' AS info;
SELECT COUNT(*) AS result_rows FROM (
  SELECT order_id, order_no, total_amount, status, pay_time
  FROM t_order FORCE INDEX(idx_user_status_created)
  WHERE user_id = 12345
    AND status = 1
    AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
  ORDER BY created_at DESC
  LIMIT 20
) t;

SELECT '========== profiling 耗时对比 ==========' AS info;
SELECT query_id, LEFT(sql_text, 70) AS sql_preview,
       ROUND(duration_ms, 2) AS duration_ms
FROM (
  SELECT query_id, sql_text, (SELECT ROUND(SUM(dur)*1000, 2)
          FROM information_schema.profiling p2
          WHERE p2.query_id = p.query_id) AS duration_ms
  FROM information_schema.profiling p
  GROUP BY query_id, sql_text
) t
WHERE sql_text LIKE '%t_order%' AND sql_text NOT LIKE '%EXPLAIN%'
ORDER BY query_id;

-- 多次跑取稳定耗时
SELECT '========== 多次采样平均耗时（ms）=========' AS info;
SELECT 'before_avg_ms' AS metric,
  ROUND((SELECT SUM(dur) FROM information_schema.profiling WHERE query_id=1)*1000, 2) AS val
UNION ALL
SELECT 'after_avg_ms',
  ROUND((SELECT SUM(dur) FROM information_schema.profiling WHERE query_id=2)*1000, 2);
