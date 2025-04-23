import functools
from flask import jsonify, request, current_app, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt, jwt_required
from utils.response import error_response
from models.user import User
from functools import wraps


def get_current_user():
    """
    获取当前用户
    :return: 用户对象或None
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if user_id:
            user = User.query.get(int(user_id))
            return user
        return None
    except:
        return None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户未登录或不存在'}), 401
        # 将用户对象附加到request
        request.user = user
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_admin:
                return jsonify({'message': '无权限访问'}), 403
            # 将用户对象附加到request
            request.user = user
            return fn(*args, **kwargs)
        return wrapper
    
    if fn is None:
        return decorator
    return decorator(fn)


def generate_token_payload(user):
    """
    生成JWT令牌负载
    :param user: 用户对象
    :return: 令牌负载字典
    """
    payload = {
        "sub": str(user.id),  # 用户ID，转换为字符串
        "username": user.username,  # 用户名
        "is_admin": bool(user.is_admin),  # 是否是管理员，确保是布尔值
    }
    return payload


def record_admin_activity(module, action, description=None):
    """
    记录管理员活动的装饰器
    :param module: 模块名称
    :param action: 操作类型
    :param description: 操作描述
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # 获取当前管理员
                user = get_current_user()
                if not user or not user.is_admin:
                    return fn(*args, **kwargs)

                # 获取请求信息
                method = request.method
                path = request.path
                ip = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                params = request.get_json() if request.is_json else request.form.to_dict()

                # 记录活动
                from models.operation_log import OperationLog
                
                OperationLog.add_log(
                    user_id=user.id,
                    module=module,
                    action=action,
                    description=description,
                    ip=ip,
                    user_agent=user_agent,
                    request_method=method,
                    request_path=path,
                    request_params=str(params) if params else None
                )

                # 执行原函数
                return fn(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"记录管理员活动失败: {str(e)}")
                return fn(*args, **kwargs)
        return wrapper
    return decorator 