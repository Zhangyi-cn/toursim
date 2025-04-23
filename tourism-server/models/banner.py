from datetime import datetime
from extensions import db

class Banner(db.Model):
    """轮播图模型"""
    __tablename__ = 'banners'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='轮播图ID')
    title = db.Column(db.String(100), nullable=False, comment='标题')
    image_url = db.Column(db.String(255), nullable=False, comment='图片URL')
    link_url = db.Column(db.String(255), comment='链接URL')
    description = db.Column(db.String(255), comment='描述')
    sort_order = db.Column(db.Integer, comment='排序')
    is_active = db.Column(db.Boolean, comment='是否启用')
    created_at = db.Column(db.DateTime, comment='创建时间')
    updated_at = db.Column(db.DateTime, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image_url,
            'link_url': self.link_url,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '轮播图表 - 存储首页轮播图信息'
    } 