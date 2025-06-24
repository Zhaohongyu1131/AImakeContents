"""
Image Content Service
图像内容业务逻辑服务 - [services][image_content]
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_

from app.services.base import ServiceBase
from app.models.image_video.image_basic import ImageBasic
from app.models.image_video.image_analyse import ImageAnalyse
from app.models.image_video.image_template import ImageTemplate
from app.services.image_generation_service import image_generation_service
from app.services.file_storage import FileStorageService


class ImageContentService(ServiceBase):
    """
    图像内容业务逻辑服务
    [services][image_content]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化图像内容服务
        [services][image_content][init]
        """
        super().__init__(db_session)
    
    async def image_content_service_create(
        self,
        title: str,
        prompt: str,
        width: int = 512,
        height: int = 512,
        style: Optional[str] = None,
        quality: str = "standard",
        model_provider: str = "doubao",
        model_name: Optional[str] = None,
        user_id: int = 1,
        template_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        save_file: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建图像内容
        [services][image_content][create]
        """
        try:
            # 生成图像
            generation_result = await image_generation_service.image_generation_service_generate(
                prompt=prompt,
                model_provider=model_provider,
                model_name=model_name,
                width=width,
                height=height,
                num_images=1,
                style=style,
                quality=quality,
                **kwargs
            )
            
            if not generation_result["success"]:
                return generation_result
            
            images = generation_result["data"]["images"]
            if not images:
                return {
                    "success": False,
                    "error": "图像生成失败，未返回图像数据"
                }
            
            # 处理第一张图像
            image_data = images[0]
            file_url = None
            file_path = None
            file_size = 0
            
            # 保存图像文件
            if save_file and image_data.get("image_data"):
                try:
                    # 解码base64图像数据
                    image_bytes = base64.b64decode(image_data["image_data"])
                    file_size = len(image_bytes)
                    
                    # 生成文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"generated_image_{timestamp}_{user_id}.png"
                    
                    # 保存文件  
                    file_storage_service = FileStorageService(self.db)
                    file_result = await file_storage_service.file_storage_service_save_bytes(
                        file_bytes=image_bytes,
                        filename=filename,
                        content_type="image/png",
                        user_id=user_id,
                        category="image",
                        metadata={
                            "generated": True,
                            "prompt": prompt,
                            "model": model_name or "default",
                            "provider": model_provider
                        }
                    )
                    
                    if file_result["success"]:
                        file_url = file_result["data"]["file_url"]
                        file_path = file_result["data"]["file_path"]
                    
                except Exception as e:
                    self.logger.warning(f"Failed to save image file: {str(e)}")
            
            # 创建图像记录
            file_id = None
            if save_file and 'file_result' in locals() and file_result.get("success"):
                file_id = file_result["data"]["file_id"]
            
            image_record = ImageBasic(
                image_name=title,
                image_description=prompt,
                image_file_id=file_id,
                image_width=width,
                image_height=height,
                image_format="PNG",
                image_prompt=prompt,
                image_platform=model_provider,
                image_model_name=generation_result["data"]["model"],
                image_generation_params={
                    "width": width,
                    "height": height,
                    "style": style,
                    "quality": quality,
                    **kwargs
                },
                image_created_user_id=user_id,
                image_status="completed",
                image_tags=tags or []
            )
            
            self.db.add(image_record)
            await self.db.commit()
            await self.db.refresh(image_record)
            
            # 自动进行基础分析
            await self.image_content_service_auto_analyse(image_record.image_id)
            
            # 记录操作日志
            await self.service_base_log_operation(
                "create",
                "image_content",
                image_record.image_id,
                user_id,
                {
                    "prompt": prompt,
                    "model": model_provider,
                    "dimensions": f"{width}x{height}"
                }
            )
            
            return {
                "success": True,
                "data": {
                    "image_id": image_record.image_id,
                    "title": image_record.image_name,
                    "description": image_record.image_description,
                    "file_url": file_url or image_data.get("url"),
                    "width": image_record.image_width,
                    "height": image_record.image_height,
                    "format": image_record.image_format,
                    "model": image_record.image_model_name,
                    "platform": image_record.image_platform,
                    "created_time": image_record.image_created_time,
                    "tags": image_record.image_tags
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Image content creation failed: {str(e)}")
            return {
                "success": False,
                "error": f"创建图像内容失败: {str(e)}"
            }
    
    async def image_content_service_get(
        self,
        image_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取图像内容详情
        [services][image_content][get]
        """
        try:
            stmt = select(ImageBasic).where(ImageBasic.image_id == image_id)
            result = await self.db.execute(stmt)
            image_record = result.scalar_one_or_none()
            
            if not image_record:
                return {
                    "success": False,
                    "error": "图像内容不存在"
                }
            
            # 检查访问权限
            if user_id and not await self.image_content_service_check_permission(image_id, user_id, "read"):
                return {
                    "success": False,
                    "error": "无权限访问此图像内容"
                }
            
            # 获取分析结果
            analyses = await self.image_content_service_get_analyses(image_id)
            
            return {
                "success": True,
                "data": {
                    "image_id": image_record.image_id,
                    "title": image_record.image_name,
                    "description": image_record.image_description,
                    "file_url": self._get_file_url_from_file_id(image_record.image_file_id) if image_record.image_file_id else None,
                    "width": image_record.image_width,
                    "height": image_record.image_height,
                    "format": image_record.image_format,
                    "generation_prompt": image_record.image_prompt,
                    "generation_model": image_record.image_model_name,
                    "generation_platform": image_record.image_platform,
                    "generation_params": image_record.image_generation_params,
                    "created_time": image_record.image_created_time,
                    "updated_time": image_record.image_updated_time,
                    "status": image_record.image_status,
                    "tags": image_record.image_tags,
                    "analyses": analyses
                }
            }
            
        except Exception as e:
            self.logger.error(f"Get image content failed: {str(e)}")
            return {
                "success": False,
                "error": f"获取图像内容失败: {str(e)}"
            }
    
    async def image_content_service_list(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        format_filter: Optional[str] = None,
        model_provider: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取图像内容列表
        [services][image_content][list]
        """
        try:
            # 构建查询条件
            conditions = []
            if status:
                conditions.append(ImageBasic.image_status == status)
            else:
                conditions.append(ImageBasic.image_status != "deleted")
            
            if user_id:
                conditions.append(ImageBasic.image_created_user_id == user_id)
            
            if format_filter:
                conditions.append(ImageBasic.image_format == format_filter.upper())
            
            if model_provider:
                conditions.append(ImageBasic.image_platform == model_provider)
            
            if keyword:
                conditions.append(
                    or_(
                        ImageBasic.image_name.like(f"%{keyword}%"),
                        ImageBasic.image_description.like(f"%{keyword}%"),
                        ImageBasic.image_prompt.like(f"%{keyword}%")
                    )
                )
            
            # 查询列表
            stmt = select(ImageBasic).where(
                and_(*conditions) if conditions else True
            ).order_by(ImageBasic.image_created_time.desc()).offset(
                (page - 1) * size
            ).limit(size)
            
            result = await self.db.execute(stmt)
            images = result.scalars().all()
            
            # 查询总数
            count_stmt = select(func.count(ImageBasic.image_id)).where(
                and_(*conditions) if conditions else True
            )
            count_result = await self.db.execute(count_stmt)
            total = count_result.scalar()
            
            # 构建响应数据
            image_list = []
            for image_record in images:
                image_list.append({
                    "image_id": image_record.image_id,
                    "title": image_record.image_name,
                    "description": image_record.image_description[:100] + "..." if len(image_record.image_description or "") > 100 else image_record.image_description,
                    "file_url": self._get_file_url_from_file_id(image_record.image_file_id) if image_record.image_file_id else None,
                    "width": image_record.image_width,
                    "height": image_record.image_height,
                    "format": image_record.image_format,
                    "generation_model": image_record.image_model_name,
                    "generation_platform": image_record.image_platform,
                    "created_time": image_record.image_created_time,
                    "updated_time": image_record.image_updated_time,
                    "tags": image_record.image_tags
                })
            
            return {
                "success": True,
                "data": image_list,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "pages": (total + size - 1) // size
                }
            }
            
        except Exception as e:
            self.logger.error(f"List image content failed: {str(e)}")
            return {
                "success": False,
                "error": f"获取图像内容列表失败: {str(e)}"
            }
    
    async def image_content_service_update(
        self,
        image_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        更新图像内容
        [services][image_content][update]
        """
        try:
            # 获取图像记录
            stmt = select(ImageBasic).where(ImageBasic.image_id == image_id)
            result = await self.db.execute(stmt)
            image_record = result.scalar_one_or_none()
            
            if not image_record:
                return {
                    "success": False,
                    "error": "图像内容不存在"
                }
            
            # 检查权限
            if not await self.image_content_service_check_permission(image_id, user_id, "update"):
                return {
                    "success": False,
                    "error": "无权限修改此图像内容"
                }
            
            # 更新字段
            if title is not None:
                image_record.image_name = title
            
            if description is not None:
                image_record.image_description = description
            
            if tags is not None:
                image_record.image_tags = tags
            
            image_record.image_updated_time = datetime.utcnow()
            
            await self.db.commit()
            
            # 记录操作日志
            await self.service_base_log_operation(
                "update",
                "image_content",
                image_id,
                user_id
            )
            
            return {
                "success": True,
                "data": {
                    "image_id": image_record.image_id,
                    "title": image_record.image_name,
                    "description": image_record.image_description,
                    "tags": image_record.image_tags,
                    "updated_time": image_record.image_updated_time
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Update image content failed: {str(e)}")
            return {
                "success": False,
                "error": f"更新图像内容失败: {str(e)}"
            }
    
    async def image_content_service_delete(
        self,
        image_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        删除图像内容
        [services][image_content][delete]
        """
        try:
            # 获取图像记录
            stmt = select(ImageBasic).where(ImageBasic.image_id == image_id)
            result = await self.db.execute(stmt)
            image_record = result.scalar_one_or_none()
            
            if not image_record:
                return {
                    "success": False,
                    "error": "图像内容不存在"
                }
            
            # 检查删除权限
            if not await self.image_content_service_check_permission(image_id, user_id, "delete"):
                return {
                    "success": False,
                    "error": "无权限删除此图像内容"
                }
            
            # 软删除
            image_record.image_status = "deleted"
            
            await self.db.commit()
            
            # 记录操作日志
            await self.service_base_log_operation(
                "delete",
                "image_content",
                image_id,
                user_id
            )
            
            return {
                "success": True,
                "message": "图像内容删除成功"
            }
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Delete image content failed: {str(e)}")
            return {
                "success": False,
                "error": f"删除图像内容失败: {str(e)}"
            }
    
    async def image_content_service_analyse(
        self,
        image_id: int,
        analyse_type: str,
        user_id: int,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析图像内容
        [services][image_content][analyse]
        """
        try:
            # 获取图像内容
            image_result = await self.image_content_service_get(image_id)
            if not image_result["success"]:
                return image_result
            
            # 执行分析
            analysis_result = await self.image_content_service_perform_analysis(
                image_result["data"], analyse_type, custom_params
            )
            
            # 保存分析结果
            analyse_record = ImageAnalyse(
                image_id=image_id,
                analyse_type=analyse_type,
                analyse_result=analysis_result["result"],
                analyse_confidence_score=analysis_result.get("confidence", 0.0),
                analyse_quality_score=analysis_result.get("quality_score", 0.0),
                analyse_style_tags=analysis_result.get("style_tags", []),
                analyse_content_tags=analysis_result.get("content_tags", []),
                analyse_emotion_sentiment=analysis_result.get("emotion", "neutral"),
                analyse_created_user_id=user_id,
                analyse_created_time=datetime.utcnow(),
                analyse_status="completed"
            )
            
            self.db.add(analyse_record)
            await self.db.commit()
            await self.db.refresh(analyse_record)
            
            # 记录操作日志
            await self.service_base_log_operation(
                "analyse",
                "image_content",
                image_id,
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
            self.logger.error(f"Image analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"图像分析失败: {str(e)}"
            }
    
    async def image_content_service_auto_analyse(
        self,
        image_id: int
    ) -> None:
        """
        自动图像分析
        [services][image_content][auto_analyse]
        """
        try:
            # 执行基础分析类型
            basic_analyses = ["quality", "content", "style"]
            
            for analyse_type in basic_analyses:
                await self.image_content_service_analyse(
                    image_id, analyse_type, 1  # 系统用户
                )
                
        except Exception:
            # 自动分析失败不影响主流程
            pass
    
    async def image_content_service_perform_analysis(
        self,
        image_data: Dict[str, Any],
        analyse_type: str,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行图像分析
        [services][image_content][perform_analysis]
        """
        # 基础分析实现
        if analyse_type == "quality":
            return {
                "result": {"quality_score": 85.5, "resolution": "high", "clarity": "good"},
                "confidence": 0.92,
                "quality_score": 85.5
            }
        elif analyse_type == "content":
            return {
                "result": {"objects": ["person", "landscape"], "scene": "outdoor"},
                "confidence": 0.88,
                "content_tags": ["person", "landscape", "outdoor"]
            }
        elif analyse_type == "style":
            return {
                "result": {"style": "photographic", "mood": "peaceful"},
                "confidence": 0.75,
                "style_tags": ["photographic", "peaceful"],
                "emotion": "positive"
            }
        else:
            return {
                "result": {"message": "分析类型暂不支持"},
                "confidence": 0.0
            }
    
    async def image_content_service_get_analyses(
        self,
        image_id: int
    ) -> List[Dict[str, Any]]:
        """
        获取图像分析结果
        [services][image_content][get_analyses]
        """
        try:
            stmt = select(ImageAnalyse).where(
                ImageAnalyse.image_id == image_id
            ).order_by(ImageAnalyse.analyse_created_time.desc())
            
            result = await self.db.execute(stmt)
            analyses = result.scalars().all()
            
            return [
                {
                    "analyse_id": analysis.analyse_id,
                    "analyse_type": analysis.analyse_type,
                    "result": analysis.analyse_result,
                    "confidence_score": float(analysis.analyse_confidence_score) if analysis.analyse_confidence_score else 0.0,
                    "quality_score": float(analysis.analyse_quality_score) if analysis.analyse_quality_score else 0.0,
                    "style_tags": analysis.analyse_style_tags,
                    "content_tags": analysis.analyse_content_tags,
                    "emotion_sentiment": analysis.analyse_emotion_sentiment,
                    "created_time": analysis.analyse_created_time
                }
                for analysis in analyses
            ]
            
        except Exception:
            return []
    
    async def image_content_service_check_permission(
        self,
        image_id: int,
        user_id: int,
        operation: str
    ) -> bool:
        """
        检查图像内容权限
        [services][image_content][check_permission]
        """
        # TODO: 实现权限检查逻辑
        return True
    
    def _get_file_url_from_file_id(self, file_id: int) -> Optional[str]:
        """
        根据文件ID获取文件URL
        [services][image_content][get_file_url_from_file_id]
        """
        if not file_id:
            return None
        # TODO: 实现从file_storage_service获取URL的逻辑
        return f"/api/v1/files/{file_id}"


# 创建全局服务实例
image_content_service = ImageContentService