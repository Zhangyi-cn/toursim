from flask import request, jsonify, g, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

from models.travel_guide import TravelGuide, TravelGuideCategory
from models.tag import Tag, ContentTag
from extensions import db
from utils.response import success_response, error_response
from utils.auth import admin_required

class GuideAdminController:
    """旅游攻略管理控制器"""
    
    @staticmethod
    @admin_required()
    def get_guides():
        """获取旅游攻略列表"""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            keyword = request.args.get('keyword', '')
            category_id = request.args.get('category_id')
            
            query = TravelGuide.query
            
            # 按关键词筛选
            if keyword:
                query = query.filter(TravelGuide.title.like(f'%{keyword}%'))
                
            # 按分类筛选
            if category_id:
                query = query.filter(TravelGuide.category_id == category_id)
                
            # 分页
            pagination = query.order_by(TravelGuide.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            guides = pagination.items
            total = pagination.total
            
            # 构造返回数据
            items = []
            for guide in guides:
                guide_dict = guide.to_dict()
                
                # 获取分类名称
                if guide.category_id:
                    category = TravelGuideCategory.query.get(guide.category_id)
                    guide_dict['category_name'] = category.name if category else ''
                else:
                    guide_dict['category_name'] = ''
                    
                # 获取标签
                tags = db.session.query(Tag).join(ContentTag).filter(
                    ContentTag.content_id == guide.id,
                    ContentTag.content_type == 'guide'
                ).all()
                
                guide_dict['tags'] = [tag.to_dict() for tag in tags]
                items.append(guide_dict)
            
            return success_response("获取旅游攻略列表成功", {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page
            })
            
        except Exception as e:
            return error_response(f"获取旅游攻略列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def create_guide():
        """创建旅游攻略"""
        try:
            data = request.get_json()
            
            title = data.get('title', '')
            content = data.get('content', '')
            cover_image = data.get('cover_image', '')
            category_id = data.get('category_id')
            tags = data.get('tags', [])
            user_id = data.get('user_id')
            is_official = data.get('is_official', False)
            is_hot = data.get('is_hot', False)
            view_count = data.get('view_count', 0)
            like_count = data.get('like_count', 0)
            status = data.get('status', 1)
            
            # 验证必填字段
            if not title:
                return error_response("标题不能为空", 400)
                
            if not content:
                return error_response("内容不能为空", 400)
                
            if not cover_image:
                return error_response("封面图不能为空", 400)
                
            # 验证分类是否存在
            if category_id:
                category = TravelGuideCategory.query.get(category_id)
                if not category:
                    return error_response("指定的分类不存在", 400)
            
            # 创建攻略
            guide = TravelGuide(
                title=title,
                content=content,
                cover_image=cover_image,
                category_id=category_id,
                user_id=user_id,
                is_official=is_official,
                is_hot=is_hot,
                view_count=view_count,
                like_count=like_count,
                status=status
            )
            
            db.session.add(guide)
            db.session.flush()  # 获取ID但不提交事务
            
            # 处理标签
            if tags:
                for tag_name in tags:
                    # 查找或创建标签
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                        db.session.flush()
                        
                    # 创建内容标签关联
                    content_tag = ContentTag(
                        content_id=guide.id,
                        content_type='guide',
                        tag_id=tag.id
                    )
                    db.session.add(content_tag)
            
            db.session.commit()
            
            return success_response("创建旅游攻略成功", guide.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建旅游攻略失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_guide(guide_id):
        """获取旅游攻略详情"""
        try:
            guide = TravelGuide.query.get(guide_id)
            
            if not guide:
                return error_response("旅游攻略不存在", 404)
                
            guide_dict = guide.to_dict()
            
            # 获取分类名称
            if guide.category_id:
                category = TravelGuideCategory.query.get(guide.category_id)
                guide_dict['category_name'] = category.name if category else ''
            else:
                guide_dict['category_name'] = ''
                
            # 获取标签
            tags = db.session.query(Tag).join(ContentTag).filter(
                ContentTag.content_id == guide.id,
                ContentTag.content_type == 'guide'
            ).all()
            
            guide_dict['tags'] = [tag.name for tag in tags]
            
            return success_response("获取旅游攻略详情成功", guide_dict)
            
        except Exception as e:
            return error_response(f"获取旅游攻略详情失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_guide(guide_id):
        """更新旅游攻略"""
        try:
            guide = TravelGuide.query.get(guide_id)
            
            if not guide:
                return error_response("旅游攻略不存在", 404)
                
            data = request.get_json()
            
            # 可更新的字段
            updatable_fields = [
                'title', 'content', 'cover_image', 'category_id', 
                'user_id', 'is_official', 'is_hot', 'view_count', 
                'like_count', 'status'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(guide, field, data[field])
            
            # 验证分类是否存在
            if 'category_id' in data and data['category_id']:
                category = TravelGuideCategory.query.get(data['category_id'])
                if not category:
                    return error_response("指定的分类不存在", 400)
                    
            # 更新标签
            if 'tags' in data:
                # 删除旧标签关联
                ContentTag.query.filter_by(content_id=guide.id, content_type='guide').delete()
                
                # 添加新标签
                for tag_name in data['tags']:
                    # 查找或创建标签
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                        db.session.flush()
                        
                    # 创建内容标签关联
                    content_tag = ContentTag(
                        content_id=guide.id,
                        content_type='guide',
                        tag_id=tag.id
                    )
                    db.session.add(content_tag)
            
            guide.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新旅游攻略成功", guide.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新旅游攻略失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def delete_guide(guide_id):
        """删除旅游攻略"""
        try:
            guide = TravelGuide.query.get(guide_id)
            
            if not guide:
                return error_response("旅游攻略不存在", 404)
                
            # 删除相关的内容标签关联
            ContentTag.query.filter_by(content_id=guide.id, content_type='guide').delete()
            
            # 删除攻略
            db.session.delete(guide)
            db.session.commit()
            
            return success_response("删除旅游攻略成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除旅游攻略失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_categories():
        """获取攻略分类列表"""
        try:
            categories = TravelGuideCategory.query.order_by(TravelGuideCategory.sort_order.asc()).all()
            
            result = [category.to_dict() for category in categories]
            
            return success_response("获取攻略分类列表成功", result)
            
        except Exception as e:
            return error_response(f"获取攻略分类列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def create_category():
        """创建攻略分类"""
        try:
            data = request.get_json()
            
            name = data.get('name', '')
            icon = data.get('icon', '')
            sort_order = data.get('sort_order', 0)
            status = data.get('status', 1)
            
            # 验证必填字段
            if not name:
                return error_response("分类名称不能为空", 400)
                
            # 创建分类
            category = TravelGuideCategory(
                name=name,
                icon=icon,
                sort_order=sort_order,
                status=status
            )
            
            db.session.add(category)
            db.session.commit()
            
            return success_response("创建攻略分类成功", category.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建攻略分类失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_category(category_id):
        """更新攻略分类"""
        try:
            category = TravelGuideCategory.query.get(category_id)
            
            if not category:
                return error_response("攻略分类不存在", 404)
                
            data = request.get_json()
            
            # 可更新的字段
            updatable_fields = ['name', 'icon', 'sort_order', 'status']
            
            for field in updatable_fields:
                if field in data:
                    setattr(category, field, data[field])
            
            category.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新攻略分类成功", category.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新攻略分类失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def delete_category(category_id):
        """删除攻略分类"""
        try:
            category = TravelGuideCategory.query.get(category_id)
            
            if not category:
                return error_response("攻略分类不存在", 404)
                
            # 检查是否有攻略使用此分类
            guide_count = TravelGuide.query.filter_by(category_id=category_id).count()
            if guide_count > 0:
                return error_response(f"无法删除该分类，有{guide_count}个攻略使用了此分类", 400)
                
            # 删除分类
            db.session.delete(category)
            db.session.commit()
            
            return success_response("删除攻略分类成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除攻略分类失败: {str(e)}", 500) 