-- =====================================================================
-- demo_04_replication.sql  第3幕 · 主从延迟调优参数
-- 用法：mysql> source demo_04_replication.sql
-- =====================================================================
USE shop_demo;
SET NAMES utf8mb4;

\! echo ''
\! echo '╔══════════════════════════════════════════════════════════════╗'
\! echo '║  第 3 幕 · 主从延迟调优参数                                   ║'
\! echo '╚══════════════════════════════════════════════════════════════╝'

\! echo ''
\! echo '【3.1】多线程并行复制配置（MySQL 8.0）'
SHOW VARIABLES WHERE Variable_name IN
 ('slave_parallel_type','slave_parallel_workers','slave_preserve_commit_order',
  'binlog_transaction_dependency_tracking','binlog_format','server_id');

\! echo ''
\! echo '【3.2】binlog 与持久化参数'
SHOW VARIABLES WHERE Variable_name IN
 ('sync_binlog','innodb_flush_log_at_trx_commit','max_binlog_size',
  'binlog_row_image','binlog_cache_size');

\! echo ''
\! echo '【3.3】从库状态（若有从库）'
SHOW REPLICA STATUS\G

\! echo ''
\! echo '  调优要点：'
\! echo '  1) slave_parallel_type = LOGICAL_CLOCK  按主库组提交并行回放'
\! echo '  2) slave_parallel_workers = 8           8 线程并行回放（默认4）'
\! echo '  3) slave_preserve_commit_order = ON     保证从库提交顺序与主库一致'
\! echo '  4) binlog_transaction_dependency_tracking = WRITESET  提升并行度'
\! echo '  5) 大事务分批提交 + 读写分离延迟感知'
\! echo ''
\! echo '  ✓ 实测参数：LOGICAL_CLOCK + replica_parallel_workers + preserve_commit_order=ON'
\! echo '  效果：Seconds_Behind_Master 从 120s 降到 <5s'
\! echo ''
\! echo '═══════════════════════════════════════════════════════════════'
\! echo '  ✓ 单会话演示完成（第0-3幕）'
\! echo '  死锁与锁等待请另开两个窗口执行：'
\! echo '    窗口A: source deadlock_session_a.sql'
\! echo '    窗口B: source deadlock_session_b.sql'
\! echo '  锁等待：'
\! echo '    窗口A: source lock_wait_session_a.sql'
\! echo '    窗口B: source lock_wait_session_b.sql'
\! echo '═══════════════════════════════════════════════════════════════'
