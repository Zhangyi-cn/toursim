from datetime import datetime
from extensions import db


class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '订单表 - 存储用户预订景点门票的订单信息'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(64), unique=True, nullable=False, comment='订单号')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='用户ID')
    amount = db.Column(db.Numeric(10, 2), nullable=False, comment='订单金额')
    status = db.Column(db.Integer, default=1, comment='订单状态：1=待支付,2=已支付,3=已完成,4=已取消')
    pay_method = db.Column(db.String(20), nullable=True, comment='支付方式：alipay,wechat,balance')
    pay_time = db.Column(db.DateTime, nullable=True, comment='支付时间')
    pay_no = db.Column(db.String(64), nullable=True, comment='支付流水号')
    contact_name = db.Column(db.String(50), nullable=False, comment='联系人姓名')
    contact_phone = db.Column(db.String(20), nullable=False, comment='联系人电话')
    visit_date = db.Column(db.Date, nullable=False, comment='游玩日期')
    remark = db.Column(db.String(255), nullable=True, comment='备注')
    cancel_time = db.Column(db.DateTime, nullable=True, comment='取消时间')
    cancel_reason = db.Column(db.String(255), nullable=True, comment='取消原因')
    complete_time = db.Column(db.DateTime, nullable=True, comment='完成时间')
    refund_time = db.Column(db.DateTime, nullable=True, comment='退款时间')
    refund_amount = db.Column(db.Numeric(10, 2), nullable=True, comment='退款金额')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 订单项关联
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def total_amount(self):
        """获取订单总金额，用于统计"""
        return self.amount
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'order_no': self.order_no,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'status': self.status,
            'status_text': self.get_status_text(),
            'pay_method': self.pay_method,
            'pay_time': self.pay_time.strftime('%Y-%m-%d %H:%M:%S') if self.pay_time else None,
            'pay_no': self.pay_no,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'visit_date': self.visit_date.strftime('%Y-%m-%d') if self.visit_date else None,
            'remark': self.remark,
            'cancel_time': self.cancel_time.strftime('%Y-%m-%d %H:%M:%S') if self.cancel_time else None,
            'cancel_reason': self.cancel_reason,
            'complete_time': self.complete_time.strftime('%Y-%m-%d %H:%M:%S') if self.complete_time else None,
            'refund_time': self.refund_time.strftime('%Y-%m-%d %H:%M:%S') if self.refund_time else None,
            'refund_amount': float(self.refund_amount) if self.refund_amount else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_status_text(self):
        """获取状态文本"""
        status_map = {
            1: '待支付',
            2: '已支付',
            3: '已完成',
            4: '已取消'
        }
        return status_map.get(self.status, '未知状态')


class OrderItem(db.Model):
    """订单项模型"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, comment='订单ID')
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, comment='门票ID')
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False, comment='景点ID')
    ticket_name = db.Column(db.String(100), nullable=False, comment='门票名称')
    attraction_name = db.Column(db.String(100), nullable=False, comment='景点名称')
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='单价')
    quantity = db.Column(db.Integer, nullable=False, comment='数量')
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, comment='小计')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'ticket_id': self.ticket_id,
            'attraction_id': self.attraction_id,
            'ticket_name': self.ticket_name,
            'attraction_name': self.attraction_name,
            'price': float(self.price),
            'quantity': self.quantity,
            'subtotal': float(self.subtotal),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def generate_order_no(cls):
        """生成订单号"""
        import random
        now = datetime.now()
        order_no = now.strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
        return order_no

    def __repr__(self):
        return f'<Order {self.order_no}>' 