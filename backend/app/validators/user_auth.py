"""
User Authentication Validators
用户认证业务规则验证器 - [validators][user_auth]
"""

from typing import Dict, Any, List
from app.validators.base import ValidatorBase, ValidationResult


class UserAuthValidator(ValidatorBase):
    """
    用户认证业务规则验证器
    [validators][user_auth]
    """
    
    def __init__(self):
        """
        初始化用户认证验证器
        [validators][user_auth][init]
        """
        super().__init__()
        
        # 用户名规则配置
        self.username_rules = {
            "min_length": 3,
            "max_length": 50,
            "allowed_chars": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
            "forbidden_usernames": ["admin", "root", "system", "test", "user", "guest"]
        }
        
        # 密码规则配置
        self.password_rules = {
            "min_length": 8,
            "max_length": 128,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digit": True,
            "require_special": True
        }
        
        # 用户类型
        self.allowed_user_types = ["user", "admin", "moderator", "vip"]
        self.allowed_user_statuses = ["active", "inactive", "suspended", "pending"]
    
    def validate(self, data: Dict[str, Any], operation: str = "create") -> ValidationResult:
        """
        执行用户认证验证
        [validators][user_auth][validate]
        """
        result = self.validator_base_create_result()
        
        if operation == "register" or operation == "create":
            self._validate_registration(data, result)
        elif operation == "login":
            self._validate_login(data, result)
        elif operation == "update":
            self._validate_update(data, result)
        elif operation == "change_password":
            self._validate_change_password(data, result)
        elif operation == "reset_password":
            self._validate_reset_password(data, result)
        
        return result
    
    def _validate_registration(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证用户注册
        [validators][user_auth][_validate_registration]
        """
        # 验证用户名
        username = data.get("username")
        if not self.validator_base_validate_required(username, "用户名", result):
            return
        
        self._validate_username(username, result)
        
        # 验证邮箱
        email = data.get("email")
        if not self.validator_base_validate_required(email, "邮箱", result):
            return
        
        self.validator_base_validate_email(email, "邮箱", result)
        
        # 验证密码
        password = data.get("password")
        if not self.validator_base_validate_required(password, "密码", result):
            return
        
        self._validate_password(password, result)
        
        # 验证确认密码
        confirm_password = data.get("confirm_password")
        if confirm_password and password != confirm_password:
            result.add_error(
                code="PASSWORD_MISMATCH",
                message="密码和确认密码不匹配",
                field="confirm_password"
            )
        
        # 验证用户类型
        user_type = data.get("user_type", "user")
        self.validator_base_validate_enum(
            user_type, "用户类型", self.allowed_user_types, result
        )
        
        # 验证手机号（如果提供）
        phone = data.get("phone")
        if phone:
            self.validator_base_validate_phone(phone, "手机号", result)
        
        # 业务规则验证
        self._validate_registration_business_rules(data, result)
    
    def _validate_login(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证用户登录
        [validators][user_auth][_validate_login]
        """
        # 验证登录标识（用户名或邮箱）
        username = data.get("username")
        email = data.get("email")
        
        if not username and not email:
            result.add_error(
                code="LOGIN_IDENTIFIER_REQUIRED",
                message="请提供用户名或邮箱",
                field="username"
            )
            return
        
        if username:
            self._validate_username_format(username, result)
        
        if email:
            self.validator_base_validate_email(email, "邮箱", result)
        
        # 验证密码
        password = data.get("password")
        if not self.validator_base_validate_required(password, "密码", result):
            return
        
        # 验证登录IP（如果提供）
        login_ip = data.get("login_ip")
        if login_ip:
            self._validate_ip_address(login_ip, result)
    
    def _validate_update(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证用户信息更新
        [validators][user_auth][_validate_update]
        """
        # 验证邮箱（如果提供）
        email = data.get("email")
        if email:
            self.validator_base_validate_email(email, "邮箱", result)
        
        # 验证手机号（如果提供）
        phone = data.get("phone")
        if phone:
            self.validator_base_validate_phone(phone, "手机号", result)
        
        # 验证全名（如果提供）
        full_name = data.get("full_name")
        if full_name:
            self.validator_base_validate_length(
                full_name, "全名", min_length=2, max_length=100, result=result
            )
        
        # 验证用户状态（如果提供）
        user_status = data.get("user_status")
        if user_status:
            self.validator_base_validate_enum(
                user_status, "用户状态", self.allowed_user_statuses, result
            )
    
    def _validate_change_password(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证修改密码
        [validators][user_auth][_validate_change_password]
        """
        # 验证当前密码
        current_password = data.get("current_password")
        if not self.validator_base_validate_required(current_password, "当前密码", result):
            return
        
        # 验证新密码
        new_password = data.get("new_password")
        if not self.validator_base_validate_required(new_password, "新密码", result):
            return
        
        self._validate_password(new_password, result)
        
        # 验证确认新密码
        confirm_new_password = data.get("confirm_new_password")
        if confirm_new_password and new_password != confirm_new_password:
            result.add_error(
                code="NEW_PASSWORD_MISMATCH",
                message="新密码和确认密码不匹配",
                field="confirm_new_password"
            )
        
        # 检查新密码是否与当前密码相同
        if current_password == new_password:
            result.add_error(
                code="SAME_AS_CURRENT_PASSWORD",
                message="新密码不能与当前密码相同",
                field="new_password"
            )
    
    def _validate_reset_password(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证重置密码
        [validators][user_auth][_validate_reset_password]
        """
        # 验证重置令牌
        reset_token = data.get("reset_token")
        if not self.validator_base_validate_required(reset_token, "重置令牌", result):
            return
        
        # 验证新密码
        new_password = data.get("new_password")
        if not self.validator_base_validate_required(new_password, "新密码", result):
            return
        
        self._validate_password(new_password, result)
        
        # 验证确认新密码
        confirm_new_password = data.get("confirm_new_password")
        if confirm_new_password and new_password != confirm_new_password:
            result.add_error(
                code="NEW_PASSWORD_MISMATCH",
                message="新密码和确认密码不匹配",
                field="confirm_new_password"
            )
    
    def _validate_username(self, username: str, result: ValidationResult):
        """
        验证用户名
        [validators][user_auth][_validate_username]
        """
        self._validate_username_format(username, result)
        self._validate_username_business_rules(username, result)
    
    def _validate_username_format(self, username: str, result: ValidationResult):
        """
        验证用户名格式
        [validators][user_auth][_validate_username_format]
        """
        # 长度验证
        self.validator_base_validate_length(
            username, 
            "用户名", 
            min_length=self.username_rules["min_length"],
            max_length=self.username_rules["max_length"],
            result=result
        )
        
        # 字符验证
        allowed_chars = self.username_rules["allowed_chars"]
        if not all(c in allowed_chars for c in username):
            result.add_error(
                code="INVALID_USERNAME_CHARS",
                message="用户名只能包含字母、数字、下划线和连字符",
                field="username"
            )
        
        # 首字符验证
        if username and not username[0].isalpha():
            result.add_error(
                code="USERNAME_MUST_START_WITH_LETTER",
                message="用户名必须以字母开头",
                field="username"
            )
        
        # 连续特殊字符验证
        if "--" in username or "__" in username or "-_" in username or "_-" in username:
            result.add_error(
                code="USERNAME_INVALID_CONSECUTIVE_CHARS",
                message="用户名不能包含连续的特殊字符",
                field="username"
            )
    
    def _validate_username_business_rules(self, username: str, result: ValidationResult):
        """
        验证用户名业务规则
        [validators][user_auth][_validate_username_business_rules]
        """
        # 禁用用户名检查
        if username.lower() in self.username_rules["forbidden_usernames"]:
            result.add_error(
                code="FORBIDDEN_USERNAME",
                message="该用户名不可用",
                field="username"
            )
        
        # 敏感词检查
        sensitive_words = ["fuck", "shit", "admin", "root", "test"]
        if any(word in username.lower() for word in sensitive_words):
            result.add_warning(
                code="USERNAME_CONTAINS_SENSITIVE_WORD",
                message="用户名包含敏感词汇",
                field="username"
            )
    
    def _validate_password(self, password: str, result: ValidationResult):
        """
        验证密码
        [validators][user_auth][_validate_password]
        """
        self.validator_base_validate_password_strength(
            password,
            "密码",
            result,
            min_length=self.password_rules["min_length"],
            require_uppercase=self.password_rules["require_uppercase"],
            require_lowercase=self.password_rules["require_lowercase"],
            require_digit=self.password_rules["require_digit"],
            require_special=self.password_rules["require_special"]
        )
        
        # 最大长度验证
        self.validator_base_validate_length(
            password,
            "密码",
            max_length=self.password_rules["max_length"],
            result=result
        )
        
        # 常见密码检查
        common_passwords = [
            "12345678", "password", "123456789", "qwerty", 
            "abc123", "password123", "admin123"
        ]
        
        if password.lower() in common_passwords:
            result.add_error(
                code="COMMON_PASSWORD",
                message="密码过于简单，请使用更复杂的密码",
                field="password"
            )
    
    def _validate_registration_business_rules(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证注册业务规则
        [validators][user_auth][_validate_registration_business_rules]
        """
        # 用户名和邮箱唯一性检查（这里只是示例，实际需要查询数据库）
        username = data.get("username")
        email = data.get("email")
        
        # 注册频率限制检查
        user_ip = data.get("user_ip")
        if user_ip:
            # 这里可以添加IP注册频率限制的逻辑
            pass
        
        # 邮箱域名验证
        if email:
            domain = email.split("@")[1] if "@" in email else ""
            blocked_domains = ["tempmail.com", "10minutemail.com", "guerrillamail.com"]
            
            if domain in blocked_domains:
                result.add_error(
                    code="BLOCKED_EMAIL_DOMAIN",
                    message="不支持临时邮箱注册",
                    field="email"
                )
    
    def _validate_ip_address(self, ip_address: str, result: ValidationResult):
        """
        验证IP地址格式
        [validators][user_auth][_validate_ip_address]
        """
        import re
        
        # IPv4格式验证
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        # IPv6格式验证
        ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        
        if not (re.match(ipv4_pattern, ip_address) or re.match(ipv6_pattern, ip_address)):
            result.add_error(
                code="INVALID_IP_FORMAT",
                message="IP地址格式不正确",
                field="login_ip"
            )
    
    def validate_session_data(self, session_data: Dict[str, Any]) -> ValidationResult:
        """
        验证会话数据
        [validators][user_auth][validate_session_data]
        """
        result = self.validator_base_create_result()
        
        # 验证用户ID
        user_id = session_data.get("user_id")
        if not self.validator_base_validate_required(user_id, "用户ID", result):
            return result
        
        if not isinstance(user_id, int) or user_id <= 0:
            result.add_error(
                code="INVALID_USER_ID",
                message="用户ID必须是正整数",
                field="user_id"
            )
        
        # 验证会话令牌
        token = session_data.get("token")
        if not self.validator_base_validate_required(token, "会话令牌", result):
            return result
        
        # 验证过期时间
        expires_at = session_data.get("expires_at")
        if expires_at:
            from datetime import datetime
            if isinstance(expires_at, str):
                try:
                    expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                except ValueError:
                    result.add_error(
                        code="INVALID_EXPIRES_FORMAT",
                        message="过期时间格式不正确",
                        field="expires_at"
                    )
            
            if expires_at and expires_at <= datetime.utcnow():
                result.add_error(
                    code="SESSION_EXPIRED",
                    message="会话已过期",
                    field="expires_at"
                )
        
        return result
    
    def validate_profile_data(self, profile_data: Dict[str, Any]) -> ValidationResult:
        """
        验证用户资料数据
        [validators][user_auth][validate_profile_data]
        """
        result = self.validator_base_create_result()
        
        # 验证头像URL
        avatar_url = profile_data.get("avatar_url")
        if avatar_url:
            self.validator_base_validate_url(avatar_url, "头像URL", result)
        
        # 验证个人介绍
        bio = profile_data.get("bio")
        if bio:
            self.validator_base_validate_length(
                bio, "个人介绍", max_length=500, result=result
            )
        
        # 验证个人网站
        website = profile_data.get("website")
        if website:
            self.validator_base_validate_url(website, "个人网站", result)
        
        # 验证社交媒体链接
        social_links = profile_data.get("social_links", {})
        if social_links:
            for platform, url in social_links.items():
                if url:
                    self.validator_base_validate_url(url, f"{platform}链接", result)
        
        return result