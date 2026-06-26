-- =====================================================================
-- 02_init_data.sql  造数脚本
-- 用存储过程批量生成：用户 5 万、商品 1 万、订单 100 万、明细 ~200 万
-- 造数量足够大，使得“无索引/回表”扫描能真实触发慢查询。
-- 执行：mysql -uroot -p < 02_init_data.sql   （需先跑 01_schema.sql）
-- =====================================================================
USE shop_demo;

-- 关闭自动提交，加速批量写入
SET autocommit = 0;

-- ---------------------------------------------------------------------
-- 1. 用户 5 万
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS gen_users;
DELIMITER $$
CREATE PROCEDURE gen_users(IN n INT)
BEGIN
  DECLARE i INT DEFAULT 0;
  WHILE i < n DO
    INSERT INTO t_user(username, phone, email, city)
    VALUES (CONCAT('user_', i),
            CONCAT('138', LPAD(i, 8, '0')),
            CONCAT('user_', i, '@demo.com'),
            ELT((i % 5)+1, '北京','上海','广州','深圳','杭州'));
    SET i = i + 1;
  END WHILE;
  COMMIT;
END$$
DELIMITER ;

CALL gen_users(50000);

-- ---------------------------------------------------------------------
-- 2. 商品 1 万（分布在 20 个类目）
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS gen_products;
DELIMITER $$
CREATE PROCEDURE gen_products(IN n INT)
BEGIN
  DECLARE i INT DEFAULT 0;
  WHILE i < n DO
    INSERT INTO t_product(product_name, category_id, price, stock, status)
    VALUES (CONCAT('商品-', LPAD(i, 6, '0')),
            (i % 20) + 1,
            ROUND(10 + (i % 990) + (i*0.01), 2),
            1000,
            IF((i % 50)=0, 0, 1));          -- 少量下架商品
    SET i = i + 1;
  END WHILE;
  COMMIT;
END$$
DELIMITER ;

CALL gen_products(10000);

-- ---------------------------------------------------------------------
-- 3. 订单 100 万（90% 已支付，制造大范围 status 过滤场景）
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS gen_orders;
DELIMITER $$
CREATE PROCEDURE gen_orders(IN n INT)
BEGIN
  DECLARE i INT DEFAULT 0;
  DECLARE v_uid BIGINT;
  DECLARE v_amt DECIMAL(12,2);
  DECLARE v_status TINYINT;
  DECLARE v_pid BIGINT;
  WHILE i < n DO
    SET v_uid    = (i % 50000) + 1;
    SET v_amt    = ROUND(50 + RAND() * 9950, 2);
    SET v_status = IF(RAND() < 0.9, 1, 0);  -- 90% 已支付
    INSERT INTO t_order(order_no, user_id, total_amount, status, pay_time, created_at)
    VALUES (CONCAT('NO', LPAD(i, 12, '0')),
            v_uid, v_amt, v_status,
            IF(v_status=1, DATE_SUB(NOW(), INTERVAL FLOOR(RAND()*30) DAY), NULL),
            DATE_SUB(NOW(), INTERVAL FLOOR(RAND()*180) DAY));

    -- 每单 1~3 条明细
    INSERT INTO t_order_item(order_id, product_id, quantity, unit_price)
    VALUES (LAST_INSERT_ID(),
            (i % 10000) + 1,
            (i % 5) + 1,
            v_amt);

    IF (i % 3) = 0 THEN
      INSERT INTO t_order_item(order_id, product_id, quantity, unit_price)
      VALUES (LAST_INSERT_ID(), ((i+1) % 10000)+1, (i%3)+1, ROUND(v_amt/2,2));
    END IF;

    SET i = i + 1;
    IF (i % 5000) = 0 THEN COMMIT; END IF;  -- 分批提交
  END WHILE;
  COMMIT;
END$$
DELIMITER ;

CALL gen_orders(1000000);

COMMIT;
SET autocommit = 1;

-- 统计核对
SELECT '用户数' AS tbl, COUNT(*) AS cnt FROM t_user
UNION ALL SELECT '商品数', COUNT(*) FROM t_product
UNION ALL SELECT '订单数', COUNT(*) FROM t_order
UNION ALL SELECT '明细数', COUNT(*) FROM t_order_item;
