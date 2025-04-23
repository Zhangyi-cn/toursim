from flask import request, jsonify, current_app, Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

from extensions import db
from models.user import User
from models.collection import Collection
from models.like import Like
from models.notification import Notification
from models.travel_note import TravelNote
from models.comment import Comment
from models.order import Order
from models.user_behavior import UserBehavior
from models.attraction import Attraction
from models.travel_guide import TravelGuide

from utils.response import success_response, error_response, pagination_response
from utils.auth import generate_token_payload, get_current_user, login_required, admin_required
from utils.validator import validate_required, is_valid_email, is_valid_phone, is_valid_password, get_page_params
from utils.upload import allowed_file, save_file, save_image
from controllers.notification_controller import NotificationController

# 创建用户蓝图
user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取用户个人资料"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'phone': current_user.phone,
        'nickname': current_user.nickname,
        'avatar': current_user.avatar,
        'bio': current_user.bio,
        'created_at': current_user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'last_login': current_user.last_login.strftime('%Y-%m-%d %H:%M:%S') if current_user.last_login else None,
        'is_admin': current_user.is_admin
    }
    
    return jsonify(success_response("获取用户资料成功", user_data))


@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户个人资料"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    data = request.get_json()
    
    # 更新昵称
    if 'nickname' in data:
        current_user.nickname = data['nickname']
    
    # 更新头像
    if 'avatar' in data:
        current_user.avatar = data['avatar']
    
    # 更新个人简介
    if 'bio' in data:
        current_user.bio = data['bio']
    
    # 更新手机号
    if 'phone' in data and data['phone'] != current_user.phone:
        # 检查手机号是否被占用
        if data['phone'] and User.query.filter_by(phone=data['phone']).first():
            return jsonify(error_response("手机号已被占用")), 400
        current_user.phone = data['phone']
    
    # 更新邮箱
    if 'email' in data and data['email'] != current_user.email:
        # 检查邮箱是否有效
        if not is_valid_email(data['email']):
            return jsonify(error_response("邮箱格式不正确")), 400
        
        # 检查邮箱是否被占用
        if User.query.filter_by(email=data['email']).first():
            return jsonify(error_response("邮箱已被占用")), 400
        
        current_user.email = data['email']
    
    # 更新时间
    current_user.updated_at = datetime.now()
    
    db.session.commit()
    
    return jsonify(success_response("更新资料成功"))


@user_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """修改用户密码"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    # 验证字段
    if not old_password or not new_password:
        return jsonify(error_response("旧密码和新密码不能为空")), 400
    
    # 检查旧密码是否正确
    if not current_user.verify_password(old_password):
        return jsonify(error_response("旧密码不正确")), 400
    
    # 检查新密码是否有效
    if not is_valid_password(new_password):
        return jsonify(error_response("新密码不符合要求，密码长度至少为6位")), 400
    
    # 如果旧密码和新密码相同，则无需修改
    if old_password == new_password:
        return jsonify(error_response("新密码不能与旧密码相同")), 400
    
    # 更新密码
    current_user.password = new_password
    current_user.updated_at = datetime.now()
    
    db.session.commit()
    
    return jsonify(success_response("密码修改成功"))


@user_bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """上传头像"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    # 检查是否包含文件
    if 'avatar' not in request.files:
        return jsonify(error_response("未找到头像文件")), 400
    
    file = request.files['avatar']
    
    # 检查文件是否为空
    if file.filename == '':
        return jsonify(error_response("未选择文件")), 400
    
    # 检查文件类型
    if not file.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
        return jsonify(error_response("不支持的文件类型，只允许png/jpg/jpeg/gif")), 400
    
    try:
        # 保存文件
        avatar_url = save_image(file, 'avatars')
        
        # 更新用户头像
        current_user.avatar = avatar_url
        current_user.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify(success_response("头像上传成功", {'avatar': avatar_url}))
    
    except Exception as e:
        current_app.logger.error(f"头像上传失败: {str(e)}")
        return jsonify(error_response("头像上传失败")), 500


