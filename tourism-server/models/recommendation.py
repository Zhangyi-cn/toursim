from extensions import db
from datetime import datetime

class Recommendation(db.Model):
    """推荐表"""
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # attraction, guide, note
    target_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False, default=0)
    reason = db.Column(db.String(100))
    status = db.Column(db.Integer, nullable=False, default=1)  # 1: 有效, 0: 无效
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'score': self.score,
            'reason': self.reason,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class RecommendationRule(db.Model):
    """推荐规则表"""
    __tablename__ = 'recommendation_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    weight = db.Column(db.Float, nullable=False, default=1.0)
    status = db.Column(db.Integer, nullable=False, default=1)  # 1: 启用, 0: 禁用
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'weight': self.weight,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } 