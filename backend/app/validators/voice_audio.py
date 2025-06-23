"""
Voice Audio Validators
音频管理业务规则验证器 - [validators][voice_audio]
"""

from typing import Dict, Any, List, Optional
from app.validators.base import ValidatorBase, ValidationResult


class VoiceAudioValidator(ValidatorBase):
    """
    音频管理业务规则验证器
    [validators][voice_audio]
    """
    
    def __init__(self):
        """
        初始化音频管理验证器
        [validators][voice_audio][init]
        """
        super().__init__()
        
        # 音频名称规则
        self.audio_name_rules = {
            "min_length": 1,
            "max_length": 200
        }
        
        # 支持的音频格式
        self.allowed_formats = ["mp3", "wav", "flac", "aac", "ogg", "m4a"]
        
        # 支持的采样率
        self.allowed_sample_rates = [8000, 16000, 22050, 44100, 48000, 96000]
        
        # 支持的音频平台
        self.allowed_platforms = ["volcano", "azure", "openai", "local"]
        
        # 音频状态
        self.allowed_statuses = ["pending", "processing", "completed", "failed", "deleted"]
        
        # 合成参数规则
        self.synthesis_rules = {
            "max_text_length": 10000,    # 最大文本长度
            "min_text_length": 1,        # 最小文本长度
            "max_speed": 3.0,            # 最大语速
            "min_speed": 0.1,            # 最小语速
            "max_pitch": 3.0,            # 最大音调
            "min_pitch": 0.1,            # 最小音调
            "max_volume": 2.0,           # 最大音量
            "min_volume": 0.1            # 最小音量
        }
        
        # 音频处理规则
        self.processing_rules = {
            "max_duration": 7200.0,      # 最大时长2小时
            "min_duration": 0.1,         # 最小时长0.1秒
            "max_merge_files": 20,       # 最大合并文件数
            "min_merge_files": 2         # 最小合并文件数
        }
        
        # 分析类型
        self.allowed_analyse_types = [
            "quality", "emotion", "speech_rate", "volume", "clarity", 
            "noise", "silence", "pitch", "energy", "spectral"
        ]
        
        # 支持的处理类型
        self.allowed_process_types = [
            "denoise", "enhance", "normalize", "fade_in", "fade_out", 
            "trim", "speed_change", "pitch_shift", "volume_adjust", "compress"
        ]
    
    def validate(self, data: Dict[str, Any], operation: str = "create") -> ValidationResult:
        """
        执行音频管理验证
        [validators][voice_audio][validate]
        """
        result = self.validator_base_create_result()
        
        if operation == "synthesize":
            self._validate_synthesize(data, result)
        elif operation == "batch_synthesize":
            self._validate_batch_synthesize(data, result)
        elif operation == "process":
            self._validate_process(data, result)
        elif operation == "merge":
            self._validate_merge(data, result)
        elif operation == "analyse":
            self._validate_analyse(data, result)
        elif operation == "update":
            self._validate_update(data, result)
        elif operation == "template_create":
            self._validate_template_create(data, result)
        
        return result
    
    def _validate_synthesize(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音频合成
        [validators][voice_audio][_validate_synthesize]
        """
        # 验证源文本
        source_text = data.get("source_text")
        if not self.validator_base_validate_required(source_text, "源文本", result):
            return
        
        self._validate_synthesis_text(source_text, result)
        
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
        
        # 验证合成参数
        synthesis_params = data.get("synthesis_params", {})
        if synthesis_params:
            self._validate_synthesis_params(synthesis_params, result)
        
        # 验证输出格式
        output_format = data.get("output_format", "mp3")
        self.validator_base_validate_enum(
            output_format, "输出格式", self.allowed_formats, result
        )
        
        # 验证采样率
        sample_rate = data.get("sample_rate", 44100)
        self.validator_base_validate_enum(
            sample_rate, "采样率", self.allowed_sample_rates, result
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
        self._validate_synthesis_business_rules(data, result)
    
    def _validate_batch_synthesize(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证批量音频合成
        [validators][voice_audio][_validate_batch_synthesize]
        """
        # 验证文本列表
        text_list = data.get("text_list")
        if not self.validator_base_validate_required(text_list, "文本列表", result):
            return
        
        if not isinstance(text_list, list):
            result.add_error(
                code="INVALID_TEXT_LIST_FORMAT",
                message="文本列表必须是数组格式",
                field="text_list"
            )
            return
        
        if len(text_list) == 0:
            result.add_error(
                code="EMPTY_TEXT_LIST",
                message="文本列表不能为空",
                field="text_list"
            )
            return
        
        if len(text_list) > 50:
            result.add_error(
                code="TOO_MANY_TEXTS",
                message="批量合成文本数量不能超过50个",
                field="text_list"
            )
        
        # 验证每个文本
        for i, text in enumerate(text_list):
            if not isinstance(text, str):
                result.add_error(
                    code="INVALID_TEXT_TYPE",
                    message=f"第{i+1}个文本必须是字符串",
                    field=f"text_list[{i}]"
                )
                continue
            
            if not text.strip():
                result.add_error(
                    code="EMPTY_TEXT_ITEM",
                    message=f"第{i+1}个文本不能为空",
                    field=f"text_list[{i}]"
                )
                continue
            
            if len(text) > self.synthesis_rules["max_text_length"]:
                result.add_error(
                    code="TEXT_TOO_LONG",
                    message=f"第{i+1}个文本长度超过限制",
                    field=f"text_list[{i}]"
                )
        
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
        
        # 验证公共参数
        common_params = data.get("common_params", {})
        if common_params:
            self._validate_synthesis_params(common_params, result)
        
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
    
    def _validate_process(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音频处理
        [validators][voice_audio][_validate_process]
        """
        # 验证音频ID
        audio_id = data.get("audio_id")
        if not self.validator_base_validate_required(audio_id, "音频ID", result):
            return
        
        if not isinstance(audio_id, int) or audio_id <= 0:
            result.add_error(
                code="INVALID_AUDIO_ID",
                message="音频ID必须是正整数",
                field="audio_id"
            )
        
        # 验证处理类型
        process_type = data.get("process_type")
        if not self.validator_base_validate_required(process_type, "处理类型", result):
            return
        
        self.validator_base_validate_enum(
            process_type, "处理类型", self.allowed_process_types, result
        )
        
        # 验证处理参数
        process_params = data.get("process_params", {})
        if process_params:
            self._validate_process_params(process_type, process_params, result)
        
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
    
    def _validate_merge(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音频合并
        [validators][voice_audio][_validate_merge]
        """
        # 验证音频ID列表
        audio_ids = data.get("audio_ids")
        if not self.validator_base_validate_required(audio_ids, "音频ID列表", result):
            return
        
        if not isinstance(audio_ids, list):
            result.add_error(
                code="INVALID_AUDIO_IDS_FORMAT",
                message="音频ID列表必须是数组格式",
                field="audio_ids"
            )
            return
        
        # 验证数量
        if len(audio_ids) < self.processing_rules["min_merge_files"]:
            result.add_error(
                code="TOO_FEW_MERGE_FILES",
                message=f"至少需要{self.processing_rules['min_merge_files']}个音频文件",
                field="audio_ids"
            )
        
        if len(audio_ids) > self.processing_rules["max_merge_files"]:
            result.add_error(
                code="TOO_MANY_MERGE_FILES",
                message=f"合并音频数量不能超过{self.processing_rules['max_merge_files']}个",
                field="audio_ids"
            )
        
        # 验证每个音频ID
        for i, audio_id in enumerate(audio_ids):
            if not isinstance(audio_id, int) or audio_id <= 0:
                result.add_error(
                    code="INVALID_AUDIO_ID",
                    message=f"第{i+1}个音频ID必须是正整数",
                    field=f"audio_ids[{i}]"
                )
        
        # 检查重复ID
        if len(audio_ids) != len(set(audio_ids)):
            result.add_error(
                code="DUPLICATE_AUDIO_IDS",
                message="音频ID列表包含重复项",
                field="audio_ids"
            )
        
        # 验证输出名称
        output_name = data.get("output_name")
        if not self.validator_base_validate_required(output_name, "输出名称", result):
            return
        
        self.validator_base_validate_length(
            output_name,
            "输出名称",
            min_length=self.audio_name_rules["min_length"],
            max_length=self.audio_name_rules["max_length"],
            result=result
        )
        
        # 验证合并参数
        merge_params = data.get("merge_params", {})
        if merge_params:
            self._validate_merge_params(merge_params, result)
        
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
    
    def _validate_analyse(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音频分析
        [validators][voice_audio][_validate_analyse]
        """
        # 验证音频ID
        audio_id = data.get("audio_id")
        if not self.validator_base_validate_required(audio_id, "音频ID", result):
            return
        
        if not isinstance(audio_id, int) or audio_id <= 0:
            result.add_error(
                code="INVALID_AUDIO_ID",
                message="音频ID必须是正整数",
                field="audio_id"
            )
        
        # 验证分析类型
        analyse_type = data.get("analyse_type")
        if not self.validator_base_validate_required(analyse_type, "分析类型", result):
            return
        
        self.validator_base_validate_enum(
            analyse_type, "分析类型", self.allowed_analyse_types, result
        )
        
        # 验证自定义参数
        custom_params = data.get("custom_params", {})
        if custom_params:
            self._validate_analyse_params(analyse_type, custom_params, result)
        
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
        验证音频更新
        [validators][voice_audio][_validate_update]
        """
        # 验证音频ID
        audio_id = data.get("audio_id")
        if not self.validator_base_validate_required(audio_id, "音频ID", result):
            return
        
        if not isinstance(audio_id, int) or audio_id <= 0:
            result.add_error(
                code="INVALID_AUDIO_ID",
                message="音频ID必须是正整数",
                field="audio_id"
            )
        
        # 验证新名称（如果提供）
        new_name = data.get("new_name")
        if new_name:
            self.validator_base_validate_length(
                new_name,
                "音频名称",
                min_length=self.audio_name_rules["min_length"],
                max_length=self.audio_name_rules["max_length"],
                result=result
            )
        
        # 验证新描述（如果提供）
        new_description = data.get("new_description")
        if new_description:
            self.validator_base_validate_length(
                new_description, "音频描述", max_length=500, result=result
            )
        
        # 验证新状态（如果提供）
        new_status = data.get("new_status")
        if new_status:
            self.validator_base_validate_enum(
                new_status, "音频状态", self.allowed_statuses, result
            )
        
        # 验证新标签（如果提供）
        new_tags = data.get("new_tags")
        if new_tags:
            self._validate_tags(new_tags, result)
    
    def _validate_template_create(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证音频模板创建
        [validators][voice_audio][_validate_template_create]
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
        
        # 验证模板类型
        template_type = data.get("template_type", "synthesis")
        allowed_template_types = ["synthesis", "processing", "analysis"]
        self.validator_base_validate_enum(
            template_type, "模板类型", allowed_template_types, result
        )
        
        # 验证关联音色ID
        timbre_id = data.get("timbre_id")
        if timbre_id:
            if not isinstance(timbre_id, int) or timbre_id <= 0:
                result.add_error(
                    code="INVALID_TIMBRE_ID",
                    message="音色ID必须是正整数",
                    field="timbre_id"
                )
        
        # 验证合成参数
        synthesis_params = data.get("synthesis_params", {})
        if synthesis_params:
            self._validate_synthesis_params(synthesis_params, result)
    
    def _validate_synthesis_text(self, text: str, result: ValidationResult):
        """
        验证合成文本
        [validators][voice_audio][_validate_synthesis_text]
        """
        # 长度验证
        self.validator_base_validate_length(
            text,
            "源文本",
            min_length=self.synthesis_rules["min_text_length"],
            max_length=self.synthesis_rules["max_text_length"],
            result=result
        )
        
        # 内容检查
        if text.strip() == "":
            result.add_error(
                code="EMPTY_SYNTHESIS_TEXT",
                message="合成文本不能为空",
                field="source_text"
            )
        
        # 字符统计
        char_count = len(text.replace(' ', ''))
        word_count = len(text.split())
        
        result.add_info(
            code="TEXT_STATS",
            message=f"文本统计: {word_count}词, {char_count}字符",
            details={
                "word_count": word_count,
                "character_count": char_count,
                "estimated_duration": char_count * 0.15  # 估算时长（秒）
            }
        )
        
        # 特殊字符检查
        special_chars = ['<', '>', '{', '}', '[', ']', '|', '\\']
        if any(char in text for char in special_chars):
            result.add_warning(
                code="SYNTHESIS_TEXT_SPECIAL_CHARS",
                message="文本包含特殊字符，可能影响合成效果",
                field="source_text"
            )
    
    def _validate_synthesis_params(self, params: Dict[str, Any], result: ValidationResult):
        """
        验证合成参数
        [validators][voice_audio][_validate_synthesis_params]
        """
        # 验证语速
        speed = params.get("speed")
        if speed is not None:
            self.validator_base_validate_range(
                speed,
                "语速",
                min_value=self.synthesis_rules["min_speed"],
                max_value=self.synthesis_rules["max_speed"],
                result=result
            )
        
        # 验证音调
        pitch = params.get("pitch")
        if pitch is not None:
            self.validator_base_validate_range(
                pitch,
                "音调",
                min_value=self.synthesis_rules["min_pitch"],
                max_value=self.synthesis_rules["max_pitch"],
                result=result
            )
        
        # 验证音量
        volume = params.get("volume")
        if volume is not None:
            self.validator_base_validate_range(
                volume,
                "音量",
                min_value=self.synthesis_rules["min_volume"],
                max_value=self.synthesis_rules["max_volume"],
                result=result
            )
        
        # 验证情感参数
        emotion = params.get("emotion")
        if emotion is not None:
            allowed_emotions = [
                "neutral", "happy", "sad", "angry", "excited", "calm", 
                "serious", "friendly", "professional", "gentle"
            ]
            self.validator_base_validate_enum(
                emotion, "情感", allowed_emotions, result
            )
        
        # 验证停顿参数
        pause_time = params.get("pause_time")
        if pause_time is not None:
            self.validator_base_validate_range(
                pause_time, "停顿时间", min_value=0.0, max_value=10.0, result=result
            )
    
    def _validate_process_params(self, process_type: str, params: Dict[str, Any], result: ValidationResult):
        """
        验证处理参数
        [validators][voice_audio][_validate_process_params]
        """
        if process_type == "denoise":
            # 降噪参数
            noise_level = params.get("noise_level")
            if noise_level is not None:
                self.validator_base_validate_range(
                    noise_level, "噪声级别", min_value=0.0, max_value=1.0, result=result
                )
        
        elif process_type == "normalize":
            # 归一化参数
            target_level = params.get("target_level")
            if target_level is not None:
                self.validator_base_validate_range(
                    target_level, "目标音量", min_value=-60.0, max_value=0.0, result=result
                )
        
        elif process_type == "speed_change":
            # 变速参数
            speed_factor = params.get("speed_factor")
            if speed_factor is not None:
                self.validator_base_validate_range(
                    speed_factor, "变速倍数", min_value=0.1, max_value=3.0, result=result
                )
        
        elif process_type == "pitch_shift":
            # 变调参数
            semitones = params.get("semitones")
            if semitones is not None:
                self.validator_base_validate_range(
                    semitones, "半音数", min_value=-12.0, max_value=12.0, result=result
                )
        
        elif process_type in ["fade_in", "fade_out"]:
            # 淡入淡出参数
            fade_duration = params.get("fade_duration")
            if fade_duration is not None:
                self.validator_base_validate_range(
                    fade_duration, "淡化时长", min_value=0.1, max_value=10.0, result=result
                )
        
        elif process_type == "trim":
            # 裁剪参数
            start_time = params.get("start_time")
            end_time = params.get("end_time")
            
            if start_time is not None:
                self.validator_base_validate_range(
                    start_time, "开始时间", min_value=0.0, result=result
                )
            
            if end_time is not None:
                self.validator_base_validate_range(
                    end_time, "结束时间", min_value=0.0, result=result
                )
            
            if start_time is not None and end_time is not None:
                if start_time >= end_time:
                    result.add_error(
                        code="INVALID_TRIM_RANGE",
                        message="开始时间必须小于结束时间",
                        field="process_params"
                    )
    
    def _validate_merge_params(self, params: Dict[str, Any], result: ValidationResult):
        """
        验证合并参数
        [validators][voice_audio][_validate_merge_params]
        """
        # 验证输出格式
        output_format = params.get("output_format", "mp3")
        self.validator_base_validate_enum(
            output_format, "输出格式", self.allowed_formats, result
        )
        
        # 验证间隔时间
        gap_duration = params.get("gap_duration")
        if gap_duration is not None:
            self.validator_base_validate_range(
                gap_duration, "间隔时间", min_value=0.0, max_value=10.0, result=result
            )
        
        # 验证音量调整
        volume_adjust = params.get("volume_adjust")
        if volume_adjust is not None:
            self.validator_base_validate_range(
                volume_adjust, "音量调整", min_value=0.1, max_value=2.0, result=result
            )
        
        # 验证交叉淡化
        crossfade_duration = params.get("crossfade_duration")
        if crossfade_duration is not None:
            self.validator_base_validate_range(
                crossfade_duration, "交叉淡化时长", min_value=0.0, max_value=5.0, result=result
            )
    
    def _validate_analyse_params(self, analyse_type: str, params: Dict[str, Any], result: ValidationResult):
        """
        验证分析参数
        [validators][voice_audio][_validate_analyse_params]
        """
        if analyse_type == "quality":
            # 质量分析参数
            quality_metrics = params.get("metrics", [])
            allowed_metrics = ["snr", "thd", "clarity", "naturalness"]
            
            for metric in quality_metrics:
                if metric not in allowed_metrics:
                    result.add_error(
                        code="INVALID_QUALITY_METRIC",
                        message=f"不支持的质量指标: {metric}",
                        field="custom_params.metrics"
                    )
        
        elif analyse_type == "emotion":
            # 情感分析参数
            granularity = params.get("granularity", "global")
            allowed_granularity = ["global", "segment", "frame"]
            
            self.validator_base_validate_enum(
                granularity, "分析粒度", allowed_granularity, result
            )
        
        elif analyse_type == "speech_rate":
            # 语速分析参数
            window_size = params.get("window_size")
            if window_size is not None:
                self.validator_base_validate_range(
                    window_size, "窗口大小", min_value=0.1, max_value=10.0, result=result
                )
    
    def _validate_tags(self, tags: List[str], result: ValidationResult):
        """
        验证标签
        [validators][voice_audio][_validate_tags]
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
    
    def _validate_synthesis_business_rules(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证合成业务规则
        [validators][voice_audio][_validate_synthesis_business_rules]
        """
        source_text = data.get("source_text", "")
        synthesis_params = data.get("synthesis_params", {})
        
        # 文本长度与质量建议
        text_length = len(source_text)
        
        if text_length > 5000:
            result.add_warning(
                code="LONG_TEXT_SYNTHESIS",
                message="长文本合成可能需要较长时间",
                field="source_text"
            )
        
        # 参数组合检查
        speed = synthesis_params.get("speed", 1.0)
        pitch = synthesis_params.get("pitch", 1.0)
        
        if speed > 2.0 and pitch > 1.5:
            result.add_warning(
                code="EXTREME_PARAM_COMBINATION",
                message="极端的语速和音调组合可能影响音质",
                field="synthesis_params"
            )
        
        # 平台特定检查
        # 这里可以根据不同平台添加特定的业务规则验证
        result.add_info(
            code="SYNTHESIS_ESTIMATE",
            message=f"预计合成时长: {text_length * 0.15:.1f}秒",
            details={"text_length": text_length}
        )
    
    def validate_audio_metadata(self, metadata: Dict[str, Any]) -> ValidationResult:
        """
        验证音频元数据
        [validators][voice_audio][validate_audio_metadata]
        """
        result = self.validator_base_create_result()
        
        # 验证时长
        duration = metadata.get("duration")
        if duration is not None:
            self.validator_base_validate_range(
                duration,
                "音频时长",
                min_value=self.processing_rules["min_duration"],
                max_value=self.processing_rules["max_duration"],
                result=result
            )
        
        # 验证比特率
        bitrate = metadata.get("bitrate")
        if bitrate is not None:
            if not isinstance(bitrate, int) or bitrate <= 0:
                result.add_error(
                    code="INVALID_BITRATE",
                    message="比特率必须是正整数",
                    field="bitrate"
                )
        
        # 验证声道数
        channels = metadata.get("channels")
        if channels is not None:
            if channels not in [1, 2]:
                result.add_error(
                    code="INVALID_CHANNELS",
                    message="音频声道数只能是1（单声道）或2（立体声）",
                    field="channels"
                )
        
        return result