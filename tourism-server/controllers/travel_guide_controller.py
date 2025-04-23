from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from sqlalchemy import desc, func, or_, and_
import os
from werkzeug.utils import secure_filename

from models.travel_guide import TravelGuide, TravelGuideCategory
from models.user import User
from models.comment import Comment
from models.like import Like
from models.collection import Collection
from models.tag import Tag, ContentTag
from extensions import db, cache
from utils.response import success_response, error_response, pagination_response
from utils.auth import get_current_user, login_required, admin_required
from utils.validator import get_page_params, validate_required, validate_params
from utils.rich_content import extract_summary, extract_images
from utils.pagination import paginate_query
from utils.upload import allowed_file, save_file

# 创建旅游攻略蓝图
travel_guide_bp = Blueprint('travel_guide', __name__, url_prefix='')


@travel_guide_bp.route('', methods=['GET'])
def get_guides():
    """获取攻略列表，支持分页、筛选和排序"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '')
    is_hot = request.args.get('is_hot', type=int)
    is_official = request.args.get('is_official', type=int)
    order_by = request.args.get('order_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    # 构建查询 - 排除已删除的攻略
    query = TravelGuide.query.filter(TravelGuide.status != 2)
    
    # 应用筛选条件
    if category_id:
        query = query.filter(TravelGuide.category_id == category_id)
        
    if keyword:
        query = query.filter(or_(
            TravelGuide.title.like(f'%{keyword}%'),
            TravelGuide.content.like(f'%{keyword}%')
        ))
    
    if is_hot is not None:
        query = query.filter(TravelGuide.is_hot == bool(is_hot))
        
    if is_official is not None:
        query = query.filter(TravelGuide.is_official == bool(is_official))
    
    # 应用排序
    if order == 'desc':
        query = query.order_by(desc(getattr(TravelGuide, order_by)))
    else:
        query = query.order_by(getattr(TravelGuide, order_by))
    
    # 分页处理
    pagination = paginate_query(query, page, per_page)
    
    # 转换为字典
    guides = [guide.to_dict(with_content=False) for guide in pagination.items]
    
    # 创建可序列化的分页信息字典
    pagination_info = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }
    
    return jsonify(success_response("获取攻略列表成功", {
        'guides': guides,
        'pagination': pagination_info
    }))


@travel_guide_bp.route('/<int:guide_id>', methods=['GET'])
def get_guide(guide_id):
    """获取攻略详情"""
    guide = TravelGuide.query.get_or_404(guide_id)
    
    # 检查攻略状态
    if guide.status != 1:
        return jsonify(error_response("攻略不可用")), 404
    
    # 增加浏览量
    guide.view_count += 1
    db.session.commit()
    
    # 获取当前用户ID，如果已登录
    user_id = None
    try:
        from flask_jwt_extended import get_jwt_identity
        current_user = get_jwt_identity()
        if current_user:
            user_id = current_user
    except:
        pass
    
    return jsonify(success_response("获取攻略详情成功", guide.to_dict(user_id=user_id)))


@travel_guide_bp.route('', methods=['POST'])
@login_required
def create_guide():
    """创建攻略"""
    current_user = get_current_user()
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('title'):
        return jsonify(error_response("攻略标题不能为空")), 400
    
    if not data.get('content'):
        return jsonify(error_response("攻略内容不能为空")), 400
    
    if not data.get('category_id'):
        return jsonify(error_response("请选择分类")), 400
    
    # 验证分类是否存在
    category = TravelGuideCategory.query.get(data.get('category_id'))
    if not category:
        return jsonify(error_response("分类不存在")), 400
    
    # 创建攻略
    guide = TravelGuide(
        title=data.get('title'),
        content=data.get('content'),
        cover_image=data.get('cover_image', ''),
        category_id=data.get('category_id'),
        user_id=current_user.id,
        status=data.get('status', 1)  # 默认为已发布状态
    )
    
    # 如果是管理员，可以设置是否官方和热门
    if current_user.is_admin:
        guide.is_official = data.get('is_official', False)
        guide.is_hot = data.get('is_hot', False)
    
    db.session.add(guide)
    db.session.commit()
    
    return jsonify(success_response("创建攻略成功", guide.to_dict())), 201


@travel_guide_bp.route('/<int:guide_id>', methods=['PUT'])
@login_required
def update_guide(guide_id):
    """更新攻略"""
    current_user = get_current_user()
    guide = TravelGuide.query.get_or_404(guide_id)
    
    # 检查权限
    if guide.user_id != current_user.id and not current_user.is_admin:
        return jsonify(error_response("没有权限修改此攻略")), 403
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        guide.title = data.get('title')
    
    if 'content' in data:
        guide.content = data.get('content')
    
    if 'cover_image' in data:
        guide.cover_image = data.get('cover_image')
    
    if 'category_id' in data:
        # 验证分类是否存在
        category = TravelGuideCategory.query.get(data.get('category_id'))
        if not category:
            return jsonify(error_response("分类不存在")), 400
        guide.category_id = data.get('category_id')
    
    if 'status' in data and current_user.is_admin:
        guide.status = data.get('status')
    
    if 'is_hot' in data and current_user.is_admin:
        guide.is_hot = data.get('is_hot')
    
    guide.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify(success_response("更新攻略成功", guide.to_dict()))


@travel_guide_bp.route('/<int:guide_id>', methods=['DELETE'])
@login_required
def delete_guide(guide_id):
    """删除攻略"""
    try:
        current_user = get_current_user()
        guide = TravelGuide.query.get_or_404(guide_id)
        
        # 检查权限
        if guide.user_id != current_user.id and not current_user.is_admin:
            return jsonify(error_response("没有权限删除此攻略")), 403
        
        # 检查当前状态
        if guide.status == 2:
            return jsonify(error_response("攻略已被删除")), 400
        
        # 软删除
        guide.status = 2
        guide.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify(success_response("删除攻略成功"))
        
    except Exception as e:
        db.session.rollback()
        return jsonify(error_response(f"删除攻略失败: {str(e)}")), 500


@travel_guide_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_guides(user_id):
    """获取用户发布的攻略"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # 只获取未删除的攻略
    query = TravelGuide.query.filter(
        TravelGuide.user_id == user_id,
        TravelGuide.status != 2
    )
    query = query.order_by(desc(TravelGuide.created_at))
    
    # 分页处理
    pagination = paginate_query(query, page, per_page)
    
    # 转换为字典
    guides = [guide.to_dict(with_content=False) for guide in pagination.items]
    
    # 创建可序列化的分页信息字典
    pagination_info = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }
    
    return jsonify(success_response("获取用户攻略成功", {
        'guides': guides,
        'pagination': pagination_info
    }))


