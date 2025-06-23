"""
Voice Timbre Validators
音色管理业务规则验证器 - [validators][voice_timbre]
"""

from typing import Dict, Any, List, Optional
from app.validators.base import ValidatorBase, ValidationResult


class VoiceTimbreValidator(ValidatorBase):
    """
    音色管理业务规则验证器
    [validators][voice_timbre]
    """
    
    def __init__(self):
        """
        初始化音色管理验证器
        [validators][voice_timbre][init]
        """
        super().__init__()
        
        # 音色名称规则
        self.timbre_name_rules = {
            "min_length": 2,
            "max_length": 100,
            "forbidden_names": ["admin", "system", "test", "default"]
        }
        
        # 支持的平台
        self.allowed_platforms = ["volcano", "azure", "openai", "local"]
        
        # 支持的语言
        self.allowed_languages = [
            "zh-CN", "zh-TW", "en-US", "en-GB", "ja-JP", 
            "ko-KR", "fr-FR", "de-DE", "es-ES", "it-IT"
        ]
        
        # 支持的性别
        self.allowed_genders = ["male", "female", "neutral", "child"]
        
        # 支持的年龄范围
        self.allowed_age_ranges = [
            "0-12", "13-17", "18-25", "26-35", "36-45", 
            "46-55", "56-65", "65+", "unknown"
        ]
        
        # 支持的音色风格
        self.allowed_styles = [
            "natural", "professional", "warm", "cool", "energetic", 
            "calm", "cheerful", "serious", "friendly", "authoritative",
            "cute", "mature", "deep", "soft", "clear"
        ]
        
        # 音色状态
        self.allowed_statuses = ["training", "ready", "failed", "deleted"]
        
        # 克隆参数规则
        self.clone_rules = {
            "min_duration": 10.0,     # 最少10秒
            "max_duration": 3600.0,   # 最多1小时
            "max_epochs": 1000,
            "min_batch_size": 1,
            "max_batch_size": 64
        }
        
        # 质量评分范围
        self.quality_score_range = {"min": 0.0, "max": 100.0}
    
    def validate(self, data: Dict[str, Any], operation: str = "create") -> ValidationResult:
        """
        执行音色管理验证
        [validators][voice_timbre][validate]
        """
        result = self.validator_base_create_result()
        
        if operation == "create":
            self._validate_create(data, result)
        elif operation == "clone":
            self._validate_clone(data, result)
        elif operation == "test":
            self._validate_test(data, result)
        elif operation == "update":
            self._validate_update(data, result)
        elif operation == "template_create":
            self._validate_template_create(data, result)
        
        return result
    
    def _validate_create(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音色创建
        [validators][voice_timbre][_validate_create]
        """
        # 验证音色名称
        timbre_name = data.get("timbre_name")
        if not self.validator_base_validate_required(timbre_name, "音色名称", result):
            return
        
        self._validate_timbre_name(timbre_name, result)
        
        # 验证描述
        description = data.get("description")
        if description:
            self.validator_base_validate_length(
                description, "音色描述", max_length=500, result=result
            )
        
        # 验证平台
        platform = data.get("platform", "volcano")
        self.validator_base_validate_enum(
            platform, "平台", self.allowed_platforms, result
        )
        
        # 验证语言
        language = data.get("language", "zh-CN")
        self.validator_base_validate_enum(
            language, "语言", self.allowed_languages, result
        )
        
        # 验证性别
        gender = data.get("gender", "female")
        self.validator_base_validate_enum(
            gender, "性别", self.allowed_genders, result
        )
        
        # 验证年龄范围
        age_range = data.get("age_range", "25-35")
        self.validator_base_validate_enum(
            age_range, "年龄范围", self.allowed_age_ranges, result
        )
        
        # 验证音色风格
        style = data.get("style", "natural")
        self.validator_base_validate_enum(
            style, "音色风格", self.allowed_styles, result
        )
        
        # 验证源文件ID（如果提供）
        source_file_id = data.get("source_file_id")
        if source_file_id:
            if not isinstance(source_file_id, int) or source_file_id <= 0:
                result.add_error(
                    code="INVALID_SOURCE_FILE_ID",
                    message="源文件ID必须是正整数",
                    field="source_file_id"
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
        
        # 验证标签（如果提供）
        tags = data.get("tags", [])
        if tags:
            self._validate_tags(tags, result)
        
        # 业务规则验证
        self._validate_create_business_rules(data, result)
    
    def _validate_clone(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音色克隆
        [validators][voice_timbre][_validate_clone]
        """
        # 验证源文件ID
        source_file_id = data.get("source_file_id")
        if not self.validator_base_validate_required(source_file_id, "源文件ID", result):
            return
        
        if not isinstance(source_file_id, int) or source_file_id <= 0:
            result.add_error(
                code="INVALID_SOURCE_FILE_ID",
                message="源文件ID必须是正整数",
                field="source_file_id"
            )
        
        # 验证音色名称
        timbre_name = data.get("timbre_name")
        if not self.validator_base_validate_required(timbre_name, "音色名称", result):
            return
        
        self._validate_timbre_name(timbre_name, result)
        
        # 验证克隆参数
        clone_params = data.get("clone_params", {})
        if clone_params:
            self._validate_clone_params(clone_params, result)
        
        # 验证源音频时长（如果提供）
        source_duration = data.get("source_duration")
        if source_duration:
            self.validator_base_validate_range(
                source_duration,
                "源音频时长",
                min_value=self.clone_rules["min_duration"],
                max_value=self.clone_rules["max_duration"],
                result=result
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
    
    def _validate_test(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音色测试
        [validators][voice_timbre][_validate_test]
        """
        # 验证音色ID
        timbre_id = data.get("timbre_id")
        if not self.validator_base_validate_required(timbre_id, "音色ID", result):
            return
        
        if not isinstance(timbre_id, int) or timbre_id <= 0:
            result.add_error(
                code="INVALID_TIMBRE_ID",
                message="音色ID必须是正整数",
                field="timbre_id"
            )
        
        # 验证测试文本
        test_text = data.get("test_text")
        if not self.validator_base_validate_required(test_text, "测试文本", result):
            return
        
        self._validate_test_text(test_text, result)
        
        # 验证合成参数
        synthesis_params = data.get("synthesis_params", {})
        if synthesis_params:
            self._validate_synthesis_params(synthesis_params, result)
        
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
    
    def _validate_update(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音色更新
        [validators][voice_timbre][_validate_update]
        """
        # 验证音色ID
        timbre_id = data.get("timbre_id")
        if not self.validator_base_validate_required(timbre_id, "音色ID", result):
            return
        
        if not isinstance(timbre_id, int) or timbre_id <= 0:
            result.add_error(
                code="INVALID_TIMBRE_ID",
                message="音色ID必须是正整数",
                field="timbre_id"
            )
        
        # 验证新名称（如果提供）
        new_name = data.get("new_name")
        if new_name:
            self._validate_timbre_name(new_name, result)
        
        # 验证新描述（如果提供）
        new_description = data.get("new_description")
        if new_description:
            self.validator_base_validate_length(
                new_description, "音色描述", max_length=500, result=result
            )
        
        # 验证新状态（如果提供）
        new_status = data.get("new_status")
        if new_status:
            self.validator_base_validate_enum(
                new_status, "音色状态", self.allowed_statuses, result
            )
        
        # 验证质量评分（如果提供）
        quality_score = data.get("quality_score")
        if quality_score is not None:
            self.validator_base_validate_range(
                quality_score,
                "质量评分",
                min_value=self.quality_score_range["min"],
                max_value=self.quality_score_range["max"],
                result=result
            )
        
        # 验证新标签（如果提供）
        new_tags = data.get("new_tags")
        if new_tags:
            self._validate_tags(new_tags, result)
    
    def _validate_template_create(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音色模板创建
        [validators][voice_timbre][_validate_template_create]
        """
        # 验证模板名称
        template_name = data.get("template_name")
        if not self.validator_base_validate_required(template_name, "模板名称", result):
            return
        
        self.validator_base_validate_length(
            template_name, "模板名称", min_length=2, max_length=100, result=result
        )
        
        # 验证模板描述
        template_description = data.get("template_description")
        if template_description:
            self.validator_base_validate_length(
                template_description, "模板描述", max_length=500, result=result
            )
        
        # 验证关联音色ID
        timbre_id = data.get("timbre_id")
        if not self.validator_base_validate_required(timbre_id, "音色ID", result):
            return
        
        if not isinstance(timbre_id, int) or timbre_id <= 0:
            result.add_error(
                code="INVALID_TIMBRE_ID",
                message="音色ID必须是正整数",
                field="timbre_id"
            )
        
        # 验证克隆参数
        clone_params = data.get("clone_params", {})
        if clone_params:
            self._validate_clone_params(clone_params, result)
        
        # 验证质量要求
        quality_requirements = data.get("quality_requirements", {})
        if quality_requirements:
            self._validate_quality_requirements(quality_requirements, result)
    
    def _validate_timbre_name(self, timbre_name: str, result: ValidationResult):
        """
        验证音色名称
        [validators][voice_timbre][_validate_timbre_name]
        """
        # 长度验证
        self.validator_base_validate_length(
            timbre_name,
            "音色名称",
            min_length=self.timbre_name_rules["min_length"],
            max_length=self.timbre_name_rules["max_length"],
            result=result
        )
        
        # 禁用名称检查
        if timbre_name.lower() in self.timbre_name_rules["forbidden_names"]:
            result.add_error(
                code="FORBIDDEN_TIMBRE_NAME",
                message="该音色名称不可用",
                field="timbre_name"
            )
        
        # 特殊字符检查
        import re
        if not re.match(r'^[\u4e00-\u9fff\w\s\-_()（）]+$', timbre_name):
            result.add_error(
                code="INVALID_TIMBRE_NAME_CHARS",
                message="音色名称只能包含中文、字母、数字、空格和常用符号",
                field="timbre_name"
            )
        
        # 开头结尾空格检查
        if timbre_name != timbre_name.strip():
            result.add_warning(
                code="TIMBRE_NAME_WHITESPACE",
                message="音色名称开头或结尾包含空格",
                field="timbre_name"
            )
    
    def _validate_clone_params(self, clone_params: Dict[str, Any], result: ValidationResult):
        """
        验证克隆参数
        [validators][voice_timbre][_validate_clone_params]
        """
        # 验证训练轮数
        epochs = clone_params.get("epochs")
        if epochs is not None:
            if not isinstance(epochs, int) or epochs <= 0:
                result.add_error(
                    code="INVALID_EPOCHS",
                    message="训练轮数必须是正整数",
                    field="clone_params.epochs"
                )
            elif epochs > self.clone_rules["max_epochs"]:
                result.add_error(
                    code="EPOCHS_TOO_LARGE",
                    message=f"训练轮数不能超过{self.clone_rules['max_epochs']}",
                    field="clone_params.epochs"
                )
        
        # 验证批量大小
        batch_size = clone_params.get("batch_size")
        if batch_size is not None:
            self.validator_base_validate_range(
                batch_size,
                "批量大小",
                min_value=self.clone_rules["min_batch_size"],
                max_value=self.clone_rules["max_batch_size"],
                result=result
            )
        
        # 验证学习率
        learning_rate = clone_params.get("learning_rate")
        if learning_rate is not None:
            if not isinstance(learning_rate, (int, float)) or learning_rate <= 0:
                result.add_error(
                    code="INVALID_LEARNING_RATE",
                    message="学习率必须是正数",
                    field="clone_params.learning_rate"
                )
            elif learning_rate > 1.0:
                result.add_warning(
                    code="HIGH_LEARNING_RATE",
                    message="学习率过高可能影响训练效果",
                    field="clone_params.learning_rate"
                )
        
        # 验证质量阈值
        quality_threshold = clone_params.get("quality_threshold")
        if quality_threshold is not None:
            self.validator_base_validate_range(
                quality_threshold,
                "质量阈值",
                min_value=0.0,
                max_value=1.0,
                result=result
            )
    
    def _validate_test_text(self, test_text: str, result: ValidationResult):
        """
        验证测试文本
        [validators][voice_timbre][_validate_test_text]
        """
        # 长度验证
        self.validator_base_validate_length(
            test_text, "测试文本", min_length=1, max_length=500, result=result
        )
        
        # 内容检查
        if test_text.strip() == "":
            result.add_error(
                code="EMPTY_TEST_TEXT",
                message="测试文本不能为空",
                field="test_text"
            )
        
        # 建议长度检查
        if len(test_text) < 10:
            result.add_warning(
                code="TEST_TEXT_TOO_SHORT",
                message="测试文本过短，建议至少10个字符",
                field="test_text"
            )
        
        # 特殊字符检查
        if any(char in test_text for char in ['<', '>', '{', '}', '[', ']']):
            result.add_warning(
                code="TEST_TEXT_SPECIAL_CHARS",
                message="测试文本包含特殊字符，可能影响合成效果",
                field="test_text"
            )
    
    def _validate_synthesis_params(self, synthesis_params: Dict[str, Any], result: ValidationResult):
        """
        验证合成参数
        [validators][voice_timbre][_validate_synthesis_params]
        """
        # 验证语速
        speed = synthesis_params.get("speed")
        if speed is not None:
            self.validator_base_validate_range(
                speed, "语速", min_value=0.1, max_value=3.0, result=result
            )
        
        # 验证音调
        pitch = synthesis_params.get("pitch")
        if pitch is not None:
            self.validator_base_validate_range(
                pitch, "音调", min_value=0.1, max_value=3.0, result=result
            )
        
        # 验证音量
        volume = synthesis_params.get("volume")
        if volume is not None:
            self.validator_base_validate_range(
                volume, "音量", min_value=0.1, max_value=2.0, result=result
            )
        
        # 验证情感参数
        emotion = synthesis_params.get("emotion")
        if emotion is not None:
            allowed_emotions = [
                "neutral", "happy", "sad", "angry", "excited", 
                "calm", "serious", "friendly", "professional"
            ]
            self.validator_base_validate_enum(
                emotion, "情感", allowed_emotions, result
            )
        
        # 验证停顿时长
        pause_duration = synthesis_params.get("pause_duration")
        if pause_duration is not None:
            self.validator_base_validate_range(
                pause_duration, "停顿时长", min_value=0.0, max_value=5.0, result=result
            )
    
    def _validate_tags(self, tags: List[str], result: ValidationResult):
        """
        验证标签
        [validators][voice_timbre][_validate_tags]
        """
        if not isinstance(tags, list):
            result.add_error(
                code="INVALID_TAGS_FORMAT",
                message="标签必须是列表格式",
                field="tags"
            )
            return
        
        if len(tags) > 10:
            result.add_error(
                code="TOO_MANY_TAGS",
                message="标签数量不能超过10个",
                field="tags"
            )
        
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                result.add_error(
                    code="INVALID_TAG_TYPE",
                    message=f"第{i+1}个标签必须是字符串",
                    field=f"tags[{i}]"
                )
                continue
            
            self.validator_base_validate_length(
                tag, f"标签{i+1}", min_length=1, max_length=50, result=result
            )
            
            # 检查重复标签
            if tags.count(tag) > 1:
                result.add_warning(
                    code="DUPLICATE_TAG",
                    message=f"标签重复: {tag}",
                    field=f"tags[{i}]"
                )
    
    def _validate_quality_requirements(self, requirements: Dict[str, Any], result: ValidationResult):
        """
        验证质量要求
        [validators][voice_timbre][_validate_quality_requirements]
        """
        # 验证最小评分
        min_score = requirements.get("min_score")
        if min_score is not None:
            self.validator_base_validate_range(
                min_score,
                "最小质量评分",
                min_value=0.0,
                max_value=100.0,
                result=result
            )
        
        # 验证最大训练时间
        max_training_time = requirements.get("max_training_time")
        if max_training_time is not None:
            if not isinstance(max_training_time, int) or max_training_time <= 0:
                result.add_error(
                    code="INVALID_MAX_TRAINING_TIME",
                    message="最大训练时间必须是正整数",
                    field="quality_requirements.max_training_time"
                )
        
        # 验证最大重试次数
        max_retries = requirements.get("max_retries")
        if max_retries is not None:
            self.validator_base_validate_range(
                max_retries,
                "最大重试次数",
                min_value=0,
                max_value=10,
                result=result
            )
    
    def _validate_create_business_rules(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证创建业务规则
        [validators][voice_timbre][_validate_create_business_rules]
        """
        platform = data.get("platform", "volcano")
        language = data.get("language", "zh-CN")
        gender = data.get("gender", "female")
        
        # 平台特定验证
        if platform == "volcano":
            # 火山引擎特定规则
            if language not in ["zh-CN", "en-US", "ja-JP"]:
                result.add_warning(
                    code="UNSUPPORTED_LANGUAGE_FOR_PLATFORM",
                    message=f"火山引擎可能不完全支持语言: {language}",
                    field="language"
                )
        
        elif platform == "azure":
            # Azure特定规则
            if gender == "child":
                result.add_warning(
                    code="LIMITED_CHILD_VOICE_SUPPORT",
                    message="Azure对儿童音色支持有限",
                    field="gender"
                )
        
        # 组合检查
        if language == "zh-CN" and gender == "neutral":
            result.add_info(
                code="RARE_COMBINATION",
                message="中性音色在中文语音合成中较少见",
                details={"language": language, "gender": gender}
            )
        
        # 源文件检查
        source_file_id = data.get("source_file_id")
        if source_file_id:
            # 这里可以添加源文件格式、质量检查
            result.add_info(
                code="CLONE_MODE_ENABLED",
                message="已启用音色克隆模式",
                details={"source_file_id": source_file_id}
            )
    
    def validate_clone_progress(self, progress_data: Dict[str, Any]) -> ValidationResult:
        """
        验证克隆进度数据
        [validators][voice_timbre][validate_clone_progress]
        """
        result = self.validator_base_create_result()
        
        # 验证克隆ID
        clone_id = progress_data.get("clone_id")
        if not self.validator_base_validate_required(clone_id, "克隆ID", result):
            return result
        
        if not isinstance(clone_id, int) or clone_id <= 0:
            result.add_error(
                code="INVALID_CLONE_ID",
                message="克隆ID必须是正整数",
                field="clone_id"
            )
        
        # 验证进度值
        progress = progress_data.get("progress")
        if progress is not None:
            self.validator_base_validate_range(
                progress, "进度", min_value=0, max_value=100, result=result
            )
        
        # 验证状态
        status = progress_data.get("status")
        if status:
            allowed_clone_statuses = ["pending", "training", "completed", "failed"]
            self.validator_base_validate_enum(
                status, "克隆状态", allowed_clone_statuses, result
            )
        
        # 验证错误信息
        error_message = progress_data.get("error_message")
        if error_message:
            self.validator_base_validate_length(
                error_message, "错误信息", max_length=1000, result=result
            )
        
        return result