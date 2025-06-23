"""
File Storage Validators
文件存储业务规则验证器 - [validators][file_storage]
"""

from typing import Dict, Any, List, Optional
from app.validators.base import ValidatorBase, ValidationResult


class FileStorageValidator(ValidatorBase):
    """
    文件存储业务规则验证器
    [validators][file_storage]
    """
    
    def __init__(self):
        """
        初始化文件存储验证器
        [validators][file_storage][init]
        """
        super().__init__()
        
        # 文件大小限制（字节）
        self.file_size_limits = {
            "image": 10 * 1024 * 1024,      # 10MB
            "audio": 100 * 1024 * 1024,     # 100MB
            "video": 500 * 1024 * 1024,     # 500MB
            "document": 50 * 1024 * 1024,   # 50MB
            "default": 20 * 1024 * 1024     # 20MB
        }
        
        # 允许的文件类型
        self.allowed_file_types = {
            "image": [
                "image/jpeg", "image/jpg", "image/png", "image/gif", 
                "image/webp", "image/svg+xml", "image/bmp"
            ],
            "audio": [
                "audio/mpeg", "audio/mp3", "audio/wav", "audio/flac", 
                "audio/aac", "audio/ogg", "audio/m4a", "audio/wma"
            ],
            "video": [
                "video/mp4", "video/avi", "video/mov", "video/wmv", 
                "video/flv", "video/webm", "video/mkv", "video/m4v"
            ],
            "document": [
                "application/pdf", "application/msword", 
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "text/plain", "text/csv"
            ]
        }
        
        # 文件名规则
        self.filename_rules = {
            "max_length": 255,
            "min_length": 1,
            "forbidden_chars": ["<", ">", ":", '"', "|", "?", "*", "\\", "/"],
            "forbidden_names": ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "LPT1", "LPT2"]
        }
        
        # 文件分类
        self.allowed_categories = [
            "general", "avatar", "document", "media", "voice_sample", 
            "audio_output", "temp", "backup", "upload"
        ]
    
    def validate(self, data: Dict[str, Any], operation: str = "upload") -> ValidationResult:
        """
        执行文件存储验证
        [validators][file_storage][validate]
        """
        result = self.validator_base_create_result()
        
        if operation == "upload":
            self._validate_upload(data, result)
        elif operation == "update":
            self._validate_update(data, result)
        elif operation == "delete":
            self._validate_delete(data, result)
        elif operation == "move":
            self._validate_move(data, result)
        
        return result
    
    def _validate_upload(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证文件上传
        [validators][file_storage][_validate_upload]
        """
        # 验证文件名
        filename = data.get("filename")
        if not self.validator_base_validate_required(filename, "文件名", result):
            return
        
        self._validate_filename(filename, result)
        
        # 验证文件大小
        file_size = data.get("file_size")
        if not self.validator_base_validate_required(file_size, "文件大小", result):
            return
        
        if not isinstance(file_size, int) or file_size <= 0:
            result.add_error(
                code="INVALID_FILE_SIZE",
                message="文件大小必须是正整数",
                field="file_size"
            )
            return
        
        # 验证文件类型
        file_type = data.get("file_type")
        if not self.validator_base_validate_required(file_type, "文件类型", result):
            return
        
        self._validate_file_type_and_size(file_type, file_size, result)
        
        # 验证文件分类
        category = data.get("category", "general")
        self.validator_base_validate_enum(
            category, "文件分类", self.allowed_categories, result
        )
        
        # 验证文件描述
        description = data.get("description")
        if description:
            self.validator_base_validate_length(
                description, "文件描述", max_length=500, result=result
            )
        
        # 验证用户ID
        user_id = data.get("user_id")
        if not self.validator_base_validate_required(user_id, "用户ID", result):
            return
        
        if not isinstance(user_id, int) or user_id <= 0:
            result.add_error(
                code="INVALID_USER_ID",
                message="用户ID必须是正整数",
                field="user_id"
            )
        
        # 业务规则验证
        self._validate_upload_business_rules(data, result)
    
    def _validate_update(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证文件信息更新
        [validators][file_storage][_validate_update]
        """
        # 验证文件ID
        file_id = data.get("file_id")
        if not self.validator_base_validate_required(file_id, "文件ID", result):
            return
        
        if not isinstance(file_id, int) or file_id <= 0:
            result.add_error(
                code="INVALID_FILE_ID",
                message="文件ID必须是正整数",
                field="file_id"
            )
        
        # 验证新文件名（如果提供）
        new_filename = data.get("new_filename")
        if new_filename:
            self._validate_filename(new_filename, result)
        
        # 验证新描述（如果提供）
        new_description = data.get("new_description")
        if new_description:
            self.validator_base_validate_length(
                new_description, "文件描述", max_length=500, result=result
            )
        
        # 验证新分类（如果提供）
        new_category = data.get("new_category")
        if new_category:
            self.validator_base_validate_enum(
                new_category, "文件分类", self.allowed_categories, result
            )
    
    def _validate_delete(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证文件删除
        [validators][file_storage][_validate_delete]
        """
        # 验证文件ID
        file_id = data.get("file_id")
        if not self.validator_base_validate_required(file_id, "文件ID", result):
            return
        
        if not isinstance(file_id, int) or file_id <= 0:
            result.add_error(
                code="INVALID_FILE_ID",
                message="文件ID必须是正整数",
                field="file_id"
            )
        
        # 验证用户ID
        user_id = data.get("user_id")
        if not self.validator_base_validate_required(user_id, "用户ID", result):
            return
        
        if not isinstance(user_id, int) or user_id <= 0:
            result.add_error(
                code="INVALID_USER_ID",
                message="用户ID必须是正整数",
                field="user_id"
            )
        
        # 验证删除原因（如果提供）
        delete_reason = data.get("delete_reason")
        if delete_reason:
            self.validator_base_validate_length(
                delete_reason, "删除原因", max_length=200, result=result
            )
    
    def _validate_move(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证文件移动
        [validators][file_storage][_validate_move]
        """
        # 验证文件ID
        file_id = data.get("file_id")
        if not self.validator_base_validate_required(file_id, "文件ID", result):
            return
        
        if not isinstance(file_id, int) or file_id <= 0:
            result.add_error(
                code="INVALID_FILE_ID",
                message="文件ID必须是正整数",
                field="file_id"
            )
        
        # 验证目标分类
        target_category = data.get("target_category")
        if not self.validator_base_validate_required(target_category, "目标分类", result):
            return
        
        self.validator_base_validate_enum(
            target_category, "目标分类", self.allowed_categories, result
        )
    
    def _validate_filename(self, filename: str, result: ValidationResult):
        """
        验证文件名
        [validators][file_storage][_validate_filename]
        """
        # 长度验证
        self.validator_base_validate_length(
            filename,
            "文件名",
            min_length=self.filename_rules["min_length"],
            max_length=self.filename_rules["max_length"],
            result=result
        )
        
        # 非法字符验证
        forbidden_chars = self.filename_rules["forbidden_chars"]
        for char in forbidden_chars:
            if char in filename:
                result.add_error(
                    code="INVALID_FILENAME_CHARS",
                    message=f"文件名不能包含字符: {char}",
                    field="filename"
                )
                break
        
        # 非法文件名验证
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in self.filename_rules["forbidden_names"]:
            result.add_error(
                code="FORBIDDEN_FILENAME",
                message="文件名不可用",
                field="filename"
            )
        
        # 文件扩展名验证
        if '.' not in filename:
            result.add_warning(
                code="NO_FILE_EXTENSION",
                message="文件名没有扩展名",
                field="filename"
            )
        
        # 隐藏文件检查
        if filename.startswith('.'):
            result.add_warning(
                code="HIDDEN_FILE",
                message="文件名以点开头，可能是隐藏文件",
                field="filename"
            )
        
        # 连续点检查
        if '..' in filename:
            result.add_error(
                code="INVALID_FILENAME_DOTS",
                message="文件名不能包含连续的点",
                field="filename"
            )
    
    def _validate_file_type_and_size(self, file_type: str, file_size: int, result: ValidationResult):
        """
        验证文件类型和大小
        [validators][file_storage][_validate_file_type_and_size]
        """
        # 确定文件主类型
        main_type = self._get_file_main_type(file_type)
        
        # 验证文件类型是否允许
        allowed_types = []
        for category, types in self.allowed_file_types.items():
            allowed_types.extend(types)
        
        if file_type not in allowed_types:
            result.add_error(
                code="UNSUPPORTED_FILE_TYPE",
                message=f"不支持的文件类型: {file_type}",
                field="file_type",
                details={"file_type": file_type}
            )
            return
        
        # 验证文件大小限制
        size_limit = self.file_size_limits.get(main_type, self.file_size_limits["default"])
        
        if file_size > size_limit:
            size_mb = size_limit / (1024 * 1024)
            result.add_error(
                code="FILE_SIZE_EXCEEDED",
                message=f"{main_type}文件大小不能超过{size_mb:.1f}MB",
                field="file_size",
                details={
                    "max_size": size_limit,
                    "actual_size": file_size,
                    "file_type": main_type
                }
            )
        
        # 最小文件大小检查
        min_size = 1  # 1字节
        if file_size < min_size:
            result.add_error(
                code="FILE_SIZE_TOO_SMALL",
                message="文件大小不能为0",
                field="file_size"
            )
    
    def _get_file_main_type(self, file_type: str) -> str:
        """
        获取文件主类型
        [validators][file_storage][_get_file_main_type]
        """
        if file_type.startswith("image/"):
            return "image"
        elif file_type.startswith("audio/"):
            return "audio"
        elif file_type.startswith("video/"):
            return "video"
        elif file_type.startswith("application/") or file_type.startswith("text/"):
            return "document"
        else:
            return "default"
    
    def _validate_upload_business_rules(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证上传业务规则
        [validators][file_storage][_validate_upload_business_rules]
        """
        file_type = data.get("file_type")
        category = data.get("category", "general")
        file_size = data.get("file_size", 0)
        
        # 特定分类的文件类型检查
        if category == "avatar":
            if not file_type.startswith("image/"):
                result.add_error(
                    code="INVALID_AVATAR_TYPE",
                    message="头像文件必须是图片格式",
                    field="file_type"
                )
            
            # 头像大小限制更严格
            avatar_size_limit = 2 * 1024 * 1024  # 2MB
            if file_size > avatar_size_limit:
                result.add_error(
                    code="AVATAR_SIZE_EXCEEDED",
                    message="头像文件大小不能超过2MB",
                    field="file_size"
                )
        
        elif category == "voice_sample":
            if not file_type.startswith("audio/"):
                result.add_error(
                    code="INVALID_VOICE_SAMPLE_TYPE",
                    message="语音样本必须是音频格式",
                    field="file_type"
                )
        
        # 危险文件类型检查
        dangerous_types = [
            "application/x-executable", "application/x-msdownload",
            "application/x-msdos-program", "application/x-msi",
            "application/x-bat", "application/x-sh"
        ]
        
        if file_type in dangerous_types:
            result.add_error(
                code="DANGEROUS_FILE_TYPE",
                message="不允许上传可执行文件",
                field="file_type"
            )
        
        # 文件名与类型一致性检查
        filename = data.get("filename", "")
        if filename and '.' in filename:
            ext = filename.split('.')[-1].lower()
            expected_exts = self._get_expected_extensions(file_type)
            
            if expected_exts and ext not in expected_exts:
                result.add_warning(
                    code="FILENAME_TYPE_MISMATCH",
                    message="文件名扩展名与文件类型不匹配",
                    field="filename",
                    details={
                        "filename_ext": ext,
                        "file_type": file_type,
                        "expected_exts": expected_exts
                    }
                )
    
    def _get_expected_extensions(self, file_type: str) -> List[str]:
        """
        根据文件类型获取期望的扩展名
        [validators][file_storage][_get_expected_extensions]
        """
        type_ext_map = {
            "image/jpeg": ["jpg", "jpeg"],
            "image/png": ["png"],
            "image/gif": ["gif"],
            "image/webp": ["webp"],
            "audio/mpeg": ["mp3"],
            "audio/wav": ["wav"],
            "audio/flac": ["flac"],
            "video/mp4": ["mp4"],
            "video/avi": ["avi"],
            "application/pdf": ["pdf"],
            "text/plain": ["txt"],
            "text/csv": ["csv"]
        }
        
        return type_ext_map.get(file_type, [])
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> ValidationResult:
        """
        验证文件元数据
        [validators][file_storage][validate_metadata]
        """
        result = self.validator_base_create_result()
        
        # 验证元数据键
        meta_key = metadata.get("meta_key")
        if not self.validator_base_validate_required(meta_key, "元数据键", result):
            return result
        
        self.validator_base_validate_length(
            meta_key, "元数据键", min_length=1, max_length=100, result=result
        )
        
        # 验证元数据值
        meta_value = metadata.get("meta_value")
        if meta_value is not None:
            # 如果是字符串，检查长度
            if isinstance(meta_value, str):
                if len(meta_value) > 10000:  # 10KB限制
                    result.add_error(
                        code="METADATA_VALUE_TOO_LARGE",
                        message="元数据值过大",
                        field="meta_value"
                    )
            
            # 如果是JSON，验证格式
            meta_type = metadata.get("meta_type", "string")
            if meta_type == "json" and isinstance(meta_value, str):
                self.validator_base_validate_json(meta_value, "元数据值", result)
        
        return result
    
    def validate_storage_quota(self, user_storage_data: Dict[str, Any]) -> ValidationResult:
        """
        验证存储配额
        [validators][file_storage][validate_storage_quota]
        """
        result = self.validator_base_create_result()
        
        # 获取用户存储信息
        used_storage = user_storage_data.get("used_storage", 0)
        storage_quota = user_storage_data.get("storage_quota", 0)
        new_file_size = user_storage_data.get("new_file_size", 0)
        
        # 检查存储配额
        if storage_quota > 0:
            if used_storage + new_file_size > storage_quota:
                remaining = storage_quota - used_storage
                result.add_error(
                    code="STORAGE_QUOTA_EXCEEDED",
                    message=f"存储空间不足，剩余{remaining / (1024*1024):.1f}MB",
                    field="file_size",
                    details={
                        "used_storage": used_storage,
                        "storage_quota": storage_quota,
                        "new_file_size": new_file_size,
                        "remaining": remaining
                    }
                )
        
        # 检查文件数量限制
        file_count = user_storage_data.get("file_count", 0)
        max_files = user_storage_data.get("max_files", 0)
        
        if max_files > 0 and file_count >= max_files:
            result.add_error(
                code="FILE_COUNT_LIMIT_EXCEEDED",
                message=f"文件数量已达上限({max_files}个)",
                field="file_count",
                details={
                    "file_count": file_count,
                    "max_files": max_files
                }
            )
        
        return result