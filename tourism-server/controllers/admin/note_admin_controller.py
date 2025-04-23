from flask import request, jsonify, g, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

from models.travel_note import TravelNote, TravelNoteImage
from models.comment import Comment as TravelNoteComment
from models.user import User
from models.tag import Tag, ContentTag
from extensions import db
from utils.response import success_response, error_response
from utils.auth import admin_required

class NoteAdminController:
    """旅行笔记管理控制器"""
    
    @staticmethod
    @admin_required()
    def get_notes():
        """获取旅行笔记列表"""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            keyword = request.args.get('keyword', '')
            status = request.args.get('status')
            
            query = TravelNote.query
            
            # 按关键词筛选
            if keyword:
                query = query.filter(TravelNote.title.like(f'%{keyword}%'))
                
            # 按状态筛选
            if status is not None:
                query = query.filter(TravelNote.status == status)
                
            # 分页
            pagination = query.order_by(TravelNote.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            notes = pagination.items
            total = pagination.total
            
            # 构造返回数据
            items = []
            for note in notes:
                note_dict = note.to_dict()
                
                # 获取用户信息
                if note.user_id:
                    user = User.query.get(note.user_id)
                    if user:
                        note_dict['user'] = {
                            'id': user.id,
                            'username': user.username,
                            'nickname': user.nickname,
                            'avatar': user.avatar
                        }
                        
                # 获取标签
                tags = db.session.query(Tag).join(ContentTag).filter(
                    ContentTag.content_id == note.id,
                    ContentTag.content_type == 'note'
                ).all()
                
                note_dict['tags'] = [tag.to_dict() for tag in tags]
                
                # 获取图片数量
                image_count = TravelNoteImage.query.filter_by(note_id=note.id).count()
                note_dict['image_count'] = image_count
                
                # 获取评论数量
                comment_count = TravelNoteComment.query.filter_by(
                    content_id=note.id,
                    content_type='travel_note'
                ).count()
                note_dict['comment_count'] = comment_count
                
                items.append(note_dict)
            
            return success_response("获取旅行笔记列表成功", {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page
            })
            
        except Exception as e:
            return error_response(f"获取旅行笔记列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_note(note_id):
        """获取旅行笔记详情"""
        try:
            note = TravelNote.query.get(note_id)
            
            if not note:
                return error_response("旅行笔记不存在", 404)
                
            note_dict = note.to_dict()
            
            # 获取用户信息
            if note.user_id:
                user = User.query.get(note.user_id)
                if user:
                    note_dict['user'] = {
                        'id': user.id,
                        'username': user.username,
                        'nickname': user.nickname,
                        'avatar': user.avatar
                    }
                    
            # 获取标签
            tags = db.session.query(Tag).join(ContentTag).filter(
                ContentTag.content_id == note.id,
                ContentTag.content_type == 'note'
            ).all()
            
            note_dict['tags'] = [tag.name for tag in tags]
            
            # 获取图片
            images = TravelNoteImage.query.filter_by(note_id=note.id).order_by(TravelNoteImage.sort_order.asc()).all()
            note_dict['images'] = [image.to_dict() for image in images]
            
            return success_response("获取旅行笔记详情成功", note_dict)
            
        except Exception as e:
            return error_response(f"获取旅行笔记详情失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_note(note_id):
        """更新旅行笔记"""
        try:
            note = TravelNote.query.get(note_id)
            
            if not note:
                return error_response("旅行笔记不存在", 404)
                
            data = request.get_json()
            
            # 可更新的字段
            updatable_fields = [
                'title', 'content', 'destination', 'cover_image', 'status', 
                'visibility', 'view_count', 'like_count', 'comment_count', 
                'featured', 'featured_at'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(note, field, data[field])
            
            # 更新标签
            if 'tags' in data:
                # 删除旧标签关联
                ContentTag.query.filter_by(content_id=note.id, content_type='note').delete()
                
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
                        content_id=note.id,
                        content_type='note',
                        tag_id=tag.id
                    )
                    db.session.add(content_tag)
            
            note.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新旅行笔记成功", note.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新旅行笔记失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def delete_note(note_id):
        """删除旅行笔记"""
        try:
            note = TravelNote.query.get(note_id)
            
            if not note:
                return error_response("旅行笔记不存在", 404)
                
            # 删除标签关联
            ContentTag.query.filter_by(content_id=note_id, content_type='note').delete()
            
            # 删除图片
            TravelNoteImage.query.filter_by(note_id=note_id).delete()
            
            # 删除评论
            TravelNoteComment.query.filter_by(note_id=note_id).delete()
            
            # 删除笔记
            db.session.delete(note)
            db.session.commit()
            
            return success_response("删除旅行笔记成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除旅行笔记失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_comments():
        """获取笔记评论列表"""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            note_id = request.args.get('note_id')
            
            query = TravelNoteComment.query
            
            # 按笔记ID筛选
            if note_id:
                query = query.filter(TravelNoteComment.note_id == note_id)
                
            # 分页
            pagination = query.order_by(TravelNoteComment.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            comments = pagination.items
            total = pagination.total
            
            # 构造返回数据
            items = []
            for comment in comments:
                comment_dict = comment.to_dict()
                
                # 获取用户信息
                if comment.user_id:
                    user = User.query.get(comment.user_id)
                    if user:
                        comment_dict['user'] = {
                            'id': user.id,
                            'username': user.username,
                            'nickname': user.nickname,
                            'avatar': user.avatar
                        }
                        
                # 获取笔记信息
                if comment.note_id:
                    note = TravelNote.query.get(comment.note_id)
                    if note:
                        comment_dict['note'] = {
                            'id': note.id,
                            'title': note.title
                        }
                        
                items.append(comment_dict)
            
            return success_response("获取笔记评论列表成功", {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page
            })
            
        except Exception as e:
            return error_response(f"获取笔记评论列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def delete_comment(comment_id):
        """删除笔记评论"""
        try:
            comment = TravelNoteComment.query.get(comment_id)
            
            if not comment:
                return error_response("评论不存在", 404)
                
            db.session.delete(comment)
            db.session.commit()
            
            # 更新评论数量
            note = TravelNote.query.get(comment.note_id)
            if note:
                comment_count = TravelNoteComment.query.filter_by(note_id=note.id).count()
                note.comment_count = comment_count
                db.session.commit()
            
            return success_response("删除评论成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除评论失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def feature_note(note_id):
        """将笔记设为精选"""
        try:
            note = TravelNote.query.get(note_id)
            
            if not note:
                return error_response("旅行笔记不存在", 404)
                
            note.featured = True
            note.featured_at = datetime.now()
            db.session.commit()
            
            return success_response("设置精选成功", note.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"设置精选失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def unfeature_note(note_id):
        """取消笔记精选状态"""
        try:
            note = TravelNote.query.get(note_id)
            
            if not note:
                return error_response("旅行笔记不存在", 404)
                
            note.featured = False
            note.featured_at = None
            db.session.commit()
            
            return success_response("取消精选成功", note.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"取消精选失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_note_status(note_id):
        """更新游记状态"""
        try:
            note = TravelNote.query.get(note_id)
            
            if not note:
                return error_response("游记不存在", 404)
                
            data = request.get_json()
            status = data.get('status')
            
            if status is None:
                return error_response("状态参数不能为空", 400)
                
            # 更新状态
            note.status = status
            note.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新游记状态成功", note.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新游记状态失败: {str(e)}", 500) 