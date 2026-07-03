-- =====================================================================
-- 06_lock_wait_demo.sql  锁等待排查与调优
-- 场景：后台批量改价事务长时间持有锁，前端下单更新价格被阻塞，
--       达到 innodb_lock_wait_timeout(10s) 后报 ERROR 1205 Lock wait timeout
-- 复现方式：开两个会话 A(长事务)、B(被阻塞)
-- =====================================================================
USE shop_demo;

-- =====================================================================
-- 【第一步：复现锁等待】
-- 会话 A：开事务更新商品 1 但不提交（模拟长事务持锁）
--   mysql> BEGIN;
--   mysql> UPDATE t_product SET price=price*1.1 WHERE product_id=1;  -- 持锁不提交
--
-- 会话 B：尝试更新同一行 → 阻塞 → 10s 超时报错
--   mysql> BEGIN;
--   mysql> UPDATE t_product SET stock=stock-1 WHERE product_id=1;
--   ERROR 1205 (HY000): Lock wait timeout exceeded...
-- =====================================================================

-- =====================================================================
-- 【第二步：排查正在运行的事务与锁等待】
-- =====================================================================
-- 1) 查看所有活动事务（找长事务）
SELECT trx_id, trx_state, trx_started,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS hold_sec,
       trx_rows_locked, trx_mysql_thread_id, trx_query
FROM information_schema.INNODB_TRX
ORDER BY trx_started ASC;

-- 2) 查看锁等待关系（谁等谁）
SELECT r.trx_id AS waiting_trx_id,
       r.trx_mysql_thread_id AS waiting_thread,
       r.trx_query AS waiting_query,
       b.trx_id AS blocking_trx_id,
       b.trx_mysql_thread_id AS blocking_thread,
       b.trx_query AS blocking_query,
       TIMESTAMPDIFF(SECOND, b.trx_started, NOW()) AS blocking_sec
FROM information_schema.INNODB_LOCK_WAITS w
JOIN information_schema.INNODB_TRX b ON b.trx_id = w.blocking_trx_id
JOIN information_schema.INNODB_TRX r ON r.trx_id = w.requesting_trx_id;

-- 3) MySQL 8.0：performance_schema 行锁视图（更直观）
SELECT * FROM performance_schema.data_lock_waits;
SELECT * FROM performance_schema.data_locks WHERE object_name='t_product';

-- 4) 看会话状态
SELECT id, user, host, db, command, time, state, info
FROM information_schema.PROCESSLIST
WHERE info IS NOT NULL OR time > 5;

-- =====================================================================
-- 【第三步：应急处置】确认阻塞事务非关键后，KILL 释放锁
-- =====================================================================
-- 上面查到的 blocking_thread 即为阻塞线程 ID
-- KILL <blocking_thread>;

-- =====================================================================
-- 【第四步：根因分析】
-- 根因1：批量改价事务“BEGIN 后长时间不提交”，行锁 X 锁持续占用
-- 根因2：改价与下单更新同一商品行，X 锁互斥
-- 根因3：innodb_lock_wait_timeout 默认 50s 过长，前端堆积超时
-- =====================================================================

-- =====================================================================
-- 【第五步：调优方案】
-- 方案1：长事务拆分 + 及时提交，批量改价分批 commit（每 500 条提交）
-- 方案2：改价用「低峰期 + 小批次」，避免高峰改价
-- 方案3：前端下单更新改为「乐观锁 / 版本号」，减少行锁持有
-- 方案4：合理设置锁等待超时（业务侧 5s 快速失败 + 重试）
-- =====================================================================
SET SESSION innodb_lock_wait_timeout = 5;   -- 业务会话快速失败

-- ✅ 调优写法：批量改价分批提交，避免长事务
-- 应用层伪代码：
--   UPDATE t_product SET price=? WHERE product_id=? AND version=old_version;
--   -- affected_rows=0 → 版本冲突，重试

-- 监控：长事务预警（超过 5s 的事务告警）
SELECT trx_id, trx_started,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS hold_sec,
       trx_query
FROM information_schema.INNODB_TRX
HAVING hold_sec > 5;

-- =====================================================================
-- 【小结】锁等待排查四步法：
--   1. INNODB_TRX / PROCESSLIST 找持锁长事务
--   2. INNODB_LOCK_WAITS / data_lock_waits 定位“谁等谁”
--   3. 确认安全后 KILL 阻塞事务应急
--   4. 拆分长事务 + 乐观锁 + 合理超时，根治
-- =====================================================================
