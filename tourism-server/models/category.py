from extensions import db
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Category(db.Model):
    """分类模型"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, comment='分类ID')
    name = Column(String(50), nullable=False, comment='分类名称')
    description = Column(String(200), comment='分类描述')
    type = Column(Integer, default=1, comment='分类类型(1景点分类,2游记分类)')
    sort_order = Column(Integer, default=0, comment='排序')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 添加反向关系
    attractions = relationship('Attraction', back_populates='category', foreign_keys='Attraction.category_id')

    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '分类表 - 存储景点和游记的分类信息'
    }

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'sort_order': self.sort_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        } 