@travel_guide_bp.route('/my', methods=['GET'])
@login_required
def get_my_guides():
    """获取当前用户发布的攻略"""
    current_user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    status = request.args.get('status', type=int)
    
    # 构建查询
    query = TravelGuide.query.filter_by(user_id=current_user.id)
    
    # 筛选状态
    if status is not None:
        query = query.filter_by(status=status)
    else:
        # 如果没有指定状态，默认排除已删除的攻略
        query = query.filter(TravelGuide.status != 2)
    
    query = query.order_by(desc(TravelGuide.created_at))
    
    # 分页处理
    pagination = paginate_query(query, page, per_page)
    
    # 转换为字典
    guides = [guide.to_dict(with_content=False) for guide in pagination.items]
    
    # 创建可序列化的分页信息字典
    pagination_info = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }
    
    return jsonify(success_response("获取我的攻略成功", {
        'guides': guides,
        'pagination': pagination_info
    }))


@travel_guide_bp.route('/hot', methods=['GET'])
def get_hot_guides():
    """获取热门攻略"""
    limit = min(request.args.get('limit', 10, type=int), 50)
    
    guides = TravelGuide.query.filter(
        TravelGuide.status != 2,  # 排除已删除的攻略
        TravelGuide.is_hot == True
    ).order_by(
        desc(TravelGuide.view_count)
    ).limit(limit).all()
    
    guides_data = [guide.to_dict(with_content=False) for guide in guides]
    
    return jsonify(success_response("获取热门攻略成功", guides_data))


