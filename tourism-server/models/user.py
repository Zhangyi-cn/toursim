from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from extensions import db


class User(db.Model):
    """用户模型"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, comment='用户ID')
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    password_hash = Column(String(255), nullable=False, comment='密码(加密存储)')
    email = Column(String(100), unique=True, nullable=False, comment='邮箱')
    phone = Column(String(20), unique=True, comment='手机号')
    nickname = Column(String(50), comment='昵称')
    avatar = Column(String(255), comment='头像URL')
    bio = Column(Text, comment='个人简介')
    role = Column(Integer, default=0, comment='角色(0普通用户,1管理员)')
    status = Column(Integer, default=1, comment='状态(0禁用,1正常)')
    last_login = Column(DateTime, comment='最后登录时间')
    interest_tags = Column(String(255), comment='兴趣标签,用于推荐(逗号分隔)')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联关系
    travel_notes = db.relationship('TravelNote', back_populates='user', lazy='dynamic')

    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '用户表 - 存储用户基本信息及认证信息'
    }

    @property
    def password(self):
        """密码属性不可读"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """设置密码时自动加密"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """是否是管理员"""
        return self.role == 1  # role=1表示管理员

    @is_admin.setter
    def is_admin(self, value):
        """设置是否为管理员"""
        self.role = 1 if value else 0

    def is_active(self):
        """账号是否激活"""
        return self.status == 1

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.now()
        db.session.commit()

    def get_interest_list(self):
        """获取兴趣标签列表"""
        if not self.interest_tags:
            return []
        return self.interest_tags.split(',')

    def set_interest_list(self, interests):
        """设置兴趣标签列表"""
        if not interests:
            self.interest_tags = ''
        else:
            self.interest_tags = ','.join(interests)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'avatar': self.avatar,
            'bio': self.bio,
            'role': self.role,
            'status': self.status,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
            'interest_tags': self.get_interest_list(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __repr__(self):
        return f'<User {self.username}>' 