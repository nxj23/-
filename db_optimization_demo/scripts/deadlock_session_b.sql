-- =====================================================================
-- deadlock_session_b.sql  死锁演示 · 会话 B（窗口2）
-- 用法：另开一个 mysql cmd 窗口执行  source deadlock_session_b.sql
-- 必须在会话A 已锁定 product_id=1 之后执行
--
-- 执行后：会话B 锁 p2 → 尝试锁 p1（A正持有）→ 死锁 → B 被回滚
-- =====================================================================
USE shop_demo;
SET autocommit = 0;
SET NAMES utf8mb4;

\! echo '=== 死锁演示 · 会话B ==='
\! echo '步骤1: 会话B 锁定 product_id=2（与A相反顺序：先扣商品2）'

-- 第1步：锁定 product_id=2
UPDATE t_product SET stock = stock - 1 WHERE product_id = 2;
\! echo '  ✓ 会话B 已锁定 product_id=2'
\! echo ''
\! echo '步骤2: 会话B 尝试锁 product_id=1（A正持有 p1 等 p2）'
\! echo '       AB-BA 死锁环形成 → InnoDB 检测 → 回滚 B'
\! echo '       下面这条语句会触发 ERROR 1213'
\! echo ''

-- 第2步：尝试锁 product_id=1 → 触发死锁，B 被回滚，报 ERROR 1213
UPDATE t_product SET stock = stock - 1 WHERE product_id = 1;

-- 若上面没报错（A已释放），则正常提交
COMMIT;
\! echo '=== 会话B 完成（若前面报 1213 则事务已被自动回滚）==='
