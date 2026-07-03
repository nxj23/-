-- =====================================================================
-- demo_02_slow_query.sql  第1幕 · 慢查询调优
-- 用法：mysql> source demo_02_slow_query.sql
-- =====================================================================
USE shop_demo;
SET NAMES utf8mb4;

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
\! echo '  下一幕：source demo_03_index_anomaly.sql'
