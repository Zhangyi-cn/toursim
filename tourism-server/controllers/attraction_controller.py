from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from models import Attraction, Category, AttractionImage
from models.ticket import Ticket
from app import db
from utils.response import success_response, error_response
from utils.auth import login_required, admin_required, get_current_user
from utils.upload import allowed_file, save_file
from sqlalchemy import or_, desc, func, and_
from models.travel_season import TravelSeason
from utils.pagination import paginate_query
from models.like import Like
from models.collection import Collection
from models.browse_history import BrowseHistory
from extensions import cache
from utils.validator import get_page_params
from utils.activity import record_activity
from models.comment import Comment
from models.tag import Tag, ContentTag

# 创建蓝图
attraction_bp = Blueprint('attractions', __name__)


@attraction_bp.route('', methods=['GET'])
def get_attractions():
    """获取景点列表，支持分页、筛选和排序"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        category_id = request.args.get('category_id', type=int)
        keyword = request.args.get('keyword', '')
        is_hot = request.args.get('is_hot')
        is_recommended = request.args.get('is_recommended')
        order_by = request.args.get('order_by', 'created_at')
        order = request.args.get('order', 'desc')
        
        # 打印请求参数
        current_app.logger.info(f"查询参数: page={page}, per_page={per_page}, category_id={category_id}, "
                            f"keyword={keyword}, is_hot={is_hot}, is_recommended={is_recommended}, "
                            f"order_by={order_by}, order={order}")
        
        # 构建查询
        query = Attraction.query
        
        # 应用筛选条件
        query = query.filter(Attraction.status == 1)
        
        if category_id and category_id > 0:
            query = query.filter(Attraction.category_id == category_id)
            
        if keyword:
            query = query.filter(or_(
                Attraction.name.like(f'%{keyword}%'),
                Attraction.description.like(f'%{keyword}%'),
                Attraction.address.like(f'%{keyword}%')
            ))
        
        # 只在请求热门景点时进行过滤
        if is_hot is not None and is_hot.lower() == 'true':
            query = query.filter(Attraction.is_hot == True)
            current_app.logger.info("应用热门筛选: 只显示热门景点")
            
        # 只在请求推荐景点时进行过滤
        if is_recommended is not None and is_recommended.lower() == 'true':
            query = query.filter(Attraction.is_recommended == True)
            current_app.logger.info("应用推荐筛选: 只显示推荐景点")
        
        # 应用排序
        if order == 'desc':
            query = query.order_by(desc(getattr(Attraction, order_by)))
        else:
            query = query.order_by(getattr(Attraction, order_by))
        
        # 打印实际执行的 SQL 语句
        from sqlalchemy.dialects import mysql
        sql = query.statement.compile(
            dialect=mysql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
        current_app.logger.info(f"执行的 SQL 语句: {str(sql)}")
        
        # 分页处理
        pagination = paginate_query(query, page, per_page)
        
        # 打印结果数量
        current_app.logger.info(f"查询结果: 总数={pagination.total}, 当前页数据量={len(pagination.items)}")
        
        # 转换为字典
        attractions = [attraction.to_dict() for attraction in pagination.items]
        
        return jsonify(success_response("获取景点列表成功", {
            'items': attractions,
            'pagination': {
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }))
    except Exception as e:
        current_app.logger.error(f"获取景点列表失败: {str(e)}")
        return jsonify(error_response("获取景点列表失败")), 500


@attraction_bp.route('/<int:attraction_id>', methods=['GET'])
def get_attraction(attraction_id):
    """获取景点详情"""
    try:
        # 查询景点
        attraction = Attraction.query.get_or_404(attraction_id)
        
        # 检查景点状态
        if attraction.status != 1:
            return jsonify(error_response("景点不可用")), 404
        
        # 增加浏览量并立即提交
        attraction.view_count = attraction.view_count + 1 if attraction.view_count else 1
        
        # 获取当前用户
        current_user = None
        try:
            current_user = get_current_user()
        except:
            pass
        
        # 获取景点详情
        data = attraction.to_dict()
        
        # 获取景点季节信息
        seasons = TravelSeason.query.filter_by(attraction_id=attraction_id).all()
        seasons_data = [season.to_dict() for season in seasons]
        data['seasons'] = seasons_data
        
        # 添加点赞和收藏状态
        if current_user:
            # 检查是否已点赞
            is_liked = Like.query.filter_by(
                user_id=current_user.id,
                target_type=Like.TARGET_TYPE_ATTRACTION,
                target_id=attraction_id
            ).first() is not None
            data['is_liked'] = is_liked
            
            # 检查是否已收藏
            is_collected = Collection.query.filter_by(
                user_id=current_user.id,
                target_type='attraction',
                target_id=attraction_id
            ).first() is not None
            data['is_collected'] = is_collected
        else:
            data['is_liked'] = False
            data['is_collected'] = False
        
        # 添加点赞和收藏数量
        data['like_count'] = attraction.like_count or 0
        data['collection_count'] = attraction.collection_count or 0
        
        # 记录浏览历史
        if current_user:
            try:
                browse_history = BrowseHistory(
                    user_id=current_user.id,
                    target_type='attraction',
                    target_id=attraction_id
                )
                db.session.add(browse_history)
            except:
                pass  # 忽略浏览历史记录失败的情况
        
        db.session.commit()
        
        return jsonify(success_response("获取景点详情成功", data))
        
    except Exception as e:
        current_app.logger.error(f"获取景点详情失败: {str(e)}")
        db.session.rollback()
        return jsonify(error_response("获取景点详情失败")), 500


@attraction_bp.route('/', methods=['POST'])
@login_required
def create_attraction():
    """创建景点(仅管理员)"""
    current_user = get_current_user()
    
    # 检查权限
    if not current_user.is_admin:
        return jsonify(error_response("没有权限创建景点")), 403
    
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('name'):
        return jsonify(error_response("景点名称不能为空")), 400
    
    if not data.get('category_id'):
        return jsonify(error_response("请选择分类")), 400
    
    # 验证分类是否存在
    category = Category.query.get(data.get('category_id'))
    if not category:
        return jsonify(error_response("分类不存在")), 400
    
    # 创建景点
    attraction = Attraction(
        name=data.get('name'),
        description=data.get('description', ''),
        cover_image=data.get('cover_image', ''),
        images=','.join(data.get('images', [])) if isinstance(data.get('images'), list) else data.get('images', ''),
        address=data.get('address', ''),
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        category_id=data.get('category_id'),
        open_time=data.get('open_time', ''),
        ticket_info=data.get('ticket_info', ''),
        contact=data.get('contact', ''),
        tips=data.get('tips', ''),
        status=data.get('status', 1),
        is_hot=data.get('is_hot', False),
        is_recommended=data.get('is_recommended', False)
    )
    
    db.session.add(attraction)
    db.session.commit()
    
    # 添加季节数据
    seasons_data = data.get('seasons', [])
    if seasons_data:
        for season_data in seasons_data:
            season = TravelSeason(
                attraction_id=attraction.id,
                season=season_data.get('season'),
                recommendation=season_data.get('recommendation', '')
            )
            db.session.add(season)
        
        db.session.commit()
    
    # 记录用户活动
    record_activity(
        user_id=current_user.id,
        action_type='create',
        target_type='attraction',
        target_id=attraction.id
    )
    
    return jsonify(success_response("创建景点成功", attraction.to_dict())), 201


@attraction_bp.route('/<int:attraction_id>', methods=['PUT'])
@login_required
def update_attraction(attraction_id):
    """更新景点(仅管理员)"""
    current_user = get_current_user()
    
    # 检查权限
    if not current_user.is_admin:
        return jsonify(error_response("没有权限修改景点")), 403
    
    attraction = Attraction.query.get_or_404(attraction_id)
    data = request.get_json()
    
    # 更新字段
    if 'name' in data:
        attraction.name = data.get('name')
    
    if 'description' in data:
        attraction.description = data.get('description')
    
    if 'cover_image' in data:
        attraction.cover_image = data.get('cover_image')
    
    if 'images' in data:
        attraction.images = ','.join(data.get('images')) if isinstance(data.get('images'), list) else data.get('images')
    
    if 'address' in data:
        attraction.address = data.get('address')
    
    if 'longitude' in data:
        attraction.longitude = data.get('longitude')
    
    if 'latitude' in data:
        attraction.latitude = data.get('latitude')
    
    if 'category_id' in data:
        # 验证分类是否存在
        category = Category.query.get(data.get('category_id'))
        if not category:
            return jsonify(error_response("分类不存在")), 400
        attraction.category_id = data.get('category_id')
    
    if 'open_time' in data:
        attraction.open_time = data.get('open_time')
    
    if 'ticket_info' in data:
        attraction.ticket_info = data.get('ticket_info')
    
    if 'contact' in data:
        attraction.contact = data.get('contact')
    
    if 'tips' in data:
        attraction.tips = data.get('tips')
    
    if 'status' in data:
        attraction.status = data.get('status')
    
    if 'is_hot' in data:
        attraction.is_hot = data.get('is_hot')
    
    if 'is_recommended' in data:
        attraction.is_recommended = data.get('is_recommended')
    
    attraction.updated_at = datetime.now()
    db.session.commit()
    
    # 更新季节数据
    seasons_data = data.get('seasons')
    if seasons_data is not None:
        # 删除旧的季节数据
        TravelSeason.query.filter_by(attraction_id=attraction_id).delete()
        
        # 添加新的季节数据
        for season_data in seasons_data:
            season = TravelSeason(
                attraction_id=attraction.id,
                season=season_data.get('season'),
                recommendation=season_data.get('recommendation', '')
            )
            db.session.add(season)
        
        db.session.commit()
    
    # 记录用户活动
    record_activity(
        user_id=current_user.id,
        action_type='update',
        target_type='attraction',
        target_id=attraction.id
    )
    
    return jsonify(success_response("更新景点成功", attraction.to_dict()))


@attraction_bp.route('/<int:attraction_id>', methods=['DELETE'])
@login_required
def delete_attraction(attraction_id):
    """删除景点(仅管理员)"""
    current_user = get_current_user()
    
    # 检查权限
    if not current_user.is_admin:
        return jsonify(error_response("没有权限删除景点")), 403
    
    attraction = Attraction.query.get_or_404(attraction_id)
    
    # 软删除
    attraction.status = 0
    db.session.commit()
    
    # 记录用户活动
    record_activity(
        user_id=current_user.id,
        action_type='delete',
        target_type='attraction',
        target_id=attraction.id
    )
    
    return jsonify(success_response("删除景点成功"))


@attraction_bp.route('/hot', methods=['GET'])
def get_hot_attractions():
    """获取热门景点"""
    limit = min(request.args.get('limit', 10, type=int), 50)
    
    attractions = Attraction.query.filter_by(status=1, is_hot=True).order_by(
        desc(Attraction.view_count)
    ).limit(limit).all()
    
    attractions_data = [attraction.to_dict() for attraction in attractions]
    
    return jsonify(success_response("获取热门景点成功", attractions_data))


@attraction_bp.route('/recommended', methods=['GET'])
def get_recommended_attractions():
    """获取推荐景点"""
    limit = min(request.args.get('limit', 10, type=int), 50)
    
    attractions = Attraction.query.filter_by(status=1, is_recommended=True).order_by(
        desc(Attraction.created_at)
    ).limit(limit).all()
    
    attractions_data = [attraction.to_dict() for attraction in attractions]
    
    return jsonify(success_response("获取推荐景点成功", attractions_data))


@attraction_bp.route('/seasons/<int:season>', methods=['GET'])
def get_attractions_by_season(season):
    """根据季节获取景点"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # 获取所有该季节的景点ID
    season_records = TravelSeason.query.filter_by(season=season).all()
    attraction_ids = [record.attraction_id for record in season_records]
    
    # 查询景点 - 使用with_entities指定要查询的字段
    query = Attraction.query.with_entities(
        Attraction.id,
        Attraction.name,
        Attraction.description,
        Attraction.cover_image,
        Attraction.address,
        Attraction.longitude,
        Attraction.latitude,
        Attraction.category_id,
        Attraction.region_id,
        Attraction.open_time,
        Attraction.ticket_info,
        Attraction.traffic_info,
        Attraction.tips,
        Attraction.status,
        Attraction.like_count,
        Attraction.collection_count,
        Attraction.comment_count,
        Attraction.view_count,
        Attraction.is_hot,
        Attraction.is_recommended,
        Attraction.created_at,
        Attraction.updated_at
    ).filter(
        Attraction.id.in_(attraction_ids),
        Attraction.status == 1
    ).order_by(desc(Attraction.view_count))
    
    # 手动分页
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    
    # 创建分页对象
    from collections import namedtuple
    Pagination = namedtuple('Pagination', ['items', 'page', 'per_page', 'total', 'pages', 'has_next', 'has_prev'])
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1
    pagination = Pagination(items, page, per_page, total, pages, has_next, has_prev)
    
    # 转换为字典并添加季节推荐
    attractions = []
    for attraction in pagination.items:
        # 将查询结果转换为字典
        data = {}
        for idx, key in enumerate(query.column_descriptions):
            column_name = key['name']
            data[column_name] = attraction[idx]
        
        # 添加季节推荐
        season_record = next((s for s in season_records if s.attraction_id == data['id']), None)
        if season_record:
            data['season_recommendation'] = {
                'description': season_record.description,
                'temperature': season_record.temperature,
                'rainfall': season_record.rainfall,
                'tips': season_record.tips
            }
        
        # 添加分类名称
        if data.get('category_id'):
            from models.attraction import Category
            category = Category.query.get(data['category_id'])
            if category:
                data['category_name'] = category.name
                
        # 创建图片列表
        data['images'] = []
        data['attraction_images'] = []
        
        attractions.append(data)
    
    # 创建分页数据
    pagination_data = {
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }
    
    return jsonify(success_response(f"获取{TravelSeason.get_season_name(season)}景点成功", {
        'attractions': attractions,
        'pagination': pagination_data
    }))


