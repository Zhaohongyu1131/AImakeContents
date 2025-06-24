-- DataSay Database Setup Script
-- Run this script to set up the DataSay database

-- 1. Create database
CREATE DATABASE datasay;
\c datasay;

-- 2. Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 3. Create all tables

CREATE TABLE user_auth_basic (
	user_id SERIAL NOT NULL, 
	user_name VARCHAR(50) NOT NULL, 
	user_email VARCHAR(100) NOT NULL, 
	user_phone VARCHAR(20), 
	user_password_hash VARCHAR(255) NOT NULL, 
	user_status VARCHAR(20) NOT NULL, 
	user_role VARCHAR(20) NOT NULL, 
	user_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	user_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	user_last_login_time TIMESTAMP WITH TIME ZONE, 
	user_profile_avatar VARCHAR(500), 
	user_profile_nickname VARCHAR(100), 
	PRIMARY KEY (user_id)
)

;
CREATE INDEX ix_user_auth_basic_user_status ON user_auth_basic (user_status);
CREATE INDEX ix_user_auth_basic_user_role ON user_auth_basic (user_role);
CREATE UNIQUE INDEX ix_user_auth_basic_user_name ON user_auth_basic (user_name);
CREATE UNIQUE INDEX ix_user_auth_basic_user_email ON user_auth_basic (user_email);
CREATE INDEX ix_user_auth_basic_user_id ON user_auth_basic (user_id);
COMMENT ON COLUMN user_auth_basic.user_id IS '用户ID';
COMMENT ON COLUMN user_auth_basic.user_name IS '用户名';
COMMENT ON COLUMN user_auth_basic.user_email IS '邮箱地址';
COMMENT ON COLUMN user_auth_basic.user_phone IS '手机号码';
COMMENT ON COLUMN user_auth_basic.user_password_hash IS '密码哈希';
COMMENT ON COLUMN user_auth_basic.user_status IS '用户状态';
COMMENT ON COLUMN user_auth_basic.user_role IS '用户角色';
COMMENT ON COLUMN user_auth_basic.user_created_time IS '创建时间';
COMMENT ON COLUMN user_auth_basic.user_updated_time IS '更新时间';
COMMENT ON COLUMN user_auth_basic.user_last_login_time IS '最后登录时间';
COMMENT ON COLUMN user_auth_basic.user_profile_avatar IS '头像URL';
COMMENT ON COLUMN user_auth_basic.user_profile_nickname IS '昵称';

