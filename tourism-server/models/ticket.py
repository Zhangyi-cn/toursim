from datetime import datetime
from extensions import db


class Ticket(db.Model):
    """门票模型"""
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True, comment='门票ID')
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False, comment='景点ID')
    name = db.Column(db.String(100), nullable=False, comment='门票名称')
    description = db.Column(db.Text, comment='门票描述')
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='价格')
    original_price = db.Column(db.Numeric(10, 2), nullable=True, comment='原价')
    type = db.Column(db.Integer, default=1, comment='门票类型：1=普通票，2=学生票，3=儿童票，4=老人票')
    notice = db.Column(db.Text, nullable=True, comment='购票须知')
    valid_period = db.Column(db.String(100), nullable=True, comment='有效期')
    status = db.Column(db.Integer, default=1, comment='状态：0=下架，1=上架')
    sold_count = db.Column(db.Integer, default=0, comment='销售数量')
    sort_order = db.Column(db.Integer, default=0, comment='排序序号')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联景点
    attraction = db.relationship('Attraction', back_populates='tickets')
    
    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '门票表 - 存储景点门票信息'
    }
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'attraction_id': self.attraction_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'original_price': float(self.original_price) if self.original_price else None,
            'type': self.type,
            'type_text': self.get_type_text(),
            'notice': self.notice,
            'valid_period': self.valid_period,
            'status': self.status,
            'status_text': self.get_status_text(),
            'sold_count': self.sold_count,
            'sort_order': self.sort_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_type_text(self):
        """获取类型文本"""
        type_map = {
            1: '普通票',
            2: '学生票',
            3: '儿童票',
            4: '老人票'
        }
        return type_map.get(self.type, '未知类型')
    
    def get_status_text(self):
        """获取状态文本"""
        status_map = {
            0: '已下架',
            1: '已上架'
        }
        return status_map.get(self.status, '未知状态')

    def __repr__(self):
        return f'<Ticket {self.id}>' 