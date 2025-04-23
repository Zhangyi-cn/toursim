from flask import request, jsonify, g
from flask_jwt_extended import jwt_required
from datetime import datetime

from models.tag import Tag, ContentTag
from extensions import db
from utils.response import success_response, error_response
from utils.auth import admin_required

class TagAdminController:
    """标签管理控制器"""
    
    @staticmethod
    @admin_required()
    def get_tags():
        """获取标签列表"""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            keyword = request.args.get('keyword', '')
            
            query = Tag.query
            
            # 按关键词筛选
            if keyword:
                query = query.filter(Tag.name.like(f'%{keyword}%'))
                
            # 分页
            pagination = query.order_by(db.desc(Tag.created_at)).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            tags = pagination.items
            total = pagination.total
            
            # 构造返回数据
            items = []
            for tag in tags:
                tag_dict = tag.to_dict()
                
                # 统计各种内容引用数量
                attraction_count = ContentTag.query.filter_by(tag_id=tag.id, content_type='attraction').count()
                guide_count = ContentTag.query.filter_by(tag_id=tag.id, content_type='guide').count()
                note_count = ContentTag.query.filter_by(tag_id=tag.id, content_type='note').count()
                
                tag_dict['attraction_count'] = attraction_count
                tag_dict['guide_count'] = guide_count
                tag_dict['note_count'] = note_count
                tag_dict['total_usage'] = attraction_count + guide_count + note_count
                
                items.append(tag_dict)
            
            return success_response("获取标签列表成功", {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page
            })
            
        except Exception as e:
            return error_response(f"获取标签列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def create_tag():
        """创建标签"""
        try:
            data = request.get_json()
            
            name = data.get('name', '').strip()
            
            if not name:
                return error_response("标签名称不能为空", 400)
                
            # 检查是否已存在同名标签
            exist = Tag.query.filter_by(name=name).first()
            if exist:
                return error_response(f"标签 '{name}' 已存在", 400)
                
            tag = Tag(name=name)
            
            db.session.add(tag)
            db.session.commit()
            
            return success_response("创建标签成功", tag.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建标签失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_tag(tag_id):
        """更新标签"""
        try:
            tag = Tag.query.get(tag_id)
            
            if not tag:
                return error_response("标签不存在", 404)
                
            data = request.get_json()
            
            name = data.get('name', '').strip()
            
            if not name:
                return error_response("标签名称不能为空", 400)
                
            # 检查是否已存在同名标签（排除自身）
            if name != tag.name:
                exist = Tag.query.filter_by(name=name).first()
                if exist:
                    return error_response(f"标签 '{name}' 已存在", 400)
                    
                tag.name = name
                
            tag.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新标签成功", tag.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新标签失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def delete_tag(tag_id):
        """删除标签"""
        try:
            tag = Tag.query.get(tag_id)
            
            if not tag:
                return error_response("标签不存在", 404)
                
            # 检查标签是否被引用
            usage_count = ContentTag.query.filter_by(tag_id=tag_id).count()
            if usage_count > 0:
                return error_response(f"该标签已被引用 {usage_count} 次，无法删除", 400)
                
            db.session.delete(tag)
            db.session.commit()
            
            return success_response("删除标签成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除标签失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def merge_tags():
        """合并标签"""
        try:
            data = request.get_json()
            
            source_tag_ids = data.get('source_tag_ids', [])
            target_tag_id = data.get('target_tag_id')
            
            if not source_tag_ids:
                return error_response("源标签ID列表不能为空", 400)
                
            if not target_tag_id:
                return error_response("目标标签ID不能为空", 400)
                
            # 检查目标标签是否存在
            target_tag = Tag.query.get(target_tag_id)
            if not target_tag:
                return error_response("目标标签不存在", 404)
                
            # 检查源标签是否与目标标签相同
            if target_tag_id in source_tag_ids:
                return error_response("源标签不能包含目标标签", 400)
                
            # 获取源标签
            source_tags = Tag.query.filter(Tag.id.in_(source_tag_ids)).all()
            if len(source_tags) != len(source_tag_ids):
                return error_response("部分源标签不存在", 404)
                
            # 合并标签引用
            for source_tag in source_tags:
                # 更新内容标签关联
                ContentTag.query.filter_by(tag_id=source_tag.id).update({'tag_id': target_tag_id})
                
                # 删除源标签
                db.session.delete(source_tag)
                
            # 更新目标标签的使用计数
            target_tag.usage_count = ContentTag.query.filter_by(tag_id=target_tag_id).count()
            db.session.commit()
            
            return success_response("合并标签成功", target_tag.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"合并标签失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_tag_usages(tag_id):
        """获取标签使用情况"""
        try:
            tag = Tag.query.get(tag_id)
            
            if not tag:
                return error_response("标签不存在", 404)
                
            # 获取关联内容
            content_tags = ContentTag.query.filter_by(tag_id=tag_id).all()
            
            # 按内容类型分组
            usages = {
                'attraction': [],
                'guide': [],
                'note': []
            }
            
            for content_tag in content_tags:
                if content_tag.content_type in usages:
                    usages[content_tag.content_type].append(content_tag.content_id)
            
            # 构造返回数据
            result = {
                'tag': tag.to_dict(),
                'usages': {
                    'attraction_count': len(usages['attraction']),
                    'guide_count': len(usages['guide']),
                    'note_count': len(usages['note']),
                    'total_count': len(content_tags)
                }
            }
            
            return success_response("获取标签使用情况成功", result)
            
        except Exception as e:
            return error_response(f"获取标签使用情况失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_popular_tags():
        """获取热门标签"""
        try:
            limit = int(request.args.get('limit', 20))
            
            # 使用子查询统计每个标签被使用的次数
            from sqlalchemy import func
            tag_counts = db.session.query(
                ContentTag.tag_id,
                func.count(ContentTag.id).label('count')
            ).group_by(ContentTag.tag_id).subquery()
            
            # 获取标签，按使用次数排序
            tags = db.session.query(Tag).\
                outerjoin(tag_counts, Tag.id == tag_counts.c.tag_id).\
                order_by(db.desc(tag_counts.c.count), db.desc(Tag.created_at)).\
                limit(limit).all()
            
            items = [tag.to_dict() for tag in tags]
            
            return success_response("获取热门标签成功", items)
            
        except Exception as e:
            return error_response(f"获取热门标签失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_content_tags():
        """获取内容标签列表"""
        try:
            content_type = request.args.get('content_type')
            content_id = request.args.get('content_id')
            
            if not content_type or not content_id:
                return error_response("内容类型和ID不能为空", 400)
                
            # 获取内容的标签
            content_tags = ContentTag.query.filter_by(
                content_type=content_type,
                content_id=content_id
            ).all()
            
            # 获取标签详情
            tags = []
            for content_tag in content_tags:
                tag = Tag.query.get(content_tag.tag_id)
                if tag:
                    tag_dict = tag.to_dict()
                    tag_dict['content_tag_id'] = content_tag.id
                    tags.append(tag_dict)
            
            return success_response("获取内容标签成功", tags)
            
        except Exception as e:
            return error_response(f"获取内容标签失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def add_content_tag():
        """添加内容标签"""
        try:
            data = request.get_json()
            
            content_type = data.get('content_type')
            content_id = data.get('content_id')
            tag_name = data.get('tag_name', '').strip()
            
            if not content_type or not content_id or not tag_name:
                return error_response("内容类型、ID和标签名称不能为空", 400)
                
            # 查找或创建标签
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.flush()
                
            # 检查标签是否已添加
            exist = ContentTag.query.filter_by(
                content_type=content_type,
                content_id=content_id,
                tag_id=tag.id
            ).first()
            
            if exist:
                return error_response(f"标签 '{tag_name}' 已添加", 400)
                
            # 创建内容标签关联
            content_tag = ContentTag(
                content_type=content_type,
                content_id=content_id,
                tag_id=tag.id
            )
            
            db.session.add(content_tag)
            
            # 更新标签使用计数
            tag.usage_count = ContentTag.query.filter_by(tag_id=tag.id).count() + 1
            
            db.session.commit()
            
            # 返回标签信息
            tag_dict = tag.to_dict()
            tag_dict['content_tag_id'] = content_tag.id
            
            return success_response("添加内容标签成功", tag_dict)
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"添加内容标签失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def delete_content_tag(content_tag_id):
        """删除内容标签"""
        try:
            content_tag = ContentTag.query.get(content_tag_id)
            
            if not content_tag:
                return error_response("内容标签不存在", 404)
                
            # 获取标签
            tag = Tag.query.get(content_tag.tag_id)
            
            # 删除内容标签关联
            db.session.delete(content_tag)
            
            # 更新标签使用计数
            if tag:
                tag.usage_count = ContentTag.query.filter_by(tag_id=tag.id).count()
            
            db.session.commit()
            
            return success_response("删除内容标签成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除内容标签失败: {str(e)}", 500) 