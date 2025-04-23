from datetime import datetime
from extensions import db
from sqlalchemy import func, Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.tag import ContentTag, Tag


class TravelGuideCategory(db.Model):
    """旅游攻略分类模型"""
    __tablename__ = 'travel_guide_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, comment='分类名称')
    icon = Column(String(255), comment='分类图标')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    status = Column(Integer, default=1, comment='状态 0-禁用 1-启用')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 与攻略的关系
    guides = relationship('TravelGuide', back_populates='category')
    
    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '旅游攻略分类表 - 存储旅游攻略的分类信息'
    }
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TravelGuideCategory {self.id}>'


class TravelGuide(db.Model):
    """旅游攻略模型"""
    __tablename__ = 'travel_guides'
    
    id = Column(Integer, primary_key=True, comment='ID')
    title = Column(String(100), nullable=False, comment='标题')
    content = Column(Text, nullable=False, comment='内容')
    cover_image = Column(String(255), comment='封面图片')
    category_id = Column(Integer, ForeignKey('travel_guide_categories.id'), comment='分类ID')
    user_id = Column(Integer, ForeignKey('user.id'), comment='作者ID')
    status = Column(Integer, default=1, comment='状态 0-草稿 1-已发布 2-已删除')
    is_official = Column(Boolean, default=False, comment='是否官方攻略')
    is_hot = Column(Boolean, default=False, comment='是否热门')
    view_count = Column(Integer, default=0, comment='浏览量')
    like_count = Column(Integer, default=0, comment='点赞数')
    collection_count = Column(Integer, default=0, comment='收藏数')
    comment_count = Column(Integer, default=0, comment='评论数')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 与其他模型的关系
    category = relationship('TravelGuideCategory', back_populates='guides')
    attractions = relationship('GuideAttraction', back_populates='guide')
    
    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '旅游攻略表 - 存储旅游攻略信息'
    }
    
    def to_dict(self, with_content=True, user_id=None):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content if with_content else None,
            'cover_image': self.cover_image,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'user_id': self.user_id,
            'status': self.status,
            'is_official': self.is_official,
            'is_hot': self.is_hot,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'collection_count': self.collection_count,
            'comment_count': self.comment_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        
        # 获取标签
        tags = self.get_tags()
        if tags:
            data['tags'] = tags
        
        # 判断用户是否已点赞和收藏
        if user_id:
            from models.like import Like
            from models.collection import Collection
            
            # 判断是否已点赞
            like = Like.query.filter_by(
                user_id=user_id,
                target_type=2,  # 2表示guide
                target_id=self.id
            ).first()
            data['has_liked'] = bool(like)
            
            # 判断是否已收藏
            collection = Collection.query.filter_by(
                user_id=user_id,
                target_type='guide',
                target_id=self.id
            ).first()
            data['has_collected'] = bool(collection)
        else:
            data['has_liked'] = False
            data['has_collected'] = False
        
        return data
    
    def get_status_text(self):
        """获取状态文本"""
        status_mapping = {
            0: '草稿',
            1: '已发布',
            2: '已删除'
        }
        return status_mapping.get(self.status, '未知状态')
    
    def get_tags(self):
        """获取标签列表"""
        tags = db.session.query(
            ContentTag.tag_id,
            Tag.name
        ).join(
            Tag, ContentTag.tag_id == Tag.id
        ).filter(
            ContentTag.content_type == 'guide',
            ContentTag.content_id == self.id
        ).all()
        
        return [{'id': tag_id, 'name': name} for tag_id, name in tags]


class GuideAttraction(db.Model):
    """攻略景点关联模型"""
    __tablename__ = 'guide_attractions'
    
    id = Column(Integer, primary_key=True)
    guide_id = Column(Integer, ForeignKey('travel_guides.id'), nullable=False)
    attraction_id = Column(Integer, ForeignKey('attractions.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # 建立与景点和攻略的关系
    guide = relationship('TravelGuide', back_populates='attractions')
    attraction = relationship('Attraction', back_populates='guides')
    
    # 表注释
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci', 
        'mysql_comment': '攻略景点关联表 - 存储攻略与景点的关联关系'
    }

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'guide_id': self.guide_id,
            'attraction_id': self.attraction_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __repr__(self):
        return f'<GuideAttraction {self.id}>' 