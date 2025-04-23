from flask import request
from models.user_behavior import UserBehavior
from app import db

def record_activity(user_id, action_type, target_type, target_id, duration=0):
    """
    记录用户行为
    :param user_id: 用户ID
    :param action_type: 行为类型(view:1, search:2, click:3, stay:4, share:5, like:3, collect:3)
    :param target_type: 目标类型(attraction/guide/note)
    :param target_id: 目标ID
    :param duration: 停留时长(秒)
    """
    try:
        # 将action_type转换为对应的数字类型
        action_type_map = {
            'view': 1,
            'search': 2,
            'click': 3,
            'stay': 4,
            'share': 5,
            'like': 3,    # 点赞行为也算作点击行为
            'collect': 3  # 收藏行为也算作点击行为
        }
        
        behavior_type = action_type_map.get(action_type, 3)  # 默认为点击行为
        
        # 创建用户行为记录
        behavior = UserBehavior(
            user_id=user_id,
            behavior_type=behavior_type,
            target_type=target_type,
            target_id=target_id,
            duration=duration,
            ip=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.add(behavior)
        db.session.commit()
        
        return True
    except Exception as e:
        db.session.rollback()
        print(f"记录用户行为失败: {str(e)}")
        return False 