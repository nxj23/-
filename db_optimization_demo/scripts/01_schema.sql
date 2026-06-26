-- =====================================================================
-- 01_schema.sql  电商订单系统建表脚本
-- 业务背景：模拟线上电商订单系统，用于全链路性能瓶颈排查与调优演示
-- 引擎：InnoDB  字符集：utf8mb4
-- 设计说明：本脚本故意保留部分“未优化的索引/字段类型”，以便演示慢查询、
--          索引失效、死锁、锁等待、主从延迟等生产故障，后续脚本再逐项调优。
-- =====================================================================

DROP DATABASE IF EXISTS shop_demo;
CREATE DATABASE shop_demo DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shop_demo;

-- ---------------------------------------------------------------------
-- 用户表
-- ---------------------------------------------------------------------
CREATE TABLE t_user (
    user_id      BIGINT       NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    username     VARCHAR(64)  NOT NULL COMMENT '用户名',
    phone        VARCHAR(20)  NOT NULL COMMENT '手机号',
    email        VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
    city         VARCHAR(32) DEFAULT NULL COMMENT '所在城市',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    PRIMARY KEY (user_id),
    UNIQUE KEY uk_username (username)
) ENGINE=InnoDB COMMENT='用户表';

-- ---------------------------------------------------------------------
-- 商品表（故意不给 status 建索引，演示索引异常/慢查询）
-- ---------------------------------------------------------------------
CREATE TABLE t_product (
    product_id    BIGINT        NOT NULL AUTO_INCREMENT COMMENT '商品ID',
    product_name  VARCHAR(128)  NOT NULL COMMENT '商品名',
    category_id   INT           NOT NULL COMMENT '类目ID',
    price         DECIMAL(10,2) NOT NULL COMMENT '售价',
    stock         INT           NOT NULL DEFAULT 0 COMMENT '库存',
    status        TINYINT       NOT NULL DEFAULT 1 COMMENT '1上架 0下架',
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (product_id),
    KEY idx_category (category_id)
) ENGINE=InnoDB COMMENT='商品表';

-- ---------------------------------------------------------------------
-- 订单主表
-- 故意只建单列索引 idx_user，缺少 (user_id, status) 复合索引，
-- 演示“回表 + 大范围扫描”导致的慢查询；order_no 列故意未建唯一索引
-- ---------------------------------------------------------------------
CREATE TABLE t_order (
    order_id      BIGINT        NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    order_no      VARCHAR(32)   NOT NULL COMMENT '订单号(业务)',
    user_id       BIGINT        NOT NULL COMMENT '下单用户',
    total_amount DECIMAL(12,2) NOT NULL COMMENT '订单金额',
    status        TINYINT       NOT NULL DEFAULT 0 COMMENT '0待支付 1已支付 2已发货 3已完成 4已取消',
    pay_time      DATETIME      DEFAULT NULL COMMENT '支付时间',
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
    PRIMARY KEY (order_id),
    KEY idx_user (user_id)
) ENGINE=InnoDB COMMENT='订单主表';

-- ---------------------------------------------------------------------
-- 订单明细表
-- ---------------------------------------------------------------------
CREATE TABLE t_order_item (
    item_id      BIGINT        NOT NULL AUTO_INCREMENT COMMENT '明细ID',
    order_id     BIGINT        NOT NULL COMMENT '订单ID',
    product_id   BIGINT        NOT NULL COMMENT '商品ID',
    quantity     INT           NOT NULL COMMENT '购买数量',
    unit_price   DECIMAL(10,2) NOT NULL COMMENT '成交单价',
    PRIMARY KEY (item_id),
    KEY idx_order (order_id)
) ENGINE=InnoDB COMMENT='订单明细表';

-- ---------------------------------------------------------------------
-- 库存变更日志（用于演示主从延迟下的大写入量）
-- ---------------------------------------------------------------------
CREATE TABLE t_inventory_log (
    id          BIGINT      NOT NULL AUTO_INCREMENT,
    product_id  BIGINT      NOT NULL,
    delta       INT         NOT NULL COMMENT '变更数量(正进负出)',
    order_no    VARCHAR(32) DEFAULT NULL COMMENT '关联订单号',
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_product (product_id)
) ENGINE=InnoDB COMMENT='库存变更日志';

-- ---------------------------------------------------------------------
-- 关键参数（仅演示用，生产请按容量评估）
-- 慢查询日志：开启 + 阈值 1s + 记录未用索引
-- ---------------------------------------------------------------------
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;
SET GLOBAL log_queries_not_using_indexes = ON;
SET GLOBAL innodb_lock_wait_timeout = 10;   -- 锁等待超时 10s，便于演示
SET GLOBAL innodb_deadlock_detect = ON;

-- 查看生效情况
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
