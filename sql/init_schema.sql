-- ============================================================
-- 饰品虚拟试戴与电商系统 - 数据库初始化 DDL
-- MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS jewelry_vtryon
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE jewelry_vtryon;

-- -----------------------------------------------------------
-- 1. 用户表
-- -----------------------------------------------------------
CREATE TABLE users (
    id              BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    nickname        VARCHAR(64)         NOT NULL,
    avatar_url      VARCHAR(512)        DEFAULT NULL,
    phone           VARCHAR(20)         DEFAULT NULL,
    password_hash   VARCHAR(128)        NOT NULL,
    gender          TINYINT             NOT NULL DEFAULT 0 COMMENT '0-未知 1-男 2-女',
    created_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME            DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 2. 用户面部数据表
-- -----------------------------------------------------------
CREATE TABLE user_face_data (
    id                  BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    user_id             BIGINT UNSIGNED     NOT NULL,
    image_url           VARCHAR(512)        NOT NULL COMMENT '原始上传图片 OSS 路径',
    face_shape          ENUM('oval','round','square','heart','oblong','diamond') NOT NULL COMMENT '脸型分类',
    face_shape_vector   JSON                NOT NULL COMMENT '脸型分类概率向量',
    skin_tone_lab       JSON                NOT NULL COMMENT 'CIELab 肤色值',
    skin_tone_category  VARCHAR(32)         DEFAULT NULL COMMENT '肤色分类标签',
    face_landmarks_468  JSON                DEFAULT NULL COMMENT 'MediaPipe 468关键点快照',
    jaw_width_ratio     DECIMAL(5,4)        DEFAULT NULL COMMENT '下颌宽度比',
    confidence          DECIMAL(5,4)        NOT NULL COMMENT '模型置信度 0~1',
    model_version       VARCHAR(32)         NOT NULL DEFAULT 'resnet18_v1',
    created_at          DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_user_id (user_id),
    INDEX idx_face_shape (face_shape),
    CONSTRAINT fk_face_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 3. 商品 SPU 表
-- -----------------------------------------------------------
CREATE TABLE goods_spu (
    id                      BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    name                    VARCHAR(200)        NOT NULL,
    category                ENUM('earring','necklace','hairpin','bracelet','brooch') NOT NULL,
    sub_category            VARCHAR(64)         DEFAULT NULL,
    brand                   VARCHAR(100)        DEFAULT NULL,
    description             TEXT                DEFAULT NULL,
    description_vector      JSON                DEFAULT NULL COMMENT 'Sentence-BERT 768维语义向量',
    style_tags              JSON                NOT NULL COMMENT '风格标签数组',
    occasion_tags           JSON                DEFAULT NULL COMMENT '适用场景标签',
    material                VARCHAR(64)         DEFAULT NULL,
    target_face_shapes      JSON                DEFAULT NULL COMMENT '适合脸型数组',
    mount_type              ENUM('ear_lobe','ear_top','neck','hair','wrist') NOT NULL COMMENT 'AR挂载点类型',
    cover_url               VARCHAR(512)        DEFAULT NULL,
    detail_images           JSON                DEFAULT NULL,
    status                  TINYINT             NOT NULL DEFAULT 1 COMMENT '0-下架 1-上架',
    sort_weight             INT                 NOT NULL DEFAULT 0,
    match_penalty_matrix    JSON                DEFAULT NULL COMMENT '负反馈脸型惩罚矩阵',
    created_at              DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME            DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_category (category),
    INDEX idx_mount_type (mount_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 4. 商品 SKU 表
-- -----------------------------------------------------------
CREATE TABLE goods_sku (
    id                  BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    spu_id              BIGINT UNSIGNED     NOT NULL,
    sku_name            VARCHAR(200)        NOT NULL,
    color               VARCHAR(32)         DEFAULT NULL,
    size                VARCHAR(32)         DEFAULT NULL,
    price               DECIMAL(10,2)       NOT NULL,
    original_price      DECIMAL(10,2)       DEFAULT NULL,
    stock               INT UNSIGNED        NOT NULL DEFAULT 0,
    frozen_stock        INT UNSIGNED        NOT NULL DEFAULT 0 COMMENT '已下单未支付冻结库存',
    ar_asset_url        VARCHAR(512)        DEFAULT NULL COMMENT 'AR素材路径(透明PNG)',
    ar_offset_x         DECIMAL(6,2)        NOT NULL DEFAULT 0.00 COMMENT '素材X偏移量(px)',
    ar_offset_y         DECIMAL(6,2)        NOT NULL DEFAULT 0.00 COMMENT '素材Y偏移量(px)',
    ar_scale_base       DECIMAL(5,3)        NOT NULL DEFAULT 1.000 COMMENT '素材基础缩放系数',
    ar_rotation_offset  DECIMAL(5,2)        NOT NULL DEFAULT 0.00 COMMENT '素材旋转角度偏移(度)',
    weight_g            DECIMAL(6,2)        DEFAULT NULL COMMENT '重量(克)',
    status              TINYINT             NOT NULL DEFAULT 1 COMMENT '0-停售 1-在售',
    created_at          DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME            DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_spu_id (spu_id),
    INDEX idx_status (status),
    CONSTRAINT fk_sku_spu FOREIGN KEY (spu_id) REFERENCES goods_spu (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 5. 订单主表
-- -----------------------------------------------------------
CREATE TABLE orders (
    id                  BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    order_no            VARCHAR(32)         NOT NULL,
    user_id             BIGINT UNSIGNED     NOT NULL,
    total_amount        DECIMAL(10,2)       NOT NULL,
    pay_amount          DECIMAL(10,2)       DEFAULT NULL,
    status              ENUM('pending_pay','paid','shipped','received','completed','cancelled')
                                            NOT NULL DEFAULT 'pending_pay',
    receiver_name       VARCHAR(64)         DEFAULT NULL,
    receiver_phone      VARCHAR(20)         DEFAULT NULL,
    receiver_address    VARCHAR(512)        DEFAULT NULL,
    remark              VARCHAR(256)        DEFAULT NULL,
    pay_time            DATETIME            DEFAULT NULL,
    ship_time           DATETIME            DEFAULT NULL,
    receive_time        DATETIME            DEFAULT NULL,
    cancel_time         DATETIME            DEFAULT NULL,
    cancel_reason       VARCHAR(256)        DEFAULT NULL,
    created_at          DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME            DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_order_no (order_no),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 6. 订单明细表
-- -----------------------------------------------------------
CREATE TABLE order_items (
    id              BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    order_id        BIGINT UNSIGNED     NOT NULL,
    spu_id          BIGINT UNSIGNED     NOT NULL,
    sku_id          BIGINT UNSIGNED     NOT NULL,
    sku_name        VARCHAR(200)        DEFAULT NULL COMMENT 'SKU名称快照',
    cover_url       VARCHAR(512)        DEFAULT NULL COMMENT '商品图片快照',
    price           DECIMAL(10,2)       NOT NULL COMMENT '下单时单价快照',
    quantity        INT UNSIGNED        NOT NULL DEFAULT 1,
    subtotal        DECIMAL(10,2)       NOT NULL COMMENT '小计',
    PRIMARY KEY (id),
    INDEX idx_order_id (order_id),
    CONSTRAINT fk_item_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 7. 售后/退货表（逆向物流状态机）
-- -----------------------------------------------------------
CREATE TABLE refund_orders (
    id                      BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    refund_no               VARCHAR(32)         NOT NULL,
    order_id                BIGINT UNSIGNED     NOT NULL,
    order_item_id           BIGINT UNSIGNED     NOT NULL,
    user_id                 BIGINT UNSIGNED     NOT NULL,
    sku_id                  BIGINT UNSIGNED     NOT NULL,
    quantity                INT UNSIGNED        NOT NULL DEFAULT 1,
    refund_amount           DECIMAL(10,2)       NOT NULL,
    reason_type             ENUM('style_mismatch','size_issue','quality_defect','ar_expectation_gap','other')
                                                NOT NULL COMMENT '退货原因分类',
    reason_detail           VARCHAR(512)        DEFAULT NULL,
    status                  ENUM('pending_review','approved','rejected','pending_return',
                                 'returned','pending_restock','restocked','refunded','closed')
                                                NOT NULL DEFAULT 'pending_review',
    face_shape_at_purchase  VARCHAR(32)         DEFAULT NULL COMMENT '购买时脸型(用于负反馈)',
    feedback_processed      TINYINT             NOT NULL DEFAULT 0 COMMENT '负反馈是否已回写',
    review_note             VARCHAR(512)        DEFAULT NULL,
    reviewed_at             DATETIME            DEFAULT NULL,
    return_tracking_no      VARCHAR(64)         DEFAULT NULL COMMENT '退货物流单号',
    restocked_at            DATETIME            DEFAULT NULL,
    refunded_at             DATETIME            DEFAULT NULL,
    created_at              DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME            DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_refund_no (refund_no),
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    CONSTRAINT fk_refund_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE RESTRICT,
    CONSTRAINT fk_refund_item FOREIGN KEY (order_item_id) REFERENCES order_items (id) ON DELETE RESTRICT,
    CONSTRAINT fk_refund_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 8. 购物车表
-- -----------------------------------------------------------
CREATE TABLE cart_items (
    id              BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED     NOT NULL,
    sku_id          BIGINT UNSIGNED     NOT NULL,
    quantity        INT UNSIGNED        NOT NULL DEFAULT 1,
    selected        TINYINT             NOT NULL DEFAULT 1 COMMENT '是否勾选',
    created_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME            DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_sku (user_id, sku_id),
    CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_sku FOREIGN KEY (sku_id) REFERENCES goods_sku (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 9. AI 导购对话记录表
-- -----------------------------------------------------------
CREATE TABLE ai_guide_sessions (
    id                      BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    user_id                 BIGINT UNSIGNED     NOT NULL,
    session_token           VARCHAR(64)         NOT NULL,
    intent_tags             JSON                DEFAULT NULL COMMENT '用户意图标签累积',
    face_data_id            BIGINT UNSIGNED     DEFAULT NULL,
    recommended_spu_ids     JSON                DEFAULT NULL COMMENT '推荐过的SPU ID列表',
    converted_order_id      BIGINT UNSIGNED     DEFAULT NULL COMMENT '转化订单ID',
    created_at              DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at             DATETIME            DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_session_token (session_token),
    INDEX idx_user_id (user_id),
    CONSTRAINT fk_guide_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_guide_face FOREIGN KEY (face_data_id) REFERENCES user_face_data (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 10. 管理员表（简化版）
-- -----------------------------------------------------------
CREATE TABLE admins (
    id              BIGINT UNSIGNED     NOT NULL AUTO_INCREMENT,
    username        VARCHAR(64)         NOT NULL,
    password_hash   VARCHAR(128)        NOT NULL,
    role            ENUM('super_admin','operator') NOT NULL DEFAULT 'operator',
    created_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 初始管理员（密码: admin123，实际部署时需更换）
-- -----------------------------------------------------------
INSERT INTO admins (username, password_hash, role) VALUES
('admin', '$2b$12$placeholder_hash_replace_in_production', 'super_admin');
