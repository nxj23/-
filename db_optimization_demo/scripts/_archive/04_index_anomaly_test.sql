-- 索引异常真实测试：6类失效场景的 EXPLAIN 对比
-- 先补建对比所需索引（演示"建了索引却不用"的典型场景）
USE shop_demo;

SELECT '========== 0. 补建演示用索引（幂等）=========' AS info;
SET @s = IF((SELECT COUNT(*) FROM information_schema.statistics
             WHERE table_schema='shop_demo' AND table_name='t_order' AND index_name='uk_order_no')=0,
            'ALTER TABLE t_order ADD UNIQUE KEY uk_order_no (order_no)','SELECT "uk_order_no exists"');
PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @s = IF((SELECT COUNT(*) FROM information_schema.statistics
             WHERE table_schema='shop_demo' AND table_name='t_user' AND index_name='idx_user_created')=0,
            'ALTER TABLE t_user ADD KEY idx_user_created (created_at)','SELECT "idx_user_created exists"');
PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @s = IF((SELECT COUNT(*) FROM information_schema.statistics
             WHERE table_schema='shop_demo' AND table_name='t_product' AND index_name='idx_product_name')=0,
            'ALTER TABLE t_product ADD KEY idx_product_name (product_name)','SELECT "idx_product_name exists"');
PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ANALYZE TABLE t_order, t_user, t_product;

SELECT '========== 场景1：隐式类型转换 ==========' AS info;
SELECT '--- 错误写法：VARCHAR列传入数字（索引失效，全表扫描）---' AS info;
EXPLAIN SELECT * FROM t_order WHERE order_no = 123;

SELECT '--- 正确写法：传入字符串（命中 uk_order_no）---' AS info;
EXPLAIN SELECT * FROM t_order WHERE order_no = 'NO000000000123';

SELECT '========== 场景2：函数作用于列 ==========' AS info;
SELECT '--- 错误写法：LEFT()函数使索引失效 ---' AS info;
EXPLAIN SELECT * FROM t_order WHERE LEFT(order_no, 13) = 'NO00000000012';

SELECT '--- 正确写法：改写为 LIKE 前缀（命中 uk_order_no）---' AS info;
EXPLAIN SELECT * FROM t_order WHERE order_no LIKE 'NO00000000012%';

SELECT '========== 场景3：LIKE 左模糊 ==========' AS info;
SELECT '--- 错误写法：%关键词 左模糊（索引失效）---' AS info;
EXPLAIN SELECT * FROM t_product WHERE product_name LIKE '%商品-0001%';

SELECT '--- 正确写法：关键词% 右模糊（命中 idx_product_name）---' AS info;
EXPLAIN SELECT * FROM t_product WHERE product_name LIKE '商品-0001%';

SELECT '========== 场景4：OR 连接非索引列 ==========' AS info;
SELECT '--- 错误写法：OR 中含非索引列（整体走全表扫描）---' AS info;
EXPLAIN SELECT * FROM t_order WHERE user_id = 12345 OR total_amount > 9000;

SELECT '--- 正确写法：UNION ALL 拆分，各自命中索引 ---' AS info;
EXPLAIN SELECT * FROM t_order WHERE user_id = 12345
UNION ALL
SELECT * FROM t_order WHERE total_amount > 9000;

SELECT '========== 场景5：违反最左前缀 ==========' AS info;
SELECT '--- 错误写法：跳过 user_id 直接用 status（复合索引失效）---' AS info;
EXPLAIN SELECT * FROM t_order WHERE status = 1 AND created_at > '2025-01-01';

SELECT '--- 正确写法：带最左列 user_id（命中复合索引）---' AS info;
EXPLAIN SELECT * FROM t_order
WHERE user_id = 12345 AND status = 1 AND created_at > '2025-01-01';

SELECT '========== 场景6：!= / NOT IN ==========' AS info;
SELECT '--- 错误写法：!= 无法走索引（全表扫描）---' AS info;
EXPLAIN SELECT * FROM t_order WHERE user_id != 12345;

SELECT '--- 正确写法：改写为 IN 明确列表 / 范围 ---' AS info;
EXPLAIN SELECT * FROM t_order WHERE user_id IN (12346, 12347, 12348);

SELECT '========== 冗余/未用索引检测 ==========' AS info;
SELECT object_name AS tbl, index_name, COUNT_READ AS read_cnt
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema='shop_demo' AND index_name IS NOT NULL
ORDER BY COUNT_READ DESC LIMIT 10;

SELECT '========== 索引统计（cardinality）=========' AS info;
SELECT table_name, index_name, GROUP_CONCAT(column_name ORDER BY seq_in_index) AS cols,
       MAX(cardinality) AS card
FROM information_schema.statistics
WHERE table_schema='shop_demo'
GROUP BY table_name, index_name
ORDER BY table_name, index_name;
