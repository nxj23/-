-- =====================================================================
-- demo_01_env.sql  第0幕 · 环境核对
-- 用法：mysql> source demo_01_env.sql
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
\! echo '  下一幕：source demo_02_slow_query.sql'
