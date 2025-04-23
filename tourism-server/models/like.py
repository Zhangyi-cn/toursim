from datetime import datetime
from extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey


class Like(db.Model):
    """点赞模型"""
    __tablename__ = 'likes'
    
    # 目标类型映射
    TARGET_TYPE_ATTRACTION = 1  # 景点
    TARGET_TYPE_GUIDE = 2      # 攻略
    TARGET_TYPE_NOTE = 3       # 游记
    TARGET_TYPE_COMMENT = 4    # 评论
    
    # 目标类型映射字典
    TARGET_TYPE_MAP = {
        'attraction': TARGET_TYPE_ATTRACTION,
        'guide': TARGET_TYPE_GUIDE,
        'note': TARGET_TYPE_NOTE,
        'comment': TARGET_TYPE_COMMENT
    }
    
    # 反向映射
    TARGET_TYPE_MAP_REVERSE = {
        TARGET_TYPE_ATTRACTION: 'attraction',
        TARGET_TYPE_GUIDE: 'guide',
        TARGET_TYPE_NOTE: 'note',
        TARGET_TYPE_COMMENT: 'comment'
    }
    
    id = Column(Integer, primary_key=True, comment='点赞ID')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='用户ID')
    target_type = Column(Integer, nullable=False, comment='点赞目标类型(1景点,2攻略,3游记,4评论)')
    target_id = Column(Integer, nullable=False, comment='点赞目标ID')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 关联用户
    # user = relationship('User', back_populates='likes')
    
    # 添加唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='uix_user_target'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_comment': '点赞表 - 存储用户对景点和游记的点赞记录'
        }
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_type': self.TARGET_TYPE_MAP_REVERSE.get(self.target_type, 'unknown'),
            'target_id': self.target_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def is_liked(user_id, target_id, target_type):
        """检查用户是否已点赞"""
        # 将字符串类型转换为整数类型
        target_type_num = Like.TARGET_TYPE_MAP.get(target_type)
        if target_type_num is None:
            return False
            
        like = Like.query.filter_by(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type_num
        ).first()
        
        return like is not None
    
    @staticmethod
    def add_like(user_id, target_id, target_type):
        """添加点赞"""
        # 将字符串类型转换为整数类型
        target_type_num = Like.TARGET_TYPE_MAP.get(target_type)
        if target_type_num is None:
            return False
            
        # 检查是否已点赞
        if Like.is_liked(user_id, target_id, target_type):
            return False
        
        # 添加点赞记录
        like = Like(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type_num
        )
        
        try:
            db.session.add(like)
            
            # 更新目标对象的点赞数
            Like._update_target_like_count(target_id, target_type, 1)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def remove_like(user_id, target_id, target_type):
        """取消点赞"""
        # 将字符串类型转换为整数类型
        target_type_num = Like.TARGET_TYPE_MAP.get(target_type)
        if target_type_num is None:
            return False
            
        # 查找点赞记录
        like = Like.query.filter_by(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type_num
        ).first()
        
        if not like:
            return False
        
        try:
            db.session.delete(like)
            
            # 更新目标对象的点赞数
            Like._update_target_like_count(target_id, target_type, -1)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def _update_target_like_count(target_id, target_type, increment):
        """更新目标对象的点赞数"""
        if target_type == 'attraction':
            from models.attraction import Attraction
            target = Attraction.query.get(target_id)
            if target:
                target.like_count += increment
        elif target_type == 'note':
            from models.travel_note import TravelNote
            target = TravelNote.query.get(target_id)
            if target:
                target.like_count += increment
        elif target_type == 'guide':
            from models.travel_guide import TravelGuide
            target = TravelGuide.query.get(target_id)
            if target:
                target.like_count += increment
        elif target_type == 'comment':
            from models.comment import Comment
            target = Comment.query.get(target_id)
            if target:
                target.like_count += increment

    def __repr__(self):
        return f'<Like {self.id}>'

    @staticmethod
    def toggle_like(user_id, target_id, target_type):
        """
        切换点赞状态
        :param user_id: 用户ID
        :param target_id: 目标ID
        :param target_type: 目标类型
        :return: bool 当前点赞状态
        """
        is_liked = Like.is_liked(user_id, target_id, target_type)
        
        if is_liked:
            # 已点赞，取消点赞
            Like.remove_like(user_id, target_id, target_type)
            return False
        else:
            # 未点赞，添加点赞
            Like.add_like(user_id, target_id, target_type)
            return True
    
    @staticmethod
    def count_likes(target_id, target_type):
        """
        统计点赞数量
        :param target_id: 目标ID
        :param target_type: 目标类型
        :return: int 点赞数量
        """
        return Like.query.filter_by(
            target_id=target_id,
            target_type=target_type
        ).count() 