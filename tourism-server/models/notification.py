from datetime import datetime
from extensions import db


class Notification(db.Model):
    """通知模型"""
    __tablename__ = 'notifications'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '通知表 - 存储用户的系统通知和消息提醒'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='用户ID')
    title = db.Column(db.String(100), nullable=False, comment='标题')
    content = db.Column(db.Text, nullable=False, comment='内容')
    type = db.Column(db.Integer, default=1, comment='类型(1系统,3订单)')
    is_read = db.Column(db.Boolean, default=False, comment='是否已读')
    read_time = db.Column(db.DateTime, comment='阅读时间')
    target_id = db.Column(db.Integer, comment='目标ID')
    target_type = db.Column(db.String(50), comment='目标类型')
    sender_id = db.Column(db.Integer, comment='发送者ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 定义关系
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'type_text': self.get_type_text(),
            'is_read': self.is_read,
            'read_time': self.read_time.strftime('%Y-%m-%d %H:%M:%S') if self.read_time else None,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'sender_id': self.sender_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def get_type_text(self):
        """获取类型文本"""
        type_map = {
            1: '系统通知',
            3: '订单通知'
        }
        return type_map.get(self.type, '未知')

    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_time = datetime.now()
            db.session.commit()

    @classmethod
    def send_notification(cls, user_id, title, content, type=1, target_id=None, target_type=None, sender_id=None):
        """发送通知"""
        notification = cls(
            user_id=user_id,
            title=title,
            content=content,
            type=type,
            target_id=target_id,
            target_type=target_type,
            sender_id=sender_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def send_system_notification(cls, user_ids, title, content):
        """发送系统通知"""
        notifications = []
        for user_id in user_ids:
            notification = cls.send_notification(user_id, title, content, type=1)
            notifications.append(notification)
        return notifications

    def __repr__(self):
        return f'<Notification {self.id}>' 