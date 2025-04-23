from datetime import datetime
from extensions import db


class Tag(db.Model):
    """标签模型"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='标签ID')
    name = db.Column(db.String(50), nullable=False, comment='标签名称')
    type = db.Column(db.String(20), default='common', comment='标签类型')
    icon = db.Column(db.String(255), comment='标签图标')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    status = db.Column(db.Integer, default=1, comment='状态(0-禁用,1-启用)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 内容关联
    content_tags = db.relationship('ContentTag', back_populates='tag', lazy='dynamic', cascade='all, delete-orphan')
    
    # 表注释和约束
    __table_args__ = (
        db.UniqueConstraint('name', 'type', name='uix_tag_name_type'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_comment': '标签表 - 存储景点和游记的标签信息'
        }
    )

    @property
    def usage_count(self):
        """标签使用次数"""
        return self.content_tags.count() if self.content_tags else 0

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'status': self.status,
            'usage_count': self.usage_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Tag {self.name}>'


class ContentTag(db.Model):
    """内容标签关联模型"""
    __tablename__ = 'content_tags'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_id = db.Column(db.Integer, nullable=False, comment='内容ID')
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False, comment='标签ID')
    content_type = db.Column(db.String(20), nullable=False, comment='内容类型(attraction/travel_note/travel_guide)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    # 与标签的关系
    tag = db.relationship('Tag', back_populates='content_tags')
    
    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '内容标签关联表 - 存储内容与标签的关联关系'
    }
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'tag_id': self.tag_id,
            'content_type': self.content_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __repr__(self):
        return f'<ContentTag {self.id}>' 