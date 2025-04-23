-- 旅游网站数据库设计
-- 创建数据库
CREATE DATABASE IF NOT EXISTS tourism DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE tourism;

-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码(加密存储)',
    `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    `bio` TEXT DEFAULT NULL COMMENT '个人简介',
    `role` TINYINT(1) DEFAULT 0 COMMENT '角色(0普通用户,1管理员)',
    `status` TINYINT(1) DEFAULT 1 COMMENT '状态(0禁用,1正常)',
    `last_login` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `interest_tags` VARCHAR(255) DEFAULT NULL COMMENT '兴趣标签,用于推荐(逗号分隔)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 景点类别表
CREATE TABLE IF NOT EXISTS `attraction_category` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '类别ID',
    `name` VARCHAR(50) NOT NULL COMMENT '类别名称',
    `description` TEXT DEFAULT NULL COMMENT '类别描述',
    `icon` VARCHAR(255) DEFAULT NULL COMMENT '类别图标',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='景点类别表';

-- 地区表
CREATE TABLE IF NOT EXISTS `region` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '地区ID',
    `name` VARCHAR(50) NOT NULL COMMENT '地区名称',
    `parent_id` INT UNSIGNED DEFAULT NULL COMMENT '父级地区ID',
    `level` TINYINT(1) NOT NULL COMMENT '级别(1省/直辖市,2市,3区/县)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `parent_id` (`parent_id`),
    CONSTRAINT `region_parent_id` FOREIGN KEY (`parent_id`) REFERENCES `region` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地区表';

-- 景点表
CREATE TABLE IF NOT EXISTS `attraction` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '景点ID',
    `name` VARCHAR(100) NOT NULL COMMENT '景点名称',
    `category_id` INT UNSIGNED NOT NULL COMMENT '类别ID',
    `region_id` INT UNSIGNED NOT NULL COMMENT '所在地区ID',
    `address` VARCHAR(255) NOT NULL COMMENT '详细地址',
    `longitude` DECIMAL(10,7) DEFAULT NULL COMMENT '经度',
    `latitude` DECIMAL(10,7) DEFAULT NULL COMMENT '纬度',
    `description` TEXT NOT NULL COMMENT '景点描述',
    `open_time` VARCHAR(100) DEFAULT NULL COMMENT '开放时间',
    `ticket_info` TEXT DEFAULT NULL COMMENT '门票信息',
    `tips` TEXT DEFAULT NULL COMMENT '游玩提示',
    `cover_image` VARCHAR(255) DEFAULT NULL COMMENT '封面图片URL',
    `visit_count` INT UNSIGNED DEFAULT 0 COMMENT '访问次数',
    `rating` DECIMAL(2,1) DEFAULT 5.0 COMMENT '评分(1-5分)',
    `status` TINYINT(1) DEFAULT 1 COMMENT '状态(0下架,1上架)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `category_id` (`category_id`),
    KEY `region_id` (`region_id`),
    CONSTRAINT `attraction_category_id` FOREIGN KEY (`category_id`) REFERENCES `attraction_category` (`id`),
    CONSTRAINT `attraction_region_id` FOREIGN KEY (`region_id`) REFERENCES `region` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='景点表';

-- 景点图片表
CREATE TABLE IF NOT EXISTS `attraction_image` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '图片ID',
    `attraction_id` INT UNSIGNED NOT NULL COMMENT '景点ID',
    `url` VARCHAR(255) NOT NULL COMMENT '图片URL',
    `title` VARCHAR(100) DEFAULT NULL COMMENT '图片标题',
    `description` TEXT DEFAULT NULL COMMENT '图片描述',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `attraction_id` (`attraction_id`),
    CONSTRAINT `attraction_image_attraction_id` FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='景点图片表';

-- 攻略表
CREATE TABLE IF NOT EXISTS `travel_guide` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '攻略ID',
    `title` VARCHAR(100) NOT NULL COMMENT '攻略标题',
    `content` TEXT NOT NULL COMMENT '攻略内容',
    `author_id` INT UNSIGNED NOT NULL COMMENT '作者ID',
    `cover_image` VARCHAR(255) DEFAULT NULL COMMENT '封面图片URL',
    `route_map` TEXT DEFAULT NULL COMMENT '路线地图JSON',
    `view_count` INT UNSIGNED DEFAULT 0 COMMENT '浏览次数',
    `like_count` INT UNSIGNED DEFAULT 0 COMMENT '点赞次数',
    `collect_count` INT UNSIGNED DEFAULT 0 COMMENT '收藏次数',
    `status` TINYINT(1) DEFAULT 1 COMMENT '状态(0下架,1上架)',
    `is_recommended` TINYINT(1) DEFAULT 0 COMMENT '是否推荐(0否,1是)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `author_id` (`author_id`),
    CONSTRAINT `travel_guide_author_id` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='旅游攻略表';

-- 攻略景点关联表
CREATE TABLE IF NOT EXISTS `guide_attraction` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `guide_id` INT UNSIGNED NOT NULL COMMENT '攻略ID',
    `attraction_id` INT UNSIGNED NOT NULL COMMENT '景点ID',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    `note` TEXT DEFAULT NULL COMMENT '游玩备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `guide_attraction` (`guide_id`, `attraction_id`),
    KEY `guide_id` (`guide_id`),
    KEY `attraction_id` (`attraction_id`),
    CONSTRAINT `guide_attraction_guide_id` FOREIGN KEY (`guide_id`) REFERENCES `travel_guide` (`id`) ON DELETE CASCADE,
    CONSTRAINT `guide_attraction_attraction_id` FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='攻略景点关联表';

-- 游记表
CREATE TABLE IF NOT EXISTS `travel_note` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '游记ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `title` VARCHAR(100) NOT NULL COMMENT '游记标题',
    `content` TEXT NOT NULL COMMENT '游记内容',
    `cover_image` VARCHAR(255) DEFAULT NULL COMMENT '封面图片URL',
    `start_date` DATE DEFAULT NULL COMMENT '出行开始日期',
    `end_date` DATE DEFAULT NULL COMMENT '出行结束日期',
    `view_count` INT UNSIGNED DEFAULT 0 COMMENT '浏览次数',
    `like_count` INT UNSIGNED DEFAULT 0 COMMENT '点赞次数',
    `comment_count` INT UNSIGNED DEFAULT 0 COMMENT '评论次数',
    `status` TINYINT(1) DEFAULT 1 COMMENT '状态(0草稿,1已发布)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `travel_note_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='游记表';

