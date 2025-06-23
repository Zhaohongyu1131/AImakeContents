"""
Text Content Validators
文本内容业务规则验证器 - [validators][text_content]
"""

from typing import Dict, Any, List, Optional
from app.validators.base import ValidatorBase, ValidationResult


class TextContentValidator(ValidatorBase):
    """
    文本内容业务规则验证器
    [validators][text_content]
    """
    
    def __init__(self):
        """
        初始化文本内容验证器
        [validators][text_content][init]
        """
        super().__init__()
        
        # 文本内容规则
        self.content_rules = {
            "max_length": 50000,        # 50k字符
            "min_length": 1,
            "max_title_length": 200,
            "min_title_length": 1
        }
        
        # 允许的文本类型
        self.allowed_text_types = [
            "article", "story", "poem", "script", "dialogue", 
            "news", "blog", "review", "summary", "note", 
            "marketing", "product_description", "email", "other"
        ]
        
        # 允许的分析类型
        self.allowed_analyse_types = [
            "readability", "sentiment", "keywords", "grammar", 
            "plagiarism", "toxicity", "language_detection", 
            "topic_classification", "emotion", "intent"
        ]
        
        # 敏感词检测
        self.sensitive_words = [
            "政治敏感词", "暴力词汇", "色情内容", "欺诈信息",
            # 这里应该是完整的敏感词库
        ]
        
        # 模板规则
        self.template_rules = {
            "max_name_length": 100,
            "min_name_length": 2,
            "max_description_length": 500,
            "max_variables": 50
        }
    
    def validate(self, data: Dict[str, Any], operation: str = "create") -> ValidationResult:
        """
        执行文本内容验证
        [validators][text_content][validate]
        """
        result = self.validator_base_create_result()
        
        if operation == "create":
            self._validate_create(data, result)
        elif operation == "update":
            self._validate_update(data, result)
        elif operation == "analyse":
            self._validate_analyse(data, result)
        elif operation == "template_create":
            self._validate_template_create(data, result)
        elif operation == "template_apply":
            self._validate_template_apply(data, result)
        
        return result
    
    def _validate_create(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证文本内容创建
        [validators][text_content][_validate_create]
        """
        # 验证标题
        title = data.get("title")
        if title:
            self.validator_base_validate_length(
                title,
                "标题",
                min_length=self.content_rules["min_title_length"],
                max_length=self.content_rules["max_title_length"],
                result=result
            )
        
        # 验证内容
        content = data.get("content")
        if not self.validator_base_validate_required(content, "文本内容", result):
            return
        
        self._validate_content(content, result)
        
        # 验证文本类型
        text_type = data.get("text_type", "article")
        self.validator_base_validate_enum(
            text_type, "文本类型", self.allowed_text_types, result
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
        
        # 验证模板ID（如果提供）
        template_id = data.get("template_id")
        if template_id:
            if not isinstance(template_id, int) or template_id <= 0:
                result.add_error(
                    code="INVALID_TEMPLATE_ID",
                    message="模板ID必须是正整数",
                    field="template_id"
                )
        
        # 业务规则验证
        self._validate_content_business_rules(content, result)
    
    def _validate_update(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证文本内容更新
        [validators][text_content][_validate_update]
        """
        # 验证文本ID
        text_id = data.get("text_id")
        if not self.validator_base_validate_required(text_id, "文本ID", result):
            return
        
        if not isinstance(text_id, int) or text_id <= 0:
            result.add_error(
                code="INVALID_TEXT_ID",
                message="文本ID必须是正整数",
                field="text_id"
            )
        
        # 验证新标题（如果提供）
        new_title = data.get("new_title")
        if new_title is not None:  # 允许空字符串
            self.validator_base_validate_length(
                new_title,
                "标题",
                max_length=self.content_rules["max_title_length"],
                result=result
            )
        
        # 验证新内容（如果提供）
        new_content = data.get("new_content")
        if new_content is not None:
            if new_content.strip() == "":
                result.add_error(
                    code="EMPTY_CONTENT",
                    message="文本内容不能为空",
                    field="new_content"
                )
                return
            
            self._validate_content(new_content, result)
            self._validate_content_business_rules(new_content, result)
        
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
        验证文本分析
        [validators][text_content][_validate_analyse]
        """
        # 验证文本ID
        text_id = data.get("text_id")
        if not self.validator_base_validate_required(text_id, "文本ID", result):
            return
        
        if not isinstance(text_id, int) or text_id <= 0:
            result.add_error(
                code="INVALID_TEXT_ID",
                message="文本ID必须是正整数",
                field="text_id"
            )
        
        # 验证分析类型
        analyse_type = data.get("analyse_type")
        if not self.validator_base_validate_required(analyse_type, "分析类型", result):
            return
        
        self.validator_base_validate_enum(
            analyse_type, "分析类型", self.allowed_analyse_types, result
        )
        
        # 验证自定义参数（如果提供）
        custom_params = data.get("custom_params")
        if custom_params:
            if not isinstance(custom_params, dict):
                result.add_error(
                    code="INVALID_CUSTOM_PARAMS",
                    message="自定义参数必须是字典格式",
                    field="custom_params"
                )
            else:
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
    
    def _validate_template_create(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证模板创建
        [validators][text_content][_validate_template_create]
        """
        # 验证模板名称
        template_name = data.get("template_name")
        if not self.validator_base_validate_required(template_name, "模板名称", result):
            return
        
        self.validator_base_validate_length(
            template_name,
            "模板名称",
            min_length=self.template_rules["min_name_length"],
            max_length=self.template_rules["max_name_length"],
            result=result
        )
        
        # 验证模板描述
        template_description = data.get("template_description")
        if template_description:
            self.validator_base_validate_length(
                template_description,
                "模板描述",
                max_length=self.template_rules["max_description_length"],
                result=result
            )
        
        # 验证模板类型
        template_type = data.get("template_type", "general")
        self.validator_base_validate_enum(
            template_type, "模板类型", self.allowed_text_types, result
        )
        
        # 验证模板内容
        template_content = data.get("template_content")
        if not self.validator_base_validate_required(template_content, "模板内容", result):
            return
        
        self._validate_template_content(template_content, result)
        
        # 验证模板变量
        template_variables = data.get("template_variables", [])
        if template_variables:
            self._validate_template_variables(template_variables, result)
    
    def _validate_template_apply(self, data: Dict[str, Any], result: ValidationResult):
        """
        验证模板应用
        [validators][text_content][_validate_template_apply]
        """
        # 验证模板ID
        template_id = data.get("template_id")
        if not self.validator_base_validate_required(template_id, "模板ID", result):
            return
        
        if not isinstance(template_id, int) or template_id <= 0:
            result.add_error(
                code="INVALID_TEMPLATE_ID",
                message="模板ID必须是正整数",
                field="template_id"
            )
        
        # 验证变量值
        variables = data.get("variables", {})
        if not isinstance(variables, dict):
            result.add_error(
                code="INVALID_VARIABLES_FORMAT",
                message="变量必须是字典格式",
                field="variables"
            )
        else:
            self._validate_variable_values(variables, result)
    
    def _validate_content(self, content: str, result: ValidationResult):
        """
        验证文本内容
        [validators][text_content][_validate_content]
        """
        # 长度验证
        self.validator_base_validate_length(
            content,
            "文本内容",
            min_length=self.content_rules["min_length"],
            max_length=self.content_rules["max_length"],
            result=result
        )
        
        # 字符统计
        char_count = len(content.replace(' ', ''))
        word_count = len(content.split())
        
        # 添加统计信息
        result.add_info(
            code="CONTENT_STATS",
            message=f"文本统计: {word_count}词, {char_count}字符",
            details={
                "word_count": word_count,
                "character_count": char_count,
                "total_length": len(content)
            }
        )
        
        # 内容质量检查
        if word_count < 5:
            result.add_warning(
                code="CONTENT_TOO_SHORT",
                message="文本内容过短，可能影响分析效果",
                field="content"
            )
        
        # 重复内容检查
        if self._has_excessive_repetition(content):
            result.add_warning(
                code="EXCESSIVE_REPETITION",
                message="文本包含大量重复内容",
                field="content"
            )
    
    def _validate_content_business_rules(self, content: str, result: ValidationResult):
        """
        验证内容业务规则
        [validators][text_content][_validate_content_business_rules]
        """
        # 敏感词检测
        sensitive_found = self._detect_sensitive_content(content)
        if sensitive_found:
            result.add_error(
                code="SENSITIVE_CONTENT_DETECTED",
                message="文本包含敏感内容",
                field="content",
                details={"sensitive_words": sensitive_found}
            )
        
        # 语言检测
        detected_language = self._detect_language(content)
        if detected_language and detected_language not in ["zh", "en"]:
            result.add_warning(
                code="UNSUPPORTED_LANGUAGE",
                message=f"检测到不常见语言: {detected_language}",
                field="content",
                details={"detected_language": detected_language}
            )
        
        # 文本质量检查
        quality_issues = self._check_content_quality(content)
        if quality_issues:
            for issue in quality_issues:
                result.add_warning(
                    code=f"QUALITY_{issue['type'].upper()}",
                    message=issue["message"],
                    field="content",
                    details=issue.get("details")
                )
    
    def _validate_analyse_params(self, analyse_type: str, params: Dict[str, Any], result: ValidationResult):
        """
        验证分析参数
        [validators][text_content][_validate_analyse_params]
        """
        if analyse_type == "readability":
            # 可读性分析参数
            if "algorithm" in params:
                allowed_algorithms = ["flesch", "fog", "smog", "coleman_liau"]
                if params["algorithm"] not in allowed_algorithms:
                    result.add_error(
                        code="INVALID_READABILITY_ALGORITHM",
                        message="不支持的可读性算法",
                        field="custom_params.algorithm"
                    )
        
        elif analyse_type == "sentiment":
            # 情感分析参数
            if "granularity" in params:
                allowed_granularity = ["document", "sentence", "aspect"]
                if params["granularity"] not in allowed_granularity:
                    result.add_error(
                        code="INVALID_SENTIMENT_GRANULARITY",
                        message="不支持的情感分析粒度",
                        field="custom_params.granularity"
                    )
        
        elif analyse_type == "keywords":
            # 关键词提取参数
            if "max_keywords" in params:
                max_kw = params["max_keywords"]
                if not isinstance(max_kw, int) or max_kw < 1 or max_kw > 100:
                    result.add_error(
                        code="INVALID_MAX_KEYWORDS",
                        message="关键词数量必须在1-100之间",
                        field="custom_params.max_keywords"
                    )
    
    def _validate_template_content(self, template_content: str, result: ValidationResult):
        """
        验证模板内容
        [validators][text_content][_validate_template_content]
        """
        # 基本长度验证
        self.validator_base_validate_length(
            template_content,
            "模板内容",
            min_length=1,
            max_length=self.content_rules["max_length"],
            result=result
        )
        
        # 模板变量语法检查
        import re
        
        # 检查变量语法 {{variable_name}}
        variable_pattern = r'\{\{([^}]+)\}\}'
        variables = re.findall(variable_pattern, template_content)
        
        if len(variables) > self.template_rules["max_variables"]:
            result.add_error(
                code="TOO_MANY_TEMPLATE_VARIABLES",
                message=f"模板变量数量不能超过{self.template_rules['max_variables']}个",
                field="template_content"
            )
        
        # 检查变量名格式
        for var in variables:
            var = var.strip()
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var):
                result.add_error(
                    code="INVALID_VARIABLE_NAME",
                    message=f"无效的变量名: {var}",
                    field="template_content",
                    details={"invalid_variable": var}
                )
        
        # 检查未闭合的变量
        open_braces = template_content.count('{{')
        close_braces = template_content.count('}}')
        
        if open_braces != close_braces:
            result.add_error(
                code="UNCLOSED_TEMPLATE_VARIABLES",
                message="模板变量语法不完整",
                field="template_content"
            )
    
    def _validate_template_variables(self, variables: List[Dict[str, Any]], result: ValidationResult):
        """
        验证模板变量
        [validators][text_content][_validate_template_variables]
        """
        if len(variables) > self.template_rules["max_variables"]:
            result.add_error(
                code="TOO_MANY_VARIABLES",
                message=f"变量数量不能超过{self.template_rules['max_variables']}个",
                field="template_variables"
            )
        
        variable_names = set()
        
        for i, var in enumerate(variables):
            # 验证变量名
            var_name = var.get("name")
            if not var_name:
                result.add_error(
                    code="MISSING_VARIABLE_NAME",
                    message=f"第{i+1}个变量缺少名称",
                    field=f"template_variables[{i}].name"
                )
                continue
            
            # 检查变量名重复
            if var_name in variable_names:
                result.add_error(
                    code="DUPLICATE_VARIABLE_NAME",
                    message=f"变量名重复: {var_name}",
                    field=f"template_variables[{i}].name"
                )
            else:
                variable_names.add(var_name)
            
            # 验证变量类型
            var_type = var.get("type", "string")
            allowed_types = ["string", "number", "boolean", "date", "email", "url"]
            if var_type not in allowed_types:
                result.add_error(
                    code="INVALID_VARIABLE_TYPE",
                    message=f"不支持的变量类型: {var_type}",
                    field=f"template_variables[{i}].type"
                )
            
            # 验证变量描述
            var_description = var.get("description")
            if var_description:
                self.validator_base_validate_length(
                    var_description,
                    f"变量{var_name}描述",
                    max_length=200,
                    result=result
                )
    
    def _validate_variable_values(self, variables: Dict[str, Any], result: ValidationResult):
        """
        验证变量值
        [validators][text_content][_validate_variable_values]
        """
        for var_name, var_value in variables.items():
            # 变量名格式检查
            import re
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                result.add_error(
                    code="INVALID_VARIABLE_NAME_FORMAT",
                    message=f"无效的变量名格式: {var_name}",
                    field=f"variables.{var_name}"
                )
            
            # 变量值长度检查
            if isinstance(var_value, str) and len(var_value) > 1000:
                result.add_error(
                    code="VARIABLE_VALUE_TOO_LONG",
                    message=f"变量{var_name}的值过长",
                    field=f"variables.{var_name}"
                )
    
    def _has_excessive_repetition(self, content: str) -> bool:
        """
        检查是否有过度重复
        [validators][text_content][_has_excessive_repetition]
        """
        words = content.split()
        if len(words) < 10:
            return False
        
        word_count = {}
        for word in words:
            word_lower = word.lower()
            word_count[word_lower] = word_count.get(word_lower, 0) + 1
        
        # 如果某个词出现次数超过总词数的30%，认为过度重复
        total_words = len(words)
        for count in word_count.values():
            if count / total_words > 0.3:
                return True
        
        return False
    
    def _detect_sensitive_content(self, content: str) -> List[str]:
        """
        检测敏感内容
        [validators][text_content][_detect_sensitive_content]
        """
        # 简化的敏感词检测
        found_words = []
        content_lower = content.lower()
        
        for word in self.sensitive_words:
            if word.lower() in content_lower:
                found_words.append(word)
        
        return found_words
    
    def _detect_language(self, content: str) -> Optional[str]:
        """
        检测文本语言
        [validators][text_content][_detect_language]
        """
        # 简化的语言检测
        chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
        total_chars = len(content.replace(' ', ''))
        
        if total_chars == 0:
            return None
        
        chinese_ratio = chinese_chars / total_chars
        
        if chinese_ratio > 0.5:
            return "zh"
        elif chinese_ratio < 0.1:
            return "en"
        else:
            return "mixed"
    
    def _check_content_quality(self, content: str) -> List[Dict[str, Any]]:
        """
        检查内容质量
        [validators][text_content][_check_content_quality]
        """
        issues = []
        
        # 检查句子长度
        sentences = content.split('。')
        avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences)
        
        if avg_sentence_length > 200:
            issues.append({
                "type": "long_sentences",
                "message": "平均句子长度过长，可能影响可读性",
                "details": {"avg_length": avg_sentence_length}
            })
        
        # 检查段落结构
        paragraphs = content.split('\n\n')
        if len(paragraphs) == 1 and len(content) > 500:
            issues.append({
                "type": "no_paragraphs",
                "message": "长文本建议分段显示",
                "details": {"content_length": len(content)}
            })
        
        return issues