@user_bp.route('/collections', methods=['GET'])
@login_required
def get_collections():
    """获取用户收藏列表"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    # 支持两种参数格式：直接参数和params[param]格式
    params = request.args.to_dict()
    
    # 检查是否使用params[type]格式
    target_type = params.get('type', '')
    page_param = params.get('page', '1')
    per_page_param = params.get('per_page', '10')
    
    # 如果没有直接参数，则尝试params[param]格式
    if not target_type and 'params[type]' in params:
        target_type = params.get('params[type]', '')
    
    if 'params[page]' in params:
        page_param = params.get('params[page]', '1')
        
    if 'params[per_page]' in params:
        per_page_param = params.get('params[per_page]', '10')
    
    # 转换为整数
    try:
        page = int(page_param)
        per_page = int(per_page_param)
    except ValueError:
        page = 1
        per_page = 10
    
    print(f"\n\n===== 用户收藏API调试 =====")
    print(f"用户ID: {current_user.id}, 收藏类型: {target_type}, 页码: {page}, 每页数量: {per_page}")
    print(f"原始请求参数: {params}")
    
    # 确定使用的收藏类型数字值
    numeric_type = None
    if target_type == 'attraction':
        numeric_type = Collection.TARGET_TYPE_ATTRACTION
    elif target_type == 'guide':
        numeric_type = Collection.TARGET_TYPE_GUIDE
    elif target_type == 'note':
        numeric_type = Collection.TARGET_TYPE_NOTE
    
    # 构建查询
    query = Collection.query.filter_by(user_id=current_user.id)
    
    # 按类型过滤
    if numeric_type is not None:
        query = query.filter_by(target_type=numeric_type)
        print(f"按类型{numeric_type}过滤")
    
    # 打印总收藏数
    total_collections = query.count()
    print(f"用户总收藏数: {total_collections}")
    
    # 按收藏时间倒序排序
    query = query.order_by(Collection.created_at.desc())
    
    # 分页查询
    paginate = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 构建响应数据
    items = []
    for collection in paginate.items:
        # 打印每个收藏项的详情
        print(f"处理收藏: ID={collection.id}, 类型={collection.target_type}, 目标ID={collection.target_id}")
        
        # 获取收藏的目标对象
        target = None
        target_data = {}
        target_type_str = Collection.TARGET_TYPE_MAP_REVERSE.get(collection.target_type, 'unknown')
        
        if collection.target_type == Collection.TARGET_TYPE_ATTRACTION:
            target = Attraction.query.get(collection.target_id)
            if target:
                target_data = {
                    "id": target.id,
                    "title": target.name,
                    "cover": target.cover_image,
                    "type": "attraction"
                }
                print(f"  - 找到景点: ID={target.id}, 名称={target.name}")
            else:
                print(f"  - 未找到景点ID={collection.target_id}")
        
        elif collection.target_type == Collection.TARGET_TYPE_GUIDE:
            target = TravelGuide.query.get(collection.target_id)
            if target:
                target_data = {
                    "id": target.id,
                    "title": target.title,
                    "cover": target.cover_image,
                    "type": "guide"
                }
                print(f"  - 找到攻略: ID={target.id}, 标题={target.title}")
            else:
                print(f"  - 未找到攻略ID={collection.target_id}")
                
        elif collection.target_type == Collection.TARGET_TYPE_NOTE:
            from models.travel_note import TravelNote
            target = TravelNote.query.get(collection.target_id)
            if target:
                target_data = {
                    "id": target.id,
                    "title": target.title,
                    "cover": target.cover_image,
                    "type": "note"
                }
                print(f"  - 找到游记: ID={target.id}, 标题={target.title}")
            else:
                print(f"  - 未找到游记ID={collection.target_id}")
        
        # 添加目标对象信息
        collection_data = {
            'id': collection.id,
            'target_type': target_type_str,
            'target_id': collection.target_id,
            'created_at': collection.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'target_info': target_data
        }
        items.append(collection_data)
    
    print(f"最终返回{len(items)}条收藏记录")
    
    return jsonify(pagination_response(
        items=items,
        total=paginate.total,
        page=page,
        per_page=per_page,
        message="获取收藏列表成功"
    ))


@user_bp.route('/likes', methods=['GET'])
@login_required
def get_likes():
    """获取用户点赞列表"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    target_type = request.args.get('type', '')
    page, per_page = get_page_params()
    
    # 构建查询
    query = Like.query.filter_by(user_id=current_user.id)
    
    # 按类型过滤
    if target_type:
        query = query.filter_by(target_type=target_type)
    
    # 按点赞时间倒序排序
    query = query.order_by(Like.created_at.desc())
    
    # 分页查询
    paginate = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 构建响应数据
    items = []
    for like in paginate.items:
        # 获取点赞的目标对象
        target = None
        target_data = {}
        
        if like.target_type == 'attraction':
            from models.attraction import Attraction
            target = Attraction.query.get(like.target_id)
            if target:
                target_data = target.to_dict()
        
        elif like.target_type == 'guide':
            from models.travel_guide import TravelGuide
            target = TravelGuide.query.get(like.target_id)
            if target:
                target_data = target.to_dict(with_content=False)
        
        elif like.target_type == 'note':
            target = TravelNote.query.get(like.target_id)
            if target:
                target_data = target.to_dict(with_content=False)
        
        # 添加目标对象信息
        like_data = {
            'id': like.id,
            'target_type': like.target_type,
            'target_id': like.target_id,
            'created_at': like.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'target_info': target_data
        }
        items.append(like_data)
    
    return jsonify(pagination_response(
        items=items,
        total=paginate.total,
        page=page,
        per_page=per_page,
        message="获取点赞列表成功"
    ))


