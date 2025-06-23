"""
Base Validator Class
业务规则验证器基类 - [validators][base]
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """
    验证级别枚举
    [validators][base][validation_level]
    """
    ERROR = "error"      # 错误 - 阻止操作继续
    WARNING = "warning"  # 警告 - 允许操作但需要提醒
    INFO = "info"        # 信息 - 仅提供信息


@dataclass
class ValidationMessage:
    """
    验证消息
    [validators][base][validation_message]
    """
    level: ValidationLevel
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """
    验证结果
    [validators][base][validation_result]
    """
    is_valid: bool
    messages: List[ValidationMessage]
    
    def add_error(self, code: str, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        添加错误消息
        [validators][base][validation_result][add_error]
        """
        self.messages.append(ValidationMessage(
            level=ValidationLevel.ERROR,
            code=code,
            message=message,
            field=field,
            details=details
        ))
        self.is_valid = False
    
    def add_warning(self, code: str, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        添加警告消息
        [validators][base][validation_result][add_warning]
        """
        self.messages.append(ValidationMessage(
            level=ValidationLevel.WARNING,
            code=code,
            message=message,
            field=field,
            details=details
        ))
    
    def add_info(self, code: str, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        添加信息消息
        [validators][base][validation_result][add_info]
        """
        self.messages.append(ValidationMessage(
            level=ValidationLevel.INFO,
            code=code,
            message=message,
            field=field,
            details=details
        ))
    
    def get_errors(self) -> List[ValidationMessage]:
        """
        获取错误消息列表
        [validators][base][validation_result][get_errors]
        """
        return [msg for msg in self.messages if msg.level == ValidationLevel.ERROR]
    
    def get_warnings(self) -> List[ValidationMessage]:
        """
        获取警告消息列表
        [validators][base][validation_result][get_warnings]
        """
        return [msg for msg in self.messages if msg.level == ValidationLevel.WARNING]
    
    def get_infos(self) -> List[ValidationMessage]:
        """
        获取信息消息列表
        [validators][base][validation_result][get_infos]
        """
        return [msg for msg in self.messages if msg.level == ValidationLevel.INFO]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        [validators][base][validation_result][to_dict]
        """
        return {
            "is_valid": self.is_valid,
            "errors": [
                {
                    "code": msg.code,
                    "message": msg.message,
                    "field": msg.field,
                    "details": msg.details
                }
                for msg in self.get_errors()
            ],
            "warnings": [
                {
                    "code": msg.code,
                    "message": msg.message,
                    "field": msg.field,
                    "details": msg.details
                }
                for msg in self.get_warnings()
            ],
            "infos": [
                {
                    "code": msg.code,
                    "message": msg.message,
                    "field": msg.field,
                    "details": msg.details
                }
                for msg in self.get_infos()
            ]
        }


class ValidatorBase(ABC):
    """
    业务规则验证器基类
    [validators][base]
    """
    
    def __init__(self):
        """
        初始化验证器基类
        [validators][base][init]
        """
        self.rules = {}
    
    def validator_base_create_result(self) -> ValidationResult:
        """
        创建验证结果对象
        [validators][base][create_result]
        """
        return ValidationResult(is_valid=True, messages=[])
    
    def validator_base_validate_required(
        self,
        value: Any,
        field_name: str,
        result: ValidationResult
    ) -> bool:
        """
        验证必填字段
        [validators][base][validate_required]
        """
        if value is None or (isinstance(value, str) and len(value.strip()) == 0):
            result.add_error(
                code="FIELD_REQUIRED",
                message=f"{field_name}不能为空",
                field=field_name
            )
            return False
        return True
    
    def validator_base_validate_length(
        self,
        value: str,
        field_name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        result: ValidationResult = None
    ) -> bool:
        """
        验证字符串长度
        [validators][base][validate_length]
        """
        if value is None:
            return True
        
        length = len(value)
        
        if min_length is not None and length < min_length:
            result.add_error(
                code="LENGTH_TOO_SHORT",
                message=f"{field_name}长度不能少于{min_length}个字符",
                field=field_name,
                details={"min_length": min_length, "actual_length": length}
            )
            return False
        
        if max_length is not None and length > max_length:
            result.add_error(
                code="LENGTH_TOO_LONG",
                message=f"{field_name}长度不能超过{max_length}个字符",
                field=field_name,
                details={"max_length": max_length, "actual_length": length}
            )
            return False
        
        return True
    
    def validator_base_validate_range(
        self,
        value: Union[int, float],
        field_name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        result: ValidationResult = None
    ) -> bool:
        """
        验证数值范围
        [validators][base][validate_range]
        """
        if value is None:
            return True
        
        if min_value is not None and value < min_value:
            result.add_error(
                code="VALUE_TOO_SMALL",
                message=f"{field_name}不能小于{min_value}",
                field=field_name,
                details={"min_value": min_value, "actual_value": value}
            )
            return False
        
        if max_value is not None and value > max_value:
            result.add_error(
                code="VALUE_TOO_LARGE",
                message=f"{field_name}不能大于{max_value}",
                field=field_name,
                details={"max_value": max_value, "actual_value": value}
            )
            return False
        
        return True
    
    def validator_base_validate_email(
        self,
        email: str,
        field_name: str,
        result: ValidationResult
    ) -> bool:
        """
        验证邮箱格式
        [validators][base][validate_email]
        """
        import re
        
        if not email:
            return True
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            result.add_error(
                code="INVALID_EMAIL_FORMAT",
                message=f"{field_name}格式不正确",
                field=field_name
            )
            return False
        
        return True
    
    def validator_base_validate_phone(
        self,
        phone: str,
        field_name: str,
        result: ValidationResult
    ) -> bool:
        """
        验证手机号格式
        [validators][base][validate_phone]
        """
        import re
        
        if not phone:
            return True
        
        # 中国手机号格式
        phone_pattern = r'^1[3-9]\d{9}$'
        
        if not re.match(phone_pattern, phone):
            result.add_error(
                code="INVALID_PHONE_FORMAT",
                message=f"{field_name}格式不正确",
                field=field_name
            )
            return False
        
        return True
    
    def validator_base_validate_url(
        self,
        url: str,
        field_name: str,
        result: ValidationResult
    ) -> bool:
        """
        验证URL格式
        [validators][base][validate_url]
        """
        import re
        
        if not url:
            return True
        
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.]*))?(?:#(?:\w*))?)?$'
        
        if not re.match(url_pattern, url):
            result.add_error(
                code="INVALID_URL_FORMAT",
                message=f"{field_name}格式不正确",
                field=field_name
            )
            return False
        
        return True
    
    def validator_base_validate_enum(
        self,
        value: Any,
        field_name: str,
        allowed_values: List[Any],
        result: ValidationResult
    ) -> bool:
        """
        验证枚举值
        [validators][base][validate_enum]
        """
        if value is None:
            return True
        
        if value not in allowed_values:
            result.add_error(
                code="INVALID_ENUM_VALUE",
                message=f"{field_name}必须是以下值之一: {', '.join(map(str, allowed_values))}",
                field=field_name,
                details={"allowed_values": allowed_values, "actual_value": value}
            )
            return False
        
        return True
    
    def validator_base_validate_file_size(
        self,
        file_size: int,
        field_name: str,
        max_size: int,
        result: ValidationResult
    ) -> bool:
        """
        验证文件大小
        [validators][base][validate_file_size]
        """
        if file_size is None:
            return True
        
        if file_size > max_size:
            result.add_error(
                code="FILE_SIZE_TOO_LARGE",
                message=f"{field_name}大小不能超过{max_size}字节",
                field=field_name,
                details={"max_size": max_size, "actual_size": file_size}
            )
            return False
        
        return True
    
    def validator_base_validate_file_type(
        self,
        file_type: str,
        field_name: str,
        allowed_types: List[str],
        result: ValidationResult
    ) -> bool:
        """
        验证文件类型
        [validators][base][validate_file_type]
        """
        if not file_type:
            return True
        
        # 检查主类型或完整类型
        main_type = file_type.split('/')[0] if '/' in file_type else file_type
        
        type_match = any(
            file_type == allowed_type or 
            main_type == allowed_type or
            file_type.startswith(allowed_type)
            for allowed_type in allowed_types
        )
        
        if not type_match:
            result.add_error(
                code="INVALID_FILE_TYPE",
                message=f"{field_name}类型不支持，支持的类型: {', '.join(allowed_types)}",
                field=field_name,
                details={"allowed_types": allowed_types, "actual_type": file_type}
            )
            return False
        
        return True
    
    def validator_base_validate_json(
        self,
        json_str: str,
        field_name: str,
        result: ValidationResult
    ) -> bool:
        """
        验证JSON格式
        [validators][base][validate_json]
        """
        if not json_str:
            return True
        
        try:
            import json
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            result.add_error(
                code="INVALID_JSON_FORMAT",
                message=f"{field_name}不是有效的JSON格式",
                field=field_name
            )
            return False
    
    def validator_base_validate_password_strength(
        self,
        password: str,
        field_name: str,
        result: ValidationResult,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True
    ) -> bool:
        """
        验证密码强度
        [validators][base][validate_password_strength]
        """
        if not password:
            return True
        
        is_valid = True
        
        # 长度检查
        if len(password) < min_length:
            result.add_error(
                code="PASSWORD_TOO_SHORT",
                message=f"{field_name}长度不能少于{min_length}个字符",
                field=field_name
            )
            is_valid = False
        
        # 大写字母检查
        if require_uppercase and not any(c.isupper() for c in password):
            result.add_error(
                code="PASSWORD_MISSING_UPPERCASE",
                message=f"{field_name}必须包含大写字母",
                field=field_name
            )
            is_valid = False
        
        # 小写字母检查
        if require_lowercase and not any(c.islower() for c in password):
            result.add_error(
                code="PASSWORD_MISSING_LOWERCASE",
                message=f"{field_name}必须包含小写字母",
                field=field_name
            )
            is_valid = False
        
        # 数字检查
        if require_digit and not any(c.isdigit() for c in password):
            result.add_error(
                code="PASSWORD_MISSING_DIGIT",
                message=f"{field_name}必须包含数字",
                field=field_name
            )
            is_valid = False
        
        # 特殊字符检查
        if require_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                result.add_error(
                    code="PASSWORD_MISSING_SPECIAL",
                    message=f"{field_name}必须包含特殊字符",
                    field=field_name
                )
                is_valid = False
        
        return is_valid
    
    @abstractmethod
    def validate(self, data: Dict[str, Any], operation: str = "create") -> ValidationResult:
        """
        执行验证
        [validators][base][validate]
        """
        pass