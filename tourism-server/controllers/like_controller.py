from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Like, Attraction, TravelNote
from models.user import User
from models.travel_guide import TravelGuide
from app import db
from utils.response import success_response, error_response
from utils.auth import login_required

# 创建蓝图
like_bp = Blueprint('like', __name__, url_prefix='/likes')


# 添加测试路由
@like_bp.route('/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt():
    """测试JWT验证"""
    user_id = get_jwt_identity()
    return jsonify(success_response("JWT验证成功", {"user_id": user_id}))

# 添加测试路由
@like_bp.route('/test-login', methods=['GET'])
@login_required
def test_login():
    """测试自定义登录验证"""
    user = g.user
    return jsonify(success_response("登录验证成功", {"user_id": user.id}))


@like_bp.route('/<string:target_type>/<int:target_id>', methods=['POST'])
@jwt_required()
def add_like(target_type, target_id):
    """
    添加点赞
    ---
    tags:
      - 点赞
    parameters:
      - name: target_type
        in: path
        type: string
        required: true
        description: 点赞对象类型（attraction/guide/note/comment）
      - name: target_id
        in: path
        type: integer
        required: true
        description: 点赞对象ID
    responses:
      200:
        description: 点赞成功
      400:
        description: 请求参数错误
      401:
        description: 未授权
      404:
        description: 资源不存在
    """
    # 获取当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(error_response("用户不存在", 404)), 404

    # 验证target_type
    target_type_map = {
        'attraction': 1,
        'guide': 2,
        'note': 3,
        'comment': 4
    }
    
    if target_type not in target_type_map:
        return jsonify(error_response(f"不支持的点赞类型: {target_type}", 400)), 400
    
    # 获取数值类型
    target_type_num = target_type_map[target_type]
    
    # 验证目标对象是否存在
    target_obj = None
    if target_type == 'attraction':
        target_obj = Attraction.query.get(target_id)
    elif target_type == 'guide':
        target_obj = TravelGuide.query.get(target_id)
    elif target_type == 'note':
        target_obj = TravelNote.query.get(target_id)
    
    if not target_obj:
        return jsonify(error_response(f"指定的{target_type}不存在", 404)), 404
    
    # 检查是否已点赞
    existing_like = Like.query.filter_by(
        user_id=user.id,
        target_type=target_type_num,
        target_id=target_id
    ).first()
    
    if existing_like:
        return jsonify(success_response("已点赞过该对象"))
    
    # 添加点赞
    try:
        new_like = Like(
            user_id=user.id,
            target_type=target_type_num,
            target_id=target_id,
            created_at=datetime.now()
        )
        db.session.add(new_like)
        db.session.commit()
        
        return jsonify(success_response("点赞成功"))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"点赞失败: {str(e)}")
        return jsonify(error_response("点赞失败，服务器错误", 500)), 500


@like_bp.route('/<string:target_type>/<int:target_id>', methods=['DELETE'])
@jwt_required()
def remove_like(target_type, target_id):
    """
    取消点赞
    ---
    tags:
      - 点赞
    parameters:
      - name: target_type
        in: path
        type: string
        required: true
        description: 点赞对象类型（attraction/guide/note/comment）
      - name: target_id
        in: path
        type: integer
        required: true
        description: 点赞对象ID
    responses:
      200:
        description: 取消点赞成功
      400:
        description: 请求参数错误
      401:
        description: 未授权
      404:
        description: 资源不存在
    """
    # 获取当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(error_response("用户不存在", 404)), 404
    
    # 验证target_type
    target_type_map = {
        'attraction': 1,
        'guide': 2,
        'note': 3,
        'comment': 4
    }
    
    if target_type not in target_type_map:
        return jsonify(error_response(f"不支持的点赞类型: {target_type}", 400)), 400
        
    # 获取数值类型
    target_type_num = target_type_map[target_type]
    
    # 查找点赞记录
    like = Like.query.filter_by(
        user_id=user.id,
        target_type=target_type_num,
        target_id=target_id
    ).first()
    
    if not like:
        return jsonify(error_response(f"未对该{target_type}点赞", 404)), 404
    
    # 删除点赞
    try:
        db.session.delete(like)
        db.session.commit()
        
        return jsonify(success_response("取消点赞成功"))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"取消点赞失败: {str(e)}")
        return jsonify(error_response("取消点赞失败，服务器错误", 500)), 500


@like_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_likes():
    """
    获取用户点赞列表
    ---
    tags:
      - 点赞
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 页码
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: 每页数量
    responses:
      200:
        description: 成功获取点赞列表
      401:
        description: 未授权
    """
    # 获取当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(error_response("用户不存在", 404)), 404
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取点赞列表
    likes = Like.query.filter_by(user_id=user.id).order_by(Like.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 构建响应数据
    data = {
        "items": [like.to_dict() for like in likes.items],
        "total": likes.total,
        "pages": likes.pages,
        "page": page,
        "per_page": per_page
    }
    
    return jsonify(success_response("获取点赞列表成功", data))


@like_bp.route('', methods=['GET'])
@jwt_required()
def get_likes():
    """
    获取用户点赞列表
    ---
    tags:
      - 点赞
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 页码
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: 每页数量
    responses:
      200:
        description: 成功获取点赞列表
      401:
        description: 未授权
    """
    return get_user_likes() 