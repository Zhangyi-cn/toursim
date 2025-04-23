from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc, and_

from models.tag import Tag, ContentTag
from extensions import db, cache
from utils.response import success_response, error_response, pagination_response
from utils.validator import get_page_params

tag_bp = Blueprint('tag', __name__)


class TagController:
    """标签控制器"""
    
    @staticmethod
    @tag_bp.route('', methods=['GET'])
    def get_tags():
        """
        获取标签列表
        ---
        tags:
          - 标签管理
        parameters:
          - name: type
            in: query
            type: string
            description: 标签类型
          - name: keyword
            in: query
            type: string
            description: 搜索关键词
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        # 获取查询参数
        tag_type = request.args.get('type', '')
        keyword = request.args.get('keyword', '')
        page, per_page = get_page_params()
        
        # 构建查询
        query = Tag.query.filter(Tag.status == 1)
        
        # 应用过滤条件
        if tag_type:
            query = query.filter(Tag.type == tag_type)
        
        if keyword:
            query = query.filter(Tag.name.like(f'%{keyword}%'))
        
        # 应用排序
        query = query.order_by(Tag.sort_order, desc(Tag.id))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 转换为字典列表
        items = [tag.to_dict() for tag in paginate.items]
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="获取标签列表成功"
        ))
    
    @staticmethod
    @tag_bp.route('/hot', methods=['GET'])
    def get_hot_tags():
        """
        获取热门标签
        ---
        tags:
          - 标签管理
        parameters:
          - name: type
            in: query
            type: string
            description: 内容类型(attraction,guide,note)
          - name: limit
            in: query
            type: integer
            default: 10
            description: 返回数量
        """
        # 获取查询参数
        content_type = request.args.get('type', '')
        limit = request.args.get('limit', 10, type=int)
        
        # 从缓存获取
        cache_key = f'hot_tags_{content_type}_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return jsonify(success_response("获取热门标签成功", cached_data))
        
        # 构建查询
        query = db.session.query(
            Tag.id,
            Tag.name,
            Tag.icon,
            func.count(ContentTag.id).label('count')
        ).join(
            ContentTag,
            Tag.id == ContentTag.tag_id
        ).filter(
            Tag.status == 1
        )
        
        # 按内容类型过滤
        if content_type:
            query = query.filter(ContentTag.content_type == content_type)
        
        # 分组、排序和限制
        query = query.group_by(
            Tag.id
        ).order_by(
            desc('count'),
            Tag.sort_order
        ).limit(limit)
        
        # 执行查询
        tags = query.all()
        
        # 转换为字典列表
        result = [
            {
                'id': tag.id,
                'name': tag.name,
                'icon': tag.icon,
                'count': tag.count
            }
            for tag in tags
        ]
        
        # 设置缓存，有效期1小时
        cache.set(cache_key, result, timeout=3600)
        
        return jsonify(success_response("获取热门标签成功", result))
    
    @staticmethod
    @tag_bp.route('/<int:tag_id>', methods=['GET'])
    def get_tag(tag_id):
        """
        获取标签详情
        ---
        tags:
          - 标签管理
        parameters:
          - name: tag_id
            in: path
            required: true
            type: integer
            description: 标签ID
        """
        # 查询标签
        tag = Tag.query.get(tag_id)
        if not tag:
            return jsonify(error_response("标签不存在")), 404
        
        # 返回标签信息
        return jsonify(success_response("获取标签详情成功", tag.to_dict()))
    
    @staticmethod
    @tag_bp.route('/<int:tag_id>/contents', methods=['GET'])
    def get_tag_contents(tag_id):
        """
        获取标签下的内容列表
        ---
        tags:
          - 标签管理
        parameters:
          - name: tag_id
            in: path
            required: true
            type: integer
            description: 标签ID
          - name: type
            in: query
            type: string
            description: 内容类型(attraction,guide,note)
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        # 查询标签
        tag = Tag.query.get(tag_id)
        if not tag:
            return jsonify(error_response("标签不存在")), 404
        
        # 获取查询参数
        content_type = request.args.get('type', '')
        page, per_page = get_page_params()
        
        # 构建查询
        query = ContentTag.query.filter(ContentTag.tag_id == tag_id)
        
        # 按内容类型过滤
        if content_type:
            query = query.filter(ContentTag.content_type == content_type)
        
        # 按创建时间倒序排序
        query = query.order_by(desc(ContentTag.created_at))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备结果数据
        items = []
        for content_tag in paginate.items:
            # 获取内容详情
            content_data = {
                'tag_id': content_tag.tag_id,
                'content_id': content_tag.content_id,
                'content_type': content_tag.content_type,
                'created_at': content_tag.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 根据内容类型获取详细信息
            if content_tag.content_type == 'attraction':
                from models.attraction import Attraction
                attraction = Attraction.query.get(content_tag.content_id)
                if attraction:
                    content_data.update({
                        'title': attraction.name,
                        'cover_image': attraction.cover_image,
                        'details': attraction.to_dict(with_details=False)
                    })
            
            elif content_tag.content_type == 'guide':
                from models.travel_guide import TravelGuide
                guide = TravelGuide.query.get(content_tag.content_id)
                if guide:
                    content_data.update({
                        'title': guide.title,
                        'cover_image': guide.cover_image,
                        'details': guide.to_dict(with_content=False)
                    })
            
            elif content_tag.content_type == 'note':
                from models.travel_note import TravelNote
                note = TravelNote.query.get(content_tag.content_id)
                if note:
                    content_data.update({
                        'title': note.title,
                        'cover_image': note.cover_image,
                        'details': note.to_dict(with_content=False)
                    })
            
            items.append(content_data)
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="获取标签内容列表成功"
        )) 