from datetime import datetime
from extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String


class TravelSeason(db.Model):
    """旅游季节模型"""
    __tablename__ = 'travel_seasons'

    id = Column(Integer, primary_key=True, comment='ID')
    attraction_id = Column(Integer, ForeignKey('attractions.id'), nullable=False, comment='景点ID')
    season = Column(String(20), nullable=False, comment='季节(spring,summer,autumn,winter)')
    description = Column(Text, comment='季节描述')
    temperature = Column(String(50), comment='温度范围')
    rainfall = Column(String(50), comment='降雨情况')
    tips = Column(Text, comment='游玩建议')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 添加与景点的关系
    attraction = relationship('Attraction', back_populates='seasons')

    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_comment': '旅游季节表 - 记录景点的最佳游览季节信息'
    }

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'attraction_id': self.attraction_id,
            'season': self.season,
            'season_name': self.get_season_name(),
            'description': self.description,
            'temperature': self.temperature,
            'rainfall': self.rainfall,
            'tips': self.tips,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_season_name(self):
        """获取季节名称"""
        season_names = {1: "春季", 2: "夏季", 3: "秋季", 4: "冬季"}
        return season_names.get(self.season, "未知季节")

    @staticmethod
    def get_season_name_by_id(season_id):
        """根据季节ID获取季节名称"""
        season_names = {1: "春季", 2: "夏季", 3: "秋季", 4: "冬季"}
        return season_names.get(season_id, "未知季节")

    def __repr__(self):
        return f'<TravelSeason {self.id}>' 