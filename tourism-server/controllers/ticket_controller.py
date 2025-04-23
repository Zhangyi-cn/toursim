from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from datetime import datetime

from models.ticket import Ticket
from models.attraction import Attraction
from extensions import db, cache
from utils.response import success_response, error_response, pagination_response
from utils.validator import get_page_params

# 创建蓝图
ticket_bp = Blueprint('ticket', __name__)


@ticket_bp.route('/attractions/<int:attraction_id>/tickets', methods=['GET'])
def get_tickets(attraction_id):
    """
    获取景点门票列表
    ---
    tags:
      - 门票
    parameters:
      - name: attraction_id
        in: path
        required: true
        type: integer
        description: 景点ID
    responses:
      200:
        description: 获取成功
      404:
        description: 景点不存在
    """
    # 验证景点是否存在
    attraction = Attraction.query.get(attraction_id)
    if not attraction:
        return jsonify(error_response("景点不存在")), 404
    
    # 从缓存中获取门票列表
    cache_key = f'attraction_tickets_{attraction_id}'
    cached_tickets = cache.get(cache_key)
    
    if cached_tickets:
        return jsonify(success_response("获取门票列表成功", cached_tickets))
    
    # 查询门票列表
    tickets = Ticket.query.filter_by(
        attraction_id=attraction_id,
        status=1  # 只查询上架的门票
    ).order_by(Ticket.sort_order.desc(), Ticket.price.asc()).all()
    
    # 格式化返回数据
    ticket_list = [ticket.to_dict() for ticket in tickets]
    
    # 存入缓存
    cache.set(cache_key, ticket_list, timeout=3600)  # 缓存1小时
    
    return jsonify(success_response("获取门票列表成功", ticket_list))


@ticket_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket_detail(ticket_id):
    """
    获取门票详情
    ---
    tags:
      - 门票
    parameters:
      - name: ticket_id
        in: path
        required: true
        type: integer
        description: 门票ID
    responses:
      200:
        description: 获取成功
      404:
        description: 门票不存在
    """
    # 查询门票
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify(error_response("门票不存在")), 404
    
    # 判断门票状态
    if ticket.status != 1:
        return jsonify(error_response("门票已下架")), 403
    
    # 查询关联景点
    attraction = Attraction.query.get(ticket.attraction_id)
    
    # 格式化返回数据
    ticket_data = ticket.to_dict()
    if attraction:
        ticket_data['attraction'] = {
            'id': attraction.id,
            'name': attraction.name,
            'cover_image': attraction.cover_image
        }
    
    return jsonify(success_response("获取门票详情成功", ticket_data))


@ticket_bp.route('/admin/tickets', methods=['POST'])
@jwt_required()
def create_ticket():
    """
    创建门票（管理员）
    ---
    tags:
      - 门票
      - 管理员
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - attraction_id
            - name
            - price
          properties:
            attraction_id:
              type: integer
              description: 景点ID
            name:
              type: string
              description: 门票名称
            description:
              type: string
              description: 门票描述
            price:
              type: number
              description: 价格
            discount_price:
              type: number
              description: 折扣价
            validity_period:
              type: integer
              description: 有效期(天)
            notice:
              type: string
              description: 购票须知
            status:
              type: integer
              enum: [0, 1]
              description: 状态(0:下架, 1:上架)
    responses:
      201:
        description: 创建成功
      400:
        description: 参数错误
      401:
        description: 未授权
      403:
        description: 权限不足
      404:
        description: 景点不存在
    """
    # 获取当前用户
    user_id = get_jwt_identity()
    
    # 校验是否是管理员
    # 这里应该有检查用户是否是管理员的逻辑
    
    # 获取请求数据
    data = request.get_json()
    
    # 验证必填参数
    if not data.get('attraction_id') or not data.get('name') or not data.get('price'):
        return jsonify(error_response("缺少必填参数")), 400
    
    attraction_id = data.get('attraction_id')
    name = data.get('name')
    price = data.get('price')
    
    # 校验景点是否存在
    attraction = Attraction.query.get(attraction_id)
    if not attraction:
        return jsonify(error_response("景点不存在")), 404
    
    # 创建门票
    ticket = Ticket(
        attraction_id=attraction_id,
        name=name,
        description=data.get('description', ''),
        price=price,
        discount_price=data.get('discount_price', price),
        validity_period=data.get('validity_period', 1),
        notice=data.get('notice', ''),
        status=data.get('status', 1),
        created_at=datetime.now()
    )
    
    try:
        db.session.add(ticket)
        db.session.commit()
        
        # 清除缓存
        cache_key = f'attraction_tickets_{attraction_id}'
        cache.delete(cache_key)
        
        return jsonify(success_response("创建门票成功", ticket.to_dict())), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建门票失败: {str(e)}")
        return jsonify(error_response(f"创建门票失败: {str(e)}")), 500


