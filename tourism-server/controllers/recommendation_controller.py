from flask import Blueprint, request, jsonify
from utils.response import success_response, error_response
from sqlalchemy import desc, func, case
from models.attraction import Attraction
from models.travel_guide import TravelGuide
from models.travel_note import TravelNote
from utils.cache import cache
from datetime import datetime, timedelta
from utils.auth import login_required, get_current_user
from services.recommendation_service import RecommendationService

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('', methods=['GET'])
@login_required
def get_recommendations():
    """获取个性化推荐"""
    try:
        # 获取当前用户
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("用户未找到")), 404
            
        # 获取请求参数
        item_type = request.args.get('type', 'all')  # 可选值：attraction, guide, note, all
        limit = min(int(request.args.get('limit', 10)), 50)  # 限制最大返回数量为50
        
        # 获取推荐服务
        recommendation_service = RecommendationService()
        
        # 获取推荐结果
        recommendations = recommendation_service.get_user_recommendations(
            user_id=current_user.id,
            target_type=item_type if item_type != 'all' else None,
            limit=limit
        )
        
        return jsonify(success_response("获取推荐成功", recommendations))
        
    except Exception as e:
        return jsonify(error_response(f"获取推荐失败：{str(e)}")), 500

@recommendation_bp.route('/hot', methods=['GET'])
def get_hot_items():
    """获取热门推荐"""
    try:
        # 获取请求参数
        item_type = request.args.get('type', 'all')  # 可选值：attraction, guide, note, all
        limit = min(int(request.args.get('limit', 10)), 50)  # 限制最大返回数量为50
        
        data = {}
        
        # 计算时间衰减因子（7天内的内容权重更高）
        week_ago = datetime.now() - timedelta(days=7)
        time_factor = case(
            [(func.date(Attraction.created_at) >= week_ago, 1.2)],
            else_=1.0
        )
        
        # 根据类型返回对应的热门内容
        if item_type in ['attraction', 'all']:
            hot_attractions = Attraction.query.filter_by(status=1).order_by(
                desc(
                    (Attraction.view_count * 0.4 + 
                    Attraction.like_count * 0.3 + 
                    Attraction.collection_count * 0.3) * 
                    time_factor +
                    func.rand() * 0.2  # 添加随机因子
                )
            ).limit(limit).all()
            data['attractions'] = [attraction.to_dict(with_category=False) for attraction in hot_attractions]
            
        if item_type in ['guide', 'all']:
            hot_guides = TravelGuide.query.filter_by(status=1).order_by(
                desc(
                    (TravelGuide.view_count * 0.6 + 
                    TravelGuide.like_count * 0.4) * 
                    time_factor +
                    func.rand() * 0.2  # 添加随机因子
                )
            ).limit(limit).all()
            data['guides'] = [guide.to_dict() for guide in hot_guides]
            
        if item_type in ['note', 'all']:
            hot_notes = TravelNote.query.filter_by(status=1).order_by(
                desc(
                    (TravelNote.views * 0.4 + 
                    TravelNote.likes * 0.3 + 
                    TravelNote.collections * 0.3) * 
                    time_factor +
                    func.rand() * 0.2  # 添加随机因子
                )
            ).limit(limit).all()
            data['notes'] = [note.to_dict() for note in hot_notes]
            
        return jsonify(success_response("获取热门推荐成功", data))
        
    except Exception as e:
        return jsonify(error_response(f"获取热门推荐失败：{str(e)}")), 500

@recommendation_bp.route('/today', methods=['GET'])
@cache.cached(timeout=300)  # 缓存5分钟
def get_today_recommendations():
    """获取今日推荐"""
    try:
        # 计算时间衰减因子（7天内的内容权重更高）
        week_ago = datetime.now() - timedelta(days=7)
        
        # 获取热门景点
        hot_attractions = Attraction.query.filter_by(status=1).order_by(
            desc(
                (Attraction.view_count * 0.4 + 
                Attraction.like_count * 0.3 + 
                Attraction.collection_count * 0.3) * 
                case(
                    (func.date(Attraction.created_at) >= week_ago, 1.2),
                    else_=1.0
                ) +
                func.rand() * 0.2  # 添加随机因子
            )
        ).limit(5).all()
        
        # 获取热门攻略
        hot_guides = TravelGuide.query.filter_by(status=1).order_by(
            desc(
                (TravelGuide.view_count * 0.6 + 
                TravelGuide.like_count * 0.4) * 
                case(
                    (func.date(TravelGuide.created_at) >= week_ago, 1.2),
                    else_=1.0
                ) +
                func.rand() * 0.2  # 添加随机因子
            )
        ).limit(5).all()
        
        # 获取热门游记
        hot_notes = TravelNote.query.filter_by(status=1).order_by(
            desc(
                (TravelNote.views * 0.4 + 
                TravelNote.likes * 0.3 + 
                TravelNote.collections * 0.3) * 
                case(
                    (func.date(TravelNote.created_at) >= week_ago, 1.2),
                    else_=1.0
                ) +
                func.rand() * 0.2  # 添加随机因子
            )
        ).limit(5).all()
        
        return jsonify(success_response("获取今日推荐成功", {
            'attractions': [attraction.to_dict(with_category=False) for attraction in hot_attractions],
            'guides': [guide.to_dict() for guide in hot_guides],
            'notes': [note.to_dict() for note in hot_notes]
        }))
        
    except Exception as e:
        return jsonify(error_response(f"获取今日推荐失败：{str(e)}")), 500 