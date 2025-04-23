from datetime import datetime
from app import db
from models.user import User

class BrowseHistory(db.Model):
    """浏览历史模型"""
    __tablename__ = 'browse_histories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # 'attraction', 'guide', 'note'
    target_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联用户
    user = db.relationship('User', 
                         backref=db.backref('browse_histories', lazy='dynamic'),
                         foreign_keys=[user_id])

    def __init__(self, user_id, target_type, target_id):
        self.user_id = user_id
        self.target_type = target_type
        self.target_id = target_id

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } 