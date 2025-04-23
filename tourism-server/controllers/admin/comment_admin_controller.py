from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.comment import Comment as TravelNoteComment
from models.user import User
from utils.response import success_response, error_response
from utils.pagination import paginate
from utils.auth import admin_required


class CommentAdminController:
    """评论管理控制器"""

    @staticmethod
    def get_comments():
        """获取评论列表"""
        try:
            # 获取查询参数
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            keyword = request.args.get('keyword', '')
            status = request.args.get('status', None)
            content_id = request.args.get('content_id', None)
            content_type = request.args.get('content_type', None)

            # 构建查询
            query = TravelNoteComment.query

            # 按内容ID和类型筛选
            if content_id:
                query = query.filter(TravelNoteComment.content_id == content_id)
            if content_type:
                query = query.filter(TravelNoteComment.content_type == content_type)

            # 按状态筛选
            if status is not None:
                query = query.filter(TravelNoteComment.status == int(status))

            # 按关键词搜索
            if keyword:
                query = query.filter(TravelNoteComment.content.like(f'%{keyword}%'))

            # 按创建时间倒序排序
            query = query.order_by(TravelNoteComment.created_at.desc())

            # 分页
            pagination = paginate(query, page, per_page)
            
            # 转换为字典
            comments = [comment.to_dict() for comment in pagination.items]
            
            return success_response(data={
                'items': comments,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            })
            
        except Exception as e:
            return error_response(str(e))

    @staticmethod
    def get_comment(comment_id):
        """获取评论详情"""
        try:
            comment = TravelNoteComment.query.get(comment_id)
            if not comment:
                return error_response('评论不存在')
            
            return success_response(data=comment.to_dict())
            
        except Exception as e:
            return error_response(str(e))

    @staticmethod
    def update_comment_status(comment_id):
        """更新评论状态"""
        try:
            # 获取参数
            status = request.json.get('status')
            if status is None:
                return error_response('缺少状态参数')

            # 查询评论
            comment = TravelNoteComment.query.get(comment_id)
            if not comment:
                return error_response('评论不存在')

            # 更新状态
            comment.status = status
            comment.updated_at = datetime.now()
            db.session.commit()

            return success_response(data=comment.to_dict())

        except Exception as e:
            db.session.rollback()
            return error_response(str(e))

    @staticmethod
    def delete_comment(comment_id):
        """删除评论"""
        try:
            # 查询评论
            comment = TravelNoteComment.query.get(comment_id)
            if not comment:
                return error_response('评论不存在')

            # 删除评论
            db.session.delete(comment)
            db.session.commit()

            return success_response('删除成功')

        except Exception as e:
            db.session.rollback()
            return error_response(str(e))

    @staticmethod
    def batch_delete_comments():
        """批量删除评论"""
        try:
            # 获取评论ID列表
            comment_ids = request.json.get('comment_ids', [])
            if not comment_ids:
                return error_response('请选择要删除的评论')

            # 删除评论
            TravelNoteComment.query.filter(TravelNoteComment.id.in_(comment_ids)).delete(synchronize_session=False)
            db.session.commit()

            return success_response('删除成功')

        except Exception as e:
            db.session.rollback()
            return error_response(str(e))

    @staticmethod
    def batch_update_comment_status():
        """批量更新评论状态"""
        try:
            # 获取参数
            comment_ids = request.json.get('comment_ids', [])
            status = request.json.get('status')
            
            if not comment_ids:
                return error_response('请选择要更新的评论')
            if status is None:
                return error_response('缺少状态参数')

            # 更新状态
            TravelNoteComment.query.filter(TravelNoteComment.id.in_(comment_ids)).update(
                {
                    'status': status,
                    'updated_at': datetime.now()
                },
                synchronize_session=False
            )
            db.session.commit()

            return success_response('更新成功')

        except Exception as e:
            db.session.rollback()
            return error_response(str(e)) 