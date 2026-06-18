--
CREATE DATABASE IF NOT EXISTS teaching_research
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE teaching_research;

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键自增',
    phone VARCHAR(11) NOT NULL UNIQUE COMMENT '手机号，唯一',
    password VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    name VARCHAR(50) NOT NULL COMMENT '用户姓名',
    school VARCHAR(100) DEFAULT NULL COMMENT '所属学校',
    title VARCHAR(50) DEFAULT NULL COMMENT '职称',
    role VARCHAR(20) NOT NULL DEFAULT 'teacher' COMMENT '角色：teacher/leader/admin',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态：1启用，0禁用',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

INSERT INTO users (phone, password, name, role, create_time)
VALUES (
    '13800138000',
    '$2b$12$X5En9y6m9D7qCraZmJjKLew1o4FHzVZgBI1P6zH07ZsPE0DM6yq0G',
    '系统管理员',
    'admin',
    NOW()
);

DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    name VARCHAR(50) NOT NULL COMMENT '分类名称',
    description VARCHAR(200) DEFAULT NULL COMMENT '分类描述',
    sort_order INT(11) DEFAULT 0 COMMENT '排序权重',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_category_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子分类表';

DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '帖子ID',
    user_id INT(11) NOT NULL COMMENT '作者ID',
    category_id INT(11) NOT NULL COMMENT '分类ID',
    title VARCHAR(200) NOT NULL COMMENT '帖子标题',
    content TEXT NOT NULL COMMENT '帖子内容',
    view_count INT(11) NOT NULL DEFAULT 0 COMMENT '浏览量',
    like_count INT(11) NOT NULL DEFAULT 0 COMMENT '点赞数',
    comment_count INT(11) NOT NULL DEFAULT 0 COMMENT '评论数',
    is_pinned TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否置顶：1是 0否',
    is_essence TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否精华：1是 0否',
    is_anonymous TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否匿名：1是 0否',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态：1正常 0隐藏 2删除',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子表';

DROP TABLE IF EXISTS comments;

CREATE TABLE comments (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '评论ID',
    post_id INT(11) NOT NULL COMMENT '所属帖子ID',
    user_id INT(11) NOT NULL COMMENT '评论者ID',
    parent_id INT(11) DEFAULT NULL COMMENT '回复的评论ID，NULL表示直接回复帖子',
    content TEXT NOT NULL COMMENT '评论内容',
    is_anonymous TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否匿名：1是 0否',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态：1正常 0隐藏',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

DROP TABLE IF EXISTS likes;

CREATE TABLE likes (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '点赞ID',
    post_id INT(11) NOT NULL COMMENT '帖子ID',
    user_id INT(11) NOT NULL COMMENT '用户ID',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    UNIQUE KEY uk_post_user (post_id, user_id),
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='点赞记录表';

DROP TABLE IF EXISTS notifications;

CREATE TABLE notifications (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '通知ID',
    user_id INT(11) NOT NULL COMMENT '接收者ID',
    sender_id INT(11) NOT NULL COMMENT '触发者ID',
    type VARCHAR(20) NOT NULL COMMENT '类型：comment/like/reply',
    post_id INT(11) NOT NULL COMMENT '关联帖子ID',
    comment_id INT(11) DEFAULT NULL COMMENT '关联评论ID',
    content VARCHAR(200) NOT NULL COMMENT '通知摘要',
    is_read TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已读：1是 0否',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';

INSERT IGNORE INTO categories (name, description, sort_order, create_time) VALUES
('教案分享', '分享优秀教案与教学设计', 1, NOW()),
('课堂管理', '课堂纪律、学生互动技巧', 2, NOW()),
('考试命题', '试题设计、试卷分析', 3, NOW()),
('教学反思', '课后反思与改进记录', 4, NOW()),
('职业英语', '职场英语教学内容交流', 5, NOW()),
('AI工具', 'AI辅助教学工具与经验', 6, NOW());




