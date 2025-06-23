# 数据库脚本使用说明

本目录包含了DataSay项目的数据库管理脚本。

## 脚本说明

### 1. database_init.py - 数据库初始化脚本

用于创建、删除或重置数据库表结构。

**使用方法：**

```bash
# 创建所有数据库表
python scripts/database_init.py create

# 删除所有数据库表
python scripts/database_init.py drop

# 重置数据库表（删除后重新创建）
python scripts/database_init.py reset
```

### 2. database_test_data.py - 测试数据脚本

用于插入或清除测试数据。

**使用方法：**

```bash
# 插入测试数据
python scripts/database_test_data.py insert

# 清除所有测试数据
python scripts/database_test_data.py clear
```

**测试数据包括：**

- 管理员用户 (admin / admin@datasay.com)
- 演示用户 (demo_user / demo@datasay.com)
- 文本模板 (营销文案、新闻稿、故事创作)
- 文本内容示例
- 音色示例 (温暖女声、专业男声、活泼童声)

## 使用流程

### 首次设置数据库

```bash
# 1. 创建数据库表
python scripts/database_init.py create

# 2. 插入测试数据
python scripts/database_test_data.py insert
```

### 重置开发环境

```bash
# 1. 重置数据库表
python scripts/database_init.py reset

# 2. 重新插入测试数据
python scripts/database_test_data.py insert
```

### 清理测试数据

```bash
# 只清除数据，保留表结构
python scripts/database_test_data.py clear
```

## 注意事项

1. 确保PostgreSQL服务器正在运行，且配置正确
2. 确保.env文件中的数据库连接信息正确
3. 运行脚本前请备份重要数据
4. 生产环境请勿使用测试数据脚本

## 数据库配置

默认数据库配置：
- 主机: localhost
- 端口: 5433
- 数据库: datasay
- 用户: datasayai
- 密码: datasayai123

配置信息可在`.env`文件或`app/config/settings.py`中修改。