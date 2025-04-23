from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

from models.category import Category
from models.travel_guide import TravelGuideCategory
from extensions import db
from utils.response import success_response, error_response
from utils.auth import get_current_user, login_required

# 创建蓝图
category_bp = Blueprint('category', __name__, url_prefix='/categories')


@category_bp.route('/attractions', methods=['GET'])
def get_attraction_categories():
    """获取景点分类列表"""
    categories = Category.query.filter(
        Category.type == 1  # 1表示景点分类
    ).order_by(Category.sort_order).all()
    
    # 转换为字典
    categories_data = [category.to_dict() for category in categories]
    
    return jsonify(success_response("获取景点分类成功", categories_data))


@category_bp.route('/attractions/<int:category_id>', methods=['GET'])
def get_attraction_category(category_id):
    """获取景点分类详情"""
    category = Category.query.get(category_id)
    
    if not category or category.type != 1:  # 1表示景点分类
        return jsonify(error_response("分类不存在")), 404
    
    return jsonify(success_response("获取景点分类详情成功", category.to_dict()))


@category_bp.route('/attractions', methods=['POST'])
@login_required
def create_attraction_category():
    """创建景点分类"""
    # 检查权限
    current_user = get_current_user()
    if not current_user.is_admin:
        return jsonify(error_response("没有权限创建分类")), 403
    
    data = request.get_json()
    
    # 检查必填字段
    if not data.get('name'):
        return jsonify(error_response("分类名称不能为空")), 400
    
    # 创建分类
    category = Category(
        name=data.get('name'),
        description=data.get('description', ''),
        type=1,  # 1表示景点分类
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(success_response("创建景点分类成功", category.to_dict())), 201


@category_bp.route('/attractions/<int:category_id>', methods=['PUT'])
@login_required
def update_attraction_category(category_id):
    """更新景点分类"""
    # 检查权限
    current_user = get_current_user()
    if not current_user.is_admin:
        return jsonify(error_response("没有权限更新分类")), 403
    
    category = Category.query.get(category_id)
    
    if not category or category.type != 1:  # 1表示景点分类
        return jsonify(error_response("分类不存在")), 404
    
    data = request.get_json()
    
    # 更新字段
    if data.get('name'):
        category.name = data.get('name')
    
    if 'description' in data:
        category.description = data.get('description')
    
    if 'sort_order' in data:
        category.sort_order = data.get('sort_order')
    
    category.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify(success_response("更新景点分类成功", category.to_dict()))


@category_bp.route('/attractions/<int:category_id>', methods=['DELETE'])
@login_required
def delete_attraction_category(category_id):
    """删除景点分类"""
    # 检查权限
    current_user = get_current_user()
    if not current_user.is_admin:
        return jsonify(error_response("没有权限删除分类")), 403
    
    category = Category.query.get(category_id)
    
    if not category or category.type != 1:  # 1表示景点分类
        return jsonify(error_response("分类不存在")), 404
    
    # 检查是否有关联的景点
    if category.attractions and len(category.attractions) > 0:
        return jsonify(error_response("该分类下有关联的景点，无法删除")), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify(success_response("删除景点分类成功"))


@category_bp.route('/guides', methods=['GET'])
def get_guide_categories():
    """获取攻略分类列表"""
    categories = TravelGuideCategory.query.filter_by(status=1).order_by(TravelGuideCategory.sort_order).all()
    
    # 转换为字典
    categories_data = [category.to_dict() for category in categories]
    
    return jsonify(success_response("获取攻略分类成功", categories_data))


@category_bp.route('/guides/<int:category_id>', methods=['GET'])
def get_guide_category(category_id):
    """获取攻略分类详情"""
    category = TravelGuideCategory.query.get(category_id)
    
    if not category:
        return jsonify(error_response("分类不存在")), 404
    
    return jsonify(success_response("获取攻略分类详情成功", category.to_dict()))


@category_bp.route('/guides', methods=['POST'])
@login_required
def create_guide_category():
    """创建攻略分类"""
    # 检查权限
    current_user = get_current_user()
    if not current_user.is_admin:
        return jsonify(error_response("没有权限创建分类")), 403
    
    data = request.get_json()
    
    # 检查必填字段
    if not data.get('name'):
        return jsonify(error_response("分类名称不能为空")), 400
    
    # 创建分类
    category = TravelGuideCategory(
        name=data.get('name'),
        icon=data.get('icon', ''),
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 1)
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(success_response("创建攻略分类成功", category.to_dict())), 201


@category_bp.route('/guides/<int:category_id>', methods=['PUT'])
@login_required
def update_guide_category(category_id):
    """更新攻略分类"""
    # 检查权限
    current_user = get_current_user()
    if not current_user.is_admin:
        return jsonify(error_response("没有权限更新分类")), 403
    
    category = TravelGuideCategory.query.get(category_id)
    
    if not category:
        return jsonify(error_response("分类不存在")), 404
    
    data = request.get_json()
    
    # 更新字段
    if data.get('name'):
        category.name = data.get('name')
    
    if 'icon' in data:
        category.icon = data.get('icon')
    
    if 'sort_order' in data:
        category.sort_order = data.get('sort_order')
    
    if 'status' in data:
        category.status = data.get('status')
    
    db.session.commit()
    
    return jsonify(success_response("更新攻略分类成功", category.to_dict()))


@category_bp.route('/guides/<int:category_id>', methods=['DELETE'])
@login_required
def delete_guide_category(category_id):
    """删除攻略分类"""
    # 检查权限
    current_user = get_current_user()
    if not current_user.is_admin:
        return jsonify(error_response("没有权限删除分类")), 403
    
    category = TravelGuideCategory.query.get(category_id)
    
    if not category:
        return jsonify(error_response("分类不存在")), 404
    
    # 检查是否有关联的攻略
    if category.guides.count() > 0:
        return jsonify(error_response("该分类下有关联的攻略，无法删除")), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify(success_response("删除攻略分类成功")) 