-- 游记图片表
CREATE TABLE IF NOT EXISTS `travel_note_image` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '图片ID',
    `note_id` INT UNSIGNED NOT NULL COMMENT '游记ID',
    `url` VARCHAR(255) NOT NULL COMMENT '图片URL',
    `title` VARCHAR(100) DEFAULT NULL COMMENT '图片标题',
    `description` TEXT DEFAULT NULL COMMENT '图片描述',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `note_id` (`note_id`),
    CONSTRAINT `travel_note_image_note_id` FOREIGN KEY (`note_id`) REFERENCES `travel_note` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='游记图片表';

-- 游记景点关联表
CREATE TABLE IF NOT EXISTS `note_attraction` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `note_id` INT UNSIGNED NOT NULL COMMENT '游记ID',
    `attraction_id` INT UNSIGNED NOT NULL COMMENT '景点ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `note_attraction` (`note_id`, `attraction_id`),
    KEY `note_id` (`note_id`),
    KEY `attraction_id` (`attraction_id`),
    CONSTRAINT `note_attraction_note_id` FOREIGN KEY (`note_id`) REFERENCES `travel_note` (`id`) ON DELETE CASCADE,
    CONSTRAINT `note_attraction_attraction_id` FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='游记景点关联表';

-- 评论表 (用于景点、攻略、游记)
CREATE TABLE IF NOT EXISTS `comment` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '评论ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `content` TEXT NOT NULL COMMENT '评论内容',
    `target_id` INT UNSIGNED NOT NULL COMMENT '评论目标ID',
    `target_type` TINYINT(1) NOT NULL COMMENT '评论类型(1景点,2攻略,3游记)',
    `parent_id` INT UNSIGNED DEFAULT NULL COMMENT '父评论ID',
    `reply_to_id` INT UNSIGNED DEFAULT NULL COMMENT '回复用户ID',
    `like_count` INT UNSIGNED DEFAULT 0 COMMENT '点赞数',
    `status` TINYINT(1) DEFAULT 1 COMMENT '状态(0隐藏,1显示)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    KEY `target_id_target_type` (`target_id`, `target_type`),
    KEY `parent_id` (`parent_id`),
    CONSTRAINT `comment_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
    CONSTRAINT `comment_parent_id` FOREIGN KEY (`parent_id`) REFERENCES `comment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- 收藏表
CREATE TABLE IF NOT EXISTS `collection` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `target_id` INT UNSIGNED NOT NULL COMMENT '收藏目标ID',
    `target_type` TINYINT(1) NOT NULL COMMENT '收藏类型(1景点,2攻略,3游记)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `user_target` (`user_id`, `target_id`, `target_type`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `collection_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';

-- 点赞表
CREATE TABLE IF NOT EXISTS `like` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '点赞ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `target_id` INT UNSIGNED NOT NULL COMMENT '点赞目标ID',
    `target_type` TINYINT(1) NOT NULL COMMENT '点赞类型(1景点,2攻略,3游记,4评论)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `user_target` (`user_id`, `target_id`, `target_type`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `like_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='点赞表';

