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