from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import TravelGuide, TravelGuideCategory
from app import db
from utils.response import success_response, error_response
from utils.auth import login_required

# 创建蓝图
guide_bp = Blueprint('guide', __name__, url_prefix='/guides')


@guide_bp.route('', methods=['GET'])
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
    
    # 构建查询
    query = TravelGuide.query.filter(TravelGuide.status == 1)
    
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
    
    return jsonify(success_response("获取攻略列表成功", {
        'guides': guides,
        'pagination': pagination
    }))


@guide_bp.route('/<int:guide_id>', methods=['GET'])
def get_guide(guide_id):
    """获取攻略详情"""
    guide = TravelGuide.query.get_or_404(guide_id)
    
    # 检查攻略状态
    if guide.status != 1:
        return jsonify(error_response("攻略不可用")), 404
    
    # 增加浏览量
    guide.view_count += 1
    db.session.commit()
    
    # 记录浏览历史
    current_user = get_current_user()
    if current_user:
        # 检查是否已存在相同记录
        existing = BrowseHistory.query.filter_by(
            user_id=current_user.id,
            target_type='guide',
            target_id=guide_id
        ).first()
        
        if existing:
            # 更新浏览时间
            existing.updated_at = datetime.now()
        else:
            # 创建新记录
            history = BrowseHistory(
                user_id=current_user.id,
                target_type='guide',
                target_id=guide_id
            )
            db.session.add(history)
        
        db.session.commit()
    
    return jsonify(success_response("获取攻略详情成功", guide.to_dict()))


@guide_bp.route('', methods=['POST'])
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
        is_official=current_user.is_admin,  # 只有管理员可以创建官方攻略
        status=data.get('status', 1)  # 默认为已发布状态
    )
    
    db.session.add(guide)
    db.session.commit()
    
    return jsonify(success_response("创建攻略成功", guide.to_dict())), 201


@guide_bp.route('/<int:guide_id>', methods=['PUT'])
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


@guide_bp.route('/<int:guide_id>', methods=['DELETE'])
@login_required
def delete_guide(guide_id):
    """删除攻略"""
    current_user = get_current_user()
    guide = TravelGuide.query.get_or_404(guide_id)
    
    # 检查权限
    if guide.user_id != current_user.id and not current_user.is_admin:
        return jsonify(error_response("没有权限删除此攻略")), 403
    
    # 软删除
    guide.status = 2
    db.session.commit()
    
    return jsonify(success_response("删除攻略成功"))


@guide_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_guides(user_id):
    """获取用户发布的攻略"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # 只获取已发布的攻略
    query = TravelGuide.query.filter_by(user_id=user_id, status=1)
    query = query.order_by(desc(TravelGuide.created_at))
    
    # 分页处理
    pagination = paginate_query(query, page, per_page)
    
    # 转换为字典
    guides = [guide.to_dict(with_content=False) for guide in pagination.items]
    
    return jsonify(success_response("获取用户攻略成功", {
        'guides': guides,
        'pagination': pagination
    }))


@guide_bp.route('/my', methods=['GET'])
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
    
    query = query.order_by(desc(TravelGuide.created_at))
    
    # 分页处理
    pagination = paginate_query(query, page, per_page)
    
    # 转换为字典
    guides = [guide.to_dict(with_content=False) for guide in pagination.items]
    
    return jsonify(success_response("获取我的攻略成功", {
        'guides': guides,
        'pagination': pagination
    }))


@guide_bp.route('/hot', methods=['GET'])
def get_hot_guides():
    """获取热门攻略"""
    limit = min(request.args.get('limit', 10, type=int), 50)
    
    guides = TravelGuide.query.filter_by(status=1, is_hot=True).order_by(
        desc(TravelGuide.view_count)
    ).limit(limit).all()
    
    guides_data = [guide.to_dict(with_content=False) for guide in guides]
    
    return jsonify(success_response("获取热门攻略成功", guides_data))


@guide_bp.route('/official', methods=['GET'])
def get_official_guides():
    """获取官方攻略"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    query = TravelGuide.query.filter_by(status=1, is_official=True).order_by(
        desc(TravelGuide.created_at)
    )
    
    # 分页处理
    pagination = paginate_query(query, page, per_page)
    
    # 转换为字典
    guides = [guide.to_dict(with_content=False) for guide in pagination.items]
    
    return jsonify(success_response("获取官方攻略成功", {
        'guides': guides,
        'pagination': pagination
    })) 