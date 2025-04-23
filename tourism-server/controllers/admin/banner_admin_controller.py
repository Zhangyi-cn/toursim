from flask import request
from extensions import db
from models.banner import Banner
from utils.response import success_response, error_response
from utils.file import save_image
from datetime import datetime

class BannerAdminController:
    """轮播图管理控制器"""
    
    @staticmethod
    def get_banners():
        """获取轮播图列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            
            # 查询轮播图列表
            query = Banner.query.order_by(Banner.sort_order.desc(), Banner.id.desc())
            
            # 分页
            pagination = query.paginate(page=page, per_page=per_page)
            items = [item.to_dict() for item in pagination.items]
            
            return success_response("获取轮播图列表成功", {
                'items': items,
                'pagination': {
                    'total': pagination.total,
                    'page': page,
                    'per_page': per_page,
                    'pages': pagination.pages
                }
            })
            
        except Exception as e:
            return error_response(f"获取轮播图列表失败: {str(e)}", 500)
    
    @staticmethod
    def create_banner():
        """创建轮播图"""
        try:
            data = request.get_json()
            
            if not data.get('image_url'):
                return error_response("轮播图图片路径不能为空", 400)
            
            if not data.get('title'):
                return error_response("轮播图标题不能为空", 400)
            
            # 创建轮播图
            banner = Banner(
                title=data.get('title'),
                image_url=data.get('image_url'),
                link_url=data.get('link_url'),
                description=data.get('description'),
                sort_order=int(data.get('sort_order', 0)),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(banner)
            db.session.commit()
            
            return success_response("创建轮播图成功", banner.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建轮播图失败: {str(e)}", 500)
    
    @staticmethod
    def update_banner(banner_id):
        """更新轮播图"""
        try:
            banner = Banner.query.get(banner_id)
            if not banner:
                return error_response("轮播图不存在", 404)
            
            data = request.get_json()
            
            # 更新字段
            if 'title' in data:
                banner.title = data['title']
            if 'image_url' in data:
                banner.image_url = data['image_url']
            if 'link_url' in data:
                banner.link_url = data['link_url']
            if 'description' in data:
                banner.description = data['description']
            if 'sort_order' in data:
                banner.sort_order = int(data['sort_order'])
            if 'is_active' in data:
                banner.is_active = data['is_active']
            
            banner.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新轮播图成功", banner.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新轮播图失败: {str(e)}", 500)
    
    @staticmethod
    def delete_banner(banner_id):
        """删除轮播图"""
        try:
            banner = Banner.query.get(banner_id)
            if not banner:
                return error_response("轮播图不存在", 404)
            
            db.session.delete(banner)
            db.session.commit()
            
            return success_response("删除轮播图成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除轮播图失败: {str(e)}", 500)
    
    @staticmethod
    def update_banner_status(banner_id):
        """更新轮播图状态"""
        try:
            banner = Banner.query.get(banner_id)
            if not banner:
                return error_response("轮播图不存在", 404)
            
            data = request.get_json()
            is_active = data.get('is_active')
            
            if is_active is None:
                return error_response("状态参数不能为空", 400)
            
            banner.is_active = bool(is_active)
            banner.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新轮播图状态成功", banner.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新轮播图状态失败: {str(e)}", 500) 