@user_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """获取用户统计数据"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    # 获取用户统计数据
    stats = UserStats.query.filter_by(user_id=current_user.id).first()
    
    # 如果没有统计数据，则创建一个新的
    if not stats:
        stats = UserStats(user_id=current_user.id)
        db.session.add(stats)
        db.session.commit()
    
    # 获取用户的收藏数量
    collection_count = Collection.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户的点赞数量
    like_count = Like.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户的评论数量
    comment_count = Comment.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户的游记数量
    note_count = TravelNote.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户的订单数量
    order_count = Order.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户的行为数量
    behavior_count = UserBehavior.query.filter_by(user_id=current_user.id).count()
    
    # 构建响应数据
    stats_data = {
        'collection_count': collection_count,
        'like_count': like_count,
        'comment_count': comment_count,
        'note_count': note_count,
        'order_count': order_count,
        'behavior_count': behavior_count,
        'view_count': stats.view_count,
        'search_count': stats.search_count,
        'share_count': stats.share_count,
        'last_active': stats.last_active.strftime('%Y-%m-%d %H:%M:%S') if stats.last_active else None
    }
    
    return jsonify(success_response("获取用户统计数据成功", stats_data))


@user_bp.route('/behaviors', methods=['GET'])
@login_required
def get_user_behaviors():
    """获取用户行为列表"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    behavior_type = request.args.get('type', '')
    target_type = request.args.get('target_type', '')
    page, per_page = get_page_params()
    
    # 构建查询
    query = UserBehavior.query.filter_by(user_id=current_user.id)
    
    # 按行为类型过滤
    if behavior_type:
        query = query.filter_by(behavior_type=behavior_type)
    
    # 按目标类型过滤
    if target_type:
        query = query.filter_by(target_type=target_type)
    
    # 按时间倒序排序
    query = query.order_by(UserBehavior.created_at.desc())
    
    # 分页查询
    paginate = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 构建响应数据
    items = []
    for behavior in paginate.items:
        # 获取行为的目标对象
        target = None
        target_data = {}
        
        if behavior.target_type == 'attraction':
            from models.attraction import Attraction
            target = Attraction.query.get(behavior.target_id)
            if target:
                target_data = target.to_dict()
        
        elif behavior.target_type == 'guide':
            from models.travel_guide import TravelGuide
            target = TravelGuide.query.get(behavior.target_id)
            if target:
                target_data = target.to_dict(with_content=False)
        
        elif behavior.target_type == 'note':
            target = TravelNote.query.get(behavior.target_id)
            if target:
                target_data = target.to_dict(with_content=False)
        
        # 添加目标对象信息
        behavior_data = {
            'id': behavior.id,
            'behavior_type': behavior.behavior_type,
            'target_type': behavior.target_type,
            'target_id': behavior.target_id,
            'duration': behavior.duration,
            'created_at': behavior.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'target_info': target_data
        }
        items.append(behavior_data)
    
    return jsonify(pagination_response(
        items=items,
        total=paginate.total,
        page=page,
        per_page=per_page,
        message="获取用户行为列表成功"
    )) 