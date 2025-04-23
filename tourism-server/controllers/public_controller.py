from flask import request, jsonify
from utils.response import success_response, error_response
from models.banner import Banner

def get_banners():
    """获取轮播图列表"""
    try:
        # 获取启用的轮播图，按排序字段排序
        banners = Banner.query.filter_by(is_active=True).order_by(Banner.sort_order.desc()).all()
        return success_response("获取轮播图成功", {"items": [banner.to_dict() for banner in banners]})
    except Exception as e:
        return error_response(f"获取轮播图失败: {str(e)}", 500) 