from flask import Blueprint, jsonify
from extensions import db, cache
from models.banner import Banner
from models.region import Region
from utils.response import success_response, error_response

# 定义系统蓝图
system_bp = Blueprint('system', __name__)


class SystemController:
    """系统控制器"""

    @staticmethod
    @system_bp.route('/banners', methods=['GET'])
    def get_banners():
        """获取轮播图"""
        try:
            # 查询所有启用的轮播图
            banners = Banner.query.filter_by(is_active=True).order_by(Banner.sort_order.desc()).all()
            banner_list = [banner.to_dict() for banner in banners]
            
            return jsonify(success_response("获取轮播图成功", {"items": banner_list}))
        except Exception as e:
            return jsonify(error_response(f"获取轮播图失败: {str(e)}")), 500

    @staticmethod
    @system_bp.route('/regions', methods=['GET'])
    def get_regions():
        """获取地区列表"""
        try:
            # 查询所有地区
            regions = Region.query.all()
            
            # 构建树形结构
            result = []
            # 先找出所有省级地区
            provinces = [region for region in regions if region.parent_id is None]
            
            for province in provinces:
                province_data = province.to_dict()
                # 查找该省下的所有城市
                cities = [region for region in regions if region.parent_id == province.id]
                
                province_data['children'] = []
                for city in cities:
                    city_data = city.to_dict()
                    # 查找该市下的所有区县
                    counties = [region for region in regions if region.parent_id == city.id]
                    
                    city_data['children'] = [county.to_dict() for county in counties]
                    province_data['children'].append(city_data)
                
                result.append(province_data)
            
            return jsonify(success_response("获取地区列表成功", result))
        except Exception as e:
            return jsonify(error_response(f"获取地区列表失败: {str(e)}")), 500 