-- =====================================================================
-- lock_wait_session_b.sql  锁等待演示 · 会话 B（窗口2，被阻塞）
-- 用法：另开一个 mysql cmd 窗口执行  source lock_wait_session_b.sql
-- 必须在会话A 已持锁（未提交）后执行
--
-- 执行后：会话B 尝试更新 product_id=1 → 被A阻塞 → 5秒后 ERROR 1205
-- =====================================================================
USE shop_demo;
SET autocommit = 0;
SET NAMES utf8mb4;

-- 调小锁等待超时（5秒后报错，避免干等）
SET SESSION innodb_lock_wait_timeout = 5;

\! echo '=== 锁等待演示 · 会话B（被阻塞）==='
\! echo '步骤1: 会话B 尝试更新 product_id=1（A正持有该行锁）'
\! echo '       预计等待 5 秒后触发 ERROR 1205'
\! echo ''

-- 尝试更新同一行 → 被A的锁阻塞 → 5秒后超时
-- 此语句会触发 ERROR 1205: Lock wait timeout exceeded
UPDATE t_product SET stock = stock - 1 WHERE product_id = 1;

-- 若上面没报错（A已释放），则正常提交
COMMIT;
\! echo '=== 会话B 完成（若前面报 1205 则事务已被回滚）==='
