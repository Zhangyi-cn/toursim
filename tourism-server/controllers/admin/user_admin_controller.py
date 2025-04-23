from flask import request, jsonify, g
from flask_jwt_extended import jwt_required
from datetime import datetime
from werkzeug.security import generate_password_hash
import random
import string

from models.user import User
from extensions import db
from utils.response import success_response, error_response
from utils.auth import admin_required
from utils.validator import validate_required, validate_params

class UserAdminController:
    """用户管理控制器"""
    
    @staticmethod
    @admin_required()
    def create_user():
        """创建新用户"""
        try:
            data = request.get_json()
            
            # 验证必填参数
            required_fields = ['username', 'password', 'nickname', 'email']
            for field in required_fields:
                if field not in data or not data[field]:
                    return error_response(f"{field}参数不能为空", 400)
            
            # 检查用户名是否已存在
            if User.query.filter_by(username=data['username']).first():
                return error_response("用户名已存在", 400)
                
            # 检查邮箱是否已存在
            if User.query.filter_by(email=data['email']).first():
                return error_response("邮箱已存在", 400)
            
            # 创建新用户
            user = User(
                username=data['username'],
                nickname=data['nickname'],
                email=data['email'],
                phone=data.get('phone', ''),
                avatar=data.get('avatar', ''),
                bio=data.get('bio', ''),
                status=data.get('status', 1),
                is_admin=False
            )
            
            # 设置密码
            user.password = generate_password_hash(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            return success_response("创建用户成功", user.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建用户失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_users():
        """获取用户列表"""
        try:
            print("===== 开始获取用户列表 =====")
            print(f"请求参数: {request.args}")
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            keyword = request.args.get('keyword', '')
            status = request.args.get('status', type=int)
            
            print(f"分页: page={page}, per_page={per_page}")
            print(f"筛选: keyword={keyword}, status={status}")
            
            # 直接查询所有用户，不加过滤条件，看看是否有数据
            all_users = User.query.all()
            print(f"数据库中所有用户数量: {len(all_users)}")
            for u in all_users:
                print(f"用户ID: {u.id}, 用户名: {u.username}, 角色: {u.role}, 状态: {u.status}")
            
            # 构建查询
            query = User.query.filter(User.role != 1)
            
            # 测试条件，只加role条件，看筛选结果
            users_not_admin = User.query.filter(User.role != 1).all()
            print(f"非管理员用户数量 (role != 1): {len(users_not_admin)}")
            
            users_role_is_zero = User.query.filter(User.role == 0).all()
            print(f"普通用户数量 (role == 0): {len(users_role_is_zero)}")
            
            # 应用筛选
            if keyword:
                query = query.filter(User.username.ilike(f'%{keyword}%') | 
                                   User.nickname.ilike(f'%{keyword}%') | 
                                   User.email.ilike(f'%{keyword}%') |
                                   User.phone.ilike(f'%{keyword}%'))
            
            if status is not None:
                query = query.filter(User.status == status)
                
            # 排序
            query = query.order_by(User.created_at.desc())
            
            # 分页
            pagination = query.paginate(page=page, per_page=per_page)
            users = [user.to_dict() for user in pagination.items]
            
            print(f"分页后结果: 总数={pagination.total}, 当前页数据量={len(pagination.items)}")
            for i, user_dict in enumerate(users):
                print(f"结果[{i}]: ID={user_dict['id']}, 用户名={user_dict['username']}")
            
            result = {
                'items': users,
                'pagination': {
                    'total': pagination.total,
                    'page': page,
                    'per_page': per_page,
                    'pages': pagination.pages
                }
            }
            print("===== 用户列表获取完成 =====")
            print(f"返回数据: {result}")
            
            return success_response("获取用户列表成功", result)
        
        except Exception as e:
            return error_response(f"获取用户列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_user(user_id):
        """获取用户详情"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return error_response("用户不存在", 404)
                
            return success_response("获取用户详情成功", user.to_dict())
            
        except Exception as e:
            return error_response(f"获取用户详情失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_user(user_id):
        """更新用户信息"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return error_response("用户不存在", 404)
                
            data = request.get_json()
            
            # 可更新的字段
            allowed_fields = ['nickname', 'email', 'phone', 'avatar', 'bio']
            
            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])
                    
            db.session.commit()
            
            return success_response("更新用户成功", user.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新用户失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_user_status(user_id):
        """更新用户状态"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return error_response("用户不存在", 404)
                
            data = request.get_json()
            status = data.get('status')
            
            if status is None:
                return error_response("状态参数不能为空", 400)
                
            user.status = status
            db.session.commit()
            
            status_text = "启用" if status == 1 else "禁用"
            return success_response(f"用户{status_text}成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新用户状态失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def reset_password(user_id):
        """重置用户密码"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return error_response("用户不存在", 404)
                
            # 生成随机密码
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # 更新密码
            user.password = generate_password_hash(new_password)
            db.session.commit()
            
            return success_response("重置密码成功", {
                'new_password': new_password
            })
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"重置密码失败: {str(e)}", 500) 