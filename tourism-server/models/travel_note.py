from datetime import datetime
from extensions import db


class TravelNote(db.Model):
    """游记模型"""
    __tablename__ = 'travel_notes'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '游记表 - 存储用户发布的旅游游记内容'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='用户ID')
    title = db.Column(db.String(100), nullable=False, comment='标题')
    content = db.Column(db.Text, nullable=False, comment='内容')
    description = db.Column(db.String(255), nullable=True, comment='描述')
    cover_image = db.Column(db.String(255), nullable=True, comment='封面图片')
    views = db.Column(db.Integer, default=0, comment='浏览量')
    likes = db.Column(db.Integer, default=0, comment='点赞数')
    collections = db.Column(db.Integer, default=0, comment='收藏数')
    comments = db.Column(db.Integer, default=0, comment='评论数')
    status = db.Column(db.Integer, default=1, comment='状态：0=草稿，1=已发布，2=已删除')
    location = db.Column(db.String(100), nullable=True, comment='位置')
    latitude = db.Column(db.Float, nullable=True, comment='纬度')
    longitude = db.Column(db.Float, nullable=True, comment='经度')
    trip_start_date = db.Column(db.Date, nullable=True, comment='旅行开始日期')
    trip_end_date = db.Column(db.Date, nullable=True, comment='旅行结束日期')
    trip_days = db.Column(db.Integer, nullable=True, comment='旅行天数')
    trip_cost = db.Column(db.Numeric(10, 2), nullable=True, comment='旅行花费')
    attraction_ids = db.Column(db.String(255), nullable=True, comment='相关景点ID，逗号分隔')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联用户
    user = db.relationship('User', back_populates='travel_notes')
    
    def to_dict(self, with_details=True):
        """转换为字典"""
        base_dict = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'cover_image': self.cover_image,
            'views': self.views,
            'likes': self.likes,
            'collections': self.collections,
            'comments': self.comments,
            'status': self.status,
            'status_text': self.get_status_text(),
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'trip_start_date': self.trip_start_date.strftime('%Y-%m-%d') if self.trip_start_date else None,
            'trip_end_date': self.trip_end_date.strftime('%Y-%m-%d') if self.trip_end_date else None,
            'trip_days': self.trip_days,
            'trip_cost': float(self.trip_cost) if self.trip_cost else None,
            'attraction_ids': [int(x) for x in self.attraction_ids.split(',')] if self.attraction_ids else [],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # 是否包含详细内容
        if with_details:
            base_dict['content'] = self.content
        
        return base_dict
    
    def get_status_text(self):
        """获取状态文本"""
        status_map = {
            0: '草稿',
            1: '已发布',
            2: '已删除'
        }
        return status_map.get(self.status, '未知状态')


class TravelNoteImage(db.Model):
    """游记图片模型"""
    __tablename__ = 'travel_note_images'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '游记图片表 - 存储游记相关的图片信息'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='图片ID')
    note_id = db.Column(db.Integer, db.ForeignKey('travel_notes.id'), nullable=False, comment='游记ID')
    url = db.Column(db.String(255), nullable=False, comment='图片URL')
    title = db.Column(db.String(100), comment='图片标题')
    description = db.Column(db.Text, comment='图片描述')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'note_id': self.note_id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'sort_order': self.sort_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __repr__(self):
        return f'<TravelNoteImage {self.id}>'


class NoteAttraction(db.Model):
    """游记景点关联模型"""
    __tablename__ = 'note_attractions'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '游记景点关联表 - 存储游记与景点的关联关系'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='ID')
    note_id = db.Column(db.Integer, db.ForeignKey('travel_notes.id'), nullable=False, comment='游记ID')
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False, comment='景点ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'note_id': self.note_id,
            'attraction_id': self.attraction_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __repr__(self):
        return f'<NoteAttraction {self.id}>' 