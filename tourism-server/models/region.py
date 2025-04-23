from datetime import datetime
from extensions import db


class Region(db.Model):
    """地区模型"""
    __tablename__ = 'region'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='地区ID')
    name = db.Column(db.String(50), nullable=False, comment='地区名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('region.id'), comment='父级地区ID')
    level = db.Column(db.Integer, nullable=False, comment='级别(1省/直辖市,2市,3区/县)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 自引用关系
    parent = db.relationship('Region', remote_side=[id], backref=db.backref('children', lazy='dynamic'))
    
    # 反向引用
    attractions = db.relationship('Attraction', back_populates='region', lazy='dynamic')

    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '地区表 - 存储省市区等地理位置信息'
    }

    def get_parent_names(self):
        """获取所有父级地区名称"""
        names = []
        current = self
        while current.parent:
            names.insert(0, current.parent.name)
            current = current.parent
        return names

    def get_full_name(self):
        """获取完整地区名称（包含所有父级）"""
        names = self.get_parent_names()
        names.append(self.name)
        return ' '.join(names)

    def to_dict(self, with_children=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'level': self.level,
            'full_name': self.get_full_name(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        if with_children and self.children:
            data['children'] = [child.to_dict() for child in self.children]
        
        return data

    def __repr__(self):
        return f'<Region {self.name}>' 