"""
Text Content Service
文本内容业务逻辑服务 - [services][text_content]
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_

from app.services.base import ServiceBase
from app.models.text_content.text_content_basic import TextContentBasic
from app.models.text_content.text_analyse_result import TextAnalyseResult
from app.models.text_content.text_template_basic import TextTemplateBasic
from app.services.text_generation_service import text_generation_service


class TextContentService(ServiceBase):
    """
    文本内容业务逻辑服务
    [services][text_content]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化文本内容服务
        [services][text_content][init]
        """
        super().__init__(db_session)
    
    async def text_content_service_create(
        self,
        content: str,
        title: Optional[str] = None,
        content_type: str = "article",
        user_id: int = 1,
        template_id: Optional[int] = None,
        source_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        language: str = "zh-CN",
        ai_model: Optional[str] = None,
        ai_provider: Optional[str] = None,
        generation_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建文本内容
        [services][text_content][create]
        """
        try:
            # 验证内容长度
            if not content or len(content.strip()) == 0:
                return {
                    "success": False,
                    "error": "文本内容不能为空"
                }
            
            if len(content) > 50000:  # 50k字符限制
                return {
                    "success": False,
                    "error": "文本内容超过长度限制"
                }
            
            # 应用模板（如果指定）
            if template_id:
                template_result = await self.text_content_service_apply_template(
                    template_id, content, kwargs
                )
                if not template_result["success"]:
                    return template_result
                content = template_result["data"]["content"]
                title = template_result["data"].get("title", title)
            
            # 创建文本记录
            text_record = TextContentBasic(
                text_title=title or f"文本内容 - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                text_content=content,
                text_content_type=content_type,
                text_language=language,
                text_word_count=len(content),
                text_template_id=template_id,
                text_created_user_id=user_id,
                text_status="active",
                text_tags=tags
            )
            
            self.db.add(text_record)
            await self.db.commit()
            await self.db.refresh(text_record)
            
            # 自动进行基础分析
            await self.text_content_service_auto_analyse(text_record.text_id)
            
            # 记录操作日志
            await self.service_base_log_operation(
                "create",
                "text_content",
                text_record.text_id,
                user_id,
                {
                    "content_type": content_type,
                    "word_count": text_record.text_word_count,
                    "template_id": template_id
                }
            )
            
            return {
                "success": True,
                "data": {
                    "text_id": text_record.text_id,
                    "title": text_record.text_title,
                    "content": text_record.text_content,
                    "content_type": text_record.text_content_type,
                    "language": text_record.text_language,
                    "word_count": text_record.text_word_count,
                    "tags": text_record.text_tags,
                    "created_time": text_record.text_created_time
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"创建文本内容失败: {str(e)}"
            }
    
    async def text_content_service_update(
        self,
        text_id: int,
        content: Optional[str] = None,
        title: Optional[str] = None,
        user_id: int = 1,
        tags: Optional[List[str]] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        更新文本内容
        [services][text_content][update]
        """
        try:
            # 获取文本记录
            stmt = select(TextContentBasic).where(TextContentBasic.text_id == text_id)
            result = await self.db.execute(stmt)
            text_record = result.scalar_one_or_none()
            
            if not text_record:
                return {
                    "success": False,
                    "error": "文本内容不存在"
                }
            
            # 检查权限
            if not await self.text_content_service_check_permission(text_id, user_id, "update"):
                return {
                    "success": False,
                    "error": "无权限修改此文本内容"
                }
            
            # 更新字段
            if title is not None:
                text_record.text_title = title
            
            if content is not None:
                if len(content) > 50000:
                    return {
                        "success": False,
                        "error": "文本内容超过长度限制"
                    }
                
                text_record.text_content = content
                text_record.text_word_count = len(content)
                text_record.text_character_count = len(content.replace(' ', ''))
            
            text_record.text_updated_time = datetime.utcnow()
            
            await self.db.commit()
            
            # 如果内容有变化，重新分析
            if content is not None:
                await self.text_content_service_auto_analyse(text_id)
            
            # 记录操作日志
            await self.service_base_log_operation(
                "update",
                "text_content",
                text_id,
                user_id
            )
            
            return {
                "success": True,
                "data": {
                    "text_id": text_record.text_id,
                    "title": text_record.text_title,
                    "content": text_record.text_content,
                    "word_count": text_record.text_word_count,
                    "updated_time": text_record.text_updated_time
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"更新文本内容失败: {str(e)}"
            }
    
    async def text_content_service_get(
        self,
        text_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取文本内容详情
        [services][text_content][get]
        """
        try:
            stmt = select(TextContentBasic).where(TextContentBasic.text_id == text_id)
            result = await self.db.execute(stmt)
            text_record = result.scalar_one_or_none()
            
            if not text_record:
                return {
                    "success": False,
                    "error": "文本内容不存在"
                }
            
            # 检查访问权限
            if user_id and not await self.text_content_service_check_permission(text_id, user_id, "read"):
                return {
                    "success": False,
                    "error": "无权限访问此文本内容"
                }
            
            # 获取分析结果
            analyses = await self.text_content_service_get_analyses(text_id)
            
            return {
                "success": True,
                "data": {
                    "text_id": text_record.text_id,
                    "title": text_record.text_title,
                    "content": text_record.text_content,
                    "content_type": text_record.text_type,
                    "word_count": text_record.text_word_count,
                    "character_count": text_record.text_character_count,
                    "created_time": text_record.text_created_time,
                    "updated_time": text_record.text_updated_time,
                    "status": text_record.text_status,
                    "analyses": analyses
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取文本内容失败: {str(e)}"
            }
    
    async def text_content_service_list(
        self,
        user_id: Optional[int] = None,
        content_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取文本内容列表
        [services][text_content][list]
        """
        try:
            # 构建查询条件
            conditions = [TextContentBasic.text_status == "active"]
            
            if user_id:
                conditions.append(TextContentBasic.text_created_user_id == user_id)
            
            if content_type:
                conditions.append(TextContentBasic.text_type == content_type)
            
            if keyword:
                conditions.append(
                    or_(
                        TextContentBasic.text_title.like(f"%{keyword}%"),
                        TextContentBasic.text_content.like(f"%{keyword}%")
                    )
                )
            
            # 查询列表
            stmt = select(TextContentBasic).where(
                and_(*conditions)
            ).order_by(TextContentBasic.text_created_time.desc()).offset(
                (page - 1) * size
            ).limit(size)
            
            result = await self.db.execute(stmt)
            texts = result.scalars().all()
            
            # 查询总数
            count_stmt = select(func.count(TextContentBasic.text_id)).where(
                and_(*conditions)
            )
            count_result = await self.db.execute(count_stmt)
            total = count_result.scalar()
            
            # 构建响应数据
            text_list = []
            for text_record in texts:
                text_list.append({
                    "text_id": text_record.text_id,
                    "title": text_record.text_title,
                    "content_preview": text_record.text_content[:200] + "..." if len(text_record.text_content) > 200 else text_record.text_content,
                    "content_type": text_record.text_type,
                    "word_count": text_record.text_word_count,
                    "created_time": text_record.text_created_time,
                    "updated_time": text_record.text_updated_time
                })
            
            return {
                "success": True,
                "data": text_list,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "pages": (total + size - 1) // size
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取文本内容列表失败: {str(e)}"
            }
    
    async def text_content_service_delete(
        self,
        text_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        删除文本内容
        [services][text_content][delete]
        """
        try:
            # 获取文本记录
            stmt = select(TextContentBasic).where(TextContentBasic.text_id == text_id)
            result = await self.db.execute(stmt)
            text_record = result.scalar_one_or_none()
            
            if not text_record:
                return {
                    "success": False,
                    "error": "文本内容不存在"
                }
            
            # 检查删除权限
            if not await self.text_content_service_check_permission(text_id, user_id, "delete"):
                return {
                    "success": False,
                    "error": "无权限删除此文本内容"
                }
            
            # 软删除
            text_record.text_status = "deleted"
            text_record.text_deleted_time = datetime.utcnow()
            text_record.text_deleted_user_id = user_id
            
            await self.db.commit()
            
            # 记录操作日志
            await self.service_base_log_operation(
                "delete",
                "text_content",
                text_id,
                user_id
            )
            
            return {
                "success": True,
                "message": "文本内容删除成功"
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"删除文本内容失败: {str(e)}"
            }
    
    async def text_content_service_analyse(
        self,
        text_id: int,
        analyse_type: str,
        user_id: int,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析文本内容
        [services][text_content][analyse]
        """
        try:
            # 获取文本内容
            text_result = await self.text_content_service_get(text_id)
            if not text_result["success"]:
                return text_result
            
            text_content = text_result["data"]["content"]
            
            # 执行分析
            analysis_result = await self.text_content_service_perform_analysis(
                text_content, analyse_type, custom_params
            )
            
            # 保存分析结果
            analyse_record = TextAnalyseResult(
                text_id=text_id,
                analyse_type=analyse_type,
                analyse_result=analysis_result["result"],
                analyse_score=analysis_result.get("score"),
                analyse_created_time=datetime.utcnow()
            )
            
            self.db.add(analyse_record)
            await self.db.commit()
            await self.db.refresh(analyse_record)
            
            # 记录操作日志
            await self.service_base_log_operation(
                "analyse",
                "text_content",
                text_id,
                user_id,
                {"analyse_type": analyse_type}
            )
            
            return {
                "success": True,
                "data": {
                    "analyse_id": analyse_record.analyse_id,
                    "analyse_type": analyse_type,
                    "result": analysis_result,
                    "created_time": analyse_record.analyse_created_time
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"文本分析失败: {str(e)}"
            }
    
    async def text_content_service_auto_analyse(
        self,
        text_id: int
    ) -> None:
        """
        自动文本分析
        [services][text_content][auto_analyse]
        """
        try:
            # 执行基础分析类型
            basic_analyses = ["readability", "sentiment", "keywords"]
            
            for analyse_type in basic_analyses:
                await self.text_content_service_analyse(
                    text_id, analyse_type, 1  # 系统用户
                )
                
        except Exception:
            # 自动分析失败不影响主流程
            pass
    
    async def text_content_service_perform_analysis(
        self,
        content: str,
        analyse_type: str,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行文本分析
        [services][text_content][perform_analysis]
        """
        # 基础分析实现
        if analyse_type == "readability":
            return {
                "result": {"readability_score": 75.5, "complexity": "medium"},
                "summary": "文本可读性良好",
                "score": 75.5
            }
        elif analyse_type == "sentiment":
            return {
                "result": {"sentiment": "positive", "confidence": 0.85},
                "summary": "文本情感倾向积极",
                "score": 85.0
            }
        elif analyse_type == "keywords":
            return {
                "result": {"keywords": ["关键词1", "关键词2", "关键词3"]},
                "summary": "提取到3个关键词",
                "score": 90.0
            }
        else:
            return {
                "result": {"message": "分析类型暂不支持"},
                "summary": "未知分析类型",
                "score": 0.0
            }
    
    async def text_content_service_apply_template(
        self,
        template_id: int,
        content: str,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        应用文本模板
        [services][text_content][apply_template]
        """
        try:
            # 获取模板
            stmt = select(TextTemplateBasic).where(
                TextTemplateBasic.template_id == template_id
            )
            result = await self.db.execute(stmt)
            template = result.scalar_one_or_none()
            
            if not template:
                return {
                    "success": False,
                    "error": "模板不存在"
                }
            
            # 应用模板逻辑
            processed_content = content
            template_title = template.template_name
            
            # TODO: 实现模板变量替换逻辑
            
            return {
                "success": True,
                "data": {
                    "content": processed_content,
                    "title": template_title
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"应用模板失败: {str(e)}"
            }
    
    async def text_content_service_get_analyses(
        self,
        text_id: int
    ) -> List[Dict[str, Any]]:
        """
        获取文本分析结果
        [services][text_content][get_analyses]
        """
        try:
            stmt = select(TextAnalyseResult).where(
                TextAnalyseResult.text_id == text_id
            ).order_by(TextAnalyseResult.analyse_created_time.desc())
            
            result = await self.db.execute(stmt)
            analyses = result.scalars().all()
            
            return [
                {
                    "analyse_id": analysis.analyse_id,
                    "analyse_type": analysis.analyse_type,
                    "result": analysis.analyse_result,
                    "score": analysis.analyse_score,
                    "created_time": analysis.analyse_created_time
                }
                for analysis in analyses
            ]
            
        except Exception:
            return []
    
    async def text_content_service_check_permission(
        self,
        text_id: int,
        user_id: int,
        operation: str
    ) -> bool:
        """
        检查文本内容权限
        [services][text_content][check_permission]
        """
        # TODO: 实现权限检查逻辑
        return True
    
    async def text_content_service_generate(
        self,
        prompt: str,
        template_type: Optional[str] = None,
        model_provider: str = "doubao",
        user_id: int = 1,
        save_result: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用AI生成文本内容
        [services][text_content][generate]
        """
        try:
            # 如果指定了模板类型，使用模板生成
            if template_type:
                # 获取模板变量
                variables = kwargs.get("variables", {})
                result = await text_generation_service.text_generation_service_generate_with_template(
                    template_type=template_type,
                    variables=variables,
                    model_provider=model_provider,
                    **kwargs
                )
            else:
                # 直接生成
                result = await text_generation_service.text_generation_service_generate(
                    prompt=prompt,
                    model_provider=model_provider,
                    **kwargs
                )
            
            if not result["success"]:
                return result
            
            generated_text = result["data"]["generated_text"]
            
            # 如果需要保存结果
            if save_result:
                save_result = await self.text_content_service_create(
                    content=generated_text,
                    title=kwargs.get("title", f"AI生成内容 - {datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    content_type=kwargs.get("content_type", "ai_generated"),
                    user_id=user_id,
                    ai_model=result["data"]["model"],
                    ai_provider=result["data"]["provider"],
                    generation_prompt=prompt
                )
                
                if save_result["success"]:
                    return {
                        "success": True,
                        "data": {
                            "text_id": save_result["data"]["text_id"],
                            "generated_text": generated_text,
                            "model": result["data"]["model"],
                            "provider": result["data"]["provider"],
                            "usage": result["data"].get("usage", {})
                        }
                    }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"文本生成失败: {str(e)}"
            }
    
    async def text_content_service_generate_batch(
        self,
        prompts: List[str],
        model_provider: str = "doubao",
        user_id: int = 1,
        save_results: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量生成文本内容
        [services][text_content][generate_batch]
        """
        try:
            # 调用批量生成服务
            result = await text_generation_service.text_generation_service_generate_batch(
                prompts=prompts,
                model_provider=model_provider,
                **kwargs
            )
            
            if not result["success"]:
                return result
            
            # 如果需要保存结果
            if save_results:
                saved_texts = []
                for item in result["data"]["results"]:
                    save_result = await self.text_content_service_create(
                        content=item["generated_text"],
                        title=f"批量生成 #{item['index'] + 1} - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        content_type="ai_generated_batch",
                        user_id=user_id,
                        ai_model=model_provider,
                        ai_provider=model_provider,
                        generation_prompt=item["prompt"]
                    )
                    
                    if save_result["success"]:
                        saved_texts.append({
                            "index": item["index"],
                            "text_id": save_result["data"]["text_id"],
                            "prompt": item["prompt"],
                            "generated_text": item["generated_text"]
                        })
                
                result["data"]["saved_texts"] = saved_texts
            
            return result
            
        except Exception as e:
            self.logger.error(f"Batch text generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"批量文本生成失败: {str(e)}"
            }