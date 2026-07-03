-- =====================================================================
-- deadlock_session_a.sql  死锁演示 · 会话 A（窗口1）
-- 用法：开一个 mysql cmd 窗口执行  source deadlock_session_a.sql
-- 配合窗口B 同时执行 deadlock_session_b.sql 触发 AB-BA 死锁
--
-- 操作流程：
--   1. 窗口A 执行 source deadlock_session_a.sql（会锁定 product_id=1）
--   2. 窗口B 执行 source deadlock_session_b.sql（锁定 p2 后尝试 p1 → 死锁）
--   3. 回窗口A 执行 source deadlock_session_a_commit.sql 提交
-- =====================================================================
USE shop_demo;
SET autocommit = 0;
SET NAMES utf8mb4;

\! echo '=== 死锁演示 · 会话A ==='
\! echo '步骤1: 会话A 锁定 product_id=1（先扣商品1库存）'

-- 第1步：锁定 product_id=1（事务不提交，持续持锁）
UPDATE t_product SET stock = stock - 1 WHERE product_id = 1;
\! echo '  ✓ 会话A 已锁定 product_id=1，事务未提交'
\! echo ''
\! echo '>>> 现在去窗口B 执行: source deadlock_session_b.sql'
\! echo '>>> 等窗口B 报 ERROR 1213 后，回这里执行: source deadlock_session_a_commit.sql'
\! echo ''
-- 注意：事务保持打开，需另开 commit 脚本提交，或手动敲 COMMIT;
