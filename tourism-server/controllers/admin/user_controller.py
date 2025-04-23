from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from utils.auth import admin_required
from utils.response import success_response, error_response
from models.user import User
from extensions import db
from datetime import datetime

# 创建用户管理蓝图
admin_user_bp = Blueprint('admin_user', __name__)


@admin_user_bp.route('/batch/enable', methods=['POST'])
@admin_required
def batch_enable_users():
    """批量启用用户"""
    try:
        # 获取用户ID列表
        user_ids = request.json.get('user_ids', [])
        if not user_ids:
            return error_response('请选择要启用的用户')

        # 更新用户状态
        User.query.filter(User.id.in_(user_ids)).update(
            {
                'is_active': True,
                'updated_at': datetime.now()
            },
            synchronize_session=False
        )
        db.session.commit()

        return success_response('启用成功')

    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@admin_user_bp.route('/batch/disable', methods=['POST'])
@admin_required
def batch_disable_users():
    """批量禁用用户"""
    try:
        # 获取用户ID列表
        user_ids = request.json.get('user_ids', [])
        if not user_ids:
            return error_response('请选择要禁用的用户')

        # 更新用户状态
        User.query.filter(User.id.in_(user_ids)).update(
            {
                'is_active': False,
                'updated_at': datetime.now()
            },
            synchronize_session=False
        )
        db.session.commit()

        return success_response('禁用成功')

    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@admin_user_bp.route('/batch/delete', methods=['POST'])
@admin_required
def batch_delete_users():
    """批量删除用户"""
    try:
        # 获取用户ID列表
        user_ids = request.json.get('user_ids', [])
        if not user_ids:
            return error_response('请选择要删除的用户')

        # 删除用户
        User.query.filter(User.id.in_(user_ids)).delete(synchronize_session=False)
        db.session.commit()

        return success_response('删除成功')

    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@admin_user_bp.route('/batch/reset-password', methods=['POST'])
@admin_required
def batch_reset_password():
    """批量重置密码"""
    try:
        # 获取用户ID列表和新密码
        user_ids = request.json.get('user_ids', [])
        new_password = request.json.get('password')
        
        if not user_ids:
            return error_response('请选择要重置密码的用户')
        if not new_password:
            return error_response('请提供新密码')

        # 更新密码
        users = User.query.filter(User.id.in_(user_ids)).all()
        for user in users:
            user.set_password(new_password)
            user.updated_at = datetime.now()
        
        db.session.commit()

        return success_response('密码重置成功')

    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@admin_user_bp.route('/statistics', methods=['GET'])
@admin_required
def get_user_statistics():
    """获取用户统计数据"""
    try:
        # 总用户数
        total_users = User.query.count()
        
        # 活跃用户数
        active_users = User.query.filter_by(is_active=True).count()
        
        # 今日新增用户数
        today = datetime.now().date()
        new_users_today = User.query.filter(
            db.func.date(User.created_at) == today
        ).count()
        
        # 本月新增用户数
        this_month = today.replace(day=1)
        new_users_month = User.query.filter(
            db.func.date(User.created_at) >= this_month
        ).count()

        return success_response(data={
            'total_users': total_users,
            'active_users': active_users,
            'new_users_today': new_users_today,
            'new_users_month': new_users_month
        })

    except Exception as e:
        return error_response(str(e))


@staticmethod
@admin_required
def get_users():
    """获取用户列表"""


@staticmethod
@admin_required
def get_user(user_id):
    """获取用户详情"""


@staticmethod
@admin_required
def update_user(user_id):
    """更新用户信息"""


@staticmethod
@admin_required
def delete_user(user_id):
    """删除用户"""


@staticmethod
@admin_required
def reset_password(user_id):
    """重置用户密码""" 