class AttractionController:
    """景点控制器"""

    @staticmethod
    def get_attractions():
        """获取景点列表"""
        # 获取分页参数
        page, per_page = get_page_params()
        
        # 获取过滤参数
        category_id = request.args.get('category_id', type=int)
        region_id = request.args.get('region_id', type=int)
        keyword = request.args.get('keyword', '')
        sort_by = request.args.get('sort_by', 'popular')  # popular, latest, score
        season = request.args.get('season', type=int)     # 季节过滤(1春季,2夏季,3秋季,4冬季)
        
        # 构建基础查询
        query = Attraction.query.filter_by(status=1)  # 只查询状态正常的景点
        
        # 应用过滤条件
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if region_id:
            query = query.filter_by(region_id=region_id)
        
        if keyword:
            search_keyword = f"%{keyword}%"
            query = query.filter(Attraction.name.like(search_keyword) | 
                                 Attraction.description.like(search_keyword))
        
        if season:
            # 加入季节关联查询
            query = query.join(TravelSeason, Attraction.id == TravelSeason.attraction_id) \
                         .filter(TravelSeason.season == season)
        
        # 应用排序
        if sort_by == 'latest':
            query = query.order_by(desc(Attraction.created_at))
        elif sort_by == 'score':
            query = query.order_by(desc(Attraction.score))
        else:  # 默认按popularity排序
            query = query.order_by(desc(Attraction.popularity))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for attraction in paginate.items:
            # 基础数据
            attraction_data = attraction.to_dict(with_details=False)
            
            # 获取主图
            main_image = AttractionImage.query.filter_by(
                attraction_id=attraction.id, 
                is_main=True
            ).first()
            
            if main_image:
                attraction_data['main_image'] = main_image.image_url
            
            items.append(attraction_data)
        
        # 获取分类列表
        categories = Category.query.all()
        category_list = [category.to_dict() for category in categories]
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="获取景点列表成功",
            data={"categories": category_list}
        ))

    @staticmethod
    def get_attraction_detail(attraction_id):
        """获取景点详情"""
        # 查询景点
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify(error_response("景点不存在")), 404
        
        # 检查景点状态
        if attraction.status != 1:
            return jsonify(error_response("景点不可访问")), 403
        
        # 获取当前用户
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # 更新浏览量
        attraction.views += 1
        db.session.commit()
        
        # 如果有登录用户，记录浏览历史
        if user_id:
            # 检查是否已经有浏览记录
            browse_history = BrowseHistory.query.filter_by(
                user_id=user_id,
                target_id=attraction_id,
                target_type='attraction'
            ).first()
            
            if browse_history:
                # 更新已有记录
                browse_history.created_at = datetime.now()
            else:
                # 创建新记录
                browse_history = BrowseHistory(
                    user_id=user_id,
                    target_id=attraction_id,
                    target_type='attraction'
                )
                db.session.add(browse_history)
            
            db.session.commit()
            
            # 记录活动
            record_activity(
                user_id=user_id,
                action="view_attraction",
                module="attraction",
                target_id=attraction_id
            )
        
        # 获取详细数据
        result = attraction.to_dict(with_details=True)
        
        # 获取图片列表
        images = AttractionImage.query.filter_by(attraction_id=attraction_id).all()
        result['images'] = [image.to_dict() for image in images]
        
        # 获取门票信息
        tickets = Ticket.query.filter_by(
            attraction_id=attraction_id,
            status=1
        ).order_by(Ticket.price).all()
        result['tickets'] = [ticket.to_dict() for ticket in tickets]
        
        # 获取评论数量
        result['comment_count'] = Comment.query.filter_by(
            target_id=attraction_id,
            target_type='attraction',
            status=1
        ).count()
        
        # 如果用户已登录，获取用户收藏、点赞状态
        if user_id:
            result['is_collected'] = Collection.query.filter_by(
                user_id=user_id,
                target_id=attraction_id,
                target_type='attraction'
            ).first() is not None
            
            result['is_liked'] = Like.query.filter_by(
                user_id=user_id,
                target_id=attraction_id,
                target_type='attraction'
            ).first() is not None
        else:
            result['is_collected'] = False
            result['is_liked'] = False
        
        return jsonify(success_response("获取景点详情成功", result))

    @staticmethod
    def get_categories():
        """获取景点分类列表"""
        # 从缓存中获取分类列表
        cached_categories = cache.get('attraction_categories')
        if cached_categories:
            return jsonify(success_response("获取分类列表成功", cached_categories))
        
        # 如果缓存中没有，则从数据库获取
        categories = Category.query.all()
        category_list = [category.to_dict() for category in categories]
        
        # 更新缓存
        cache.set('attraction_categories', category_list, timeout=3600)  # 缓存1小时
        
        return jsonify(success_response("获取分类列表成功", category_list))

    @staticmethod
    @jwt_required()
    def like(attraction_id):
        """点赞景点"""
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("用户未找到")), 404
        
        # 查询景点
        attraction = Attraction.query.get_or_404(attraction_id)
        
        try:
            # 使用Like模型的add_like方法
            success = Like.add_like(current_user.id, attraction_id, 'attraction')
            if not success:
                return jsonify(error_response("已经点赞过了")), 400
            
            # 记录用户行为
            record_activity(
                user_id=current_user.id,
                action_type='like',
                target_type='attraction',
                target_id=attraction_id
            )
            
            return jsonify(success_response("点赞成功", {
                'like_count': attraction.like_count
            }))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"点赞失败: {str(e)}")
            return jsonify(error_response("点赞失败，服务器错误")), 500

    @staticmethod
    @jwt_required()
    def unlike(attraction_id):
        """取消点赞景点"""
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("用户未找到")), 404
        
        # 查询景点
        attraction = Attraction.query.get_or_404(attraction_id)
        
        try:
            # 使用Like模型的remove_like方法
            success = Like.remove_like(current_user.id, attraction_id, 'attraction')
            if not success:
                return jsonify(error_response("尚未点赞")), 400
            
            return jsonify(success_response("取消点赞成功", {
                'like_count': attraction.like_count
            }))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"取消点赞失败: {str(e)}")
            return jsonify(error_response("取消点赞失败，服务器错误")), 500

    @staticmethod
    @jwt_required()
    def collect(attraction_id):
        """收藏景点"""
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("用户未找到")), 404
        
        # 查询景点
        attraction = Attraction.query.get_or_404(attraction_id)
        
        try:
            # 使用Collection模型的add_collection方法
            success = Collection.add_collection(current_user.id, attraction_id, 'attraction')
            if not success:
                return jsonify(error_response("已经收藏过了")), 400
            
            # 记录用户行为
            record_activity(
                user_id=current_user.id,
                action_type='collect',
                target_type='attraction',
                target_id=attraction_id
            )
            
            return jsonify(success_response("收藏成功", {
                'collection_count': attraction.collection_count
            }))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"收藏失败: {str(e)}")
            return jsonify(error_response("收藏失败，服务器错误")), 500

    @staticmethod
    @jwt_required()
    def uncollect(attraction_id):
        """取消收藏景点"""
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("用户未找到")), 404
        
        # 查询景点
        attraction = Attraction.query.get_or_404(attraction_id)
        
        try:
            # 使用Collection模型的remove_collection方法
            success = Collection.remove_collection(current_user.id, attraction_id, 'attraction')
            if not success:
                return jsonify(error_response("尚未收藏")), 400
            
            return jsonify(success_response("取消收藏成功", {
                'collection_count': attraction.collection_count
            }))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"取消收藏失败: {str(e)}")
            return jsonify(error_response("取消收藏失败，服务器错误")), 500

    @staticmethod
    def get_comments(attraction_id):
        """获取景点评论"""
        # 查询景点
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify(error_response("景点不存在")), 404
        
        # 获取分页参数
        page, per_page = get_page_params()
        
        # 获取评论类型
        parent_id = request.args.get('parent_id', type=int)
        
        # 获取排序方式
        sort_by = request.args.get('sort_by', 'latest')  # latest, score
        
        # 构建查询
        query = Comment.query.filter_by(
            target_id=attraction_id,
            target_type='attraction',
            status=1  # 只查询已发布的评论
        )
        
        # 一级评论还是回复
        if parent_id:
            query = query.filter_by(parent_id=parent_id)
        else:
            query = query.filter(Comment.parent_id.is_(None))
        
        # 应用排序
        if sort_by == 'score':
            query = query.order_by(desc(Comment.score))
        else:  # 默认按最新排序
            query = query.order_by(desc(Comment.created_at))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for comment in paginate.items:
            comment_data = comment.to_dict()
            
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

    @staticmethod
    @jwt_required()
    def add_comment(attraction_id):
        """添加景点评论"""
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("用户未找到")), 404
        
        # 查询景点
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify(error_response("景点不存在")), 404
        
        data = request.form if request.form else request.get_json()
        
        content = data.get('content')
        parent_id = data.get('parent_id')
        images = data.get('images', [])
        
        # 验证数据
        if not content:
            return jsonify(error_response("评论内容不能为空")), 400
        
        # 创建评论
        try:
            # 根据Comment模型字段创建评论
            comment = Comment(
                user_id=current_user.id,
                content=content,
                content_id=attraction_id,
                content_type='attraction',
                parent_id=parent_id,
                images=images,
                status=1  # 默认已发布状态
            )
            
            db.session.add(comment)
            
            # 更新景点评论数
            if attraction.comment_count is None:
                attraction.comment_count = 1
            else:
                attraction.comment_count += 1
            
            db.session.commit()
            
            # 记录用户行为
            try:
                record_activity(
                    user_id=current_user.id,
                    action_type='comment',
                    target_type='attraction',
                    target_id=attraction_id
                )
            except:
                pass
            
            # 返回评论数据
            return jsonify(success_response("评论发表成功", comment.to_dict(with_user=True)))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"添加评论失败: {str(e)}")
            return jsonify(error_response(f"添加评论失败: {str(e)}")), 500


