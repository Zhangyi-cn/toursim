from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from models import Collection, Attraction, TravelNote
from models.user import User
from models.travel_guide import TravelGuide
from app import db
from utils.response import success_response, error_response
from utils.auth import login_required
from utils.validator import get_page_params

# 创建蓝图
collection_bp = Blueprint('collection', __name__, url_prefix='/collections')


@collection_bp.route('/<string:target_type>/<int:target_id>', methods=['POST'])
@jwt_required()
def add_collection(target_type, target_id):
    """
    添加收藏
    ---
    tags:
      - 收藏
    parameters:
      - name: target_type
        in: path
        type: string
        required: true
        description: 收藏对象类型（attraction/guide/note）
      - name: target_id
        in: path
        type: integer
        required: true
        description: 收藏对象ID
    responses:
      200:
        description: 收藏成功
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
    valid_types = ['attraction', 'guide', 'note']
    if target_type not in valid_types:
        return jsonify(error_response(f"不支持的收藏类型: {target_type}", 400)), 400
    
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
    
    # 使用静态方法添加收藏
    try:
        success = Collection.add_collection(user.id, target_id, target_type)
        if success:
            return jsonify(success_response("收藏成功"))
        else:
            return jsonify(success_response("已收藏过该对象"))
    except Exception as e:
        current_app.logger.error(f"收藏失败: {str(e)}")
        return jsonify(error_response("收藏失败，服务器错误", 500)), 500


@collection_bp.route('/<string:target_type>/<int:target_id>', methods=['DELETE'])
@jwt_required()
def remove_collection(target_type, target_id):
    """
    取消收藏
    ---
    tags:
      - 收藏
    parameters:
      - name: target_type
        in: path
        type: string
        required: true
        description: 收藏对象类型（attraction/guide/note）
      - name: target_id
        in: path
        type: integer
        required: true
        description: 收藏对象ID
    responses:
      200:
        description: 取消收藏成功
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
    valid_types = ['attraction', 'guide', 'note']
    if target_type not in valid_types:
        return jsonify(error_response(f"不支持的收藏类型: {target_type}", 400)), 400
    
    # 使用静态方法取消收藏
    try:
        success = Collection.remove_collection(user.id, target_id, target_type)
        if success:
            return jsonify(success_response("取消收藏成功"))
        else:
            return jsonify(error_response(f"未收藏该{target_type}", 404)), 404
    except Exception as e:
        current_app.logger.error(f"取消收藏失败: {str(e)}")
        return jsonify(error_response("取消收藏失败，服务器错误", 500)), 500