-- 用户浏览历史
CREATE TABLE IF NOT EXISTS `browse_history` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `target_id` INT UNSIGNED NOT NULL COMMENT '浏览目标ID',
    `target_type` TINYINT(1) NOT NULL COMMENT '浏览类型(1景点,2攻略,3游记)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    KEY `created_at` (`created_at`),
    CONSTRAINT `browse_history_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='浏览历史表';

-- 轮播图表
CREATE TABLE IF NOT EXISTS `banner` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '轮播图ID',
    `title` VARCHAR(100) NOT NULL COMMENT '标题',
    `image` VARCHAR(255) NOT NULL COMMENT '图片URL',
    `link` VARCHAR(255) DEFAULT NULL COMMENT '链接URL',
    `target_id` INT UNSIGNED DEFAULT NULL COMMENT '目标ID',
    `target_type` TINYINT(1) DEFAULT NULL COMMENT '目标类型(1景点,2攻略,3游记)',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT(1) DEFAULT 1 COMMENT '状态(0下架,1上架)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='轮播图表';

-- 系统配置表
CREATE TABLE IF NOT EXISTS `system_config` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '配置ID',
    `key` VARCHAR(50) NOT NULL COMMENT '配置键',
    `value` TEXT NOT NULL COMMENT '配置值',
    `description` VARCHAR(255) DEFAULT NULL COMMENT '配置描述',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 标签表
CREATE TABLE IF NOT EXISTS `tag` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '标签ID',
    `name` VARCHAR(50) NOT NULL COMMENT '标签名称',
    `type` TINYINT(1) DEFAULT 0 COMMENT '标签类型(0通用,1景点,2攻略,3游记)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `name_type` (`name`, `type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标签表';

-- 内容标签关联表
CREATE TABLE IF NOT EXISTS `content_tag` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `tag_id` INT UNSIGNED NOT NULL COMMENT '标签ID',
    `target_id` INT UNSIGNED NOT NULL COMMENT '目标ID',
    `target_type` TINYINT(1) NOT NULL COMMENT '目标类型(1景点,2攻略,3游记)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `tag_target` (`tag_id`, `target_id`, `target_type`),
    KEY `tag_id` (`tag_id`),
    CONSTRAINT `content_tag_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容标签关联表';

-- 旅游季节表
CREATE TABLE IF NOT EXISTS `travel_season` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `attraction_id` INT UNSIGNED NOT NULL COMMENT '景点ID',
    `season` TINYINT(1) NOT NULL COMMENT '季节(1春,2夏,3秋,4冬)',
    `recommendation` TEXT DEFAULT NULL COMMENT '季节推荐理由',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `attraction_season` (`attraction_id`, `season`),
    KEY `attraction_id` (`attraction_id`),
    CONSTRAINT `travel_season_attraction_id` FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='旅游季节表';

-- 用户行为记录表(用于推荐算法)
CREATE TABLE IF NOT EXISTS `user_behavior` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `target_id` INT UNSIGNED NOT NULL COMMENT '目标ID',
    `target_type` TINYINT(1) NOT NULL COMMENT '目标类型(1景点,2攻略,3游记)',
    `behavior_type` TINYINT(1) NOT NULL COMMENT '行为类型(1浏览,2收藏,3点赞,4评论)',
    `weight` DECIMAL(3,2) DEFAULT 1.00 COMMENT '行为权重',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    KEY `target_id_target_type` (`target_id`, `target_type`),
    CONSTRAINT `user_behavior_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户行为记录表';

-- 操作日志表
CREATE TABLE IF NOT EXISTS `operation_log` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `action` VARCHAR(50) NOT NULL COMMENT '操作动作',
    `target_id` INT UNSIGNED DEFAULT NULL COMMENT '目标ID',
    `target_type` VARCHAR(50) DEFAULT NULL COMMENT '目标类型',
    `content` TEXT DEFAULT NULL COMMENT '操作内容',
    `ip` VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
    `user_agent` VARCHAR(255) DEFAULT NULL COMMENT '浏览器信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `operation_log_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- 创建初始管理员账户
INSERT INTO `user` (`username`, `password`, `email`, `role`, `status`, `created_at`) VALUES 
('admin', '$2a$10$Z7Qvb0KmYUc4CL0bQswJmu1Y8dH9/WQxSGTIW8iRsEt7OBn.RsA9G', 'admin@example.com', 1, 1, NOW());

-- 添加示例景点类别
INSERT INTO `attraction_category` (`name`, `description`) VALUES 
('自然风光', '山水、湖泊、海滩等自然景观'),
('历史文化', '古迹、博物馆、文化遗址等'),
('主题公园', '游乐园、水上乐园等娱乐场所'),
('城市观光', '都市景观、地标建筑等'),
('乡村体验', '农家乐、乡村旅游等');

-- 添加系统基础配置
INSERT INTO `system_config` (`key`, `value`, `description`) VALUES 
('site_name', '旅游景点推荐系统', '网站名称'),
('site_description', '发现美丽风景，享受精彩旅程', '网站描述'),
('site_keywords', '旅游,景点,攻略,游记', '网站关键词'),
('recommendation_algorithm', 'collaborative_filtering', '推荐算法类型'); 