-- =====================================================================
-- deadlock_session_a_commit.sql  死锁演示 · 会话A 提交（窗口1）
-- 用法：等窗口B 报 ERROR 1213 后，在窗口A 执行
--   source deadlock_session_a_commit.sql
-- =====================================================================
USE shop_demo;

\! echo '=== 会话A 提交事务，释放 product_id=1 的锁 ==='
COMMIT;
\! echo '  ✓ 会话A 已提交'

\! echo ''
\! echo '【查看死锁日志】'
\! echo '  执行: SHOW ENGINE INNODB STATUS\G'
\! echo '  找到 LATEST DETECTED DEADLOCK 段，可见事务持有/等待信息'
