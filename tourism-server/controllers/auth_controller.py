from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt

from models.user import User
from extensions import db
from utils.response import success_response, error_response
from utils.auth import generate_token_payload, get_current_user
from utils.validator import validate_required, is_valid_email, is_valid_phone, is_valid_password

# 创建蓝图
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'password', 'email']
        is_valid, errors = validate_required(data, required_fields)
        if not is_valid:
            return jsonify(error_response("注册信息不完整", errors=errors)), 400
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        nickname = data.get('nickname', username)
        
        # 验证用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify(error_response("用户名已存在")), 400
        
        # 验证邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify(error_response("邮箱已被注册")), 400
        
        # 验证手机号是否已存在
        if phone and User.query.filter_by(phone=phone).first():
            return jsonify(error_response("手机号已被注册")), 400
        
        # 验证邮箱格式
        if not is_valid_email(email):
            return jsonify(error_response("邮箱格式不正确")), 400
        
        # 验证手机号格式
        if phone and not is_valid_phone(phone):
            return jsonify(error_response("手机号格式不正确")), 400
        
        # 验证密码强度
        if not is_valid_password(password):
            return jsonify(error_response("密码不符合要求，密码长度至少为6位")), 400
        
        # 创建新用户
        user = User(
            username=username,
            password=password,  # 使用password属性，它会自动加密
            email=email,
            phone=phone if phone else None,  # 如果手机号为空，设置为None
            nickname=nickname,
            status=1,  # 激活状态
            role=0,  # 普通用户
            created_at=datetime.now()
        )
        db.session.add(user)
        db.session.commit()
        
        # 生成令牌负载和访问令牌
        token_payload = generate_token_payload(user)
        access_token = create_access_token(identity=str(user.id), additional_claims=token_payload)
        
        return jsonify(success_response("注册成功", {
            "token": access_token,
            "user": user.to_dict()
        })), 201
        
    except Exception as e:
        current_app.logger.error(f"用户注册失败: {str(e)}")
        db.session.rollback()
        return jsonify(error_response("注册失败，服务器错误")), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['username', 'password']
    is_valid, errors = validate_required(data, required_fields)
    if not is_valid:
        return jsonify(error_response("登录信息不完整", errors=errors)), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # 查询用户 (支持用户名/邮箱/手机号登录)
    user = User.query.filter(
        (User.username == username) | 
        (User.email == username) | 
        (User.phone == username)
    ).first()
    
    # 验证用户是否存在
    if not user:
        return jsonify(error_response("用户不存在")), 404
    
    # 验证密码
    if not user.verify_password(password):
        return jsonify(error_response("密码错误")), 401
    
    # 验证用户状态
    if user.status != 1:
        return jsonify(error_response("账号已禁用")), 403
    
    # 生成令牌负载和访问令牌
    token_payload = generate_token_payload(user)
    access_token = create_access_token(identity=str(user.id), additional_claims=token_payload)
    
    # 更新用户最后登录时间
    user.last_login = datetime.now()
    db.session.commit()
    
    return jsonify(success_response("登录成功", {
        "token": access_token,
        "user": user.to_dict()
    }))


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error_response("用户不存在")), 404
    
    # 生成令牌负载和访问令牌
    token_payload = generate_token_payload(user)
    access_token = create_access_token(identity=str(user.id), additional_claims=token_payload)
    
    return jsonify(success_response("刷新令牌成功", {
        "token": access_token,
        "user": user.to_dict()
    }))


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    return jsonify(success_response("退出登录成功"))


@auth_bp.route('/check', methods=['GET'])
@jwt_required()
def check_auth():
    """检查认证状态"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    return jsonify(success_response("认证有效", {
        "user": current_user.to_dict()
    }))


# 注释掉管理员登录路由，使用routes/admin.py中的实现
# @auth_bp.route('/admin/login', methods=['POST'])
# def admin_login():
#     """管理员登录"""
#     data = request.get_json()
#     
#     # 验证必填字段
#     required_fields = ['username', 'password']
#     is_valid, errors = validate_required(data, required_fields)
#     if not is_valid:
#         return jsonify(error_response("登录信息不完整", errors=errors)), 400
#     
#     username = data.get('username')
#     password = data.get('password')
#     
#     # 查询用户
#     user = User.query.filter_by(username=username, is_admin=True).first()
#     
#     # 验证用户是否存在
#     if not user:
#         return jsonify(error_response("管理员不存在")), 404
#     
#     # 验证密码
#     if not user.verify_password(password):
#         # 记录登录失败日志
#         LoginLog.add_login_log(
#             user_id=user.id,
#             ip=request.remote_addr,
#             user_agent=request.user_agent.string,
#             status=0,
#             remark="管理员密码错误"
#         )
#         return jsonify(error_response("密码错误")), 401
#     
#     # 验证用户状态
#     if user.status != 1:
#         # 记录登录失败日志
#         LoginLog.add_login_log(
#             user_id=user.id,
#             ip=request.remote_addr,
#             user_agent=request.user_agent.string,
#             status=0,
#             remark="管理员账号已禁用"
#         )
#         return jsonify(error_response("账号已禁用")), 403
#     
#     # 生成令牌负载和访问令牌
#     token_payload = generate_token_payload(user)
#     access_token = create_access_token(identity=str(user.id), additional_claims=token_payload)
#     
#     # 更新用户最后登录时间
#     user.last_login = datetime.now()
#     db.session.commit()
#     
#     # 记录登录日志
#     LoginLog.add_login_log(
#         user_id=user.id,
#         ip=request.remote_addr,
#         user_agent=request.user_agent.string,
#         status=1,
#         remark="管理员登录成功"
#     ) 