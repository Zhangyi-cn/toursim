"""
数据库模型
"""

from extensions import db

# 导入所有模型
from .attraction import Attraction, AttractionImage
from .category import Category
from .region import Region
from .banner import Banner
from .user import User
from .travel_guide import TravelGuide, TravelGuideCategory
from .ticket import Ticket
from .travel_season import TravelSeason
from .comment import Comment
from .collection import Collection
from .like import Like
from .travel_note import TravelNote, TravelNoteImage, NoteAttraction
from .order import Order, OrderItem

# 导出所有模型
__all__ = [
    'Attraction',
    'Category',
    'AttractionImage',
    'Region',
    'Banner',
    'User',
    'TravelGuide',
    'TravelGuideCategory',
    'Ticket',
    'TravelSeason',
    'Comment',
    'Collection',
    'Like',
    'TravelNote',
    'TravelNoteImage',
    'NoteAttraction',
    'Order',
    'OrderItem'
] 