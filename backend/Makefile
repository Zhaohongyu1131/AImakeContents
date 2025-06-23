# DataSay Backend Makefile
# 开发环境管理 - [makefile]

.PHONY: help install dev clean test lint format docker-up docker-down

# 默认目标
help:
	@echo "DataSay Backend Development Commands:"
	@echo "  install      - Install dependencies"
	@echo "  dev          - Start development server"
	@echo "  clean        - Clean cache and temp files"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  docker-up    - Start Docker services"
	@echo "  docker-down  - Stop Docker services"
	@echo "  pre-commit   - Setup pre-commit hooks"

# 安装依赖
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# 启动开发服务器
dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 清理缓存
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# 运行测试
test:
	pytest tests/ -v --cov=app --cov-report=html

# 代码检查
lint:
	flake8 app/
	mypy app/

# 代码格式化
format:
	black app/
	isort app/

# 设置pre-commit
pre-commit:
	pip install pre-commit
	pre-commit install

# Docker开发环境
docker-up:
	docker-compose -f ../docker-compose.dev.yml up -d

docker-down:
	docker-compose -f ../docker-compose.dev.yml down

docker-logs:
	docker-compose -f ../docker-compose.dev.yml logs -f

# 数据库迁移
db-init:
	alembic init alembic

db-migration:
	alembic revision --autogenerate -m "$(message)"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

# Celery任务
celery-worker:
	celery -A app.config.celery:celery_app_instance worker --loglevel=info

celery-beat:
	celery -A app.config.celery:celery_app_instance beat --loglevel=info

celery-flower:
	celery -A app.config.celery:celery_app_instance flower --port=5555

# 生产部署
build:
	docker build -t datasay-backend .

deploy:
	@echo "Production deployment script here"