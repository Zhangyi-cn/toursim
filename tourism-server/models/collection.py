from datetime import datetime
from extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey


class Collection(db.Model):
    """收藏模型"""
    __tablename__ = 'collections'
    
    # 目标类型映射
    TARGET_TYPE_ATTRACTION = 1  # 景点
    TARGET_TYPE_GUIDE = 2      # 攻略
    TARGET_TYPE_NOTE = 3       # 游记
    
    # 目标类型映射字典
    TARGET_TYPE_MAP = {
        'attraction': TARGET_TYPE_ATTRACTION,
        'guide': TARGET_TYPE_GUIDE,
        'note': TARGET_TYPE_NOTE
    }
    
    # 反向映射
    TARGET_TYPE_MAP_REVERSE = {
        TARGET_TYPE_ATTRACTION: 'attraction',
        TARGET_TYPE_GUIDE: 'guide',
        TARGET_TYPE_NOTE: 'note'
    }
    
    id = Column(Integer, primary_key=True, comment='收藏ID')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='用户ID')
    target_type = Column(Integer, nullable=False, comment='收藏目标类型(1景点,2攻略,3游记)')
    target_id = Column(Integer, nullable=False, comment='收藏目标ID')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 关联用户
    # user = relationship('User', back_populates='collections')
    
    # 添加唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='uix_user_target'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_comment': '收藏表 - 存储用户对景点和游记的收藏记录'
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
    def is_collected(user_id, target_id, target_type):
        """检查用户是否已收藏"""
        # 将字符串类型转换为整数类型
        target_type_num = Collection.TARGET_TYPE_MAP.get(target_type)
        if target_type_num is None:
            return False
            
        collection = Collection.query.filter_by(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type_num
        ).first()
        
        return collection is not None
    
    @staticmethod
    def add_collection(user_id, target_id, target_type):
        """添加收藏"""
        # 将字符串类型转换为整数类型
        target_type_num = Collection.TARGET_TYPE_MAP.get(target_type)
        if target_type_num is None:
            return False
            
        # 检查是否已收藏
        if Collection.is_collected(user_id, target_id, target_type):
            return False
        
        # 添加收藏记录
        collection = Collection(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type_num
        )
        
        try:
            db.session.add(collection)
            
            # 更新目标对象的收藏数
            Collection._update_target_collection_count(target_id, target_type, 1)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def remove_collection(user_id, target_id, target_type):
        """取消收藏"""
        # 将字符串类型转换为整数类型
        target_type_num = Collection.TARGET_TYPE_MAP.get(target_type)
        if target_type_num is None:
            return False
            
        # 查找收藏记录
        collection = Collection.query.filter_by(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type_num
        ).first()
        
        if not collection:
            return False
        
        try:
            db.session.delete(collection)
            
            # 更新目标对象的收藏数
            Collection._update_target_collection_count(target_id, target_type, -1)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def _update_target_collection_count(target_id, target_type, increment):
        """更新目标对象的收藏数"""
        if target_type == 'attraction':
            from models.attraction import Attraction
            target = Attraction.query.get(target_id)
            if target:
                target.collection_count += increment
        elif target_type == 'note':
            from models.travel_note import TravelNote
            target = TravelNote.query.get(target_id)
            if target:
                target.collection_count += increment
        elif target_type == 'guide':
            from models.travel_guide import TravelGuide
            target = TravelGuide.query.get(target_id)
            if target:
                target.collection_count += increment

    def __repr__(self):
        return f'<Collection {self.id}>'
        
    @staticmethod
    def toggle_collection(user_id, target_id, target_type):
        """
        切换收藏状态
        :param user_id: 用户ID
        :param target_id: 目标ID
        :param target_type: 目标类型
        :return: bool 当前收藏状态
        """
        is_collected = Collection.is_collected(user_id, target_id, target_type)
        
        if is_collected:
            # 已收藏，取消收藏
            Collection.remove_collection(user_id, target_id, target_type)
            return False
        else:
            # 未收藏，添加收藏
            Collection.add_collection(user_id, target_id, target_type)
            return True
    
    @staticmethod
    def count_collections(target_id, target_type):
        """
        统计收藏数量
        :param target_id: 目标ID
        :param target_type: 目标类型
        :return: int 收藏数量
        """
        return Collection.query.filter_by(
            target_id=target_id,
            target_type=target_type
        ).count()
        
    @staticmethod
    def get_user_collections(user_id, target_type=None, limit=10, offset=0):
        """
        获取用户收藏列表
        :param user_id: 用户ID
        :param target_type: 目标类型
        :param limit: 限制数量
        :param offset: 偏移量
        :return: 收藏列表
        """
        query = Collection.query.filter_by(user_id=user_id)
        
        if target_type:
            query = query.filter_by(target_type=target_type)
        
        return query.order_by(db.desc(Collection.created_at)).limit(limit).offset(offset).all()
    
    @staticmethod
    def count_user_collections(user_id, target_type=None):
        """
        统计用户收藏数量
        :param user_id: 用户ID
        :param target_type: 目标类型
        :return: 收藏数量
        """
        query = Collection.query.filter_by(user_id=user_id)
        
        if target_type:
            query = query.filter_by(target_type=target_type)
        
        return query.count() 