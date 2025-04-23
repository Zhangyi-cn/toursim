from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from models.user import User
from models.order import Order
from models.user_behavior import UserBehavior

class UserStats:
    """用户统计模型"""

    @staticmethod
    def get_user_count(start_date=None, end_date=None):
        """获取用户数量"""
        query = User.query
        if start_date:
            query = query.filter(User.created_at >= start_date)
        if end_date:
            query = query.filter(User.created_at < end_date)
        return query.count()

    @staticmethod
    def get_user_growth(days=30):
        """获取用户增长数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 按日期分组统计新增用户
        daily_new_users = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date,
            User.created_at <= end_date
        ).group_by(
            func.date(User.created_at)
        ).all()
        
        # 转换为字典格式
        result = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            count = 0
            for date, user_count in daily_new_users:
                if date.strftime('%Y-%m-%d') == date_str:
                    count = user_count
                    break
            result.append({
                'date': date_str,
                'count': count
            })
            current_date += timedelta(days=1)
        
        return result

    @staticmethod
    def get_user_active_stats(days=30):
        """获取用户活跃度统计"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 按日期分组统计活跃用户
        daily_active_users = db.session.query(
            func.date(UserBehavior.created_at).label('date'),
            func.count(func.distinct(UserBehavior.user_id)).label('count')
        ).filter(
            UserBehavior.created_at >= start_date,
            UserBehavior.created_at <= end_date
        ).group_by(
            func.date(UserBehavior.created_at)
        ).all()
        
        # 转换为字典格式
        result = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            count = 0
            for date, user_count in daily_active_users:
                if date.strftime('%Y-%m-%d') == date_str:
                    count = user_count
                    break
            result.append({
                'date': date_str,
                'count': count
            })
            current_date += timedelta(days=1)
        
        return result

    @staticmethod
    def get_user_consumption_stats():
        """获取用户消费统计"""
        # 统计总消费金额
        total_amount = db.session.query(func.sum(Order.total_amount)).filter(Order.status == 2).scalar() or 0
        
        # 统计人均消费
        user_count = User.query.count()
        avg_amount = total_amount / user_count if user_count > 0 else 0
        
        # 统计消费区间分布
        consumption_ranges = [
            {'range': '0-100', 'min': 0, 'max': 100, 'count': 0},
            {'range': '100-500', 'min': 100, 'max': 500, 'count': 0},
            {'range': '500-1000', 'min': 500, 'max': 1000, 'count': 0},
            {'range': '1000-5000', 'min': 1000, 'max': 5000, 'count': 0},
            {'range': '5000+', 'min': 5000, 'max': float('inf'), 'count': 0}
        ]
        
        # 查询每个用户的总消费
        user_consumptions = db.session.query(
            Order.user_id,
            func.sum(Order.total_amount).label('total')
        ).filter(
            Order.status == 2
        ).group_by(
            Order.user_id
        ).all()
        
        # 统计各区间的用户数
        for _, amount in user_consumptions:
            for range_info in consumption_ranges:
                if range_info['min'] <= amount < range_info['max']:
                    range_info['count'] += 1
                    break
        
        return {
            'total_amount': total_amount,
            'avg_amount': avg_amount,
            'consumption_ranges': consumption_ranges
        }

    @staticmethod
    def get_user_preferences():
        """获取用户偏好统计"""
        # 统计用户行为类型分布
        behavior_stats = db.session.query(
            UserBehavior.behavior_type,
            func.count(UserBehavior.id).label('count')
        ).group_by(
            UserBehavior.behavior_type
        ).all()
        
        # 统计目标类型分布
        target_stats = db.session.query(
            UserBehavior.target_type,
            func.count(UserBehavior.id).label('count')
        ).group_by(
            UserBehavior.target_type
        ).all()
        
        # 转换为字典格式
        behavior_types = {
            1: '浏览',
            2: '搜索',
            3: '点击',
            4: '停留',
            5: '分享'
        }
        
        target_types = {
            'attraction': '景点',
            'guide': '攻略',
            'note': '游记'
        }
        
        behavior_data = []
        for behavior_type, count in behavior_stats:
            behavior_data.append({
                'type': behavior_types.get(behavior_type, '未知'),
                'count': count
            })
        
        target_data = []
        for target_type, count in target_stats:
            target_data.append({
                'type': target_types.get(target_type, '未知'),
                'count': count
            })
        
        return {
            'behavior_stats': behavior_data,
            'target_stats': target_data
        } 