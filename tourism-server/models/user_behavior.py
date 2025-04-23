from app import db
from datetime import datetime

class UserBehavior(db.Model):
    """用户行为模型"""
    __tablename__ = 'user_behaviors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='用户ID')
    behavior_type = db.Column(db.Integer, nullable=False, comment='行为类型(1浏览,2搜索,3点击,4停留,5分享)')
    target_id = db.Column(db.Integer, nullable=False, comment='目标ID')
    target_type = db.Column(db.String(50), nullable=False, comment='目标类型(attraction/guide/note)')
    duration = db.Column(db.Integer, default=0, comment='停留时长(秒)')
    ip = db.Column(db.String(50), nullable=True, comment='IP地址')
    user_agent = db.Column(db.String(255), nullable=True, comment='User Agent')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'behavior_type': self.behavior_type,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'duration': self.duration,
            'ip': self.ip,
            'user_agent': self.user_agent,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    @staticmethod
    def get_type_text(behavior_type):
        """获取行为类型文本"""
        type_map = {
            1: '浏览',
            2: '搜索',
            3: '点击',
            4: '停留',
            5: '分享'
        }
        return type_map.get(behavior_type, '未知') 