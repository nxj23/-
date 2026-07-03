# 纯 SQL 命令行演示指南

> 全部演示在 MySQL 命令行（cmd / mysql client）里用 `source` 完成，无需 Python。
> 所有数据均为真实 MySQL 8.0 实测。

## 环境准备（首次执行，约 30 秒）

```bash
# 登录 MySQL
mysql -uroot -proot123

# 建库 + 建表 + 造数
mysql> CREATE DATABASE IF NOT EXISTS shop_demo DEFAULT CHARSET utf8mb4;
mysql> use shop_demo;
mysql> source 01_schema.sql;
mysql> source 02_init_data.sql;     -- 约 30 秒造 100 万订单
```

## 演示脚本顺序

| 顺序 | 脚本 | 内容 | 窗口 |
|---|---|---|---|
| 1 | `demo_01_env.sql` | 环境核对：数据量、表大小、索引统计 | 单窗口 |
| 2 | `demo_02_slow_query.sql` | 慢查询 EXPLAIN 对比 + BENCHMARK 耗时 | 单窗口 |
| 3 | `demo_03_index_anomaly.sql` | 索引异常 6 类失效场景 | 单窗口 |
| 4 | `demo_04_replication.sql` | 主从延迟调优参数 | 单窗口 |
| 5 | `deadlock_session_a.sql` + `deadlock_session_b.sql` | 真实触发死锁 ERROR 1213 | 双窗口 |
| 6 | `lock_wait_session_a.sql` + `lock_wait_session_b.sql` | 真实触发锁等待 ERROR 1205 | 双窗口 |

---

## 第 0-3 幕：单窗口演示

```bash
mysql -uroot -proot123 shop_demo
```

按顺序 source，每幕讲完再 source 下一幕，节奏可控：

```sql
mysql> source demo_01_env.sql
-- 讲解数据量 →
mysql> source demo_02_slow_query.sql
-- 讲解慢查询调优 →
mysql> source demo_03_index_anomaly.sql
-- 讲解索引失效 →
mysql> source demo_04_replication.sql
-- 讲解主从配置
```

每幕脚本里有 `\! echo` 中文提示，标注关键结论。

---

## 第 4 幕：死锁演示（双窗口）

**原理**：会话A 锁 p1 等 p2，会话B 锁 p2 等 p1 → AB-BA 死锁环 → InnoDB 回滚 B。

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
-- 会话A 提交，释放锁
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

演示过程中可随时手动调优对比：

```sql
-- 现场加复合索引
mysql> ALTER TABLE t_order ADD INDEX idx_demo (user_id, status, created_at);

-- 重新 EXPLAIN 看效果
mysql> EXPLAIN SELECT ... FROM t_order WHERE user_id=12345 AND status=1 ...;

-- 删索引看退化效果
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

## 文件清单

```
scripts/
├── 01_schema.sql                       建表
├── 02_init_data.sql                    造数（100万订单）
├── demo_01_env.sql                     第0幕 环境核对
├── demo_02_slow_query.sql              第1幕 慢查询调优
├── demo_03_index_anomaly.sql           第2幕 索引异常6类
├── demo_04_replication.sql             第3幕 主从配置
├── deadlock_session_a.sql              死锁 会话A
├── deadlock_session_a_commit.sql       死锁 会话A提交
├── deadlock_session_b.sql              死锁 会话B（触发1213）
├── lock_wait_session_a.sql             锁等待 会话A（持锁）
├── lock_wait_session_a_commit.sql      锁等待 会话A提交
├── lock_wait_session_b.sql             锁等待 会话B（触发1205）
└── 纯SQL演示指南.md                    本文档
```
