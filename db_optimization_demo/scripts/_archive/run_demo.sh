#!/usr/bin/env bash
# =====================================================================
# run_demo.sh  电商订单系统数据库性能调优一键演示脚本
# 用法：
#   ./run_demo.sh                  # 默认 root 无密码，端口 3306
#   MYSQL_PWD=yourpass MYSQL_PORT=3307 ./run_demo.sh
# 执行顺序：建库建表 → 造数 → 逐项排查调优演示
# =====================================================================
set -e

MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PWD="${MYSQL_PWD:-}"
MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
MYSQL_PORT="${MYSQL_PORT:-3306}"

DIR="$(cd "$(dirname "$0")" && pwd)"
MYSQL_CMD="mysql -h${MYSQL_HOST} -P${MYSQL_PORT} -u${MYSQL_USER}"
if [ -n "$MYSQL_PWD" ]; then
  MYSQL_CMD="$MYSQL_CMD -p${MYSQL_PWD}"
fi

run_sql() {
  local file="$1"
  local title="$2"
  echo ""
  echo "============================================================"
  echo "▶ 执行: ${title}"
  echo "  文件: ${file}"
  echo "============================================================"
  $MYSQL_CMD --default-character-set=utf8mb4 < "$file"
}

echo "========================================"
echo "  电商订单系统 数据库全链路调优 演示"
echo "  MySQL: ${MYSQL_HOST}:${MYSQL_PORT}  用户: ${MYSQL_USER}"
echo "========================================"

# 1. 建库建表
run_sql "${DIR}/01_schema.sql" "建库建表 schema"

# 2. 造数（耗时较长，100万订单）
run_sql "${DIR}/02_init_data.sql" "初始化测试数据(用户/商品/订单)"

# 3. 慢查询排查与调优
run_sql "${DIR}/03_slow_query_demo.sql" "慢查询排查与调优"

# 4. 索引异常排查与调优
run_sql "${DIR}/04_index_anomaly_demo.sql" "索引异常排查与调优"

# 5. 事务死锁（需开两个会话手动复现，此处仅展示脚本）
echo ""
echo "============================================================"
echo "▶ 提示: 事务死锁需开两个 MySQL 会话手动复现"
echo "  请参考 ${DIR}/05_deadlock_demo.sql 文件中的时间线说明"
echo "============================================================"

# 6. 锁等待（需开两个会话手动复现，此处仅展示脚本）
echo ""
echo "============================================================"
echo "▶ 提示: 锁等待需开两个 MySQL 会话手动复现"
echo "  请参考 ${DIR}/06_lock_wait_demo.sql 文件中的时间线说明"
echo "============================================================"

# 7. 主从延迟（需配置主从环境，从库执行）
echo ""
echo "============================================================"
echo "▶ 提示: 主从延迟需在已配置主从的从库执行"
echo "  请参考 ${DIR}/07_replication_delay_demo.sql"
echo "============================================================"

echo ""
echo "✅ 演示流程结束"
echo "  自动执行部分(1-4)已完成；死锁/锁等待/主从延迟为交互式场景"
echo "  请按对应脚本注释手动复现。"
