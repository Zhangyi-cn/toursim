from datetime import datetime
from extensions import db
from sqlalchemy.orm import relationship


class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='评论ID')
    content_id = db.Column(db.Integer, nullable=False, comment='内容ID')
    content_type = db.Column(db.String(20), nullable=False, comment='内容类型(attraction/travel_note/travel_guide)')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='用户ID')
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), comment='父评论ID')
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    images = db.Column(db.JSON, default=[], comment='图片地址列表')
    like_count = db.Column(db.Integer, default=0, comment='点赞数')
    status = db.Column(db.Integer, default=1, comment='状态 0-已删除 1-正常')
    ip = db.Column(db.String(50), comment='IP地址')
    user_agent = db.Column(db.String(255), comment='用户代理')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联父评论
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))
    
    # 添加索引
    __table_args__ = (
        db.Index('idx_target', 'content_type', 'content_id'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_comment': '评论表 - 存储用户对景点和游记的评论信息'
        }
    )
    
    def to_dict(self, with_user=True):
        """转换为字典"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'content': self.content,
            'images': self.images,
            'parent_id': self.parent_id,
            'like_count': self.like_count,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 添加用户信息
        if with_user:
            try:
                from models.user import User
                user = User.query.get(self.user_id)
                if user:
                    result['user'] = {
                        'id': user.id,
                        'username': user.nickname or user.username,  # 优先使用昵称，如果没有则使用用户名
                        'avatar': user.avatar
                    }
            except Exception as e:
                # 如果获取用户信息失败，忽略错误
                pass
        
        return result
    
    @staticmethod
    def is_liked(user_id, comment_id):
        """检查用户是否点赞了评论"""
        from models.like import Like
        
        return Like.is_liked(
            user_id=user_id,
            target_id=comment_id,
            target_type='comment'
        )

    def get_status_text(self):
        """获取状态文本"""
        status_map = {
            0: '已删除',
            1: '正常'
        }
        return status_map.get(self.status, '未知')

    def approve(self):
        """审核通过"""
        if self.status != 1:
            self.status = 1
            db.session.commit()
            return True
        return False

    def reject(self):
        """审核拒绝"""
        if self.status != 0:
            self.status = 0
            db.session.commit()
            return True
        return False

    @classmethod
    def get_target_comments(cls, target_id, target_type, page=1, per_page=20, parent_id=None):
        """获取目标评论"""
        query = cls.query.filter_by(
            content_id=target_id,
            content_type=target_type,
            status=1
        )
        
        # 一级评论
        if parent_id is None:
            query = query.filter(cls.parent_id.is_(None))
        else:  # 回复评论
            query = query.filter_by(parent_id=parent_id)
            
        return query.order_by(cls.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def __repr__(self):
        return f'<Comment {self.id}>' 