CREATE TABLE user_auth_session (
	session_id VARCHAR(128) NOT NULL, 
	user_id INTEGER NOT NULL, 
	session_token_hash VARCHAR(255) NOT NULL, 
	session_expire_time TIMESTAMP WITH TIME ZONE NOT NULL, 
	session_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	session_ip_address INET, 
	session_user_agent VARCHAR(500), 
	PRIMARY KEY (session_id), 
	FOREIGN KEY(user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_user_auth_session_user_id ON user_auth_session (user_id);
CREATE INDEX ix_user_auth_session_session_expire_time ON user_auth_session (session_expire_time);
COMMENT ON COLUMN user_auth_session.session_id IS '会话ID';
COMMENT ON COLUMN user_auth_session.user_id IS '用户ID';
COMMENT ON COLUMN user_auth_session.session_token_hash IS '会话令牌哈希';
COMMENT ON COLUMN user_auth_session.session_expire_time IS '过期时间';
COMMENT ON COLUMN user_auth_session.session_created_time IS '创建时间';
COMMENT ON COLUMN user_auth_session.session_ip_address IS 'IP地址';
COMMENT ON COLUMN user_auth_session.session_user_agent IS '用户代理';

CREATE TABLE user_auth_profile (
	profile_id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	profile_nickname VARCHAR(100), 
	profile_avatar VARCHAR(500), 
	profile_bio TEXT, 
	profile_location VARCHAR(100), 
	profile_website VARCHAR(200), 
	profile_phone VARCHAR(20), 
	profile_wechat VARCHAR(50), 
	profile_qq VARCHAR(20), 
	profile_language VARCHAR(10) NOT NULL, 
	profile_timezone VARCHAR(50) NOT NULL, 
	profile_theme VARCHAR(20) NOT NULL, 
	profile_privacy_settings JSON, 
	profile_notification_settings JSON, 
	profile_phone_verified BOOLEAN NOT NULL, 
	profile_email_verified BOOLEAN NOT NULL, 
	profile_identity_verified BOOLEAN NOT NULL, 
	profile_login_count INTEGER NOT NULL, 
	profile_last_login_time TIMESTAMP WITH TIME ZONE, 
	profile_last_login_ip VARCHAR(45), 
	profile_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	profile_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	profile_status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (profile_id), 
	FOREIGN KEY(user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_user_auth_profile_profile_status ON user_auth_profile (profile_status);
CREATE INDEX ix_user_auth_profile_profile_id ON user_auth_profile (profile_id);
CREATE UNIQUE INDEX ix_user_auth_profile_user_id ON user_auth_profile (user_id);
COMMENT ON COLUMN user_auth_profile.profile_id IS '档案ID';
COMMENT ON COLUMN user_auth_profile.user_id IS '用户ID';
COMMENT ON COLUMN user_auth_profile.profile_nickname IS '昵称';
COMMENT ON COLUMN user_auth_profile.profile_avatar IS '头像URL';
COMMENT ON COLUMN user_auth_profile.profile_bio IS '个人简介';
COMMENT ON COLUMN user_auth_profile.profile_location IS '位置';
COMMENT ON COLUMN user_auth_profile.profile_website IS '个人网站';
COMMENT ON COLUMN user_auth_profile.profile_phone IS '电话号码';
COMMENT ON COLUMN user_auth_profile.profile_wechat IS '微信号';
COMMENT ON COLUMN user_auth_profile.profile_qq IS 'QQ号';
COMMENT ON COLUMN user_auth_profile.profile_language IS '语言偏好';
COMMENT ON COLUMN user_auth_profile.profile_timezone IS '时区';
COMMENT ON COLUMN user_auth_profile.profile_theme IS '主题偏好';
COMMENT ON COLUMN user_auth_profile.profile_privacy_settings IS '隐私设置JSON';
COMMENT ON COLUMN user_auth_profile.profile_notification_settings IS '通知设置JSON';
COMMENT ON COLUMN user_auth_profile.profile_phone_verified IS '电话是否验证';
COMMENT ON COLUMN user_auth_profile.profile_email_verified IS '邮箱是否验证';
COMMENT ON COLUMN user_auth_profile.profile_identity_verified IS '身份是否验证';
COMMENT ON COLUMN user_auth_profile.profile_login_count IS '登录次数';
COMMENT ON COLUMN user_auth_profile.profile_last_login_time IS '最后登录时间';
COMMENT ON COLUMN user_auth_profile.profile_last_login_ip IS '最后登录IP';
COMMENT ON COLUMN user_auth_profile.profile_created_time IS '创建时间';
COMMENT ON COLUMN user_auth_profile.profile_updated_time IS '更新时间';
COMMENT ON COLUMN user_auth_profile.profile_status IS '档案状态';

CREATE TABLE file_storage_basic (
	file_id SERIAL NOT NULL, 
	file_name VARCHAR(255) NOT NULL, 
	file_original_name VARCHAR(255) NOT NULL, 
	file_path VARCHAR(1000) NOT NULL, 
	file_size BIGINT NOT NULL, 
	file_type VARCHAR(100) NOT NULL, 
	file_mime_type VARCHAR(100) NOT NULL, 
	file_hash_md5 VARCHAR(32) NOT NULL, 
	file_storage_type VARCHAR(50) NOT NULL, 
	file_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	file_created_user_id INTEGER NOT NULL, 
	file_status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (file_id), 
	FOREIGN KEY(file_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_file_storage_basic_file_id ON file_storage_basic (file_id);
CREATE INDEX ix_file_storage_basic_file_hash_md5 ON file_storage_basic (file_hash_md5);
CREATE INDEX ix_file_storage_basic_file_status ON file_storage_basic (file_status);
CREATE INDEX ix_file_storage_basic_file_created_user_id ON file_storage_basic (file_created_user_id);
CREATE INDEX ix_file_storage_basic_file_type ON file_storage_basic (file_type);
COMMENT ON COLUMN file_storage_basic.file_id IS '文件ID';
COMMENT ON COLUMN file_storage_basic.file_name IS '文件名称';
COMMENT ON COLUMN file_storage_basic.file_original_name IS '原始文件名';
COMMENT ON COLUMN file_storage_basic.file_path IS '文件路径';
COMMENT ON COLUMN file_storage_basic.file_size IS '文件大小(字节)';
COMMENT ON COLUMN file_storage_basic.file_type IS '文件类型';
COMMENT ON COLUMN file_storage_basic.file_mime_type IS 'MIME类型';
COMMENT ON COLUMN file_storage_basic.file_hash_md5 IS '文件MD5哈希';
COMMENT ON COLUMN file_storage_basic.file_storage_type IS '存储类型';
COMMENT ON COLUMN file_storage_basic.file_created_time IS '创建时间';
COMMENT ON COLUMN file_storage_basic.file_created_user_id IS '创建用户ID';
COMMENT ON COLUMN file_storage_basic.file_status IS '文件状态';

CREATE TABLE text_template_basic (
	template_id SERIAL NOT NULL, 
	template_name VARCHAR(100) NOT NULL, 
	template_description TEXT, 
	template_content TEXT NOT NULL, 
	template_type VARCHAR(50) NOT NULL, 
	template_variables JSONB, 
	template_created_user_id INTEGER NOT NULL, 
	template_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	template_status VARCHAR(20) NOT NULL, 
	template_usage_count INTEGER NOT NULL, 
	PRIMARY KEY (template_id), 
	FOREIGN KEY(template_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_text_template_basic_template_type ON text_template_basic (template_type);
CREATE INDEX ix_text_template_basic_template_id ON text_template_basic (template_id);
CREATE INDEX ix_text_template_basic_template_created_user_id ON text_template_basic (template_created_user_id);
CREATE INDEX ix_text_template_basic_template_status ON text_template_basic (template_status);
COMMENT ON COLUMN text_template_basic.template_id IS '模板ID';
COMMENT ON COLUMN text_template_basic.template_name IS '模板名称';
COMMENT ON COLUMN text_template_basic.template_description IS '模板描述';
COMMENT ON COLUMN text_template_basic.template_content IS '模板内容';
COMMENT ON COLUMN text_template_basic.template_type IS '模板类型';
COMMENT ON COLUMN text_template_basic.template_variables IS '模板变量定义';
COMMENT ON COLUMN text_template_basic.template_created_user_id IS '创建用户ID';
COMMENT ON COLUMN text_template_basic.template_created_time IS '创建时间';
COMMENT ON COLUMN text_template_basic.template_status IS '模板状态';
COMMENT ON COLUMN text_template_basic.template_usage_count IS '使用次数';

CREATE TABLE mixed_content_template (
	template_id SERIAL NOT NULL, 
	template_name VARCHAR(100) NOT NULL, 
	template_description TEXT, 
	template_type VARCHAR(50) NOT NULL, 
	template_category VARCHAR(50), 
	template_text_template_ids JSONB, 
	template_image_template_ids JSONB, 
	template_audio_template_ids JSONB, 
	template_video_template_ids JSONB, 
	template_layout_config JSONB, 
	template_style_config JSONB, 
	template_timing_config JSONB, 
	template_interaction_config JSONB, 
	template_generation_params JSONB, 
	template_output_config JSONB, 
	template_quality_config JSONB, 
	template_default_content JSONB, 
	template_placeholder_data JSONB, 
	template_created_user_id INTEGER NOT NULL, 
	template_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	template_status VARCHAR(20) NOT NULL, 
	template_usage_count INTEGER NOT NULL, 
	template_rating INTEGER, 
	PRIMARY KEY (template_id), 
	FOREIGN KEY(template_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_mixed_content_template_template_category ON mixed_content_template (template_category);
CREATE INDEX ix_mixed_content_template_template_status ON mixed_content_template (template_status);
CREATE INDEX ix_mixed_content_template_template_id ON mixed_content_template (template_id);
CREATE INDEX ix_mixed_content_template_template_type ON mixed_content_template (template_type);
CREATE INDEX ix_mixed_content_template_template_created_user_id ON mixed_content_template (template_created_user_id);
COMMENT ON COLUMN mixed_content_template.template_id IS '模板ID';
COMMENT ON COLUMN mixed_content_template.template_name IS '模板名称';
COMMENT ON COLUMN mixed_content_template.template_description IS '模板描述';
COMMENT ON COLUMN mixed_content_template.template_type IS '模板类型';
COMMENT ON COLUMN mixed_content_template.template_category IS '模板分类';
COMMENT ON COLUMN mixed_content_template.template_text_template_ids IS '文本模板ID数组';
COMMENT ON COLUMN mixed_content_template.template_image_template_ids IS '图像模板ID数组';
COMMENT ON COLUMN mixed_content_template.template_audio_template_ids IS '音频模板ID数组';
COMMENT ON COLUMN mixed_content_template.template_video_template_ids IS '视频模板ID数组';
COMMENT ON COLUMN mixed_content_template.template_layout_config IS '布局配置模板';
COMMENT ON COLUMN mixed_content_template.template_style_config IS '样式配置模板';
COMMENT ON COLUMN mixed_content_template.template_timing_config IS '时序配置模板';
COMMENT ON COLUMN mixed_content_template.template_interaction_config IS '交互配置模板';
COMMENT ON COLUMN mixed_content_template.template_generation_params IS '生成参数配置';
COMMENT ON COLUMN mixed_content_template.template_output_config IS '输出配置';
COMMENT ON COLUMN mixed_content_template.template_quality_config IS '质量配置';
COMMENT ON COLUMN mixed_content_template.template_default_content IS '默认内容配置';
COMMENT ON COLUMN mixed_content_template.template_placeholder_data IS '占位符数据';
COMMENT ON COLUMN mixed_content_template.template_created_user_id IS '创建用户ID';
COMMENT ON COLUMN mixed_content_template.template_created_time IS '创建时间';
COMMENT ON COLUMN mixed_content_template.template_status IS '模板状态';
COMMENT ON COLUMN mixed_content_template.template_usage_count IS '使用次数';
COMMENT ON COLUMN mixed_content_template.template_rating IS '模板评分';

CREATE TABLE file_storage_meta (
	meta_id SERIAL NOT NULL, 
	file_id INTEGER NOT NULL, 
	meta_key VARCHAR(100) NOT NULL, 
	meta_value TEXT, 
	meta_type VARCHAR(50) NOT NULL, 
	meta_json JSON, 
	meta_category VARCHAR(50) NOT NULL, 
	meta_description VARCHAR(500), 
	meta_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	meta_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	meta_created_user_id INTEGER NOT NULL, 
	meta_status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (meta_id), 
	FOREIGN KEY(file_id) REFERENCES file_storage_basic (file_id), 
	FOREIGN KEY(meta_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_file_storage_meta_meta_id ON file_storage_meta (meta_id);
CREATE INDEX ix_file_storage_meta_file_id ON file_storage_meta (file_id);
CREATE INDEX ix_file_storage_meta_meta_category ON file_storage_meta (meta_category);
CREATE INDEX ix_file_storage_meta_meta_status ON file_storage_meta (meta_status);
CREATE INDEX ix_file_storage_meta_meta_key ON file_storage_meta (meta_key);
CREATE INDEX ix_file_storage_meta_meta_created_user_id ON file_storage_meta (meta_created_user_id);
COMMENT ON COLUMN file_storage_meta.meta_id IS '元数据ID';
COMMENT ON COLUMN file_storage_meta.file_id IS '文件ID';
COMMENT ON COLUMN file_storage_meta.meta_key IS '元数据键';
COMMENT ON COLUMN file_storage_meta.meta_value IS '元数据值';
COMMENT ON COLUMN file_storage_meta.meta_type IS '数据类型';
COMMENT ON COLUMN file_storage_meta.meta_json IS 'JSON格式元数据';
COMMENT ON COLUMN file_storage_meta.meta_category IS '元数据分类';
COMMENT ON COLUMN file_storage_meta.meta_description IS '元数据描述';
COMMENT ON COLUMN file_storage_meta.meta_created_time IS '创建时间';
COMMENT ON COLUMN file_storage_meta.meta_updated_time IS '更新时间';
COMMENT ON COLUMN file_storage_meta.meta_created_user_id IS '创建用户ID';
COMMENT ON COLUMN file_storage_meta.meta_status IS '元数据状态';

CREATE TABLE text_content_basic (
	text_id SERIAL NOT NULL, 
	text_title VARCHAR(200) NOT NULL, 
	text_content TEXT NOT NULL, 
	text_content_type VARCHAR(50) NOT NULL, 
	text_language VARCHAR(10) NOT NULL, 
	text_word_count INTEGER, 
	text_created_user_id INTEGER NOT NULL, 
	text_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	text_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	text_status VARCHAR(20) NOT NULL, 
	text_tags VARCHAR[], 
	text_template_id INTEGER, 
	PRIMARY KEY (text_id), 
	FOREIGN KEY(text_created_user_id) REFERENCES user_auth_basic (user_id), 
	FOREIGN KEY(text_template_id) REFERENCES text_template_basic (template_id)
)

;
CREATE INDEX ix_text_content_basic_text_id ON text_content_basic (text_id);
CREATE INDEX ix_text_content_basic_text_status ON text_content_basic (text_status);
CREATE INDEX ix_text_content_basic_text_content_type ON text_content_basic (text_content_type);
CREATE INDEX ix_text_content_basic_text_created_user_id ON text_content_basic (text_created_user_id);
COMMENT ON COLUMN text_content_basic.text_id IS '文本ID';
COMMENT ON COLUMN text_content_basic.text_title IS '文本标题';
COMMENT ON COLUMN text_content_basic.text_content IS '文本内容';
COMMENT ON COLUMN text_content_basic.text_content_type IS '内容类型';
COMMENT ON COLUMN text_content_basic.text_language IS '语言';
COMMENT ON COLUMN text_content_basic.text_word_count IS '字数统计';
COMMENT ON COLUMN text_content_basic.text_created_user_id IS '创建用户ID';
COMMENT ON COLUMN text_content_basic.text_created_time IS '创建时间';
COMMENT ON COLUMN text_content_basic.text_updated_time IS '更新时间';
COMMENT ON COLUMN text_content_basic.text_status IS '状态';
COMMENT ON COLUMN text_content_basic.text_tags IS '标签数组';
COMMENT ON COLUMN text_content_basic.text_template_id IS '模板ID';

CREATE TABLE voice_timbre_basic (
	timbre_id SERIAL NOT NULL, 
	timbre_name VARCHAR(100) NOT NULL, 
	timbre_description TEXT, 
	timbre_source_file_id INTEGER, 
	timbre_platform_id VARCHAR(100), 
	timbre_platform VARCHAR(50) NOT NULL, 
	timbre_language VARCHAR(10) NOT NULL, 
	timbre_gender VARCHAR(10), 
	timbre_age_range VARCHAR(20), 
	timbre_style VARCHAR(50), 
	timbre_quality_score DECIMAL(5, 2), 
	timbre_created_user_id INTEGER NOT NULL, 
	timbre_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	timbre_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	timbre_status VARCHAR(20) NOT NULL, 
	timbre_tags VARCHAR[], 
	PRIMARY KEY (timbre_id), 
	FOREIGN KEY(timbre_source_file_id) REFERENCES file_storage_basic (file_id), 
	FOREIGN KEY(timbre_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_voice_timbre_basic_timbre_status ON voice_timbre_basic (timbre_status);
CREATE INDEX ix_voice_timbre_basic_timbre_created_user_id ON voice_timbre_basic (timbre_created_user_id);
CREATE INDEX ix_voice_timbre_basic_timbre_gender ON voice_timbre_basic (timbre_gender);
CREATE INDEX ix_voice_timbre_basic_timbre_id ON voice_timbre_basic (timbre_id);
CREATE INDEX ix_voice_timbre_basic_timbre_style ON voice_timbre_basic (timbre_style);
CREATE INDEX ix_voice_timbre_basic_timbre_platform ON voice_timbre_basic (timbre_platform);
COMMENT ON COLUMN voice_timbre_basic.timbre_id IS '音色ID';
COMMENT ON COLUMN voice_timbre_basic.timbre_name IS '音色名称';
COMMENT ON COLUMN voice_timbre_basic.timbre_description IS '音色描述';
COMMENT ON COLUMN voice_timbre_basic.timbre_source_file_id IS '克隆源音频文件ID';
COMMENT ON COLUMN voice_timbre_basic.timbre_platform_id IS '第三方平台音色ID';
COMMENT ON COLUMN voice_timbre_basic.timbre_platform IS '平台名称';
COMMENT ON COLUMN voice_timbre_basic.timbre_language IS '语言';
COMMENT ON COLUMN voice_timbre_basic.timbre_gender IS '性别';
COMMENT ON COLUMN voice_timbre_basic.timbre_age_range IS '年龄范围';
COMMENT ON COLUMN voice_timbre_basic.timbre_style IS '音色风格';
COMMENT ON COLUMN voice_timbre_basic.timbre_quality_score IS '音色质量评分';
COMMENT ON COLUMN voice_timbre_basic.timbre_created_user_id IS '创建用户ID';
COMMENT ON COLUMN voice_timbre_basic.timbre_created_time IS '创建时间';
COMMENT ON COLUMN voice_timbre_basic.timbre_updated_time IS '更新时间';
COMMENT ON COLUMN voice_timbre_basic.timbre_status IS '状态';
COMMENT ON COLUMN voice_timbre_basic.timbre_tags IS '标签数组';

CREATE TABLE image_template (
	template_id SERIAL NOT NULL, 
	template_name VARCHAR(100) NOT NULL, 
	template_description TEXT, 
	template_type VARCHAR(50) NOT NULL, 
	template_text_template_id INTEGER, 
	template_generation_params JSONB, 
	template_prompt_template TEXT, 
	template_negative_prompt TEXT, 
	template_style_presets JSONB, 
	template_output_width INTEGER, 
	template_output_height INTEGER, 
	template_output_format VARCHAR(20) NOT NULL, 
	template_quality_level VARCHAR(20) NOT NULL, 
	template_platform VARCHAR(50) NOT NULL, 
	template_model_name VARCHAR(100), 
	template_platform_params JSONB, 
	template_created_user_id INTEGER NOT NULL, 
	template_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	template_status VARCHAR(20) NOT NULL, 
	template_usage_count INTEGER NOT NULL, 
	PRIMARY KEY (template_id), 
	FOREIGN KEY(template_text_template_id) REFERENCES text_template_basic (template_id), 
	FOREIGN KEY(template_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_image_template_template_status ON image_template (template_status);
CREATE INDEX ix_image_template_template_id ON image_template (template_id);
CREATE INDEX ix_image_template_template_created_user_id ON image_template (template_created_user_id);
CREATE INDEX ix_image_template_template_type ON image_template (template_type);
CREATE INDEX ix_image_template_template_platform ON image_template (template_platform);
COMMENT ON COLUMN image_template.template_id IS '模板ID';
COMMENT ON COLUMN image_template.template_name IS '模板名称';
COMMENT ON COLUMN image_template.template_description IS '模板描述';
COMMENT ON COLUMN image_template.template_type IS '模板类型';
COMMENT ON COLUMN image_template.template_text_template_id IS '文本模板ID';
COMMENT ON COLUMN image_template.template_generation_params IS '生成参数配置';
COMMENT ON COLUMN image_template.template_prompt_template IS '提示词模板';
COMMENT ON COLUMN image_template.template_negative_prompt IS '负向提示词';
COMMENT ON COLUMN image_template.template_style_presets IS '风格预设';
COMMENT ON COLUMN image_template.template_output_width IS '输出宽度';
COMMENT ON COLUMN image_template.template_output_height IS '输出高度';
COMMENT ON COLUMN image_template.template_output_format IS '输出格式';
COMMENT ON COLUMN image_template.template_quality_level IS '质量级别';
COMMENT ON COLUMN image_template.template_platform IS '平台名称';
COMMENT ON COLUMN image_template.template_model_name IS '模型名称';
COMMENT ON COLUMN image_template.template_platform_params IS '平台特定参数';
COMMENT ON COLUMN image_template.template_created_user_id IS '创建用户ID';
COMMENT ON COLUMN image_template.template_created_time IS '创建时间';
COMMENT ON COLUMN image_template.template_status IS '模板状态';
COMMENT ON COLUMN image_template.template_usage_count IS '使用次数';

CREATE TABLE mixed_content_basic (
	content_id SERIAL NOT NULL, 
	content_name VARCHAR(100) NOT NULL, 
	content_description TEXT, 
	content_type VARCHAR(50) NOT NULL, 
	content_text_ids INTEGER[], 
	content_image_ids INTEGER[], 
	content_audio_ids INTEGER[], 
	content_video_ids INTEGER[], 
	content_output_file_id INTEGER, 
	content_generation_params JSONB, 
	content_layout_config JSONB, 
	content_style_config JSONB, 
	content_timing_config JSONB, 
	content_created_user_id INTEGER NOT NULL, 
	content_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	content_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	content_status VARCHAR(20) NOT NULL, 
	content_tags VARCHAR[], 
	PRIMARY KEY (content_id), 
	FOREIGN KEY(content_output_file_id) REFERENCES file_storage_basic (file_id), 
	FOREIGN KEY(content_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_mixed_content_basic_content_type ON mixed_content_basic (content_type);
CREATE INDEX ix_mixed_content_basic_content_id ON mixed_content_basic (content_id);
CREATE INDEX ix_mixed_content_basic_content_status ON mixed_content_basic (content_status);
CREATE INDEX ix_mixed_content_basic_content_created_user_id ON mixed_content_basic (content_created_user_id);
COMMENT ON COLUMN mixed_content_basic.content_id IS '混合内容ID';
COMMENT ON COLUMN mixed_content_basic.content_name IS '内容名称';
COMMENT ON COLUMN mixed_content_basic.content_description IS '内容描述';
COMMENT ON COLUMN mixed_content_basic.content_type IS '内容类型';
COMMENT ON COLUMN mixed_content_basic.content_text_ids IS '关联的文本内容ID数组';
COMMENT ON COLUMN mixed_content_basic.content_image_ids IS '关联的图像内容ID数组';
COMMENT ON COLUMN mixed_content_basic.content_audio_ids IS '关联的音频内容ID数组';
COMMENT ON COLUMN mixed_content_basic.content_video_ids IS '关联的视频内容ID数组';
COMMENT ON COLUMN mixed_content_basic.content_output_file_id IS '输出文件ID';
COMMENT ON COLUMN mixed_content_basic.content_generation_params IS '生成参数';
COMMENT ON COLUMN mixed_content_basic.content_layout_config IS '布局配置';
COMMENT ON COLUMN mixed_content_basic.content_style_config IS '样式配置';
COMMENT ON COLUMN mixed_content_basic.content_timing_config IS '时序配置';
COMMENT ON COLUMN mixed_content_basic.content_created_user_id IS '创建用户ID';
COMMENT ON COLUMN mixed_content_basic.content_created_time IS '创建时间';
COMMENT ON COLUMN mixed_content_basic.content_updated_time IS '更新时间';
COMMENT ON COLUMN mixed_content_basic.content_status IS '状态';
COMMENT ON COLUMN mixed_content_basic.content_tags IS '标签数组';

CREATE TABLE text_analyse_result (
	analyse_id SERIAL NOT NULL, 
	text_id INTEGER NOT NULL, 
	analyse_type VARCHAR(50) NOT NULL, 
	analyse_result JSONB NOT NULL, 
	analyse_score DECIMAL(5, 2), 
	analyse_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	analyse_model_version VARCHAR(50), 
	PRIMARY KEY (analyse_id), 
	FOREIGN KEY(text_id) REFERENCES text_content_basic (text_id)
)

;
CREATE INDEX ix_text_analyse_result_text_id ON text_analyse_result (text_id);
CREATE INDEX ix_text_analyse_result_analyse_type ON text_analyse_result (analyse_type);
CREATE INDEX ix_text_analyse_result_analyse_id ON text_analyse_result (analyse_id);
COMMENT ON COLUMN text_analyse_result.analyse_id IS '分析ID';
COMMENT ON COLUMN text_analyse_result.text_id IS '文本ID';
COMMENT ON COLUMN text_analyse_result.analyse_type IS '分析类型';
COMMENT ON COLUMN text_analyse_result.analyse_result IS '分析结果JSON';
COMMENT ON COLUMN text_analyse_result.analyse_score IS '分析评分';
COMMENT ON COLUMN text_analyse_result.analyse_created_time IS '分析时间';
COMMENT ON COLUMN text_analyse_result.analyse_model_version IS '模型版本';

CREATE TABLE voice_timbre_clone (
	clone_id SERIAL NOT NULL, 
	timbre_id INTEGER NOT NULL, 
	clone_source_file_id INTEGER NOT NULL, 
	clone_source_duration DECIMAL(10, 2), 
	clone_training_params JSONB, 
	clone_progress INTEGER NOT NULL, 
	clone_created_user_id INTEGER NOT NULL, 
	clone_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	clone_completed_time TIMESTAMP WITH TIME ZONE, 
	clone_status VARCHAR(20) NOT NULL, 
	clone_error_message TEXT, 
	PRIMARY KEY (clone_id), 
	FOREIGN KEY(timbre_id) REFERENCES voice_timbre_basic (timbre_id), 
	FOREIGN KEY(clone_source_file_id) REFERENCES file_storage_basic (file_id), 
	FOREIGN KEY(clone_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_voice_timbre_clone_timbre_id ON voice_timbre_clone (timbre_id);
CREATE INDEX ix_voice_timbre_clone_clone_created_user_id ON voice_timbre_clone (clone_created_user_id);
CREATE INDEX ix_voice_timbre_clone_clone_id ON voice_timbre_clone (clone_id);
CREATE INDEX ix_voice_timbre_clone_clone_status ON voice_timbre_clone (clone_status);
COMMENT ON COLUMN voice_timbre_clone.clone_id IS '克隆记录ID';
COMMENT ON COLUMN voice_timbre_clone.timbre_id IS '音色ID';
COMMENT ON COLUMN voice_timbre_clone.clone_source_file_id IS '源音频文件ID';
COMMENT ON COLUMN voice_timbre_clone.clone_source_duration IS '源音频时长(秒)';
COMMENT ON COLUMN voice_timbre_clone.clone_training_params IS '训练参数';
COMMENT ON COLUMN voice_timbre_clone.clone_progress IS '训练进度百分比';
COMMENT ON COLUMN voice_timbre_clone.clone_created_user_id IS '创建用户ID';
COMMENT ON COLUMN voice_timbre_clone.clone_created_time IS '创建时间';
COMMENT ON COLUMN voice_timbre_clone.clone_completed_time IS '完成时间';
COMMENT ON COLUMN voice_timbre_clone.clone_status IS '克隆状态';
COMMENT ON COLUMN voice_timbre_clone.clone_error_message IS '错误信息';

CREATE TABLE voice_timbre_template (
	template_id SERIAL NOT NULL, 
	template_name VARCHAR(100) NOT NULL, 
	template_description TEXT, 
	template_timbre_id INTEGER, 
	template_clone_params JSONB, 
	template_quality_requirements JSONB, 
	template_created_user_id INTEGER NOT NULL, 
	template_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	template_status VARCHAR(20) NOT NULL, 
	template_usage_count INTEGER NOT NULL, 
	PRIMARY KEY (template_id), 
	FOREIGN KEY(template_timbre_id) REFERENCES voice_timbre_basic (timbre_id), 
	FOREIGN KEY(template_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_voice_timbre_template_template_id ON voice_timbre_template (template_id);
CREATE INDEX ix_voice_timbre_template_template_created_user_id ON voice_timbre_template (template_created_user_id);
CREATE INDEX ix_voice_timbre_template_template_status ON voice_timbre_template (template_status);
COMMENT ON COLUMN voice_timbre_template.template_id IS '模板ID';
COMMENT ON COLUMN voice_timbre_template.template_name IS '模板名称';
COMMENT ON COLUMN voice_timbre_template.template_description IS '模板描述';
COMMENT ON COLUMN voice_timbre_template.template_timbre_id IS '音色ID';
COMMENT ON COLUMN voice_timbre_template.template_clone_params IS '克隆参数配置';
COMMENT ON COLUMN voice_timbre_template.template_quality_requirements IS '质量要求';
COMMENT ON COLUMN voice_timbre_template.template_created_user_id IS '创建用户ID';
COMMENT ON COLUMN voice_timbre_template.template_created_time IS '创建时间';
COMMENT ON COLUMN voice_timbre_template.template_status IS '模板状态';
COMMENT ON COLUMN voice_timbre_template.template_usage_count IS '使用次数';

CREATE TABLE voice_audio_basic (
	audio_id SERIAL NOT NULL, 
	audio_name VARCHAR(100) NOT NULL, 
	audio_description TEXT, 
	audio_file_id INTEGER NOT NULL, 
	audio_duration DECIMAL(10, 2), 
	audio_format VARCHAR(20), 
	audio_sample_rate INTEGER, 
	audio_bitrate INTEGER, 
	audio_source_text_id INTEGER, 
	audio_timbre_id INTEGER, 
	audio_synthesis_params JSONB, 
	audio_platform VARCHAR(50) NOT NULL, 
	audio_platform_task_id VARCHAR(100), 
	audio_created_user_id INTEGER NOT NULL, 
	audio_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	audio_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	audio_status VARCHAR(20) NOT NULL, 
	audio_tags VARCHAR[], 
	PRIMARY KEY (audio_id), 
	FOREIGN KEY(audio_file_id) REFERENCES file_storage_basic (file_id), 
	FOREIGN KEY(audio_source_text_id) REFERENCES text_content_basic (text_id), 
	FOREIGN KEY(audio_timbre_id) REFERENCES voice_timbre_basic (timbre_id), 
	FOREIGN KEY(audio_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_voice_audio_basic_audio_status ON voice_audio_basic (audio_status);
CREATE INDEX ix_voice_audio_basic_audio_id ON voice_audio_basic (audio_id);
CREATE INDEX ix_voice_audio_basic_audio_platform ON voice_audio_basic (audio_platform);
CREATE INDEX ix_voice_audio_basic_audio_created_user_id ON voice_audio_basic (audio_created_user_id);
COMMENT ON COLUMN voice_audio_basic.audio_id IS '音频ID';
COMMENT ON COLUMN voice_audio_basic.audio_name IS '音频名称';
COMMENT ON COLUMN voice_audio_basic.audio_description IS '音频描述';
COMMENT ON COLUMN voice_audio_basic.audio_file_id IS '音频文件ID';
COMMENT ON COLUMN voice_audio_basic.audio_duration IS '音频时长(秒)';
COMMENT ON COLUMN voice_audio_basic.audio_format IS '音频格式';
COMMENT ON COLUMN voice_audio_basic.audio_sample_rate IS '采样率';
COMMENT ON COLUMN voice_audio_basic.audio_bitrate IS '比特率';
COMMENT ON COLUMN voice_audio_basic.audio_source_text_id IS '源文本ID';
COMMENT ON COLUMN voice_audio_basic.audio_timbre_id IS '音色ID';
COMMENT ON COLUMN voice_audio_basic.audio_synthesis_params IS '合成参数';
COMMENT ON COLUMN voice_audio_basic.audio_platform IS '平台名称';
COMMENT ON COLUMN voice_audio_basic.audio_platform_task_id IS '平台任务ID';
COMMENT ON COLUMN voice_audio_basic.audio_created_user_id IS '创建用户ID';
COMMENT ON COLUMN voice_audio_basic.audio_created_time IS '创建时间';
COMMENT ON COLUMN voice_audio_basic.audio_updated_time IS '更新时间';
COMMENT ON COLUMN voice_audio_basic.audio_status IS '状态';
COMMENT ON COLUMN voice_audio_basic.audio_tags IS '标签数组';

CREATE TABLE voice_audio_template (
	template_id SERIAL NOT NULL, 
	template_name VARCHAR(100) NOT NULL, 
	template_description TEXT, 
	template_type VARCHAR(50) NOT NULL, 
	template_timbre_id INTEGER, 
	template_text_template_id INTEGER, 
	template_synthesis_params JSONB, 
	template_output_format VARCHAR(20) NOT NULL, 
	template_sample_rate INTEGER, 
	template_bitrate INTEGER, 
	template_platform VARCHAR(50) NOT NULL, 
	template_platform_params JSONB, 
	template_created_user_id INTEGER NOT NULL, 
	template_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	template_status VARCHAR(20) NOT NULL, 
	template_usage_count INTEGER NOT NULL, 
	PRIMARY KEY (template_id), 
	FOREIGN KEY(template_timbre_id) REFERENCES voice_timbre_basic (timbre_id), 
	FOREIGN KEY(template_text_template_id) REFERENCES text_template_basic (template_id), 
	FOREIGN KEY(template_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_voice_audio_template_template_type ON voice_audio_template (template_type);
CREATE INDEX ix_voice_audio_template_template_platform ON voice_audio_template (template_platform);
CREATE INDEX ix_voice_audio_template_template_status ON voice_audio_template (template_status);
CREATE INDEX ix_voice_audio_template_template_id ON voice_audio_template (template_id);
CREATE INDEX ix_voice_audio_template_template_created_user_id ON voice_audio_template (template_created_user_id);
COMMENT ON COLUMN voice_audio_template.template_id IS '模板ID';
COMMENT ON COLUMN voice_audio_template.template_name IS '模板名称';
COMMENT ON COLUMN voice_audio_template.template_description IS '模板描述';
COMMENT ON COLUMN voice_audio_template.template_type IS '模板类型';
COMMENT ON COLUMN voice_audio_template.template_timbre_id IS '音色ID';
COMMENT ON COLUMN voice_audio_template.template_text_template_id IS '文本模板ID';
COMMENT ON COLUMN voice_audio_template.template_synthesis_params IS '合成参数配置';
COMMENT ON COLUMN voice_audio_template.template_output_format IS '输出格式';
COMMENT ON COLUMN voice_audio_template.template_sample_rate IS '采样率';
COMMENT ON COLUMN voice_audio_template.template_bitrate IS '比特率';
COMMENT ON COLUMN voice_audio_template.template_platform IS '平台名称';
COMMENT ON COLUMN voice_audio_template.template_platform_params IS '平台特定参数';
COMMENT ON COLUMN voice_audio_template.template_created_user_id IS '创建用户ID';
COMMENT ON COLUMN voice_audio_template.template_created_time IS '创建时间';
COMMENT ON COLUMN voice_audio_template.template_status IS '模板状态';
COMMENT ON COLUMN voice_audio_template.template_usage_count IS '使用次数';

CREATE TABLE image_basic (
	image_id SERIAL NOT NULL, 
	image_name VARCHAR(100) NOT NULL, 
	image_description TEXT, 
	image_file_id INTEGER NOT NULL, 
	image_width INTEGER, 
	image_height INTEGER, 
	image_format VARCHAR(20), 
	image_source_text_id INTEGER, 
	image_generation_params JSONB, 
	image_prompt TEXT, 
	image_negative_prompt TEXT, 
	image_platform VARCHAR(50) NOT NULL, 
	image_platform_task_id VARCHAR(100), 
	image_model_name VARCHAR(100), 
	image_created_user_id INTEGER NOT NULL, 
	image_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	image_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	image_status VARCHAR(20) NOT NULL, 
	image_tags VARCHAR[], 
	PRIMARY KEY (image_id), 
	FOREIGN KEY(image_file_id) REFERENCES file_storage_basic (file_id), 
	FOREIGN KEY(image_source_text_id) REFERENCES text_content_basic (text_id), 
	FOREIGN KEY(image_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_image_basic_image_platform ON image_basic (image_platform);
CREATE INDEX ix_image_basic_image_created_user_id ON image_basic (image_created_user_id);
CREATE INDEX ix_image_basic_image_id ON image_basic (image_id);
CREATE INDEX ix_image_basic_image_status ON image_basic (image_status);
COMMENT ON COLUMN image_basic.image_id IS '图像ID';
COMMENT ON COLUMN image_basic.image_name IS '图像名称';
COMMENT ON COLUMN image_basic.image_description IS '图像描述';
COMMENT ON COLUMN image_basic.image_file_id IS '图像文件ID';
COMMENT ON COLUMN image_basic.image_width IS '图像宽度';
COMMENT ON COLUMN image_basic.image_height IS '图像高度';
COMMENT ON COLUMN image_basic.image_format IS '图像格式';
COMMENT ON COLUMN image_basic.image_source_text_id IS '源文本ID';
COMMENT ON COLUMN image_basic.image_generation_params IS '生成参数';
COMMENT ON COLUMN image_basic.image_prompt IS '生成提示词';
COMMENT ON COLUMN image_basic.image_negative_prompt IS '负向提示词';
COMMENT ON COLUMN image_basic.image_platform IS '平台名称';
COMMENT ON COLUMN image_basic.image_platform_task_id IS '平台任务ID';
COMMENT ON COLUMN image_basic.image_model_name IS '使用的模型名称';
COMMENT ON COLUMN image_basic.image_created_user_id IS '创建用户ID';
COMMENT ON COLUMN image_basic.image_created_time IS '创建时间';
COMMENT ON COLUMN image_basic.image_updated_time IS '更新时间';
COMMENT ON COLUMN image_basic.image_status IS '状态';
COMMENT ON COLUMN image_basic.image_tags IS '标签数组';

CREATE TABLE mixed_content_analyse (
	analyse_id SERIAL NOT NULL, 
	content_id INTEGER NOT NULL, 
	analyse_type VARCHAR(50) NOT NULL, 
	analyse_result JSONB, 
	analyse_summary TEXT, 
	analyse_quality_score DECIMAL(5, 2), 
	analyse_confidence_score DECIMAL(5, 2), 
	analyse_coherence_score DECIMAL(5, 2), 
	analyse_synchronization_score DECIMAL(5, 2), 
	analyse_engagement_score DECIMAL(5, 2), 
	analyse_effectiveness_score DECIMAL(5, 2), 
	analyse_load_time DECIMAL(10, 2), 
	analyse_file_size INTEGER, 
	analyse_compatibility_score DECIMAL(5, 2), 
	analyse_content_balance JSONB, 
	analyse_user_flow JSONB, 
	analyse_accessibility JSONB, 
	analyse_created_user_id INTEGER NOT NULL, 
	analyse_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	analyse_status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (analyse_id), 
	FOREIGN KEY(content_id) REFERENCES mixed_content_basic (content_id), 
	FOREIGN KEY(analyse_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_mixed_content_analyse_analyse_type ON mixed_content_analyse (analyse_type);
CREATE INDEX ix_mixed_content_analyse_analyse_status ON mixed_content_analyse (analyse_status);
CREATE INDEX ix_mixed_content_analyse_analyse_id ON mixed_content_analyse (analyse_id);
CREATE INDEX ix_mixed_content_analyse_content_id ON mixed_content_analyse (content_id);
CREATE INDEX ix_mixed_content_analyse_analyse_created_user_id ON mixed_content_analyse (analyse_created_user_id);
COMMENT ON COLUMN mixed_content_analyse.analyse_id IS '分析ID';
COMMENT ON COLUMN mixed_content_analyse.content_id IS '混合内容ID';
COMMENT ON COLUMN mixed_content_analyse.analyse_type IS '分析类型';
COMMENT ON COLUMN mixed_content_analyse.analyse_result IS '分析结果';
COMMENT ON COLUMN mixed_content_analyse.analyse_summary IS '分析摘要';
COMMENT ON COLUMN mixed_content_analyse.analyse_quality_score IS '质量评分';
COMMENT ON COLUMN mixed_content_analyse.analyse_confidence_score IS '置信度评分';
COMMENT ON COLUMN mixed_content_analyse.analyse_coherence_score IS '连贯性评分';
COMMENT ON COLUMN mixed_content_analyse.analyse_synchronization_score IS '同步性评分';
COMMENT ON COLUMN mixed_content_analyse.analyse_engagement_score IS '参与度评分';
COMMENT ON COLUMN mixed_content_analyse.analyse_effectiveness_score IS '有效性评分';
COMMENT ON COLUMN mixed_content_analyse.analyse_load_time IS '加载时间(秒)';
COMMENT ON COLUMN mixed_content_analyse.analyse_file_size IS '文件大小(字节)';
COMMENT ON COLUMN mixed_content_analyse.analyse_compatibility_score IS '兼容性评分';
COMMENT ON COLUMN mixed_content_analyse.analyse_content_balance IS '内容平衡分析';
COMMENT ON COLUMN mixed_content_analyse.analyse_user_flow IS '用户流程分析';
COMMENT ON COLUMN mixed_content_analyse.analyse_accessibility IS '可访问性分析';
COMMENT ON COLUMN mixed_content_analyse.analyse_created_user_id IS '创建用户ID';
COMMENT ON COLUMN mixed_content_analyse.analyse_created_time IS '创建时间';
COMMENT ON COLUMN mixed_content_analyse.analyse_status IS '分析状态';

CREATE TABLE voice_audio_analyse (
	analyse_id SERIAL NOT NULL, 
	audio_id INTEGER NOT NULL, 
	analyse_type VARCHAR(50) NOT NULL, 
	analyse_result JSONB, 
	analyse_summary TEXT, 
	analyse_quality_score DECIMAL(5, 2), 
	analyse_confidence_score DECIMAL(5, 2), 
	analyse_volume_level DECIMAL(5, 2), 
	analyse_noise_level DECIMAL(5, 2), 
	analyse_clarity_score DECIMAL(5, 2), 
	analyse_speech_rate DECIMAL(5, 2), 
	analyse_pause_count INTEGER, 
	analyse_emotion_data JSONB, 
	analyse_created_user_id INTEGER NOT NULL, 
	analyse_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	analyse_status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (analyse_id), 
	FOREIGN KEY(audio_id) REFERENCES voice_audio_basic (audio_id), 
	FOREIGN KEY(analyse_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_voice_audio_analyse_analyse_status ON voice_audio_analyse (analyse_status);
CREATE INDEX ix_voice_audio_analyse_analyse_created_user_id ON voice_audio_analyse (analyse_created_user_id);
CREATE INDEX ix_voice_audio_analyse_analyse_id ON voice_audio_analyse (analyse_id);
CREATE INDEX ix_voice_audio_analyse_audio_id ON voice_audio_analyse (audio_id);
CREATE INDEX ix_voice_audio_analyse_analyse_type ON voice_audio_analyse (analyse_type);
COMMENT ON COLUMN voice_audio_analyse.analyse_id IS '分析ID';
COMMENT ON COLUMN voice_audio_analyse.audio_id IS '音频ID';
COMMENT ON COLUMN voice_audio_analyse.analyse_type IS '分析类型';
COMMENT ON COLUMN voice_audio_analyse.analyse_result IS '分析结果';
COMMENT ON COLUMN voice_audio_analyse.analyse_summary IS '分析摘要';
COMMENT ON COLUMN voice_audio_analyse.analyse_quality_score IS '质量评分';
COMMENT ON COLUMN voice_audio_analyse.analyse_confidence_score IS '置信度评分';
COMMENT ON COLUMN voice_audio_analyse.analyse_volume_level IS '音量水平';
COMMENT ON COLUMN voice_audio_analyse.analyse_noise_level IS '噪音水平';
COMMENT ON COLUMN voice_audio_analyse.analyse_clarity_score IS '清晰度评分';
COMMENT ON COLUMN voice_audio_analyse.analyse_speech_rate IS '语速(字/分钟)';
COMMENT ON COLUMN voice_audio_analyse.analyse_pause_count IS '停顿次数';
COMMENT ON COLUMN voice_audio_analyse.analyse_emotion_data IS '情感分析数据';
COMMENT ON COLUMN voice_audio_analyse.analyse_created_user_id IS '创建用户ID';
COMMENT ON COLUMN voice_audio_analyse.analyse_created_time IS '创建时间';
COMMENT ON COLUMN voice_audio_analyse.analyse_status IS '分析状态';

CREATE TABLE image_analyse (
	analyse_id SERIAL NOT NULL, 
	image_id INTEGER NOT NULL, 
	analyse_type VARCHAR(50) NOT NULL, 
	analyse_result JSONB, 
	analyse_summary TEXT, 
	analyse_quality_score DECIMAL(5, 2), 
	analyse_confidence_score DECIMAL(5, 2), 
	analyse_brightness DECIMAL(5, 2), 
	analyse_contrast DECIMAL(5, 2), 
	analyse_saturation DECIMAL(5, 2), 
	analyse_sharpness DECIMAL(5, 2), 
	analyse_objects_detected JSONB, 
	analyse_faces_count INTEGER, 
	analyse_text_content TEXT, 
	analyse_dominant_colors JSONB, 
	analyse_emotion_data JSONB, 
	analyse_style_tags JSONB, 
	analyse_created_user_id INTEGER NOT NULL, 
	analyse_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	analyse_status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (analyse_id), 
	FOREIGN KEY(image_id) REFERENCES image_basic (image_id), 
	FOREIGN KEY(analyse_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_image_analyse_image_id ON image_analyse (image_id);
CREATE INDEX ix_image_analyse_analyse_created_user_id ON image_analyse (analyse_created_user_id);
CREATE INDEX ix_image_analyse_analyse_type ON image_analyse (analyse_type);
CREATE INDEX ix_image_analyse_analyse_status ON image_analyse (analyse_status);
CREATE INDEX ix_image_analyse_analyse_id ON image_analyse (analyse_id);
COMMENT ON COLUMN image_analyse.analyse_id IS '分析ID';
COMMENT ON COLUMN image_analyse.image_id IS '图像ID';
COMMENT ON COLUMN image_analyse.analyse_type IS '分析类型';
COMMENT ON COLUMN image_analyse.analyse_result IS '分析结果';
COMMENT ON COLUMN image_analyse.analyse_summary IS '分析摘要';
COMMENT ON COLUMN image_analyse.analyse_quality_score IS '质量评分';
COMMENT ON COLUMN image_analyse.analyse_confidence_score IS '置信度评分';
COMMENT ON COLUMN image_analyse.analyse_brightness IS '亮度';
COMMENT ON COLUMN image_analyse.analyse_contrast IS '对比度';
COMMENT ON COLUMN image_analyse.analyse_saturation IS '饱和度';
COMMENT ON COLUMN image_analyse.analyse_sharpness IS '清晰度';
COMMENT ON COLUMN image_analyse.analyse_objects_detected IS '检测到的对象';
COMMENT ON COLUMN image_analyse.analyse_faces_count IS '人脸数量';
COMMENT ON COLUMN image_analyse.analyse_text_content IS '图像中的文本内容';
COMMENT ON COLUMN image_analyse.analyse_dominant_colors IS '主要颜色';
COMMENT ON COLUMN image_analyse.analyse_emotion_data IS '情感分析数据';
COMMENT ON COLUMN image_analyse.analyse_style_tags IS '风格标签';
COMMENT ON COLUMN image_analyse.analyse_created_user_id IS '创建用户ID';
COMMENT ON COLUMN image_analyse.analyse_created_time IS '创建时间';
COMMENT ON COLUMN image_analyse.analyse_status IS '分析状态';

CREATE TABLE video_basic (
	video_id SERIAL NOT NULL, 
	video_name VARCHAR(100) NOT NULL, 
	video_description TEXT, 
	video_file_id INTEGER NOT NULL, 
	video_duration DECIMAL(10, 2), 
	video_width INTEGER, 
	video_height INTEGER, 
	video_format VARCHAR(20), 
	video_fps DECIMAL(5, 2), 
	video_bitrate INTEGER, 
	video_source_text_id INTEGER, 
	video_source_image_id INTEGER, 
	video_source_audio_id INTEGER, 
	video_generation_params JSONB, 
	video_platform VARCHAR(50) NOT NULL, 
	video_platform_task_id VARCHAR(100), 
	video_model_name VARCHAR(100), 
	video_created_user_id INTEGER NOT NULL, 
	video_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	video_updated_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	video_status VARCHAR(20) NOT NULL, 
	video_tags VARCHAR[], 
	PRIMARY KEY (video_id), 
	FOREIGN KEY(video_file_id) REFERENCES file_storage_basic (file_id), 
	FOREIGN KEY(video_source_text_id) REFERENCES text_content_basic (text_id), 
	FOREIGN KEY(video_source_image_id) REFERENCES image_basic (image_id), 
	FOREIGN KEY(video_source_audio_id) REFERENCES voice_audio_basic (audio_id), 
	FOREIGN KEY(video_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_video_basic_video_status ON video_basic (video_status);
CREATE INDEX ix_video_basic_video_id ON video_basic (video_id);
CREATE INDEX ix_video_basic_video_created_user_id ON video_basic (video_created_user_id);
CREATE INDEX ix_video_basic_video_platform ON video_basic (video_platform);
COMMENT ON COLUMN video_basic.video_id IS '视频ID';
COMMENT ON COLUMN video_basic.video_name IS '视频名称';
COMMENT ON COLUMN video_basic.video_description IS '视频描述';
COMMENT ON COLUMN video_basic.video_file_id IS '视频文件ID';
COMMENT ON COLUMN video_basic.video_duration IS '视频时长(秒)';
COMMENT ON COLUMN video_basic.video_width IS '视频宽度';
COMMENT ON COLUMN video_basic.video_height IS '视频高度';
COMMENT ON COLUMN video_basic.video_format IS '视频格式';
COMMENT ON COLUMN video_basic.video_fps IS '帧率';
COMMENT ON COLUMN video_basic.video_bitrate IS '比特率';
COMMENT ON COLUMN video_basic.video_source_text_id IS '源文本ID';
COMMENT ON COLUMN video_basic.video_source_image_id IS '源图像ID';
COMMENT ON COLUMN video_basic.video_source_audio_id IS '源音频ID';
COMMENT ON COLUMN video_basic.video_generation_params IS '生成参数';
COMMENT ON COLUMN video_basic.video_platform IS '平台名称';
COMMENT ON COLUMN video_basic.video_platform_task_id IS '平台任务ID';
COMMENT ON COLUMN video_basic.video_model_name IS '使用的模型名称';
COMMENT ON COLUMN video_basic.video_created_user_id IS '创建用户ID';
COMMENT ON COLUMN video_basic.video_created_time IS '创建时间';
COMMENT ON COLUMN video_basic.video_updated_time IS '更新时间';
COMMENT ON COLUMN video_basic.video_status IS '状态';
COMMENT ON COLUMN video_basic.video_tags IS '标签数组';

CREATE TABLE video_template (
	template_id SERIAL NOT NULL, 
	template_name VARCHAR(100) NOT NULL, 
	template_description TEXT, 
	template_type VARCHAR(50) NOT NULL, 
	template_text_template_id INTEGER, 
	template_image_template_id INTEGER, 
	template_audio_template_id INTEGER, 
	template_generation_params JSONB, 
	template_prompt_template TEXT, 
	template_style_presets JSONB, 
	template_output_width INTEGER, 
	template_output_height INTEGER, 
	template_output_fps DECIMAL(5, 2), 
	template_output_duration DECIMAL(10, 2), 
	template_output_format VARCHAR(20) NOT NULL, 
	template_quality_level VARCHAR(20) NOT NULL, 
	template_platform VARCHAR(50) NOT NULL, 
	template_model_name VARCHAR(100), 
	template_platform_params JSONB, 
	template_created_user_id INTEGER NOT NULL, 
	template_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	template_status VARCHAR(20) NOT NULL, 
	template_usage_count INTEGER NOT NULL, 
	PRIMARY KEY (template_id), 
	FOREIGN KEY(template_text_template_id) REFERENCES text_template_basic (template_id), 
	FOREIGN KEY(template_image_template_id) REFERENCES image_template (template_id), 
	FOREIGN KEY(template_audio_template_id) REFERENCES voice_audio_template (template_id), 
	FOREIGN KEY(template_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_video_template_template_type ON video_template (template_type);
CREATE INDEX ix_video_template_template_platform ON video_template (template_platform);
CREATE INDEX ix_video_template_template_status ON video_template (template_status);
CREATE INDEX ix_video_template_template_created_user_id ON video_template (template_created_user_id);
CREATE INDEX ix_video_template_template_id ON video_template (template_id);
COMMENT ON COLUMN video_template.template_id IS '模板ID';
COMMENT ON COLUMN video_template.template_name IS '模板名称';
COMMENT ON COLUMN video_template.template_description IS '模板描述';
COMMENT ON COLUMN video_template.template_type IS '模板类型';
COMMENT ON COLUMN video_template.template_text_template_id IS '文本模板ID';
COMMENT ON COLUMN video_template.template_image_template_id IS '图像模板ID';
COMMENT ON COLUMN video_template.template_audio_template_id IS '音频模板ID';
COMMENT ON COLUMN video_template.template_generation_params IS '生成参数配置';
COMMENT ON COLUMN video_template.template_prompt_template IS '提示词模板';
COMMENT ON COLUMN video_template.template_style_presets IS '风格预设';
COMMENT ON COLUMN video_template.template_output_width IS '输出宽度';
COMMENT ON COLUMN video_template.template_output_height IS '输出高度';
COMMENT ON COLUMN video_template.template_output_fps IS '输出帧率';
COMMENT ON COLUMN video_template.template_output_duration IS '输出时长(秒)';
COMMENT ON COLUMN video_template.template_output_format IS '输出格式';
COMMENT ON COLUMN video_template.template_quality_level IS '质量级别';
COMMENT ON COLUMN video_template.template_platform IS '平台名称';
COMMENT ON COLUMN video_template.template_model_name IS '模型名称';
COMMENT ON COLUMN video_template.template_platform_params IS '平台特定参数';
COMMENT ON COLUMN video_template.template_created_user_id IS '创建用户ID';
COMMENT ON COLUMN video_template.template_created_time IS '创建时间';
COMMENT ON COLUMN video_template.template_status IS '模板状态';
COMMENT ON COLUMN video_template.template_usage_count IS '使用次数';

CREATE TABLE video_analyse (
	analyse_id SERIAL NOT NULL, 
	video_id INTEGER NOT NULL, 
	analyse_type VARCHAR(50) NOT NULL, 
	analyse_result JSONB, 
	analyse_summary TEXT, 
	analyse_quality_score DECIMAL(5, 2), 
	analyse_confidence_score DECIMAL(5, 2), 
	analyse_frame_quality DECIMAL(5, 2), 
	analyse_motion_smoothness DECIMAL(5, 2), 
	analyse_color_consistency DECIMAL(5, 2), 
	analyse_audio_sync DECIMAL(5, 2), 
	analyse_scene_changes INTEGER, 
	analyse_objects_detected JSONB, 
	analyse_faces_detected JSONB, 
	analyse_text_content TEXT, 
	analyse_emotion_timeline JSONB, 
	analyse_activity_level DECIMAL(5, 2), 
	analyse_content_tags JSONB, 
	analyse_created_user_id INTEGER NOT NULL, 
	analyse_created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	analyse_status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (analyse_id), 
	FOREIGN KEY(video_id) REFERENCES video_basic (video_id), 
	FOREIGN KEY(analyse_created_user_id) REFERENCES user_auth_basic (user_id)
)

;
CREATE INDEX ix_video_analyse_analyse_status ON video_analyse (analyse_status);
CREATE INDEX ix_video_analyse_analyse_id ON video_analyse (analyse_id);
CREATE INDEX ix_video_analyse_video_id ON video_analyse (video_id);
CREATE INDEX ix_video_analyse_analyse_created_user_id ON video_analyse (analyse_created_user_id);
CREATE INDEX ix_video_analyse_analyse_type ON video_analyse (analyse_type);
COMMENT ON COLUMN video_analyse.analyse_id IS '分析ID';
COMMENT ON COLUMN video_analyse.video_id IS '视频ID';
COMMENT ON COLUMN video_analyse.analyse_type IS '分析类型';
COMMENT ON COLUMN video_analyse.analyse_result IS '分析结果';
COMMENT ON COLUMN video_analyse.analyse_summary IS '分析摘要';
COMMENT ON COLUMN video_analyse.analyse_quality_score IS '质量评分';
COMMENT ON COLUMN video_analyse.analyse_confidence_score IS '置信度评分';
COMMENT ON COLUMN video_analyse.analyse_frame_quality IS '帧质量评分';
COMMENT ON COLUMN video_analyse.analyse_motion_smoothness IS '运动平滑度';
COMMENT ON COLUMN video_analyse.analyse_color_consistency IS '颜色一致性';
COMMENT ON COLUMN video_analyse.analyse_audio_sync IS '音画同步评分';
COMMENT ON COLUMN video_analyse.analyse_scene_changes IS '场景变化次数';
COMMENT ON COLUMN video_analyse.analyse_objects_detected IS '检测到的对象';
COMMENT ON COLUMN video_analyse.analyse_faces_detected IS '检测到的人脸';
COMMENT ON COLUMN video_analyse.analyse_text_content IS '视频中的文本内容';
COMMENT ON COLUMN video_analyse.analyse_emotion_timeline IS '情感时间线';
COMMENT ON COLUMN video_analyse.analyse_activity_level IS '活动水平';
COMMENT ON COLUMN video_analyse.analyse_content_tags IS '内容标签';
COMMENT ON COLUMN video_analyse.analyse_created_user_id IS '创建用户ID';
COMMENT ON COLUMN video_analyse.analyse_created_time IS '创建时间';
COMMENT ON COLUMN video_analyse.analyse_status IS '分析状态';