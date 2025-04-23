from datetime import datetime
from extensions import db
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.category import Category


class Attraction(db.Model):
    """景点模型"""
    __tablename__ = 'attractions'
    
    id = Column(Integer, primary_key=True, comment='景点ID')
    name = Column(String(100), nullable=False, comment='景点名称')
    description = Column(Text, comment='景点描述')
    cover_image = Column(String(255), comment='封面图片')
    images = Column(Text, comment='景点图片，逗号分隔')
    address = Column(String(255), comment='详细地址')
    longitude = Column(Float, comment='经度')
    latitude = Column(Float, comment='纬度')
    category_id = Column(Integer, ForeignKey('categories.id'), comment='分类ID')
    region_id = Column(Integer, ForeignKey('region.id'), comment='所属地区ID')
    open_time = Column(String(100), comment='开放时间')
    ticket_info = Column(Text, comment='门票信息')
    traffic_info = Column(Text, comment='交通信息')
    tips = Column(Text, comment='游玩贴士')
    status = Column(Integer, default=1, comment='状态(0下架,1上架)')
    like_count = Column(Integer, default=0, comment='点赞数')
    collection_count = Column(Integer, default=0, comment='收藏数')
    comment_count = Column(Integer, default=0, comment='评论数')
    view_count = Column(Integer, default=0, comment='浏览量')
    is_hot = Column(Boolean, default=False, comment='是否热门')
    is_recommended = Column(Boolean, default=False, comment='是否推荐')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    category = relationship('Category', back_populates='attractions')
    seasons = relationship('TravelSeason', back_populates='attraction')
    region = relationship('Region', back_populates='attractions')
    attraction_images = relationship('AttractionImage', back_populates='attraction')
    tickets = relationship('Ticket', back_populates='attraction')
    guides = relationship('GuideAttraction', back_populates='attraction')
    
    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '景点表 - 存储旅游景点基本信息'
    }
    
    def to_dict(self, with_category=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cover_image': self.cover_image,
            'address': self.address,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'category_id': self.category_id,
            'region_id': self.region_id,
            'open_time': self.open_time,
            'ticket_info': self.ticket_info,
            'traffic_info': self.traffic_info,
            'tips': self.tips,
            'status': self.status,
            'like_count': self.like_count,
            'collection_count': self.collection_count,
            'comment_count': self.comment_count,
            'view_count': self.view_count,
            'is_hot': self.is_hot,
            'is_recommended': self.is_recommended,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        
        # 添加图片信息
        if hasattr(self, 'attraction_images') and self.attraction_images:
            data['images'] = [image.url for image in self.attraction_images]
            data['attraction_images'] = [image.to_dict() for image in self.attraction_images]
        else:
            data['images'] = []
            data['attraction_images'] = []
        
        # 添加分类信息
        if with_category and self.category:
            data['category'] = self.category.to_dict()
            data['category_name'] = self.category.name
        else:
            data['category'] = None
            data['category_name'] = None
        
        return data


class AttractionImage(db.Model):
    """景点图片模型"""
    __tablename__ = 'attraction_images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='图片ID')
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False, comment='景点ID')
    url = db.Column(db.String(255), nullable=False, comment='图片URL')
    title = db.Column(db.String(100), comment='图片标题')
    description = db.Column(db.Text, comment='图片描述')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关联景点
    attraction = db.relationship('Attraction', back_populates='attraction_images')

    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '景点图片表 - 存储景点相关的图片信息'
    }

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'attraction_id': self.attraction_id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'sort_order': self.sort_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __repr__(self):
        return f'<AttractionImage {self.id}>' 