@ticket_bp.route('/admin/tickets/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    """
    更新门票（管理员）
    ---
    tags:
      - 门票
      - 管理员
    parameters:
      - name: ticket_id
        in: path
        required: true
        type: integer
        description: 门票ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: 门票名称
            description:
              type: string
              description: 门票描述
            price:
              type: number
              description: 价格
            discount_price:
              type: number
              description: 折扣价
            validity_period:
              type: integer
              description: 有效期(天)
            notice:
              type: string
              description: 购票须知
            status:
              type: integer
              enum: [0, 1]
              description: 状态(0:下架, 1:上架)
            sort_order:
              type: integer
              description: 排序值
    responses:
      200:
        description: 更新成功
      400:
        description: 参数错误
      401:
        description: 未授权
      403:
        description: 权限不足
      404:
        description: 门票不存在
    """
    # 获取当前用户
    user_id = get_jwt_identity()
    
    # 校验是否是管理员
    # 这里应该有检查用户是否是管理员的逻辑
    
    # 查询门票
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify(error_response("门票不存在")), 404
    
    # 获取请求数据
    data = request.get_json()
    
    # 更新门票信息
    if 'name' in data:
        ticket.name = data['name']
    if 'description' in data:
        ticket.description = data['description']
    if 'price' in data:
        ticket.price = data['price']
    if 'discount_price' in data:
        ticket.discount_price = data['discount_price']
    if 'validity_period' in data:
        ticket.validity_period = data['validity_period']
    if 'notice' in data:
        ticket.notice = data['notice']
    if 'status' in data:
        ticket.status = data['status']
    if 'sort_order' in data:
        ticket.sort_order = data['sort_order']
    
    ticket.updated_at = datetime.now()
    
    try:
        db.session.commit()
        
        # 清除缓存
        cache_key = f'attraction_tickets_{ticket.attraction_id}'
        cache.delete(cache_key)
        
        return jsonify(success_response("更新门票成功", ticket.to_dict()))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新门票失败: {str(e)}")
        return jsonify(error_response(f"更新门票失败: {str(e)}")), 500


@ticket_bp.route('/admin/tickets/<int:ticket_id>', methods=['DELETE'])
@jwt_required()
def delete_ticket(ticket_id):
    """
    删除门票（管理员）
    ---
    tags:
      - 门票
      - 管理员
    parameters:
      - name: ticket_id
        in: path
        required: true
        type: integer
        description: 门票ID
    responses:
      200:
        description: 删除成功
      401:
        description: 未授权
      403:
        description: 权限不足
      404:
        description: 门票不存在
    """
    # 获取当前用户
    user_id = get_jwt_identity()
    
    # 校验是否是管理员
    # 这里应该有检查用户是否是管理员的逻辑
    
    # 查询门票
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify(error_response("门票不存在")), 404
    
    attraction_id = ticket.attraction_id
    
    try:
        db.session.delete(ticket)
        db.session.commit()
        
        # 清除缓存
        cache_key = f'attraction_tickets_{attraction_id}'
        cache.delete(cache_key)
        
        return jsonify(success_response("删除门票成功"))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除门票失败: {str(e)}")
        return jsonify(error_response(f"删除门票失败: {str(e)}")), 500


@staticmethod
@ticket_bp.route('/init-test-tickets', methods=['POST'])
def init_test_tickets():
    """
    初始化测试用门票
    ---
    tags:
      - 门票管理
    """
    try:
        # 获取attraction_id参数
        data = request.get_json() or {}
        attraction_id = data.get('attraction_id')
        
        if not attraction_id:
            return jsonify(error_response("景点ID不能为空")), 400
        
        # 查询景点是否存在
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify(error_response("景点不存在")), 404
            
        # 查询是否已有该景点的门票
        existing_ticket = Ticket.query.filter_by(attraction_id=attraction_id).first()
        if existing_ticket:
            return jsonify(success_response("该景点已有门票，无需初始化", {
                "ticket_id": existing_ticket.id
            }))
        
        # 创建测试门票
        test_ticket = Ticket(
            attraction_id=attraction_id,
            name=f"{attraction.name}门票",
            description=f"{attraction.name}的标准门票",
            price=100.00,
            original_price=120.00,
            type=1,  # 普通票
            notice="仅供测试使用",
            valid_period="当天有效",
            status=1,  # 上架
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(test_ticket)
        db.session.commit()
        
        return jsonify(success_response("测试门票初始化成功", {
            "ticket_id": test_ticket.id,
            "ticket_name": test_ticket.name,
            "attraction_id": test_ticket.attraction_id
        }))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"初始化测试门票失败: {str(e)}")
        return jsonify(error_response(f"初始化测试门票失败: {str(e)}")), 500 