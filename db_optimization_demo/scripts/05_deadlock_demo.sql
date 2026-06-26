-- =====================================================================
-- 05_deadlock_demo.sql  事务死锁排查与调优
-- 场景：并发下单扣减库存，两个事务以相反顺序锁定商品行 → AB-BA 死锁
-- 复现方式：开两个会话(终端)，按表格时间线交替执行
-- =====================================================================
USE shop_demo;

-- 准备：确保商品 1、2 库存充足
UPDATE t_product SET stock = 1000 WHERE product_id IN (1, 2);

-- =====================================================================
-- 【第一步：复现死锁】需开两个 MySQL 会话 A、B
-- 时间线：
--   t1  A: BEGIN; UPDATE t_product SET stock=stock-1 WHERE product_id=1;
--   t2  B: BEGIN; UPDATE t_product SET stock=stock-1 WHERE product_id=2;
--   t3  A: UPDATE t_product SET stock=stock-1 WHERE product_id=2;  -- 等 B 的锁
--   t4  B: UPDATE t_product SET stock=stock-1 WHERE product_id=1;  -- 死锁！B 被回滚
-- 结果：B 收到 ERROR 1213 (40001): Deadlock found...
-- =====================================================================
-- ---- 会话 A ----
-- mysql> BEGIN;
-- mysql> UPDATE t_product SET stock=stock-1 WHERE product_id=1;   -- 锁住 product 1
-- mysql> UPDATE t_product SET stock=stock-1 WHERE product_id=2;   -- 阻塞，等 B
--
-- ---- 会话 B ----
-- mysql> BEGIN;
-- mysql> UPDATE t_product SET stock=stock-1 WHERE product_id=2;   -- 锁住 product 2
-- mysql> UPDATE t_product SET stock=stock-1 WHERE product_id=1;   -- 死锁，B 回滚

-- =====================================================================
-- 【第二步：查看死锁日志】
-- =====================================================================
SHOW ENGINE INNODB STATUS\G
-- 关注 LATEST DETECTED DEADLOCK 段：
--   *** (1) TRANSACTION:        事务A 持有 product_id=1 的行锁，等待 product_id=2
--   *** (1) WAITING FOR THIS LOCK...
--   *** (2) TRANSACTION:        事务B 持有 product_id=2，等待 product_id=1
--   *** (2) HOLDS THE LOCK(S)...
--   *** (2) WAITING FOR THIS LOCK...
--   *** WE ROLL BACK TRANSACTION (2)

-- 开启死锁日志完整记录（保留到错误日志，便于事后分析）
SET GLOBAL innodb_print_all_deadlocks = ON;

-- 查询当前锁等待（死锁发生瞬间可见）
SELECT * FROM performance_schema.data_locks\G        -- MySQL 8.0 行锁详情
SELECT * FROM performance_schema.data_lock_waits\G   -- 锁等待关系

-- =====================================================================
-- 【第三步：死锁根因分析】
-- 根因：两个事务以「相反顺序」更新同一批商品行，形成循环等待：
--   A: lock(1) → lock(2)
--   B: lock(2) → lock(1)   ← 与 A 相反
-- InnoDB 主动检测到 wait-for 环，回滚代价较小的一方(B)。
-- =====================================================================

-- =====================================================================
-- 【第四步：调优方案】统一加锁顺序 + 小事务 + 重试
-- 方案1（核心）：所有扣减库存逻辑按 product_id 升序加锁，打破循环等待
-- =====================================================================
-- ✅ 调优后写法：批量扣减时先排序，按统一顺序加锁
-- 会话 A：
BEGIN;
UPDATE t_product SET stock=stock-1 WHERE product_id IN (1, 2) ORDER BY product_id;
COMMIT;

-- 会话 B（同样按 product_id 升序，不再反向）：
BEGIN;
UPDATE t_product SET stock=stock-1 WHERE product_id IN (1, 2) ORDER BY product_id;
COMMIT;

-- 方案2：扣库存用「单条 UPDATE 原子操作」+ 乐观重试，避免多行持锁
-- 应用层捕获 1213 死锁错误后，重试 2~3 次
-- 方案3：事务尽量短小，扣减与下单拆分，减少锁持有时间
-- 方案4：高并发热点商品可用「库存分桶」降低单行热点

-- =====================================================================
-- 【验证】模拟并发压测（可用 mysqlslap 或两个会话循环执行）
-- 调优后统一加锁顺序，死锁次数应降为 0
-- =====================================================================
-- mysqlslap --concurrency=20 --iterations=50 --query="UPDATE shop_demo.t_product SET stock=stock-1 WHERE product_id IN (1,2) ORDER BY product_id"

-- =====================================================================
-- 【小结】死锁排查四步法：
--   1. SHOW ENGINE INNODB STATUS 取死锁日志
--   2. 解析持有/等待的锁资源与语句
--   3. 找到循环等待根因（多为加锁顺序不一致）
--   4. 统一加锁顺序 + 短事务 + 应用层重试
-- =====================================================================
