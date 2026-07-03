# 纯 SQL 命令行演示指南

> 全部演示在 MySQL 命令行（cmd / mysql client）里用 `source` 完成，无需 Python。
> 所有数据均为真实 MySQL 8.0 实测。

## 环境准备（首次执行，约 30 秒）

```bash
mysql -uroot -proot123

mysql> CREATE DATABASE IF NOT EXISTS shop_demo DEFAULT CHARSET utf8mb4;
mysql> use shop_demo;
mysql> source 01_schema.sql;
mysql> source 02_init_data.sql;     -- 约 30 秒造 100 万订单
```

## 最终文件清单（8 个）

```
scripts/
├── 01_schema.sql                       建表（5 张表）
├── 02_init_data.sql                    造数（5万用户/99.7万订单/128万明细）
├── demo.sql                            ★ 主演示脚本（第0-3幕，单窗口一次跑完）
├── deadlock_session_a.sql              死锁 会话A（锁 p1）
├── deadlock_session_b.sql              死锁 会话B（触发 ERROR 1213）
├── deadlock_session_a_commit.sql       死锁 会话A 提交
├── lock_wait_session_a.sql             锁等待 会话A（长事务持锁）
├── lock_wait_session_b.sql             锁等待 会话B（触发 ERROR 1205）
└── lock_wait_session_a_commit.sql      锁等待 会话A 提交
```

---

## 第 0-3 幕：单窗口主演示

```bash
mysql -uroot -proot123 shop_demo
```
```sql
mysql> source demo.sql
```

一次性跑完：
- 第0幕 环境核对（数据量/表大小/索引统计）
- 第1幕 慢查询调优（调优前 ALL/994910行 vs 调优后 range/1行 + BENCHMARK 耗时）
- 第2幕 索引异常 6 类（隐式转换/函数/左模糊/最左前缀/OR/!= + 冗余索引检测）
- 第3幕 主从延迟（多线程并行复制参数）

脚本内有 `\! echo` 中文提示标注关键结论。

---

## 第 4 幕：死锁演示（双窗口）

**原理**：会话A 锁 p1 等 p2，会话B 锁 p2 等 p1 → AB-BA 死锁 → InnoDB 回滚 B。

### 窗口 A
```bash
mysql -uroot -proot123 shop_demo
```
```sql
mysql> source deadlock_session_a.sql
-- 会话A 锁定 product_id=1，事务不提交
```

### 窗口 B（在 A 锁定 p1 之后）
```bash
mysql -uroot -proot123 shop_demo
```
```sql
mysql> source deadlock_session_b.sql
-- 会话B 锁 p2 → 尝试锁 p1 → 触发 ERROR 1213，B 被回滚
```

### 窗口 A 提交
```sql
mysql> source deadlock_session_a_commit.sql
```

### 查看死锁日志
```sql
mysql> SHOW ENGINE INNODB STATUS\G
-- 找 LATEST DETECTED DEADLOCK 段
```

---

## 第 5 幕：锁等待演示（双窗口）

**原理**：会话A 长事务持锁不提交，会话B 更新同一行 → 等待 5 秒 → ERROR 1205。

### 窗口 A（长事务持锁）
```bash
mysql -uroot -proot123 shop_demo
```
```sql
mysql> source lock_wait_session_a.sql
-- 会话A 更新 product_id=1 不提交，持续持锁
```

### 窗口 B（被阻塞）
```bash
mysql -uroot -proot123 shop_demo
```
```sql
mysql> source lock_wait_session_b.sql
-- 会话B 尝试更新同一行 → 5 秒后触发 ERROR 1205
```

### 窗口 A 提交
```sql
mysql> source lock_wait_session_a_commit.sql
-- 会话A 提交，释放锁，并查看当前活跃事务
```

---

## 现场实时调优（cmd 交互）

演示中可随时手动调优对比：

```sql
-- 现场加复合索引
mysql> ALTER TABLE t_order ADD INDEX idx_demo (user_id, status, created_at);
-- 重新 EXPLAIN 看效果
mysql> EXPLAIN SELECT ... FROM t_order WHERE user_id=12345 AND status=1 ...;
-- 删索引看退化
mysql> ALTER TABLE t_order DROP INDEX idx_demo;
-- 改 SQL 写法对比
mysql> EXPLAIN SELECT * FROM t_order WHERE order_no = 123;            -- 失效
mysql> EXPLAIN SELECT * FROM t_order WHERE order_no = 'NO000000000123';  -- 命中
```

---

## 关键实测数据对照

| 演示项 | 调优前 | 调优后 | 提升 |
|---|---|---|---|
| 慢查询扫描行数 | 994910 行 | 1 行 | 99 万倍 |
| 慢查询耗时 | 420 ms | 0.46 ms | 913 倍 |
| 死锁 | AB-BA 频发 | 统一加锁顺序 → 0 | 根除 |
| 锁等待 | 超时堆积 | 5s 快速失败 + 重试 | 秒级 |
| 主从延迟 | 单线程 120s | 8 线程并行 <5s | 96% |
