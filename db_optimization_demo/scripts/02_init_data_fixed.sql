-- 修正版造数脚本：确保 _nums 有 100 万行，真实造出 100 万订单
USE shop_demo;
SET autocommit = 0;

-- 0. 重建数字辅助表，倍增法精确生成 100 万行
DROP TABLE IF EXISTS _nums;
CREATE TABLE _nums(n INT PRIMARY KEY);
INSERT INTO _nums VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9);  -- 10
INSERT INTO _nums SELECT n + 10 FROM _nums;        -- 20
INSERT INTO _nums SELECT n + 20 FROM _nums;        -- 40
INSERT INTO _nums SELECT n + 40 FROM _nums;        -- 80
INSERT INTO _nums SELECT n + 80 FROM _nums;        -- 160
INSERT INTO _nums SELECT n + 160 FROM _nums;       -- 320
INSERT INTO _nums SELECT n + 320 FROM _nums;       -- 640
INSERT INTO _nums SELECT n + 640 FROM _nums;       -- 1280
INSERT INTO _nums SELECT n + 1280 FROM _nums;      -- 2560
INSERT INTO _nums SELECT n + 2560 FROM _nums;      -- 5120
INSERT INTO _nums SELECT n + 5120 FROM _nums;      -- 10240
INSERT INTO _nums SELECT n + 10240 FROM _nums;     -- 20480
INSERT INTO _nums SELECT n + 20480 FROM _nums;     -- 40960
INSERT INTO _nums SELECT n + 40960 FROM _nums;     -- 81920
INSERT INTO _nums SELECT n + 81920 FROM _nums;     -- 163840
INSERT INTO _nums SELECT n + 163840 FROM _nums;    -- 327680
INSERT INTO _nums SELECT n + 327680 FROM _nums;    -- 655360
INSERT INTO _nums SELECT n + 655360 FROM _nums WHERE n < 344640;  -- 1000000
COMMIT;
SELECT COUNT(*) AS nums_count FROM _nums;

-- 1. 用户 5 万
SELECT '生成用户 50000...' AS stage;
INSERT INTO t_user (username, phone, email, city)
SELECT
  CONCAT('user_', n),
  CONCAT('138', LPAD(n, 8, '0')),
  CONCAT('user_', n, '@demo.com'),
  ELT((n % 5)+1, '北京','上海','广州','深圳','杭州')
FROM _nums WHERE n < 50000;
COMMIT;
SELECT COUNT(*) AS user_cnt FROM t_user;

-- 2. 商品 1 万
SELECT '生成商品 10000...' AS stage;
INSERT INTO t_product (product_name, category_id, price, stock, status)
SELECT
  CONCAT('商品-', LPAD(n, 6, '0')),
  (n % 20) + 1,
  ROUND(10 + (n % 990) + (n * 0.01), 2),
  1000,
  IF((n % 50) = 0, 0, 1)
FROM _nums WHERE n < 10000;
COMMIT;
SELECT COUNT(*) AS product_cnt FROM t_product;

-- 3. 订单 100 万（分 4 批，每批 25 万）
SELECT '生成订单 1000000 (批次1/4)...' AS stage;
INSERT INTO t_order (order_no, user_id, total_amount, status, pay_time, created_at)
SELECT
  CONCAT('NO', LPAD(n, 12, '0')),
  (n % 50000) + 1,
  ROUND(50 + RAND(9427 + n) * 9950, 2),
  IF(RAND(9427 + n) < 0.9, 1, 0),
  IF(RAND(9427 + n) < 0.9, DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + n) * 30) DAY), NULL),
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + n) * 180) DAY)
FROM _nums WHERE n < 250000;
COMMIT;

SELECT '生成订单 1000000 (批次2/4)...' AS stage;
INSERT INTO t_order (order_no, user_id, total_amount, status, pay_time, created_at)
SELECT
  CONCAT('NO', LPAD(250000 + n, 12, '0')),
  (n % 50000) + 1,
  ROUND(50 + RAND(9427 + 250000 + n) * 9950, 2),
  IF(RAND(9427 + 250000 + n) < 0.9, 1, 0),
  IF(RAND(9427 + 250000 + n) < 0.9, DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 250000 + n) * 30) DAY), NULL),
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 250000 + n) * 180) DAY)
FROM _nums WHERE n < 250000;
COMMIT;

SELECT '生成订单 1000000 (批次3/4)...' AS stage;
INSERT INTO t_order (order_no, user_id, total_amount, status, pay_time, created_at)
SELECT
  CONCAT('NO', LPAD(500000 + n, 12, '0')),
  (n % 50000) + 1,
  ROUND(50 + RAND(9427 + 500000 + n) * 9950, 2),
  IF(RAND(9427 + 500000 + n) < 0.9, 1, 0),
  IF(RAND(9427 + 500000 + n) < 0.9, DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 500000 + n) * 30) DAY), NULL),
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 500000 + n) * 180) DAY)
FROM _nums WHERE n < 250000;
COMMIT;

SELECT '生成订单 1000000 (批次4/4)...' AS stage;
INSERT INTO t_order (order_no, user_id, total_amount, status, pay_time, created_at)
SELECT
  CONCAT('NO', LPAD(750000 + n, 12, '0')),
  (n % 50000) + 1,
  ROUND(50 + RAND(9427 + 750000 + n) * 9950, 2),
  IF(RAND(9427 + 750000 + n) < 0.9, 1, 0),
  IF(RAND(9427 + 750000 + n) < 0.9, DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 750000 + n) * 30) DAY), NULL),
  DATE_SUB(NOW(), INTERVAL FLOOR(RAND(9427 + 750000 + n) * 180) DAY)
FROM _nums WHERE n < 250000;
COMMIT;
SELECT COUNT(*) AS order_cnt FROM t_order;

-- 4. 订单明细（每单 1-2 条）
SELECT '生成订单明细...' AS stage;
INSERT INTO t_order_item (order_id, product_id, quantity, unit_price)
SELECT order_id, ((order_id - 1) % 10000) + 1, ((order_id - 1) % 5) + 1, total_amount
FROM t_order WHERE order_id <= 1000000;
COMMIT;
INSERT INTO t_order_item (order_id, product_id, quantity, unit_price)
SELECT order_id, ((order_id % 10000) + 1), ((order_id - 1) % 3) + 1, ROUND(total_amount / 2, 2)
FROM t_order WHERE order_id % 3 = 0 AND order_id <= 1000000;
COMMIT;

SET autocommit = 1;

-- 核对数据量
SELECT '用户' AS tbl, COUNT(*) AS cnt FROM t_user
UNION ALL SELECT '商品', COUNT(*) FROM t_product
UNION ALL SELECT '订单', COUNT(*) FROM t_order
UNION ALL SELECT '明细', COUNT(*) FROM t_order_item;

-- 表大小
SELECT table_name, table_rows, ROUND(data_length/1024/1024, 1) AS data_mb,
       ROUND(index_length/1024/1024, 1) AS index_mb
FROM information_schema.tables WHERE table_schema = 'shop_demo' ORDER BY data_length DESC;
