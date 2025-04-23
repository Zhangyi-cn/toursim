from flask import request, jsonify, g, Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

from models.user import User
from extensions import db
from utils.response import success_response, error_response
from utils.auth import get_current_user, admin_required
from utils.validator import validate_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

class AdminController:
    """管理员控制器"""
    
    @staticmethod
    def login():
        """
        管理员登录
        """
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify(error_response("用户名和密码不能为空"))
        
        # 查找用户并验证是否为管理员
        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password) or user.role != 1:
            return jsonify(error_response("用户名或密码错误"))
        
        if user.status != 1:
            return jsonify(error_response("账号已被禁用"))
        
        # 生成JWT令牌
        access_token = create_access_token(
            identity=str(user.id),  # 确保identity是字符串
            additional_claims={'is_admin': True}
        )
        
        return jsonify(success_response({
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'email': user.email,
                'role': user.role
            }
        }))
    
    @staticmethod
    @jwt_required()
    def logout():
        """管理员退出登录"""
        return jsonify(success_response("退出登录成功"))
    
    @staticmethod
    @admin_required
    def get_profile():
        """获取管理员个人资料"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(error_response("用户不存在"))
        
        return jsonify(success_response({
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'status': user.status,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }))
    
    @staticmethod
    @admin_required
    def change_password():
        """修改管理员密码"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(error_response("用户不存在"))
        
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify(error_response("旧密码和新密码不能为空"))
        
        if not user.verify_password(old_password):
            return jsonify(error_response("旧密码错误"))
        
        user.password = new_password
        db.session.commit()
        
        return jsonify(success_response("密码修改成功"))
    
    @staticmethod
    @admin_required
    def get_dashboard():
        """获取仪表盘数据"""
        try:
            # 统计用户数
            user_count = User.query.filter_by(is_admin=False).count()
            
            # 统计今日新增用户
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            new_user_count = User.query.filter(
                User.is_admin==False,
                User.created_at >= today_start
            ).count()
            
            # TODO: 添加更多仪表盘数据
            
            return jsonify(success_response({
                'user_count': user_count,
                'new_user_count': new_user_count
            }))
            
        except Exception as e:
            return jsonify(error_response(f"获取仪表盘数据失败: {str(e)}", 500))
    