@collection_bp.route('', methods=['GET'])
@jwt_required()
def get_collections():
    """
    获取收藏列表
    ---
    tags:
      - 收藏
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
      - name: type
        in: query
        type: string
        required: false
        description: 收藏类型（attraction/guide/note）
    responses:
      200:
        description: 成功获取收藏列表
      401:
        description: 未授权
    """
    # 获取当前用户
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(error_response("用户不存在", 404)), 404
    
    # 获取分页参数
    page, per_page = get_page_params()
    
    # 获取类型参数
    type_param = request.args.get('type', '')
    print(f"\n\n===== 收藏API调试 =====")
    print(f"用户ID: {user_id}, 收藏类型: {type_param}, 页码: {page}, 每页数量: {per_page}")
    
    # 可能存在的target_type类型转换
    num_type = None
    if type_param == 'attraction':
        num_type = Collection.TARGET_TYPE_ATTRACTION
    elif type_param == 'guide':
        num_type = Collection.TARGET_TYPE_GUIDE
    elif type_param == 'note':
        num_type = Collection.TARGET_TYPE_NOTE
    
    # 首先直接查询用户所有收藏记录，检查是否存在
    all_collections = Collection.query.filter_by(user_id=user.id)
    
    # 如果指定了类型，增加类型过滤
    if num_type is not None:
        all_collections = all_collections.filter_by(target_type=num_type)
    
    all_collections = all_collections.all()
    print(f"用户所有收藏记录数量: {len(all_collections)}")
    
    if len(all_collections) > 0:
        print("\n收藏记录详情:")
        for c in all_collections:
            print(f"ID: {c.id}, 类型: {c.target_type}, 目标ID: {c.target_id}")
            
            # 尝试获取原始景点信息
            if c.target_type == Collection.TARGET_TYPE_ATTRACTION:
                attr = Attraction.query.get(c.target_id)
                if attr:
                    print(f"  - 景点信息: ID={attr.id}, 名称={attr.name}, 封面={attr.cover_image}")
                else:
                    print(f"  - 景点ID={c.target_id}不存在")
            elif c.target_type == Collection.TARGET_TYPE_GUIDE:
                guide = TravelGuide.query.get(c.target_id)
                if guide:
                    print(f"  - 攻略信息: ID={guide.id}, 标题={guide.title}, 封面={guide.cover_image}")
                else:
                    print(f"  - 攻略ID={c.target_id}不存在")
    else:
        print("用户没有任何收藏记录")
    
    # 直接构建最终结果，跳过复杂查询
    print("跳过复杂查询，直接构建结果...")
    result = []
    
    for c in all_collections:
        item = c.to_dict()
        target_info = None
        
        if c.target_type == Collection.TARGET_TYPE_ATTRACTION:
            attr = Attraction.query.get(c.target_id)
            if attr:
                target_info = {
                    "id": attr.id,
                    "title": attr.name,
                    "cover": attr.cover_image,
                    "type": "attraction"
                }
                print(f"添加景点收藏到返回结果: {attr.id}, {attr.name}")
        elif c.target_type == Collection.TARGET_TYPE_GUIDE:
            guide = TravelGuide.query.get(c.target_id)
            if guide:
                target_info = {
                    "id": guide.id,
                    "title": guide.title,
                    "cover": guide.cover_image,
                    "type": "guide"
                }
                print(f"添加攻略收藏到返回结果: {guide.id}, {guide.title}")
        elif c.target_type == Collection.TARGET_TYPE_NOTE:
            note = TravelNote.query.get(c.target_id)
            if note:
                target_info = {
                    "id": note.id,
                    "title": note.title,
                    "cover": note.cover_image,
                    "type": "note"
                }
                print(f"添加游记收藏到返回结果: {note.id}, {note.title}")
        
        # 只有找到目标信息才添加到结果
        if target_info:
            item['target_info'] = target_info
            result.append(item)
    
    # 跳过复杂的联表查询，直接使用简单构建的结果
    print(f"构建的结果数量: {len(result)}")
    
    # 按创建时间排序
    result.sort(key=lambda x: x['created_at'], reverse=True)
    print(f"排序后结果数量: {len(result)}")
    
    # 手动分页
    total = len(result)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paged_items = result[start_idx:end_idx] if start_idx < total else []
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 构建响应数据
    data = {
        "items": paged_items,
        "total": total,
        "pages": total_pages,
        "page": page,
        "per_page": per_page
    }
    
    return jsonify(success_response("获取收藏列表成功", data))


def _get_target_info(target_id, target_type):
    """获取目标详情"""
    if target_type == 'attraction':  # 景点
        target = Attraction.query.get(target_id)
        if target:
            return {
                "id": target.id,
                "title": target.name,
                "cover": target.cover_image,
                "type": "attraction"
            }
    elif target_type == 'guide':  # 攻略
        target = TravelGuide.query.get(target_id)
        if target:
            return {
                "id": target.id,
                "title": target.title,
                "cover": target.cover_image,
                "type": "guide"
            }
    elif target_type == 'note':  # 游记
        target = TravelNote.query.get(target_id)
        if target:
            return {
                "id": target.id,
                "title": target.title,
                "cover": target.cover_image,
                "type": "note"
            }
    return None 