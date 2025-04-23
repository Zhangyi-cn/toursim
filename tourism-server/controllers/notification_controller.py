from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import desc

from models.notification import Notification
from models.user import User
from extensions import db
from utils.response import success_response, error_response, pagination_response
from utils.auth import get_current_user, login_required
from utils.validator import get_page_params

# 创建蓝图
notification_bp = Blueprint('notification', __name__, url_prefix='')


class NotificationController:
    """通知控制器"""
    
    @staticmethod
    @notification_bp.route('', methods=['GET'])
    @jwt_required()
    def get_notifications():
        """
        获取用户通知列表
        ---
        tags:
          - 通知
        parameters:
          - name: is_read
            in: query
            type: boolean
            description: 是否已读(不传则获取全部)
          - name: type
            in: query
            type: integer
            enum: [1, 2, 3]
            description: 通知类型(1系统,2活动,3订单)
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify(error_response("用户未找到")), 404
        
        # 获取分页参数
        page, per_page = get_page_params()
        
        # 获取过滤参数
        is_read = request.args.get('is_read')
        type_filter = request.args.get('type')
        
        # 构建查询
        query = Notification.query.filter_by(user_id=user_id)
        
        # 按已读状态过滤
        if is_read is not None:
            is_read_bool = (is_read.lower() == 'true')
            query = query.filter_by(is_read=is_read_bool)
        
        # 按通知类型过滤
        if type_filter:
            try:
                type_filter = int(type_filter)
                query = query.filter_by(type=type_filter)
            except ValueError:
                pass
        
        # 按创建时间倒序排序
        query = query.order_by(desc(Notification.created_at))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for notification in paginate.items:
            items.append(notification.to_dict())
        
        # 获取未读通知数量
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            extras={'unread_count': unread_count},
            message="获取通知列表成功"
        ))
    
    @staticmethod
    @notification_bp.route('/unread/count', methods=['GET'])
    @jwt_required()
    def get_unread_count():
        """
        获取未读通知数量
        ---
        tags:
          - 通知
        """
        user_id = get_jwt_identity()
        
        # 统计未读通知数量
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return jsonify(success_response("获取未读通知数量成功", {
            'unread_count': unread_count
        }))
    
    @staticmethod
    @notification_bp.route('/<int:notification_id>/read', methods=['POST'])
    @jwt_required()
    def mark_as_read(notification_id):
        """
        标记通知为已读
        ---
        tags:
          - 通知
        parameters:
          - name: notification_id
            in: path
            required: true
            type: integer
            description: 通知ID
        """
        user_id = get_jwt_identity()
        
        # 查询通知
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if not notification:
            return jsonify(error_response("通知不存在")), 404
        
        # 标记为已读
        if not notification.is_read:
            notification.is_read = True
            notification.read_time = datetime.now()
            db.session.commit()
        
        return jsonify(success_response("标记为已读成功"))
    
    @staticmethod
    @notification_bp.route('/read/all', methods=['POST'])
    @jwt_required()
    def mark_all_as_read():
        """
        标记所有通知为已读
        ---
        tags:
          - 通知
        """
        user_id = get_jwt_identity()
        
        try:
            # 查询所有未读通知
            notifications = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).all()
            
            # 批量更新为已读
            now = datetime.now()
            for notification in notifications:
                notification.is_read = True
                notification.read_time = now
            
            db.session.commit()
            
            return jsonify(success_response(f"已将{len(notifications)}条通知标记为已读"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"标记已读失败: {str(e)}")), 500
    
    @staticmethod
    @notification_bp.route('/<int:notification_id>', methods=['DELETE'])
    @jwt_required()
    def delete_notification(notification_id):
        """
        删除通知
        ---
        tags:
          - 通知
        parameters:
          - name: notification_id
            in: path
            required: true
            type: integer
            description: 通知ID
        """
        user_id = get_jwt_identity()
        
        # 查询通知
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if not notification:
            return jsonify(error_response("通知不存在")), 404
        
        try:
            # 删除通知
            db.session.delete(notification)
            db.session.commit()
            
            return jsonify(success_response("删除通知成功"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"删除通知失败: {str(e)}")), 500
    
    @staticmethod
    @notification_bp.route('/clear', methods=['DELETE'])
    @jwt_required()
    def clear_notifications():
        """
        清空通知
        ---
        tags:
          - 通知
        parameters:
          - name: is_read
            in: query
            type: boolean
            description: 只清空已读/未读通知(不传则清空全部)
        """
        user_id = get_jwt_identity()
        is_read = request.args.get('is_read')
        
        try:
            # 构建删除查询
            query = Notification.query.filter_by(user_id=user_id)
            
            # 按已读状态过滤
            if is_read is not None:
                is_read_bool = (is_read.lower() == 'true')
                query = query.filter_by(is_read=is_read_bool)
            
            # 执行删除
            count = query.delete()
            db.session.commit()
            
            return jsonify(success_response(f"成功清空{count}条通知"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"清空通知失败: {str(e)}")), 500
    
    @staticmethod
    def send_notification(user_id, title, content, type=1, target_id=None, target_type=None, sender_id=None):
        """
        发送通知（非路由方法，供其他控制器调用）
        
        :param user_id: 用户ID
        :param title: 标题
        :param content: 内容
        :param type: 通知类型(1系统,2活动,3订单)
        :param target_id: 目标ID
        :param target_type: 目标类型
        :param sender_id: 发送者ID
        :return: 通知对象
        """
        try:
            return Notification.send_notification(
                user_id=user_id,
                title=title,
                content=content,
                type=type,
                target_id=target_id,
                target_type=target_type,
                sender_id=sender_id
            )
        except Exception as e:
            db.session.rollback()
            return None
    
    @staticmethod
    def send_system_notification(user_ids, title, content):
        """
        发送系统通知（非路由方法，供其他控制器调用）
        
        :param user_ids: 用户ID列表
        :param title: 标题
        :param content: 内容
        :return: 通知对象列表
        """
        try:
            return Notification.send_system_notification(
                user_ids=user_ids,
                title=title,
                content=content
            )
        except Exception as e:
            db.session.rollback()
            return [] 