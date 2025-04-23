from flask import request, jsonify, g, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

from models.banner import Banner
from extensions import db, cache
from utils.response import success_response, error_response
from utils.auth import admin_required
from utils.file import allowed_file, save_image

class SystemAdminController:
    """系统管理控制器"""
    
    @staticmethod
    @admin_required
    def get_banners():
        """获取轮播图列表"""
        try:
            banners = Banner.query.order_by(Banner.sort_order.asc()).all()
            items = [banner.to_dict() for banner in banners]
            
            return success_response("获取轮播图列表成功", items)
            
        except Exception as e:
            return error_response(f"获取轮播图列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def create_banner():
        """创建轮播图"""
        try:
            data = request.get_json()
            
            image_url = data.get('image_url', '')
            title = data.get('title', '')
            description = data.get('description', '')
            link = data.get('link', '')
            target_type = data.get('target_type', '')
            target_id = data.get('target_id')
            sort_order = data.get('sort_order', 0)
            status = data.get('status', 1)
            
            if not image_url:
                return error_response("图片URL不能为空", 400)
                
            banner = Banner(
                image_url=image_url,
                title=title,
                description=description,
                link=link,
                target_type=target_type,
                target_id=target_id,
                sort_order=sort_order,
                status=status
            )
            
            db.session.add(banner)
            db.session.commit()
            
            # 清除缓存
            cache.delete('home_banners')
            
            return success_response("创建轮播图成功", banner.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建轮播图失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def update_banner(banner_id):
        """更新轮播图"""
        try:
            banner = Banner.query.get(banner_id)
            
            if not banner:
                return error_response("轮播图不存在", 404)
                
            data = request.get_json()
            
            # 可更新的字段
            updatable_fields = [
                'image_url', 'title', 'description', 'link', 
                'target_type', 'target_id', 'sort_order', 'status'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(banner, field, data[field])
            
            banner.updated_at = datetime.now()
            db.session.commit()
            
            # 清除缓存
            cache.delete('home_banners')
            
            return success_response("更新轮播图成功", banner.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新轮播图失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def delete_banner(banner_id):
        """删除轮播图"""
        try:
            banner = Banner.query.get(banner_id)
            
            if not banner:
                return error_response("轮播图不存在", 404)
                
            db.session.delete(banner)
            db.session.commit()
            
            # 清除缓存
            cache.delete('home_banners')
            
            return success_response("删除轮播图成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除轮播图失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def upload_banner():
        """上传轮播图"""
        try:
            if 'file' not in request.files:
                return error_response("未上传文件", 400)
                
            file = request.files['file']
            
            if file.filename == '':
                return error_response("未选择文件", 400)
                
            if not allowed_file(file.filename, ['jpg', 'jpeg', 'png', 'gif']):
                return error_response("不支持的文件类型", 400)
                
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{uuid.uuid4().hex}.{ext}"
            
            # 保存文件 - 路径修改为 images/banner
            upload_folder = os.path.join('static', 'images', 'banner')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            filepath = os.path.join(upload_folder, new_filename)
            file.save(filepath)
            
            # 返回URL - 只返回 banner/filename 路径
            url = f"/banner/{new_filename}"
            
            return success_response("上传成功", {
                'url': url,
                'filename': new_filename
            })
            
        except Exception as e:
            return error_response(f"上传失败: {str(e)}", 500)

    @staticmethod
    @admin_required
    def upload_banner_new():
        """上传轮播图"""
        try:
            if 'file' not in request.files:
                return error_response("未上传文件", 400)
                
            file = request.files['file']
            
            if file.filename == '':
                return error_response("未选择文件", 400)
                
            if not allowed_file(file.filename, ['jpg', 'jpeg', 'png', 'gif']):
                return error_response("不支持的文件类型", 400)
                
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{uuid.uuid4().hex}.{ext}"
            
            # 保存文件
            upload_folder = os.path.join('static', 'images', 'banner')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            filepath = os.path.join(upload_folder, new_filename)
            file.save(filepath)
            
            # 返回URL
            url = f"/banner/{new_filename}"
            
            return success_response("上传成功", {
                'url': url,
                'filename': new_filename
            })
            
        except Exception as e:
            return error_response(f"上传失败: {str(e)}", 500) 