from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required as flask_jwt_required
from datetime import datetime
from collections import namedtuple
from sqlalchemy import desc

from models.travel_season import TravelSeason
from models.attraction import Attraction
from models.comment import Comment
from extensions import db
from utils.response import success_response, error_response, pagination_response
from utils.auth import admin_required, get_current_user, login_required
from utils.pagination import paginate_query
from utils.validator import validate_required, get_page_params

# 创建蓝图
season_bp = Blueprint('season', __name__, url_prefix='')


class TravelSeasonController:
    """旅游季节控制器"""
    
    @staticmethod
    @season_bp.route('/attractions/<int:attraction_id>', methods=['GET'])
    def get_seasons_by_attraction(attraction_id):
        """
        获取景点的季节信息
        ---
        tags:
          - 旅游季节
        parameters:
          - name: attraction_id
            in: path
            required: true
            type: integer
            description: 景点ID
        """
        # 查询景点
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify(error_response("景点不存在")), 404
        
        # 查询该景点的所有季节信息
        seasons = TravelSeason.query.filter_by(attraction_id=attraction_id).all()
        
        # 准备响应数据
        items = []
        for season in seasons:
            items.append(season.to_dict())
        
        return jsonify(success_response("获取景点季节信息成功", {
            "attraction": attraction.name,
            "seasons": items
        }))
    
    @staticmethod
    @season_bp.route('/attractions/<int:attraction_id>', methods=['POST'])
    @login_required
    def add_season(attraction_id):
        """
        添加景点季节信息
        ---
        tags:
          - 旅游季节
        parameters:
          - name: attraction_id
            in: path
            required: true
            type: integer
            description: 景点ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                season:
                  type: integer
                  enum: [1, 2, 3, 4]
                  description: 季节(1春,2夏,3秋,4冬)
                recommendation:
                  type: string
                  description: 季节推荐理由
        """
        # 检查用户权限
        if not request.user.is_admin:
            return jsonify(error_response("没有操作权限")), 403
        
        # 查询景点
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify(error_response("景点不存在")), 404
        
        # 获取请求数据
        data = request.json
        
        # 验证必填字段
        required_fields = ['season', 'recommendation']
        is_valid, errors = validate_required(data, required_fields)
        if not is_valid:
            return jsonify(error_response("信息不完整", errors=errors)), 400
        
        season = data.get('season')
        recommendation = data.get('recommendation')
        
        # 验证季节值
        if season not in [1, 2, 3, 4]:
            return jsonify(error_response("无效的季节值，应为1(春)、2(夏)、3(秋)或4(冬)")), 400
        
        # 检查是否已存在相同的季节记录
        existing_season = TravelSeason.query.filter_by(
            attraction_id=attraction_id,
            season=season
        ).first()
        
        if existing_season:
            return jsonify(error_response("该季节信息已存在")), 400
        
        try:
            # 创建新季节信息
            travel_season = TravelSeason(
                attraction_id=attraction_id,
                season=season,
                recommendation=recommendation
            )
            
            db.session.add(travel_season)
            db.session.commit()
            
            return jsonify(success_response("添加季节信息成功", 
                travel_season.to_dict()
            )), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"添加季节信息失败: {str(e)}")), 500
    
    @staticmethod
    @season_bp.route('/<int:season_id>', methods=['PUT'])
    @login_required
    def update_season(season_id):
        """
        更新景点季节信息
        ---
        tags:
          - 旅游季节
        parameters:
          - name: season_id
            in: path
            required: true
            type: integer
            description: 季节ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                recommendation:
                  type: string
                  description: 季节推荐理由
        """
        # 检查用户权限
        if not request.user.is_admin:
            return jsonify(error_response("没有操作权限")), 403
        
        # 查询季节信息
        travel_season = TravelSeason.query.get(season_id)
        if not travel_season:
            return jsonify(error_response("季节信息不存在")), 404
        
        # 获取请求数据
        data = request.json
        
        # 验证必填字段
        if 'recommendation' not in data:
            return jsonify(error_response("缺少推荐理由")), 400
        
        recommendation = data.get('recommendation')
        
        try:
            # 更新季节信息
            travel_season.recommendation = recommendation
            db.session.commit()
            
            return jsonify(success_response("更新季节信息成功", 
                travel_season.to_dict()
            ))
            
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"更新季节信息失败: {str(e)}")), 500
    
    @staticmethod
    @season_bp.route('/<int:season_id>', methods=['DELETE'])
    @login_required
    def delete_season(season_id):
        """
        删除景点季节信息
        ---
        tags:
          - 旅游季节
        parameters:
          - name: season_id
            in: path
            required: true
            type: integer
            description: 季节ID
        """
        # 检查用户权限
        if not request.user.is_admin:
            return jsonify(error_response("没有操作权限")), 403
        
        # 查询季节信息
        travel_season = TravelSeason.query.get(season_id)
        if not travel_season:
            return jsonify(error_response("季节信息不存在")), 404
        
        try:
            # 删除季节信息
            db.session.delete(travel_season)
            db.session.commit()
            
            return jsonify(success_response("删除季节信息成功"))
            
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"删除季节信息失败: {str(e)}")), 500
    
    @staticmethod
    @season_bp.route('', methods=['GET'])
    def get_seasons():
        """
        获取所有季节信息(分页)
        ---
        tags:
          - 旅游季节
        parameters:
          - name: attraction_id
            in: query
            type: integer
            description: 景点ID(可选)
          - name: season
            in: query
            type: integer
            enum: [1, 2, 3, 4]
            description: 季节(1春,2夏,3秋,4冬)(可选)
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        # 获取分页参数
        page, per_page = get_page_params()
        
        # 获取过滤参数
        attraction_id = request.args.get('attraction_id', type=int)
        season = request.args.get('season', type=int)
        
        # 构建查询
        query = TravelSeason.query
        
        # 应用过滤
        if attraction_id:
            query = query.filter_by(attraction_id=attraction_id)
        
        if season and season in [1, 2, 3, 4]:
            query = query.filter_by(season=season)
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for season in paginate.items:
            # 获取景点信息
            attraction = Attraction.query.get(season.attraction_id)
            
            season_data = season.to_dict()
            if attraction:
                season_data['attraction_name'] = attraction.name
            
            items.append(season_data)
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="获取季节信息列表成功"
        ))
    
    @staticmethod
    @season_bp.route('/by_season/<int:season>', methods=['GET'])
    def get_attractions_by_season(season):
        """
        获取指定季节的推荐景点
        ---
        tags:
          - 旅游季节
        parameters:
          - name: season
            in: path
            required: true
            type: integer
            enum: [1, 2, 3, 4]
            description: 季节(1春,2夏,3秋,4冬)
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        # 验证季节值
        if season not in [1, 2, 3, 4]:
            return jsonify(error_response("无效的季节值，应为1(春)、2(夏)、3(秋)或4(冬)")), 400
        
        # 获取分页参数
        page, per_page = get_page_params()
        
        # 联合查询
        query = db.session.query(
            Attraction, TravelSeason
        ).join(
            TravelSeason, Attraction.id == TravelSeason.attraction_id
        ).filter(
            TravelSeason.season == season,
            Attraction.status == 1
        )
        
        # 获取总数
        total = query.count()
        
        # 执行分页
        results = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for attraction, travel_season in results.items:
            item = attraction.to_dict(with_details=False)
            item['season_recommendation'] = travel_season.recommendation
            items.append(item)
        
        # 获取季节名称
        season_names = {1: '春季', 2: '夏季', 3: '秋季', 4: '冬季'}
        season_name = season_names.get(season, '未知')
        
        return jsonify(pagination_response(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            message=f"获取{season_name}推荐景点成功"
        ))
    
    @staticmethod
    @season_bp.route('/<int:season_id>', methods=['GET'])
    def get_season_attractions(season_id):
        """获取特定季节推荐景点
        
        Args:
            season_id: 季节ID（1-春季, 2-夏季, 3-秋季, 4-冬季）
            
        Returns:
            季节推荐数据
        """
        try:
            # 参数验证
            if season_id not in [1, 2, 3, 4]:
                return error_response(message="无效的季节ID")
            
            # 分页参数
            page, per_page = get_page_params()
            
            # 查询季节信息 - 注意：这里使用season而不是id进行查询
            season_name = {1: '春季', 2: '夏季', 3: '秋季', 4: '冬季'}.get(season_id, '未知')
            
            # 查询该季节的所有推荐
            recommendations = TravelSeason.query.filter_by(season=season_id).all()
            if not recommendations:
                return success_response(message=f"该季节暂无推荐", data={
                    'season': {
                        'id': season_id,
                        'name': season_name
                    },
                    'attractions': [],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': 0,
                        'total_pages': 0,
                        'has_next': False,
                        'has_prev': False
                    }
                })
            
            # 获取景点IDs
            attraction_ids = [rec.attraction_id for rec in recommendations if rec.attraction_id]
            
            # 构建查询 - 获取推荐景点的详细信息
            attractions = Attraction.query.filter(
                Attraction.id.in_(attraction_ids)
            ).all()
            
            # 准备响应数据
            attraction_list = []
            for attraction in attractions:
                attraction_data = attraction.to_dict()
                
                # 获取评论数量
                attraction_data['comment_count'] = Comment.query.filter(
                    Comment.content_id == attraction.id,
                    Comment.content_type == 'attraction'
                ).count()
                
                # 查找对应的季节推荐信息
                for rec in recommendations:
                    if rec.attraction_id == attraction.id:
                        attraction_data['season_recommendation'] = rec.description
                        break
                        
                attraction_list.append(attraction_data)
            
            return success_response(data={
                'season': {
                    'id': season_id,
                    'name': season_name
                },
                'attractions': attraction_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': len(attraction_list),
                    'total_pages': (len(attraction_list) + per_page - 1) // per_page,
                    'has_next': page < ((len(attraction_list) + per_page - 1) // per_page),
                    'has_prev': page > 1
                }
            }, message=f"获取{season_name}景点成功")
        except Exception as e:
            current_app.logger.error(f"获取季节景点错误: {str(e)}")
            return error_response(message=f"获取季节景点失败: {str(e)}") 