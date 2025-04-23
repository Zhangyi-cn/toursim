from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from datetime import datetime

from models.comment import Comment
from models.user import User
from models.attraction import Attraction
from models.travel_note import TravelNote
from models.travel_guide import TravelGuide
from extensions import db
from utils.response import success_response, error_response, pagination_response
from utils.validator import get_page_params
from utils.auth import admin_required

admin_comment_bp = Blueprint('admin_comment', __name__)


class AdminCommentController:
    """后台评论管理控制器"""
    
    @staticmethod
    @admin_comment_bp.route('', methods=['GET'])
    @admin_required
    def get_comments():
        """
        获取评论列表
        ---
        tags:
          - 后台评论管理
        parameters:
          - name: keyword
            in: query
            type: string
            description: 关键词(评论内容)
          - name: user_id
            in: query
            type: integer
            description: 用户ID
          - name: target_type
            in: query
            type: string
            enum: [attraction, note, guide]
            description: 目标类型
          - name: target_id
            in: query
            type: integer
            description: 目标ID
          - name: status
            in: query
            type: integer
            enum: [0, 1, 2]
            description: 状态(0-待审核,1-已发布,2-已拒绝)
          - name: start_date
            in: query
            type: string
            format: date
            description: 开始日期
          - name: end_date
            in: query
            type: string
            format: date
            description: 结束日期
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        # 获取参数
        keyword = request.args.get('keyword', '').strip()
        user_id = request.args.get('user_id', type=int)
        target_type = request.args.get('target_type')
        target_id = request.args.get('target_id', type=int)
        status = request.args.get('status', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page, per_page = get_page_params()
        
        # 构建查询
        query = Comment.query
        
        # 应用过滤条件
        if keyword:
            query = query.filter(Comment.content.like(f'%{keyword}%'))
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if target_type:
            query = query.filter_by(target_type=target_type)
        
        if target_id:
            query = query.filter_by(target_id=target_id)
        
        if status is not None:
            query = query.filter_by(status=status)
        
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Comment.created_at >= start_datetime)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                query = query.filter(Comment.created_at <= end_datetime)
            except ValueError:
                pass
        
        # 应用排序 - 默认按创建时间倒序
        query = query.order_by(desc(Comment.created_at))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for comment in paginate.items:
            comment_data = comment.to_dict()
            
            # 获取用户信息
            user = User.query.get(comment.user_id)
            if user:
                comment_data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname,
                    'avatar': user.avatar
                }
            
            # 获取目标信息
            target_name = ""
            if comment.target_type == 'attraction':
                target = Attraction.query.get(comment.target_id)
                if target:
                    target_name = target.name
            elif comment.target_type == 'note':
                target = TravelNote.query.get(comment.target_id)
                if target:
                    target_name = target.title
            elif comment.target_type == 'guide':
                target = TravelGuide.query.get(comment.target_id)
                if target:
                    target_name = target.title
            
            comment_data['target_name'] = target_name
            
            # 获取回复数量
            if not comment.parent_id:
                replies_count = Comment.query.filter_by(parent_id=comment.id).count()
                comment_data['replies_count'] = replies_count
            
            items.append(comment_data)
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="获取评论列表成功"
        ))
    
    @staticmethod
    @admin_comment_bp.route('/<int:comment_id>', methods=['GET'])
    @admin_required
    def get_comment_detail(comment_id):
        """
        获取评论详情
        ---
        tags:
          - 后台评论管理
        parameters:
          - name: comment_id
            in: path
            required: true
            type: integer
            description: 评论ID
        """
        # 查询评论
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify(error_response("评论不存在")), 404
        
        # 准备评论数据
        comment_data = comment.to_dict()
        
        # 获取用户信息
        user = User.query.get(comment.user_id)
        if user:
            comment_data['user'] = {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'avatar': user.avatar
            }
        
        # 获取目标信息
        target_info = {}
        if comment.target_type == 'attraction':
            target = Attraction.query.get(comment.target_id)
            if target:
                target_info = {
                    'id': target.id,
                    'name': target.name,
                    'cover_image': target.cover_image
                }
        elif comment.target_type == 'note':
            target = TravelNote.query.get(comment.target_id)
            if target:
                target_info = {
                    'id': target.id,
                    'title': target.title,
                    'cover_image': target.cover_image
                }
        elif comment.target_type == 'guide':
            target = TravelGuide.query.get(comment.target_id)
            if target:
                target_info = {
                    'id': target.id,
                    'title': target.title,
                    'cover_image': target.cover_image
                }
        
        comment_data['target_info'] = target_info
        
        # 如果是回复，获取父评论
        if comment.parent_id:
            parent_comment = Comment.query.get(comment.parent_id)
            if parent_comment:
                parent_user = User.query.get(parent_comment.user_id)
                parent_info = {
                    'id': parent_comment.id,
                    'content': parent_comment.content,
                    'user': {
                        'id': parent_user.id,
                        'nickname': parent_user.nickname
                    } if parent_user else None
                }
                comment_data['parent_comment'] = parent_info
        
        # 获取评论回复列表
        if not comment.parent_id:
            replies = Comment.query.filter_by(
                parent_id=comment.id
            ).order_by(desc(Comment.created_at)).all()
            
            replies_data = []
            for reply in replies:
                reply_data = reply.to_dict()
                
                # 获取回复用户信息
                reply_user = User.query.get(reply.user_id)
                if reply_user:
                    reply_data['user'] = {
                        'id': reply_user.id,
                        'username': reply_user.username,
                        'nickname': reply_user.nickname,
                        'avatar': reply_user.avatar
                    }
                
                # 获取被回复用户信息
                if reply.reply_to:
                    reply_to_user = User.query.get(reply.reply_to)
                    if reply_to_user:
                        reply_data['reply_to_user'] = {
                            'id': reply_to_user.id,
                            'nickname': reply_to_user.nickname
                        }
                
                replies_data.append(reply_data)
            
            comment_data['replies'] = replies_data
        
        return jsonify(success_response("获取评论详情成功", comment_data))
    
    @staticmethod
    @admin_comment_bp.route('/<int:comment_id>/approve', methods=['POST'])
    @admin_required
    def approve_comment(comment_id):
        """
        审核通过评论
        ---
        tags:
          - 后台评论管理
        parameters:
          - name: comment_id
            in: path
            required: true
            type: integer
            description: 评论ID
        """
        # 查询评论
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify(error_response("评论不存在")), 404
        
        # 更新评论状态
        comment.status = 1  # 1-已发布
        
        try:
            db.session.commit()
            return jsonify(success_response("评论审核通过"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"操作失败: {str(e)}")), 500
    
    @staticmethod
    @admin_comment_bp.route('/<int:comment_id>/reject', methods=['POST'])
    @admin_required
    def reject_comment(comment_id):
        """
        拒绝评论
        ---
        tags:
          - 后台评论管理
        parameters:
          - name: comment_id
            in: path
            required: true
            type: integer
            description: 评论ID
          - name: body
            in: body
            required: true
            schema:
              properties:
                reason:
                  type: string
                  description: 拒绝原因
        """
        # 获取请求数据
        data = request.get_json()
        reason = data.get('reason', '')
        
        # 查询评论
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify(error_response("评论不存在")), 404
        
        # 更新评论状态
        comment.status = 2  # 2-已拒绝
        comment.reject_reason = reason
        
        try:
            db.session.commit()
            return jsonify(success_response("评论已拒绝"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"操作失败: {str(e)}")), 500
    
    @staticmethod
    @admin_comment_bp.route('/<int:comment_id>', methods=['DELETE'])
    @admin_required
    def delete_comment(comment_id):
        """
        删除评论
        ---
        tags:
          - 后台评论管理
        parameters:
          - name: comment_id
            in: path
            required: true
            type: integer
            description: 评论ID
        """
        # 查询评论
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify(error_response("评论不存在")), 404
        
        try:
            # 如果是一级评论，删除所有回复
            if not comment.parent_id:
                replies = Comment.query.filter_by(parent_id=comment.id).all()
                for reply in replies:
                    db.session.delete(reply)
            
            # 删除评论
            db.session.delete(comment)
            db.session.commit()
            
            return jsonify(success_response("评论已删除"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"删除评论失败: {str(e)}")), 500

    @staticmethod
    @admin_comment_bp.route('/stats', methods=['GET'])
    @admin_required
    def get_comment_stats():
        # Implementation of get_comment_stats method
        pass 