from flask import request, jsonify, g
from flask_jwt_extended import jwt_required
from datetime import datetime

from models.ticket import Ticket
from models.attraction import Attraction
from models.order import OrderItem
from extensions import db
from utils.response import success_response, error_response
from utils.auth import admin_required

class TicketAdminController:
    """门票管理控制器"""
    
    @staticmethod
    @admin_required()
    def get_tickets():
        """获取门票列表"""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            keyword = request.args.get('keyword', '')
            attraction_id = request.args.get('attraction_id')
            
            query = Ticket.query
            
            # 按关键词筛选
            if keyword:
                query = query.filter(Ticket.name.like(f'%{keyword}%'))
                
            # 按景点筛选
            if attraction_id:
                query = query.filter(Ticket.attraction_id == attraction_id)
                
            # 分页
            pagination = query.order_by(Ticket.sort_order.asc(), Ticket.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            tickets = pagination.items
            total = pagination.total
            
            # 构造返回数据
            items = []
            for ticket in tickets:
                ticket_dict = ticket.to_dict()
                
                # 获取景点信息
                if ticket.attraction_id:
                    attraction = Attraction.query.get(ticket.attraction_id)
                    if attraction:
                        ticket_dict['attraction'] = {
                            'id': attraction.id,
                            'name': attraction.name
                        }
                        
                # 获取售出数量
                ticket_dict['type_text'] = ticket.get_type_text()
                ticket_dict['status_text'] = ticket.get_status_text()
                
                items.append(ticket_dict)
            
            return success_response("获取门票列表成功", {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page
            })
            
        except Exception as e:
            return error_response(f"获取门票列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def create_ticket():
        """创建门票"""
        try:
            data = request.get_json()
            
            attraction_id = data.get('attraction_id')
            name = data.get('name', '')
            description = data.get('description', '')
            price = data.get('price', 0)
            original_price = data.get('original_price', 0)
            ticket_type = data.get('type', 1)  # 默认普通票
            notice = data.get('notice', '')
            valid_period = data.get('valid_period', 0)
            status = data.get('status', 1)  # 默认启用
            sort_order = data.get('sort_order', 0)
            
            # 验证必填字段
            if not attraction_id:
                return error_response("景点ID不能为空", 400)
                
            if not name:
                return error_response("门票名称不能为空", 400)
                
            # 验证景点是否存在
            attraction = Attraction.query.get(attraction_id)
            if not attraction:
                return error_response("指定的景点不存在", 400)
                
            # 创建门票
            ticket = Ticket(
                attraction_id=attraction_id,
                name=name,
                description=description,
                price=price,
                original_price=original_price,
                type=ticket_type,
                notice=notice,
                valid_period=valid_period,
                status=status,
                sort_order=sort_order
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            return success_response("创建门票成功", ticket.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"创建门票失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_ticket(ticket_id):
        """获取门票详情"""
        try:
            ticket = Ticket.query.get(ticket_id)
            
            if not ticket:
                return error_response("门票不存在", 404)
                
            ticket_dict = ticket.to_dict()
            
            # 获取景点信息
            if ticket.attraction_id:
                attraction = Attraction.query.get(ticket.attraction_id)
                if attraction:
                    ticket_dict['attraction'] = {
                        'id': attraction.id,
                        'name': attraction.name
                    }
                    
            # 获取售出数量
            sold_count = OrderItem.query.filter_by(ticket_id=ticket_id).count()
            ticket_dict['sold_count'] = sold_count
            
            ticket_dict['type_text'] = ticket.get_type_text()
            ticket_dict['status_text'] = ticket.get_status_text()
            
            return success_response("获取门票详情成功", ticket_dict)
            
        except Exception as e:
            return error_response(f"获取门票详情失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_ticket(ticket_id):
        """更新门票"""
        try:
            ticket = Ticket.query.get(ticket_id)
            
            if not ticket:
                return error_response("门票不存在", 404)
                
            data = request.get_json()
            
            # 可更新的字段
            updatable_fields = [
                'attraction_id', 'name', 'description', 'price', 'original_price', 
                'type', 'notice', 'valid_period', 'status', 'sort_order'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(ticket, field, data[field])
            
            # 验证景点是否存在
            if 'attraction_id' in data and data['attraction_id']:
                attraction = Attraction.query.get(data['attraction_id'])
                if not attraction:
                    return error_response("指定的景点不存在", 400)
                    
            ticket.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新门票成功", ticket.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新门票失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def delete_ticket(ticket_id):
        """删除门票"""
        try:
            ticket = Ticket.query.get(ticket_id)
            
            if not ticket:
                return error_response("门票不存在", 404)
                
            # 检查是否有订单使用该门票
            order_count = OrderItem.query.filter_by(ticket_id=ticket_id).count()
            if order_count > 0:
                return error_response(f"该门票已被订购 {order_count} 次，无法删除", 400)
                
            db.session.delete(ticket)
            db.session.commit()
            
            return success_response("删除门票成功")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"删除门票失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def get_attraction_tickets(attraction_id):
        """获取景点的门票列表"""
        try:
            # 验证景点是否存在
            attraction = Attraction.query.get(attraction_id)
            if not attraction:
                return error_response("景点不存在", 404)
                
            tickets = Ticket.query.filter_by(attraction_id=attraction_id).order_by(
                Ticket.sort_order.asc()
            ).all()
            
            items = []
            for ticket in tickets:
                ticket_dict = ticket.to_dict()
                ticket_dict['type_text'] = ticket.get_type_text()
                ticket_dict['status_text'] = ticket.get_status_text()
                
                items.append(ticket_dict)
            
            return success_response("获取景点门票列表成功", items)
            
        except Exception as e:
            return error_response(f"获取景点门票列表失败: {str(e)}", 500)
    
    @staticmethod
    @admin_required()
    def update_ticket_status(ticket_id):
        """更新门票状态"""
        try:
            ticket = Ticket.query.get(ticket_id)
            
            if not ticket:
                return error_response("门票不存在", 404)
                
            data = request.get_json()
            status = data.get('status')
            
            if status is None:
                return error_response("状态不能为空", 400)
                
            ticket.status = status
            ticket.updated_at = datetime.now()
            db.session.commit()
            
            return success_response("更新门票状态成功", ticket.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"更新门票状态失败: {str(e)}", 500) 