-- =====================================================================
-- 02_init_data.sql  高速造数版
-- 策略：用数字辅助表生成笛卡尔积，单条 INSERT...SELECT 批量生成百万行
-- 全程约 5-10 分钟（取决于机器性能）
-- =====================================================================
USE shop_demo;
SET autocommit = 0;

-- ---------------------------------------------------------------------
-- 0. 创建数字辅助表（快速生成 0~999999）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS _nums;
CREATE TABLE _nums(n INT PRIMARY KEY);
INSERT INTO _nums
SELECT a.n + b.n*10 + c.n*100 + d.n*1000 + e.n*10000
FROM
  (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
   UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
  (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) b,
  (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3) c,
  (SELECT 0 n UNION SELECT 1 UNION SELECT 2) d,
  (SELECT 0 n UNION SELECT 1) e
ORDER BY n;
SELECT COUNT(*) AS nums_count FROM _nums;  -- 应有 40 万行

-- 如果需要更多，复制扩展
INSERT IGNORE INTO _nums
SELECT n + (SELECT MAX(n) FROM _nums) FROM _nums;

-- ---------------------------------------------------------------------
-- 1. 用户 5 万
-- ---------------------------------------------------------------------
SELECT '生成用户 50000...' AS stage;
INSERT INTO t_user (username, phone, email, city)
SELECT
  CONCAT('user_', n),
  CONCAT('138', LPAD(n, 8, '0')),
  CONCAT('user_', n, '@demo.com'),
  ELT((n % 5)+1, '北京','上海','广州','深圳','杭州')
FROM _nums
WHERE n < 50000;
COMMIT;
SELECT COUNT(*) FROM t_user;

-- ---------------------------------------------------------------------
-- 2. 商品 1 万
-- ---------------------------------------------------------------------
SELECT '生成商品 10000...' AS stage;
INSERT INTO t_product (product_name, category_id, price, stock, status)
SELECT
  CONCAT('商品-', LPAD(n, 6, '0')),
  (n % 20) + 1,
  ROUND(10 + (n % 990) + (n * 0.01), 2),
  1000,
  IF((n % 50) = 0, 0, 1)
FROM _nums
WHERE n < 10000;
COMMIT;
SELECT COUNT(*) FROM t_product;

-- ---------------------------------------------------------------------
-- 3. 订单 100 万（每 10 万条提交一次）
-- ---------------------------------------------------------------------
SELECT '生成订单 1000000...' AS stage;
-- 分 4 批执行，每批 25 万（避免事务过大）
INSERT INTO t_order (order_no, user_id, total_amount, status, pay_time, created_at)
SELECT
  CONCAT('NO', LPAD(n, 12, '0')),
  (n % 50000) + 1,
  ROUND(50 + RAND(9427 + n) * 9950, 2),
  IF(RAND(9427 + n) < 0.9, 1, 0),
  IF(RAND(9427 + n) < 0.9,
     DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + n) * 30) DAY), NULL),
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + n) * 180) DAY)
FROM _nums
WHERE n < 250000;
COMMIT;

INSERT INTO t_order (order_no, user_id, total_amount, status, pay_time, created_at)
SELECT
  CONCAT('NO', LPAD(250000 + n, 12, '0')),
  (n % 50000) + 1,
  ROUND(50 + RAND(9427 + 250000 + n) * 9950, 2),
  IF(RAND(9427 + 250000 + n) < 0.9, 1, 0),
  IF(RAND(9427 + 250000 + n) < 0.9,
     DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 250000 + n) * 30) DAY), NULL),
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 250000 + n) * 180) DAY)
FROM _nums
WHERE n < 250000;
COMMIT;

INSERT INTO t_order (order_no, user_id, total_amount, status, pay_time, created_at)
SELECT
  CONCAT('NO', LPAD(500000 + n, 12, '0')),
  (n % 50000) + 1,
  ROUND(50 + RAND(9427 + 500000 + n) * 9950, 2),
  IF(RAND(9427 + 500000 + n) < 0.9, 1, 0),
  IF(RAND(9427 + 500000 + n) < 0.9,
     DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 500000 + n) * 30) DAY), NULL),
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 500000 + n) * 180) DAY)
FROM _nums
WHERE n < 250000;
COMMIT;

INSERT INTO t_order (order_no, user_id, total_amount, status, pay_time, created_at)
SELECT
  CONCAT('NO', LPAD(750000 + n, 12, '0')),
  (n % 50000) + 1,
  ROUND(50 + RAND(9427 + 750000 + n) * 9950, 2),
  IF(RAND(9427 + 750000 + n) < 0.9, 1, 0),
  IF(RAND(9427 + 750000 + n) < 0.9,
     DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 750000 + n) * 30) DAY), NULL),
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 750000 + n) * 180) DAY)
FROM _nums
WHERE n < 250000;
COMMIT;

-- ---------------------------------------------------------------------
-- 4. 订单明细（每单 1~3 条，约 150 万）
-- ---------------------------------------------------------------------
SELECT '生成订单明细...' AS stage;
INSERT INTO t_order_item (order_id, product_id, quantity, unit_price)
SELECT
  o.order_id,
  ((o.order_id - 1) % 10000) + 1,
  ((o.order_id - 1) % 5) + 1,
  o.total_amount
FROM t_order o
WHERE o.order_id <= 1000000;
COMMIT;

-- 额外明细（30% 订单有第二条）
INSERT INTO t_order_item (order_id, product_id, quantity, unit_price)
SELECT
  o.order_id,
  (((o.order_id - 1) + 1) % 10000) + 1,
  ((o.order_id - 1) % 3) + 1,
  ROUND(o.total_amount / 2, 2)
FROM t_order o
WHERE o.order_id % 3 = 0 AND o.order_id <= 1000000;
COMMIT;

SET autocommit = 1;

-- 核对
SELECT '用户' AS tbl, COUNT(*) AS cnt FROM t_user
UNION ALL SELECT '商品', COUNT(*) FROM t_product
UNION ALL SELECT '订单', COUNT(*) FROM t_order
UNION ALL SELECT '明细', COUNT(*) FROM t_order_item;

-- 索引分析
SELECT table_name, index_name, column_name, cardinality
FROM information_schema.statistics
WHERE table_schema = 'shop_demo' AND table_name IN ('t_order','t_product','t_user')
ORDER BY table_name, index_name, seq_in_index;

-- 表大小
SELECT table_name, table_rows, ROUND(data_length/1024/1024, 1) AS data_mb,
       ROUND(index_length/1024/1024, 1) AS index_mb
FROM information_schema.tables WHERE table_schema = 'shop_demo';
