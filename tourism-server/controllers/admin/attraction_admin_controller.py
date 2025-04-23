from flask import request, jsonify, g, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

from models.attraction import Attraction, AttractionImage
from models.category import Category
from models.tag import Tag, ContentTag
from models.region import Region
from extensions import db
from utils.response import success_response, error_response
from utils.auth import admin_required
from utils.file import allowed_file, save_image
from utils.validator import validate_required, validate_params

class AttractionAdminController:
    """景点管理控制器"""
    
    @staticmethod
    @admin_required
    def get_attractions():
        """获取景点列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            keyword = request.args.get('keyword', '')
            category_id = request.args.get('category_id', type=int)
            
            # 构建查询
            query = Attraction.query
            
            # 应用筛选
            if keyword:
                query = query.filter(Attraction.name.ilike(f'%{keyword}%'))
            
            if category_id:
                query = query.filter(Attraction.category_id == category_id)
                
            # 排序
            query = query.order_by(Attraction.created_at.desc())
            
            # 分页
            pagination = query.paginate(page=page, per_page=per_page)
            items = [item.to_dict() for item in pagination.items]
            
            return success_response("获取景点列表成功", {
                'items': items,
                'pagination': {
                    'total': pagination.total,
                    'page': page,
                    'per_page': per_page,
                    'pages': pagination.pages
                }
            })
        
        except Exception as e:
            return error_response(f"获取景点列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def create_attraction():
        """创建景点"""
        try:
            data = request.get_json()
            
            # 验证必填字段
            required_fields = ['name', 'category_id', 'description', 'address']
            if not validate_required(data, required_fields):
                return error_response("缺少必填字段", 400)
                
            # 检查分类是否存在
            category = Category.query.get(data.get('category_id'))
            if not category or category.type != 1:  # 1表示景点分类
                return error_response("分类不存在或不是景点分类", 400)
                
            # 创建景点
            attraction = Attraction(
                name=data.get('name'),
                description=data.get('description'),
                address=data.get('address'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                category_id=data.get('category_id'),
                open_time=data.get('open_time'),
                ticket_info=data.get('ticket_info', ''),
                traffic_info=data.get('traffic_info', ''),
                cover_image=data.get('cover_image', ''),
                tips=data.get('tips', ''),
                status=data.get('status', 1)
            )
            
            db.session.add(attraction)
            db.session.flush()  # 获取ID
            
            # 添加图片
            images = data.get('images', [])
            for img_data in images:
                image = AttractionImage(
                    attraction_id=attraction.id,
                    url=img_data.get('url', ''),
                    title=img_data.get('title', ''),
                    description=img_data.get('description', ''),
                    sort_order=img_data.get('sort_order', 0)
                )
                db.session.add(image)
            
            # 添加标签
            tags = data.get('tags', [])
            for tag_id in tags:
                tag = Tag.query.get(tag_id)
                if tag:
                    content_tag = ContentTag(
                        tag_id=tag_id,
                        content_type='attraction',
                        content_id=attraction.id
                    )
                    db.session.add(content_tag)
            
            db.session.commit()
            
            return success_response("创建景点成功", attraction.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建景点失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def get_attraction(attraction_id):
        """获取景点详情"""
        try:
            attraction = Attraction.query.get(attraction_id)
            
            if not attraction:
                return error_response("景点不存在", 404)
                
            # 获取标签
            tags = ContentTag.query.filter_by(
                content_type='attraction', 
                content_id=attraction_id
            ).all()
            
            tag_ids = [tag.tag_id for tag in tags]
            
            # 构建详细数据
            data = attraction.to_dict()
            data['tags'] = tag_ids
            
            return success_response("获取景点详情成功", data)
            
        except Exception as e:
            return error_response(f"获取景点详情失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def update_attraction(attraction_id):
        """更新景点信息"""
        try:
            attraction = Attraction.query.get(attraction_id)
            
            if not attraction:
                return error_response("景点不存在", 404)
                
            data = request.get_json()
            
            # 可更新的字段
            allowed_fields = [
                'name', 'description', 'address', 'latitude', 'longitude',
                'category_id', 'open_time', 'ticket_info', 'traffic_info',
                'cover_image', 'tips', 'status'
            ]
            
            # 更新景点基本信息
            for field in allowed_fields:
                if field in data:
                    setattr(attraction, field, data[field])
            
            # 更新图片
            if 'images' in data:
                # 删除旧图片
                AttractionImage.query.filter_by(attraction_id=attraction_id).delete()
                
                # 添加新图片
                for img_data in data['images']:
                    image = AttractionImage(
                        attraction_id=attraction.id,
                        url=img_data.get('url', ''),
                        title=img_data.get('title', ''),
                        description=img_data.get('description', ''),
                        sort_order=img_data.get('sort_order', 0)
                    )
                    db.session.add(image)
            
            # 更新标签
            if 'tags' in data:
                # 删除旧标签
                ContentTag.query.filter_by(
                    content_type='attraction', 
                    content_id=attraction_id
                ).delete()
                
                # 添加新标签
                for tag_id in data['tags']:
                    tag = Tag.query.get(tag_id)
                    if tag:
                        content_tag = ContentTag(
                            tag_id=tag_id,
                            content_type='attraction',
                            content_id=attraction.id
                        )
                        db.session.add(content_tag)
            
            db.session.commit()
            
            return success_response("更新景点成功", attraction.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新景点失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def delete_attraction(attraction_id):
        """删除景点"""
        try:
            attraction = Attraction.query.get(attraction_id)
            
            if not attraction:
                return error_response("景点不存在", 404)
                
            # 删除图片
            AttractionImage.query.filter_by(attraction_id=attraction_id).delete()
            
            # 删除标签关联
            ContentTag.query.filter_by(
                content_type='attraction', 
                content_id=attraction_id
            ).delete()
            
            # 删除景点
            db.session.delete(attraction)
            db.session.commit()
            
            return success_response("删除景点成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除景点失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def upload_image():
        """上传景点图片"""
        try:
            if 'file' not in request.files:
                return error_response("未上传文件", 400)
                
            file = request.files['file']
            
            if file.filename == '':
                return error_response("文件名为空", 400)
                
            if not allowed_file(file.filename, ['jpg', 'jpeg', 'png', 'gif']):
                return error_response("不支持的文件类型", 400)
                
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{uuid.uuid4().hex}.{ext}"
            
            # 保存到上传目录
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attractions')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            filepath = os.path.join(upload_folder, new_filename)
            file.save(filepath)
            
            # 返回访问URL
            url = f"/static/uploads/attractions/{new_filename}"
            
            return success_response("上传图片成功", {
                'url': url,
                'filename': new_filename
            })
            
        except Exception as e:
            return error_response(f"上传图片失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def get_categories():
        """获取景点分类列表"""
        try:
            categories = Category.query.filter_by(type=1).order_by(Category.sort_order).all()
            return success_response("获取分类列表成功", [category.to_dict() for category in categories])
        except Exception as e:
            return error_response(f"获取分类列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def create_category():
        """创建景点分类"""
        try:
            data = request.get_json()
            
            # 验证必填字段
            if not data.get('name'):
                return error_response("分类名称不能为空", 400)
            
            # 创建分类
            category = Category(
                name=data.get('name'),
                description=data.get('description', ''),
                type=1,  # 1表示景点分类
                sort_order=data.get('sort_order', 0)
            )
            
            db.session.add(category)
            db.session.commit()
            
            return success_response("创建分类成功", category.to_dict())
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建分类失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def update_category(category_id):
        """更新景点分类"""
        try:
            category = Category.query.get(category_id)
            
            if not category or category.type != 1:  # 1表示景点分类
                return error_response("分类不存在或不是景点分类", 404)
            
            data = request.get_json()
            
            # 更新字段
            if data.get('name'):
                category.name = data.get('name')
            
            if 'description' in data:
                category.description = data.get('description')
            
            if 'sort_order' in data:
                category.sort_order = data.get('sort_order')
            
            category.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新分类成功", category.to_dict())
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新分类失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required
    def delete_category(category_id):
        """删除景点分类"""
        try:
            category = Category.query.get(category_id)
            
            if not category or category.type != 1:  # 1表示景点分类
                return error_response("分类不存在或不是景点分类", 404)
            
            # 检查是否有关联的景点
            if category.attractions and len(category.attractions) > 0:
                return error_response("该分类下有关联的景点，无法删除", 400)
            
            db.session.delete(category)
            db.session.commit()
            
            return success_response("删除分类成功")
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除分类失败: {str(e)}", 500) 