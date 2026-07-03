-- =====================================================================
-- lock_wait_session_a_commit.sql  锁等待演示 · 会话A 提交（窗口1）
-- 用法：等窗口B 报 ERROR 1205 后，在窗口A 执行
--   source lock_wait_session_a_commit.sql
-- =====================================================================
USE shop_demo;

\! echo '=== 会话A 提交事务，释放 product_id=1 的锁 ==='
COMMIT;
\! echo '  ✓ 会话A 已提交'

\! echo ''
\! echo '【验证】当前活跃事务（应已无持锁事务）'
SELECT trx_id, trx_state, trx_started, trx_mysql_thread_id
FROM information_schema.INNODB_TRX
ORDER BY trx_started DESC LIMIT 5;
