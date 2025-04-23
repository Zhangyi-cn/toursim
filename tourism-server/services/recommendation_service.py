from datetime import datetime, timedelta
from sqlalchemy import func, desc, case, and_
from extensions import db
from models.recommendation import Recommendation
from models.attraction import Attraction
from models.travel_guide import TravelGuide
from models.travel_note import TravelNote
from models.like import Like
from models.collection import Collection
from models.user_behavior import UserBehavior
from models.browse_history import BrowseHistory
from flask import current_app
from services.collaborative_filtering import CollaborativeFiltering
import random


class RecommendationService:
    """推荐服务"""
    
    def __init__(self):
        """初始化"""
        self.cf = CollaborativeFiltering()
    
    def generate_recommendations(self, user_id, target_type=None):
        """
        生成用户推荐
        :param user_id: 用户ID
        :param target_type: 目标类型(attraction)
        """
        try:
            # 删除已有的推荐
            if target_type:
                Recommendation.query.filter_by(
                    user_id=user_id,
                    target_type=target_type
                ).delete()
            else:
                Recommendation.query.filter_by(user_id=user_id).delete()
            
            # 获取用户行为数据
            user_behaviors = UserBehavior.query.filter_by(user_id=user_id).all()
            
            # 根据用户行为生成个性化推荐
            if user_behaviors:
                # 使用协同过滤生成推荐
                cf_recommendations = self.cf.get_recommendations(user_id)
                if cf_recommendations:
                    self._save_cf_recommendations(user_id, cf_recommendations)
                else:
                    self._generate_personalized_recommendations(user_id, user_behaviors)
            else:
                self._generate_default_recommendations(user_id)
                
            return True
        except Exception as e:
            current_app.logger.error(f"生成推荐失败: {str(e)}")
            return False
    
    def _save_cf_recommendations(self, user_id, recommendations):
        """保存协同过滤推荐结果"""
        try:
            rec_objects = []
            for idx, rec in enumerate(recommendations):
                rec_objects.append(Recommendation(
                    user_id=user_id,
                    target_type='attraction',
                    target_id=rec['id'],
                    score=5.0 - idx * 0.3,  # 分数递减
                    reason='基于相似用户的推荐',
                    status=1
                ))
            
            if rec_objects:
                db.session.bulk_save_objects(rec_objects)
                db.session.commit()
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"保存协同过滤推荐失败: {str(e)}")
            # 出错时尝试生成默认推荐
            self._generate_default_recommendations(user_id)

    def get_user_recommendations(self, user_id, target_type=None, limit=10):
        """
        获取用户的推荐内容
        :param user_id: 用户ID
        :param target_type: 目标类型(attraction)
        :param limit: 限制数量
        :return: 推荐内容列表
        """
        try:
            # 强制只返回景区推荐
            target_type = 'attraction'
            
            # 查询现有的推荐
            recommendations = Recommendation.query.filter_by(
                user_id=user_id,
                target_type=target_type
            )
            
            # 按分数排序并限制数量
            recommendations = recommendations.order_by(desc(Recommendation.score)).limit(limit).all()
            
            # 如果推荐数量不足，生成新的推荐
            if len(recommendations) < limit:
                self.generate_recommendations(user_id)
                
                # 重新查询
                recommendations = Recommendation.query.filter_by(
                    user_id=user_id,
                    target_type=target_type
                )
                recommendations = recommendations.order_by(desc(Recommendation.score)).limit(limit).all()
            
            # 构造返回数据
            result = []
            for rec in recommendations:
                target = Attraction.query.get(rec.target_id)
                if target and target.status == 1:
                    result.append({
                        'id': target.id,
                        'type': 'attraction',
                        'title': target.name,
                        'cover_image': target.cover_image,
                        'description': target.description[:100] if target.description else None,
                        'view_count': target.view_count,
                        'like_count': target.like_count,
                        'collection_count': target.collection_count,
                        'score': rec.score
                    })
            
            return result
        
        except Exception as e:
            current_app.logger.error(f"获取推荐失败: {str(e)}")
            return []

    @staticmethod
    def _generate_default_recommendations(user_id):
        """生成默认推荐"""
        try:
            recommendations = []
            week_ago = datetime.now() - timedelta(days=7)
            
            # 只生成景点推荐
            attractions = Attraction.query.filter_by(status=1).order_by(
                desc(
                    (Attraction.view_count * 0.4 + 
                    Attraction.like_count * 0.3 + 
                    Attraction.collection_count * 0.3) * 
                    func.if_(
                        func.date(Attraction.created_at) >= week_ago,
                        1.5,  # 新内容权重提升50%
                        1.0
                    ) * 
                    (func.random() * 0.2 + 0.9)  # 添加10%-30%随机性
                )
            ).limit(10).all()
            
            score = 5.0
            for attraction in attractions:
                # 检查是否已存在相同的推荐记录
                existing = Recommendation.query.filter_by(
                    user_id=user_id,
                    target_type='attraction',
                    target_id=attraction.id
                ).first()
                
                if not existing:
                    recommendations.append(Recommendation(
                        user_id=user_id,
                        target_type='attraction',
                        target_id=attraction.id,
                        score=score,
                        reason='根据你的偏好推荐',
                        status=1
                    ))
                    score -= 0.3
            
            # 保存推荐
            if recommendations:
                db.session.bulk_save_objects(recommendations)
                db.session.commit()
                
            return True
        except Exception as e:
            current_app.logger.error(f"生成默认推荐失败: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def _generate_personalized_recommendations(user_id, user_behaviors):
        """根据用户行为生成个性化推荐"""
        try:
            recommendations = []
            
            # 获取推荐内容 - 只推荐景点
            attractions = Attraction.query.filter_by(status=1).order_by(
                desc(Attraction.view_count * 0.4 + 
                    Attraction.like_count * 0.3 + 
                    Attraction.collection_count * 0.3)
            ).limit(10).all()
            
            for idx, attraction in enumerate(attractions):
                # 检查是否已存在相同的推荐记录
                existing = Recommendation.query.filter_by(
                    user_id=user_id,
                    target_type='attraction',
                    target_id=attraction.id
                ).first()
                
                if not existing:
                    score = 5.0 - idx * 0.3
                    recommendations.append(Recommendation(
                        user_id=user_id,
                        target_id=attraction.id,
                        target_type='attraction',
                        score=score,
                        reason='根据你的偏好推荐',
                        status=1
                    ))
            
            # 保存推荐记录
            if recommendations:
                db.session.bulk_save_objects(recommendations)
                db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"生成个性化推荐失败: {str(e)}")
            # 出错时尝试生成默认推荐
            RecommendationService._generate_default_recommendations(user_id) 