import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models.user_behavior import UserBehavior
from models.attraction import Attraction
from extensions import db
from flask import current_app

class CollaborativeFiltering:
    """基于用户的协同过滤推荐系统"""
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_ids = None
        self.item_ids = None
        self.similarity_matrix = None
    
    def build_user_item_matrix(self):
        """构建用户-物品交互矩阵"""
        try:
            # 获取所有用户行为数据
            behaviors = UserBehavior.query.all()
            
            # 获取所有用户ID和景点ID
            user_ids = list(set(b.user_id for b in behaviors))
            item_ids = list(set(b.target_id for b in behaviors if b.target_type == 1))  # 1表示景点
            
            # 创建用户-物品矩阵
            matrix = np.zeros((len(user_ids), len(item_ids)))
            
            # 填充矩阵
            for behavior in behaviors:
                if behavior.target_type == 1:  # 只考虑景点
                    user_idx = user_ids.index(behavior.user_id)
                    item_idx = item_ids.index(behavior.target_id)
                    # 根据行为类型设置权重
                    weight = {
                        1: 1.0,  # 浏览
                        2: 2.0,  # 收藏
                        3: 3.0,  # 点赞
                        4: 2.0   # 评论
                    }.get(behavior.behavior_type, 1.0)
                    matrix[user_idx, item_idx] = weight
            
            self.user_item_matrix = matrix
            self.user_ids = user_ids
            self.item_ids = item_ids
            
            return True
        except Exception as e:
            current_app.logger.error(f"构建用户-物品矩阵失败: {str(e)}")
            return False
    
    def calculate_similarity(self):
        """计算用户相似度矩阵"""
        try:
            if self.user_item_matrix is None:
                if not self.build_user_item_matrix():
                    return False
            
            # 使用余弦相似度计算用户相似度
            self.similarity_matrix = cosine_similarity(self.user_item_matrix)
            return True
        except Exception as e:
            current_app.logger.error(f"计算用户相似度失败: {str(e)}")
            return False
    
    def get_recommendations(self, user_id, limit=10):
        """获取用户推荐"""
        try:
            if self.similarity_matrix is None:
                if not self.calculate_similarity():
                    return []
            
            # 获取用户索引
            if user_id not in self.user_ids:
                return []
            
            user_idx = self.user_ids.index(user_id)
            
            # 获取相似用户的评分
            similar_users = self.similarity_matrix[user_idx]
            
            # 计算推荐分数
            recommendations = np.zeros(len(self.item_ids))
            for i in range(len(self.user_ids)):
                if i != user_idx and similar_users[i] > 0:
                    recommendations += similar_users[i] * self.user_item_matrix[i]
            
            # 获取用户已交互的物品
            user_items = set()
            for behavior in UserBehavior.query.filter_by(user_id=user_id, target_type=1).all():
                user_items.add(behavior.target_id)
            
            # 过滤掉用户已交互的物品
            for i, item_id in enumerate(self.item_ids):
                if item_id in user_items:
                    recommendations[i] = 0
            
            # 获取推荐物品
            recommended_indices = np.argsort(recommendations)[-limit:][::-1]
            recommended_items = []
            
            for idx in recommended_indices:
                if recommendations[idx] > 0:
                    item_id = self.item_ids[idx]
                    attraction = Attraction.query.get(item_id)
                    if attraction and attraction.status == 1:
                        recommended_items.append({
                            'id': attraction.id,
                            'name': attraction.name,
                            'score': float(recommendations[idx])
                        })
            
            return recommended_items
            
        except Exception as e:
            current_app.logger.error(f"获取推荐失败: {str(e)}")
            return [] 