-- =====================================================================
-- 04_index_anomaly_demo.sql  索引异常排查与调优
-- 演示 6 类常见“索引失效”场景及对应改写/调优手段
-- =====================================================================
USE shop_demo;

-- 先补建若干索引，作为“本应被使用”的索引基线
ALTER TABLE t_product
  ADD INDEX idx_name (product_name),
  ADD INDEX idx_status (status),
  ALGORITHM=INPLACE, LOCK=NONE;

-- =====================================================================
-- 【异常 1：对索引列使用函数/表达式 → 索引失效】
-- 场景：统计某天注册用户
-- =====================================================================
-- ❌ 失败写法：DATE(created_at) 使 idx 失效 → 全表扫描
EXPLAIN SELECT * FROM t_user WHERE DATE(created_at) = CURDATE();

-- ✅ 改写：改为范围查询，命中索引
EXPLAIN SELECT * FROM t_user
WHERE created_at >= CURDATE()
  AND created_at < DATE_ADD(CURDATE(), INTERVAL 1 DAY);

-- =====================================================================
-- 【异常 2：隐式类型转换 → 索引失效】
-- 场景：order_no 是 VARCHAR，但传入数字字面量
-- =====================================================================
-- ❌ 失败写法：order_no='NO...' 被转为数字比较，索引失效
EXPLAIN SELECT * FROM t_order WHERE order_no = 123;

-- ✅ 改写：传入字符串字面量
EXPLAIN SELECT * FROM t_order WHERE order_no = '000000000123';

-- =====================================================================
-- 【异常 3：LIKE 以 % 开头 → 索引失效】
-- 场景：按商品名模糊搜索
-- =====================================================================
-- ❌ 失败写法：左模糊，全表扫描
EXPLAIN SELECT * FROM t_product WHERE product_name LIKE '%商品-0001%';

-- ✅ 改写 1：右模糊可命中索引
EXPLAIN SELECT * FROM t_product WHERE product_name LIKE '商品-0001%';

-- ✅ 改写 2：高频模糊检索建议引入全文索引或 ES
ALTER TABLE t_product ADD FULLTEXT INDEX ft_name (product_name) WITH PARSER ngram;
EXPLAIN SELECT * FROM t_product WHERE MATCH(product_name) AGAINST('商品 0001' IN BOOLEAN MODE);

-- =====================================================================
-- 【异常 4：OR 连接条件中有一侧无索引 → 整体放弃索引】
-- =====================================================================
-- ❌ 失败写法：stock 无索引，导致整条放弃索引
EXPLAIN SELECT * FROM t_product WHERE category_id = 5 OR stock < 100;

-- ✅ 改写 1：拆成 UNION ALL，各自走索引
EXPLAIN
  SELECT * FROM t_product WHERE category_id = 5
  UNION ALL
  SELECT * FROM t_product WHERE stock < 100 AND category_id <> 5;

-- ✅ 改写 2：为 stock 补索引（按需）
ALTER TABLE t_product ADD INDEX idx_stock (stock), ALGORITHM=INPLACE, LOCK=NONE;
EXPLAIN SELECT * FROM t_product WHERE category_id = 5 OR stock < 100;

-- =====================================================================
-- 【异常 5：复合索引未遵循最左前缀 → 失效】
-- 复合索引 idx_user_status_created(user_id, status, created_at)
-- =====================================================================
-- ❌ 失败写法：跳过 user_id 直接用 status，无法命中
EXPLAIN SELECT * FROM t_order WHERE status = 1;

-- ✅ 改写：带上最左列 user_id
EXPLAIN SELECT * FROM t_order WHERE user_id = 12345 AND status = 1;

-- =====================================================================
-- 【异常 6：!= / NOT IN / IS NOT NULL 导致范围扫描退化】
-- =====================================================================
-- ❌ 写法：<> 通常无法精确定位，扫描成本高
EXPLAIN SELECT * FROM t_product WHERE status <> 1;

-- ✅ 改写：枚举等值（status 只有 0/1）
EXPLAIN SELECT * FROM t_product WHERE status = 0;

-- =====================================================================
-- 【诊断工具】查看索引使用情况（MySQL 8.0 sys 库）
-- 查找“从未被使用”的冗余索引，便于清理
-- =====================================================================
SELECT object_schema, object_name, index_name,
       rows_inserted, rows_read
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'shop_demo'
ORDER BY rows_read DESC
LIMIT 10;

-- 冗余/重复索引检测
SELECT s.TABLE_SCHEMA, s.TABLE_NAME, s.INDEX_NAME, GROUP_CONCAT(s.COLUMN_NAME) AS cols
FROM information_schema.STATISTICS s
WHERE s.TABLE_SCHEMA = 'shop_demo'
GROUP BY s.TABLE_SCHEMA, s.TABLE_NAME, s.INDEX_NAME
ORDER BY s.TABLE_NAME, s.INDEX_NAME;

-- =====================================================================
-- 【小结】索引失效 6 大类：函数列、隐式转换、左模糊、OR 缺索引、
--         违反最左前缀、!=/NOT IN。逐一改写并复核 EXPLAIN。
-- =====================================================================
