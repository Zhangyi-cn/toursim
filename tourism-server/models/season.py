from extensions import db
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

class Season(db.Model):
    """季节推荐模型"""
    __tablename__ = 'seasons'
    
    id = Column(Integer, primary_key=True, comment='ID')
    attraction_id = Column(Integer, ForeignKey('attractions.id'), nullable=False, comment='景点ID')
    season = Column(Integer, nullable=False, comment='季节(1春季,2夏季,3秋季,4冬季)')
    description = Column(Text, comment='季节性描述')
    tips = Column(Text, comment='游玩建议')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '季节推荐表 - 存储景点的季节性游玩建议'
    }

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'attraction_id': self.attraction_id,
            'season': self.season,
            'description': self.description,
            'tips': self.tips,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        } 