@attraction_bp.route('/<int:attraction_id>/like', methods=['POST'])
@login_required
def like_attraction(attraction_id):
    """点赞景点"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    # 查询景点
    attraction = Attraction.query.get_or_404(attraction_id)
    
    try:
        # 使用Like模型的add_like方法
        success = Like.add_like(current_user.id, attraction_id, 'attraction')
        if not success:
            return jsonify(error_response("已经点赞过了")), 400
        
        # 记录用户行为
        record_activity(
            user_id=current_user.id,
            action_type='like',
            target_type='attraction',
            target_id=attraction_id
        )
        
        return jsonify(success_response("点赞成功", {
            'like_count': attraction.like_count
        }))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"点赞失败: {str(e)}")
        return jsonify(error_response("点赞失败，服务器错误")), 500


@attraction_bp.route('/<int:attraction_id>/unlike', methods=['POST'])
@login_required
def unlike_attraction(attraction_id):
    """取消景点点赞"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    # 查询景点
    attraction = Attraction.query.get_or_404(attraction_id)
    
    try:
        # 使用Like模型的remove_like方法
        success = Like.remove_like(current_user.id, attraction_id, 'attraction')
        if not success:
            return jsonify(error_response("尚未点赞")), 400
        
        return jsonify(success_response("取消点赞成功", {
            'like_count': attraction.like_count
        }))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"取消点赞失败: {str(e)}")
        return jsonify(error_response("取消点赞失败，服务器错误")), 500


