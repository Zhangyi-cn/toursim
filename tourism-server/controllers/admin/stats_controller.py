from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from models.user_stats import UserStats
from models.order import Order
from models.attraction import Attraction
from models.comment import Comment
from models.travel_note import TravelNote
from models.travel_guide import TravelGuide
from utils.response import success_response
from utils.auth import admin_required

admin_stats_bp = Blueprint('admin_stats', __name__)


class AdminStatsController:
    """后台统计控制器"""
    
    @staticmethod
    @admin_stats_bp.route('/dashboard', methods=['GET'])
    @admin_required
    def get_dashboard_stats():
        """
        获取仪表盘统计数据
        ---
        tags:
          - 后台统计
        """
        # 获取时间范围
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # 用户统计
        total_users = UserStats.get_user_count()
        new_users_today = UserStats.get_user_count(start_date=today)
        new_users_yesterday = UserStats.get_user_count(start_date=yesterday, end_date=today)
        new_users_this_month = UserStats.get_user_count(start_date=this_month_start)
        new_users_last_month = UserStats.get_user_count(start_date=last_month_start, end_date=this_month_start)
        
        # 订单统计
        orders_count = Order.query.count()
        orders_today = Order.query.filter(Order.created_at >= today).count()
        completed_orders = Order.query.filter(Order.status == 2).count()  # 已完成
        pending_orders = Order.query.filter(Order.status == 0).count()  # 待支付
        paid_orders = Order.query.filter(Order.status == 1).count()  # 已支付
        cancelled_orders = Order.query.filter(Order.status == 4).count()  # 已取消
        
        # 内容统计
        attractions_count = Attraction.query.count()
        notes_count = TravelNote.query.count()
        guides_count = TravelGuide.query.count()
        comments_count = Comment.query.count()
        
        # 消费统计
        consumption_stats = UserStats.get_user_consumption_stats()
        
        # 构建响应数据
        result = {
            'user_stats': {
                'total_users': total_users,
                'new_users_today': new_users_today,
                'new_users_yesterday': new_users_yesterday,
                'new_users_this_month': new_users_this_month,
                'new_users_last_month': new_users_last_month
            },
            'order_stats': {
                'orders_count': orders_count,
                'orders_today': orders_today,
                'completed_orders': completed_orders,
                'pending_orders': pending_orders,
                'paid_orders': paid_orders,
                'cancelled_orders': cancelled_orders
            },
            'content_stats': {
                'attractions_count': attractions_count,
                'notes_count': notes_count,
                'guides_count': guides_count,
                'comments_count': comments_count
            },
            'consumption_stats': consumption_stats
        }
        
        return jsonify(success_response("获取仪表盘统计数据成功", result))
    
    @staticmethod
    @admin_stats_bp.route('/users', methods=['GET'])
    @admin_required
    def get_user_stats():
        """
        获取用户统计数据
        ---
        tags:
          - 后台统计
        parameters:
          - name: days
            in: query
            type: integer
            description: 天数
        """
        # 获取参数
        days = request.args.get('days', default=30, type=int)
        
        # 获取用户统计数据
        user_growth = UserStats.get_user_growth(days=days)
        user_active_stats = UserStats.get_user_active_stats(days=days)
        
        # 构建响应数据
        result = {
            'user_growth': user_growth,
            'user_active_stats': user_active_stats
        }
        
        return jsonify(success_response("获取用户统计数据成功", result))
    
    @staticmethod
    @admin_stats_bp.route('/consumption', methods=['GET'])
    @admin_required
    def get_consumption_stats():
        """
        获取消费统计数据
        ---
        tags:
          - 后台统计
        """
        # 获取消费统计数据
        consumption_stats = UserStats.get_user_consumption_stats()
        
        return jsonify(success_response("获取消费统计数据成功", consumption_stats))
    
    @staticmethod
    @admin_stats_bp.route('/preferences', methods=['GET'])
    @admin_required
    def get_preferences_stats():
        """
        获取用户偏好统计数据
        ---
        tags:
          - 后台统计
        """
        # 获取用户偏好统计数据
        preferences_stats = UserStats.get_user_preferences()
        
        return jsonify(success_response("获取用户偏好统计数据成功", preferences_stats))
    
    @staticmethod
    @admin_stats_bp.route('/orders', methods=['GET'])
    @admin_required
    def get_order_stats():
        """
        获取订单统计数据
        ---
        tags:
          - 后台统计
        parameters:
          - name: days
            in: query
            type: integer
            description: 天数
          - name: type
            in: query
            type: string
            enum: [daily, monthly]
            description: 统计类型(daily-每日, monthly-每月)
        """
        # 获取参数
        days = request.args.get('days', default=30, type=int)
        stat_type = request.args.get('type', default='daily')
        
        # 获取订单统计数据
        from controllers.admin.order_controller import AdminOrderController
        order_stats = AdminOrderController.generate_order_stats(days, stat_type)
        
        return jsonify(success_response("获取订单统计数据成功", order_stats))
    
    @staticmethod
    @admin_stats_bp.route('/attractions', methods=['GET'])
    @admin_required
    def get_attraction_stats():
        """
        获取景点统计数据
        ---
        tags:
          - 后台统计
        """
        # 获取景点统计数据
        attraction_stats = Attraction.query.all()
        
        return jsonify(success_response("获取景点统计数据成功", attraction_stats))
    
    @staticmethod
    @admin_stats_bp.route('/activities', methods=['GET'])
    @admin_required
    def get_activity_stats():
        """
        获取活动统计数据
        ---
        tags:
          - 后台统计
        """
        # 获取活动统计数据
        activity_stats = Activity.query.all()
        
        return jsonify(success_response("获取活动统计数据成功", activity_stats))

    @staticmethod
    @admin_required
    def get_guide_stats():
        """获取攻略统计数据"""
        # Implementation needed
        pass

    @staticmethod
    @admin_required
    def get_note_stats():
        """获取游记统计数据"""
        # Implementation needed
        pass

    @staticmethod
    @admin_required
    def get_comment_stats():
        """获取评论统计数据"""
        # Implementation needed
        pass 