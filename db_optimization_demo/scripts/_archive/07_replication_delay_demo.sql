-- =====================================================================
-- 07_replication_delay_demo.sql  主从延迟排查与调优
-- 场景：大促下单写入激增，从库延迟 Seconds_Behind_Master 飙升，
--       报表/订单查询从从库读取到旧数据，业务异常
-- 说明：从库执行以下诊断命令
-- =====================================================================
USE shop_demo;

-- =====================================================================
-- 【第一步：查看主从复制状态】
-- MySQL 8.0 推荐使用 SHOW REPLICA STATUS（SHOW SLAVE STATUS 别名）
-- =====================================================================
SHOW REPLICA STATUS\G

-- 关注关键字段：
--   Replica_IO_Running: Yes          IO 线程是否正常
--   Replica_SQL_Running: Yes        SQL 线程是否正常
--   Seconds_Behind_Master: 120      ← 延迟秒数（重点关注）
--   Last_Error / Last_IO_Error      复制错误信息
--   Retrieved_Gtid_Set / Executed_Gtid_Set  GTID 位点对比

-- =====================================================================
-- 【第二步：判断延迟来源】
-- 延迟 = 主库执行时间 - 从库回放时间，分两类：
--   IO 延迟：网络/带宽不足，binlog 传输慢 → Retrieved 落后于主
--   SQL 延迟：从库单线程回放慢于主库并发写入（最常见）
-- =====================================================================

-- 1) 看 IO 线程读取与 SQL 线程执行差距（位点差）
SHOW REPLICA STATUS\G
--   Master_Log_File vs Relay_Master_Log_File
--   Read_Master_Log_Pos vs Exec_Master_Log_Pos

-- 2) 模拟大写入量（主库执行），观察从库延迟
-- 主库：批量插入库存日志，制造写入洪峰
INSERT INTO t_inventory_log(product_id, delta, order_no, created_at)
SELECT (i % 10000) + 1, -1, CONCAT('NO', LPAD(i, 12, '0')), NOW()
FROM (
  SELECT a.N + b.N*10 + c.N*100 + d.N*1000 AS i
  FROM (SELECT 0 N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
        UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
       (SELECT 0 N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
        UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
       (SELECT 0 N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
        UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) c,
       (SELECT 0 N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
        UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) d
) t
LIMIT 100000;

-- 从库立即查看延迟（大促期间会飙升）
SHOW REPLICA STATUS\G
SELECT '从库延迟(s)' AS metric, variable_value
FROM performance_schema.global_status
WHERE variable_name = 'Replica_seconds_behind_master';

-- =====================================================================
-- 【第三步：根因分析】
-- 1. 从库 SQL 线程单线程串行回放，跟不上主库并发写入
-- 2. 从库存在慢查询/大事务占用资源，拖慢回放
-- 3. 大事务（如大批量 INSERT/DELETE）单事务重放耗时长
-- 4. 网络/IO 抖动导致 binlog 传输延迟
-- =====================================================================

-- =====================================================================
-- 【第四步：调优方案】
-- 方案1：开启多线程并行复制（MTS，MySQL 8.0 LOGICAL_CLOCK）
-- =====================================================================
STOP REPLICA;
-- 并行回放：按逻辑时钟并行，主库组提交的多个事务可并行回放
SET GLOBAL replica_parallel_workers = 8;            -- 并行工作线程数
SET GLOBAL replica_parallel_type = 'LOGICAL_CLOCK'; -- 逻辑时钟并行
SET GLOBAL replica_pending_jobs_size_max = 134217728; -- 128MB 缓冲
SET GLOBAL binlog_transaction_dependency_tracking = 'WRITESET'; -- 8.0 更细粒度依赖
START REPLICA;

-- 验证并行复制生效
SHOW VARIABLES LIKE 'replica_parallel%';
SHOW VARIABLES LIKE 'binlog_transaction_dependency%';

-- =====================================================================
-- 方案2：主库侧减少大事务，分批提交
-- =====================================================================
-- ❌ 大事务：一次性插入 10 万行 → 从库回放耗时长
-- ✅ 分批：每 1000 行提交一次，平滑 binlog

-- =====================================================================
-- 方案3：从库大查询让出资源，避免占用 SQL 线程
-- =====================================================================
SET GLOBAL replica_preserve_commit_order = ON;  -- 保持提交顺序

-- =====================================================================
-- 方案4：业务侧读延迟容忍处理
-- =====================================================================
-- 关键写后读（如下单后查订单）走主库，避免读到旧数据
-- 报表等容忍延迟的查询走从库
-- 引入「读写分离 + 延迟感知」中间件，延迟超阈值自动切主

-- =====================================================================
-- 【第五步：调优后验证】
-- =====================================================================
SHOW REPLICA STATUS\G
-- 关注 Seconds_Behind_Master 是否回落到 < 5s
SELECT '并行worker' AS metric,
       variable_value
FROM performance_schema.global_status
WHERE variable_name LIKE 'Replica_parallel%';

-- =====================================================================
-- 【小结】主从延迟排查四步法：
--   1. SHOW REPLICA STATUS 看 Seconds_Behind_Master / IO、SQL 线程
--   2. 区分 IO 延迟 vs SQL 延迟（位点差）
--   3. 根因：单线程回放 / 大事务 / 慢查询 / 网络
--   4. 调优：多线程并行复制 + 分批提交 + 读写分离延迟感知
-- =====================================================================
