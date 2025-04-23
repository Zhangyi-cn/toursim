from flask import Blueprint, request, g, jsonify
from utils.response import success_response, error_response
from utils.auth import login_required, get_current_user
from models.like import Like
from models.collection import Collection
from models.browse_history import BrowseHistory
from models.attraction import Attraction
from models.travel_guide import TravelGuide
from models.travel_note import TravelNote
from sqlalchemy import desc
from extensions import db

interaction_bp = Blueprint('interaction', __name__)


class InteractionController:
    """用户交互控制器"""
    
    @staticmethod
    @interaction_bp.route('/likes', methods=['POST'])
    @login_required
    def toggle_like():
        """
        切换点赞状态
        ---
        tags:
          - 用户交互
        parameters:
          - name: body
            in: body
            required: true
            schema:
              required:
                - target_id
                - target_type
              properties:
                target_id:
                  type: integer
                  description: 目标ID
                target_type:
                  type: string
                  enum: [attraction, guide, note, comment]
                  description: 目标类型
        responses:
          200:
            description: 点赞结果
            schema:
              properties:
                code:
                  type: integer
                  example: 200
                msg:
                  type: string
                  example: 成功
                data:
                  type: object
                  properties:
                    is_liked:
                      type: boolean
                      description: 操作后的点赞状态
                    count:
                      type: integer
                      description: 当前点赞总数
        """
        # 获取当前用户
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("未找到用户信息", 404)), 404
            
        user_id = current_user.id
        
        data = request.json
        target_id = data.get('target_id')
        target_type = data.get('target_type')
        
        # 参数校验
        if not target_id or not target_type:
            return jsonify(error_response(msg='参数不完整'))
            
        if target_type not in ['attraction', 'guide', 'note', 'comment']:
            return jsonify(error_response(msg='目标类型不合法'))
        
        # 验证目标存在性
        if not InteractionController._check_target_exists(target_id, target_type):
            return jsonify(error_response(msg='目标不存在'))
        
        # 切换点赞状态
        is_liked = Like.toggle_like(user_id, target_id, target_type)
        like_count = Like.count_likes(target_id, target_type)
        
        return jsonify(success_response("操作成功", {
            'is_liked': is_liked,
            'count': like_count
        }))
    
    @staticmethod
    @interaction_bp.route('/collections', methods=['POST'])
    @login_required
    def toggle_collection():
        """
        切换收藏状态
        ---
        tags:
          - 用户交互
        parameters:
          - name: body
            in: body
            required: true
            schema:
              required:
                - target_id
                - target_type
              properties:
                target_id:
                  type: integer
                  description: 目标ID
                target_type:
                  type: string
                  enum: [attraction, guide, note]
                  description: 目标类型
        responses:
          200:
            description: 收藏结果
            schema:
              properties:
                code:
                  type: integer
                  example: 200
                msg:
                  type: string
                  example: 成功
                data:
                  type: object
                  properties:
                    is_collected:
                      type: boolean
                      description: 操作后的收藏状态
                    count:
                      type: integer
                      description: 当前收藏总数
        """
        # 获取当前用户
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("未找到用户信息", 404)), 404
            
        user_id = current_user.id
        
        data = request.json
        target_id = data.get('target_id')
        target_type = data.get('target_type')
        
        # 参数校验
        if not target_id or not target_type:
            return jsonify(error_response(msg='参数不完整'))
            
        if target_type not in ['attraction', 'guide', 'note']:
            return jsonify(error_response(msg='目标类型不合法'))
        
        # 验证目标存在性
        if not InteractionController._check_target_exists(target_id, target_type):
            return jsonify(error_response(msg='目标不存在'))
        
        # 切换收藏状态
        is_collected = Collection.toggle_collection(user_id, target_id, target_type)
        collection_count = Collection.count_collections(target_id, target_type)
        
        return jsonify(success_response("操作成功", {
            'is_collected': is_collected,
            'count': collection_count
        }))
    
    @staticmethod
    @interaction_bp.route('/collections', methods=['GET'])
    @login_required
    def get_collections():
        """
        获取用户收藏列表
        ---
        tags:
          - 用户交互
        parameters:
          - name: type
            in: query
            type: string
            enum: [attraction, guide, note, all]
            default: all
            description: 收藏类型
          - name: page
            in: query
            type: integer
            default: 1
            description: 页码
          - name: limit
            in: query
            type: integer
            default: 10
            description: 每页数量
        responses:
          200:
            description: 收藏列表
            schema:
              properties:
                code:
                  type: integer
                  example: 200
                msg:
                  type: string
                  example: 成功
                data:
                  type: object
                  properties:
                    items:
                      type: array
                      items:
                        type: object
                    total:
                      type: integer
                    page:
                      type: integer
                    limit:
                      type: integer
        """
        # 获取当前用户
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("未找到用户信息", 404)), 404
            
        user_id = current_user.id
        
        target_type = request.args.get('type', 'all')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # 处理类型参数
        if target_type == 'all':
            target_type = None
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 获取收藏列表
        collections = Collection.get_user_collections(user_id, target_type, limit, offset)
        
        # 获取收藏总数
        total = Collection.count_user_collections(user_id, target_type)
        
        # 转换结果
        result = []
        for collection in collections:
            item = collection.to_dict()
            
            # 获取目标对象信息
            target_info = InteractionController._get_target_info(
                collection.target_id, 
                collection.target_type
            )
            
            if target_info:
                item['target'] = target_info
                result.append(item)
        
        return jsonify(success_response("获取收藏列表成功", {
            'items': result,
            'total': total,
            'page': page,
            'limit': limit
        }))
    
    @staticmethod
    @interaction_bp.route('/history', methods=['GET'])
    @login_required
    def get_browse_history():
        """
        获取浏览历史列表
        ---
        tags:
          - 用户交互
        parameters:
          - name: type
            in: query
            type: string
            enum: [attraction, guide, note, all]
            default: all
            description: 浏览类型
          - name: page
            in: query
            type: integer
            default: 1
            description: 页码
          - name: limit
            in: query
            type: integer
            default: 10
            description: 每页数量
        responses:
          200:
            description: 浏览历史
            schema:
              properties:
                code:
                  type: integer
                  example: 200
                msg:
                  type: string
                  example: 成功
                data:
                  type: object
                  properties:
                    items:
                      type: array
                      items:
                        type: object
                    total:
                      type: integer
                    page:
                      type: integer
                    limit:
                      type: integer
        """
        # 获取当前用户
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("未找到用户信息", 404)), 404
            
        user_id = current_user.id
        
        target_type = request.args.get('type', 'all')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # 处理类型参数
        if target_type == 'all':
            target_type = None
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 获取浏览历史
        history = BrowseHistory.get_user_history(user_id, target_type, limit, offset)
        
        # 获取记录总数
        total = BrowseHistory.count_user_history(user_id, target_type)
        
        # 转换结果
        result = []
        for record in history:
            item = record.to_dict()
            
            # 获取目标对象信息
            target_info = InteractionController._get_target_info(
                record.target_id, 
                record.target_type
            )
            
            if target_info:
                item['target'] = target_info
                result.append(item)
        
        return jsonify(success_response("获取浏览历史成功", {
            'items': result,
            'total': total,
            'page': page,
            'limit': limit
        }))
    
    @staticmethod
    def _check_target_exists(target_id, target_type):
        """
        检查目标是否存在
        :param target_id: 目标ID
        :param target_type: 目标类型
        :return: 是否存在
        """
        if target_type == 'attraction':
            return Attraction.query.get(target_id) is not None
        elif target_type == 'guide':
            return TravelGuide.query.get(target_id) is not None
        elif target_type == 'note':
            return TravelNote.query.get(target_id) is not None
        elif target_type == 'comment':
            from models.comment import Comment
            return Comment.query.get(target_id) is not None
        
        return False
    
    @staticmethod
    def _get_target_info(target_id, target_type):
        """
        获取目标对象信息
        :param target_id: 目标ID
        :param target_type: 目标类型
        :return: 目标对象信息
        """
        if target_type == 'attraction':
            attraction = Attraction.query.get(target_id)
            if attraction:
                return attraction.to_dict(with_details=False)
                
        elif target_type == 'guide':
            guide = TravelGuide.query.get(target_id)
            if guide:
                return guide.to_dict(with_details=False)
                
        elif target_type == 'note':
            note = TravelNote.query.get(target_id)
            if note:
                return note.to_dict(with_details=False)
                
        return None 