@attraction_bp.route('/<int:attraction_id>/collect', methods=['POST'])
@login_required
def collect_attraction(attraction_id):
    """收藏景点"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    # 查询景点
    attraction = Attraction.query.get_or_404(attraction_id)
    
    try:
        # 使用Collection模型的add_collection方法
        success = Collection.add_collection(current_user.id, attraction_id, 'attraction')
        if not success:
            return jsonify(error_response("已经收藏过了")), 400
        
        # 记录用户行为
        record_activity(
            user_id=current_user.id,
            action_type='collect',
            target_type='attraction',
            target_id=attraction_id
        )
        
        return jsonify(success_response("收藏成功", {
            'collection_count': attraction.collection_count
        }))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"收藏失败: {str(e)}")
        return jsonify(error_response("收藏失败，服务器错误")), 500


@attraction_bp.route('/<int:attraction_id>/uncollect', methods=['POST'])
@login_required
def uncollect_attraction(attraction_id):
    """取消收藏景点"""
    current_user = get_current_user()
    if not current_user:
        return jsonify(error_response("用户未找到")), 404
    
    # 查询景点
    attraction = Attraction.query.get_or_404(attraction_id)
    
    try:
        # 使用Collection模型的remove_collection方法
        success = Collection.remove_collection(current_user.id, attraction_id, 'attraction')
        if not success:
            return jsonify(error_response("尚未收藏")), 400
        
        return jsonify(success_response("取消收藏成功", {
            'collection_count': attraction.collection_count
        }))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"取消收藏失败: {str(e)}")
        return jsonify(error_response("取消收藏失败，服务器错误")), 500


@attraction_bp.route('/<int:attraction_id>/comments', methods=['GET'])
def get_attraction_comments(attraction_id):
    """获取景点评论列表"""
    from controllers.comment_controller import CommentController
    
    # 转发到评论控制器
    return CommentController.get_comments('attraction', attraction_id)


@attraction_bp.route('/<int:attraction_id>/comments', methods=['POST'])
@login_required
def add_attraction_comment(attraction_id):
    """添加景点评论"""
    return AttractionController.add_comment(attraction_id)


@attraction_bp.route('/<int:attraction_id>/tickets', methods=['GET'])
def get_attraction_tickets(attraction_id):
    """获取景点的门票列表"""
    # 检查景点是否存在
    attraction = Attraction.query.get_or_404(attraction_id)
    
    # 获取门票列表
    tickets = Ticket.query.filter_by(attraction_id=attraction_id, status=1).all()
    
    # 转换为字典列表
    ticket_list = [ticket.to_dict() for ticket in tickets]
    
    return jsonify(success_response("获取门票列表成功", ticket_list)) 