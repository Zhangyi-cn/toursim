from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from flask_jwt_extended import jwt_required
import re

from models.attraction import Attraction
from models.travel_guide import TravelGuide
from models.travel_note import TravelNote
from models.user import User
from models.tag import Tag, ContentTag
from utils.response import success_response, error_response, pagination_response
from utils.validator import get_page_params

# 创建蓝图
search_bp = Blueprint('search', __name__, url_prefix='/search')


class SearchController:
    """搜索控制器"""
    
    @staticmethod
    @search_bp.route('', methods=['GET'])
    def search():
        """
        综合搜索
        ---
        tags:
          - 搜索
        parameters:
          - name: q
            in: query
            required: true
            type: string
            description: 搜索关键词
          - name: type
            in: query
            type: string
            enum: [attraction, guide, note, user, all]
            default: all
            description: 搜索类型
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        keyword = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        page, per_page = get_page_params()
        
        if not keyword:
            return jsonify(error_response("搜索关键词不能为空")), 400
        
        if search_type == 'all':
            # 综合搜索
            results = SearchController._search_all(keyword, page, per_page)
            return jsonify(success_response("搜索成功", results))
        elif search_type == 'attraction':
            # 搜索景点
            results = SearchController._search_attractions(keyword, page, per_page)
            return jsonify(results)
        elif search_type == 'guide':
            # 搜索攻略
            results = SearchController._search_guides(keyword, page, per_page)
            return jsonify(results)
        elif search_type == 'note':
            # 搜索游记
            results = SearchController._search_notes(keyword, page, per_page)
            return jsonify(results)
        elif search_type == 'user':
            # 搜索用户
            results = SearchController._search_users(keyword, page, per_page)
            return jsonify(results)
        else:
            return jsonify(error_response("不支持的搜索类型")), 400
    
    @staticmethod
    def _search_all(keyword, page, per_page):
        """综合搜索"""
        # 每种类型的结果数量
        type_limit = 3
        
        # 搜索景点
        attractions = SearchController._search_attractions_query(keyword).limit(type_limit).all()
        attraction_results = [item.to_dict() for item in attractions]
        
        # 搜索攻略
        guides = SearchController._search_guides_query(keyword).limit(type_limit).all()
        guide_results = [item.to_dict(with_content=False) for item in guides]
        
        # 搜索游记
        notes = SearchController._search_notes_query(keyword).limit(type_limit).all()
        note_results = [item.to_dict(with_content=False) for item in notes]
        
        # 搜索用户
        users = SearchController._search_users_query(keyword).limit(type_limit).all()
        user_results = [item.to_dict(with_detail=False) for item in users]
        
        # 组合结果
        return {
            'attractions': attraction_results,
            'guides': guide_results,
            'notes': note_results,
            'users': user_results
        }
    
    @staticmethod
    def _search_attractions(keyword, page, per_page):
        """搜索景点"""
        query = SearchController._search_attractions_query(keyword)
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = [item.to_dict() for item in paginate.items]
        
        return pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="搜索景点成功"
        )
    
    @staticmethod
    def _search_attractions_query(keyword):
        """构建景点搜索查询"""
        # 根据景点名称、简介、地址搜索
        query = Attraction.query.filter(
            and_(
                Attraction.status == 1,  # 只搜索正常状态的景点
                or_(
                    Attraction.name.like(f'%{keyword}%'),
                    Attraction.description.like(f'%{keyword}%'),
                    Attraction.address.like(f'%{keyword}%')
                )
            )
        )
        
        # 通过标签间接关联搜索
        tag_results = Tag.query.filter(Tag.name.like(f'%{keyword}%')).all()
        if tag_results:
            tag_ids = [tag.id for tag in tag_results]
            # 获取带有这些标签的景点IDs
            attraction_ids = ContentTag.query.filter(
                ContentTag.tag_id.in_(tag_ids),
                ContentTag.content_type == 'attraction'
            ).with_entities(ContentTag.content_id).all()
            
            attraction_ids = [item[0] for item in attraction_ids]
            
            # 如果找到了通过标签关联的景点，将它们添加到查询中
            if attraction_ids:
                query = query.union(
                    Attraction.query.filter(
                        and_(
                            Attraction.status == 1,  # 只搜索正常状态的景点
                            Attraction.id.in_(attraction_ids)
                        )
                    )
                )
        
        # 按热度排序
        return query.order_by(Attraction.view_count.desc())
    
    @staticmethod
    def _search_guides(keyword, page, per_page):
        """搜索攻略"""
        query = SearchController._search_guides_query(keyword)
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = [item.to_dict(with_content=False) for item in paginate.items]
        
        return pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="搜索攻略成功"
        )
    
    @staticmethod
    def _search_guides_query(keyword):
        """构建攻略搜索查询"""
        # 根据标题、内容搜索
        query = TravelGuide.query.filter(
            and_(
                TravelGuide.status == 1,  # 只搜索已发布的攻略
                or_(
                    TravelGuide.title.like(f'%{keyword}%'),
                    TravelGuide.content.like(f'%{keyword}%')
                )
            )
        )
        
        # 通过标签间接关联搜索
        tag_results = Tag.query.filter(Tag.name.like(f'%{keyword}%')).all()
        if tag_results:
            tag_ids = [tag.id for tag in tag_results]
            # 获取带有这些标签的攻略IDs
            guide_ids = ContentTag.query.filter(
                ContentTag.tag_id.in_(tag_ids),
                ContentTag.content_type == 'guide'
            ).with_entities(ContentTag.content_id).all()
            
            guide_ids = [item[0] for item in guide_ids]
            if guide_ids:
                # 合并基于标签的搜索结果
                query = query.union(
                    TravelGuide.query.filter(
                        and_(
                            TravelGuide.id.in_(guide_ids),
                            TravelGuide.status == 1
                        )
                    )
                )
        
        # 按热度排序
        return query.order_by(TravelGuide.views.desc())
    
    @staticmethod
    def _search_notes(keyword, page, per_page):
        """搜索游记"""
        query = SearchController._search_notes_query(keyword)
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = [item.to_dict(with_content=False) for item in paginate.items]
        
        return pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="搜索游记成功"
        )
    
    @staticmethod
    def _search_notes_query(keyword):
        """构建游记搜索查询"""
        # 根据标题、内容搜索
        query = TravelNote.query.filter(
            and_(
                TravelNote.status == 1,  # 只搜索已发布的游记
                or_(
                    TravelNote.title.like(f'%{keyword}%'),
                    TravelNote.content.like(f'%{keyword}%')
                )
            )
        )
        
        # 通过标签间接关联搜索
        tag_results = Tag.query.filter(Tag.name.like(f'%{keyword}%')).all()
        if tag_results:
            tag_ids = [tag.id for tag in tag_results]
            # 获取带有这些标签的游记IDs
            note_ids = ContentTag.query.filter(
                ContentTag.tag_id.in_(tag_ids),
                ContentTag.content_type == 'note'
            ).with_entities(ContentTag.content_id).all()
            
            note_ids = [item[0] for item in note_ids]
            if note_ids:
                # 合并基于标签的搜索结果
                query = query.union(
                    TravelNote.query.filter(
                        and_(
                            TravelNote.id.in_(note_ids),
                            TravelNote.status == 1
                        )
                    )
                )
        
        # 按热度排序
        return query.order_by(TravelNote.views.desc())
    
    @staticmethod
    def _search_users(keyword, page, per_page):
        """搜索用户"""
        query = SearchController._search_users_query(keyword)
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = [item.to_dict(with_detail=False) for item in paginate.items]
        
        return pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="搜索用户成功"
        )
    
    @staticmethod
    def _search_users_query(keyword):
        """构建用户搜索查询"""
        # 根据用户名、昵称、简介搜索
        return User.query.filter(
            and_(
                User.status == 1,  # 只搜索正常状态的用户
                or_(
                    User.username.like(f'%{keyword}%'),
                    User.nickname.like(f'%{keyword}%'),
                    User.bio.like(f'%{keyword}%')
                )
            )
        ).order_by(User.fans_count.desc())  # 按粉丝数排序 