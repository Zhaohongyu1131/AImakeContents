-- DataSay Database Initialization Script
-- 数据库初始化脚本

-- 创建数据库（如果不存在）
-- CREATE DATABASE IF NOT EXISTS datasay;

-- 设置数据库编码和校对规则
-- ALTER DATABASE datasay SET timezone TO 'Asia/Shanghai';

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建索引操作符类（用于性能优化）
-- 这些将在后续的模型创建中使用

-- 初始化完成日志
INSERT INTO information_schema.sql_implementation_info (implementation_info_id, implementation_info_name, integer_value, character_value, comments) 
VALUES ('DATASAY_INIT', 'DataSay Database Initialized', 1, CURRENT_TIMESTAMP::text, 'DataSay database initialization completed')
ON CONFLICT DO NOTHING;