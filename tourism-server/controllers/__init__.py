# 控制器模块初始化
# 此模块包含所有的控制器类，负责处理请求并返回响应 

from .auth_controller import auth_bp
from .user_controller import user_bp
from .admin.admin_controller import admin_bp
from .attraction_controller import attraction_bp
from .travel_guide_controller import travel_guide_bp
from .travel_note_controller import note_bp
from .upload_controller import upload_bp
from .comment_controller import comment_bp
from .like_controller import like_bp
from .collection_controller import collection_bp
from .notification_controller import notification_bp
from .order_controller import order_bp
from .ticket_controller import ticket_bp
from .guide_controller import guide_bp
from .recommendation_controller import recommendation_bp
from .category_controller import category_bp

# 注册所有蓝图
blueprints = [
    auth_bp,
    user_bp,
    admin_bp,
    attraction_bp,
    travel_guide_bp,
    note_bp,
    upload_bp,
    comment_bp,
    like_bp,
    collection_bp,
    notification_bp,
    order_bp,
    ticket_bp,
    guide_bp,
    recommendation_bp,
    category_bp
]

__all__ = [
    'auth_bp',
    'user_bp',
    'admin_bp',
    'attraction_bp',
    'guide_bp',
    'note_bp',
    'comment_bp',
    'upload_bp',
    'category_bp'
] 