-- =====================================================================
-- lock_wait_session_a.sql  锁等待演示 · 会话 A（窗口1，长事务持锁）
-- 用法：开一个 mysql cmd 窗口执行  source lock_wait_session_a.sql
-- 会话A 开启事务更新 product_id=1 但不提交，模拟长事务持锁
--
-- 操作流程：
--   1. 窗口A 执行 source lock_wait_session_a.sql（持锁不提交）
--   2. 窗口B 执行 source lock_wait_session_b.sql（被阻塞 5s → ERROR 1205）
--   3. 回窗口A 执行 source lock_wait_session_a_commit.sql 提交
-- =====================================================================
USE shop_demo;
SET autocommit = 0;
SET NAMES utf8mb4;

-- 先把锁等待超时调小（演示用，避免等50秒）
SET SESSION innodb_lock_wait_timeout = 5;

\! echo '=== 锁等待演示 · 会话A（长事务持锁）==='
\! echo '步骤1: 会话A 开启事务，更新 product_id=1 但不提交'

-- 持有 product_id=1 的行锁，不 COMMIT
UPDATE t_product SET stock = stock - 1 WHERE product_id = 1;
\! echo '  ✓ 会话A 已更新 product_id=1，事务未提交，持续持有行锁'
\! echo ''
\! echo '>>> 现在去窗口B 执行: source lock_wait_session_b.sql'
\! echo '>>> 会话B 会被阻塞 5 秒，然后报 ERROR 1205'
\! echo '>>> 等窗口B 报错后，回这里执行: source lock_wait_session_a_commit.sql'
\! echo ''
-- 注意：事务保持打开，需另开 commit 脚本提交，或手动敲 COMMIT;