@travel_guide_bp.route('/official', methods=['GET'])
def get_official_guides():
    """获取官方攻略"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    query = TravelGuide.query.filter(
        TravelGuide.status != 2,  # 排除已删除的攻略
        TravelGuide.is_official == True
    ).order_by(
        desc(TravelGuide.created_at)
    )
    
    # 分页处理
    pagination = paginate_query(query, page, per_page)
    
    # 转换为字典
    guides = [guide.to_dict(with_content=False) for guide in pagination.items]
    
    # 创建可序列化的分页信息字典
    pagination_info = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }
    
    return jsonify(success_response("获取官方攻略成功", {
        'guides': guides,
        'pagination': pagination_info
    }))


@travel_guide_bp.route('/guides/categories', methods=['GET'])
def get_categories():
    """获取攻略分类列表"""
    # 从缓存中获取分类列表
    cached_categories = cache.get('guide_categories')
    if cached_categories:
        return jsonify(success_response("获取分类列表成功", cached_categories))
    
    # 如果缓存中没有，则从数据库获取
    categories = TravelGuideCategory.query.all()
    category_list = [category.to_dict() for category in categories]
    
    # 更新缓存
    cache.set('guide_categories', category_list, timeout=3600)  # 缓存1小时
    
    return jsonify(success_response("获取分类列表成功", category_list))


@travel_guide_bp.route('/<int:guide_id>/comments', methods=['GET'])
def get_comments(guide_id):
    """获取攻略评论"""
    # 查询攻略
    guide = TravelGuide.query.get(guide_id)
    if not guide:
        return jsonify(error_response("攻略不存在")), 404
    
    # 获取分页参数
    page, per_page = get_page_params()
    
    # 获取评论类型
    parent_id = request.args.get('parent_id', type=int)
    
    # 获取排序方式
    sort_by = request.args.get('sort_by', 'latest')  # latest
    
    # 构建查询
    query = Comment.query.filter_by(
        content_id=guide_id,
        content_type='guide',
        status=1  # 只查询已发布的评论
    )
    
    # 一级评论还是回复
    if parent_id:
        query = query.filter_by(parent_id=parent_id)
    else:
        query = query.filter(Comment.parent_id.is_(None))
    
    # 应用排序
    if sort_by == 'latest':
        query = query.order_by(desc(Comment.created_at))
    
    # 执行分页查询
    paginate = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 准备响应数据
    items = []
    for comment in paginate.items:
        # 确保包含用户信息
        comment_data = comment.to_dict(with_user=True)
        
        # 获取回复数量
        if not parent_id:
            reply_count = Comment.query.filter_by(
                parent_id=comment.id,
                status=1
            ).count()
            comment_data['reply_count'] = reply_count
        
        items.append(comment_data)
    
    return jsonify(pagination_response(
        items=items,
        total=paginate.total,
        page=page,
        per_page=per_page,
        message="获取评论成功"
    ))


@travel_guide_bp.route('/<int:guide_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(guide_id):
    """添加攻略评论"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    # 查询攻略
    guide = TravelGuide.query.get(guide_id)
    if not guide:
        return jsonify(error_response("攻略不存在")), 404
    
    data = request.get_json()
    
    content = data.get('content')
    parent_id = data.get('parent_id')
    
    # 验证数据
    if not content:
        return jsonify(error_response("评论内容不能为空")), 400
    
    # 创建评论
    try:
        comment = Comment(
            user_id=current_user.id,
            content=content,
            content_id=guide_id,
            content_type='guide',
            parent_id=parent_id,
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            status=1  # 默认已发布状态
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # 确保返回的评论包含用户信息
        return jsonify(success_response("评论成功", comment.to_dict(with_user=True)))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加评论失败: {str(e)}")
        return jsonify(error_response("评论失败，服务器错误")), 500 