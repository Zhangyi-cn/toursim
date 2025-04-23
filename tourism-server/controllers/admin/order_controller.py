from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from sqlalchemy import desc, func, and_
import calendar

from models.order import Order, OrderItem
from models.ticket import Ticket
from models.user import User
from extensions import db
from utils.response import success_response, error_response, pagination_response
from utils.auth import admin_required, record_admin_activity
from utils.validator import get_page_params, validate_required

admin_order_bp = Blueprint('admin_order', __name__)


class AdminOrderController:
    """管理员订单控制器"""
    
    @staticmethod
    @admin_order_bp.route('', methods=['GET'])
    @jwt_required()
    @admin_required
    def get_orders():
        """
        获取订单列表
        ---
        tags:
          - 管理员-订单管理
        parameters:
          - name: status
            in: query
            type: string
            description: 订单状态，多个状态用逗号分隔
          - name: order_no
            in: query
            type: string
            description: 订单号
          - name: contact_name
            in: query
            type: string
            description: 联系人姓名
          - name: contact_phone
            in: query
            type: string
            description: 联系人电话
          - name: user_id
            in: query
            type: integer
            description: 用户ID
          - name: date_start
            in: query
            type: string
            description: 创建日期开始 (YYYY-MM-DD)
          - name: date_end
            in: query
            type: string
            description: 创建日期结束 (YYYY-MM-DD)
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
        status = request.args.get('status', '')
        order_no = request.args.get('order_no', '')
        contact_name = request.args.get('contact_name', '')
        contact_phone = request.args.get('contact_phone', '')
        user_id = request.args.get('user_id', type=int)
        date_start = request.args.get('date_start', '')
        date_end = request.args.get('date_end', '')
        
        # 构建基础查询
        query = Order.query
        
        # 应用过滤条件
        status_list = [int(s) for s in status.split(',') if s.isdigit()] if status else []
        if status_list:
            query = query.filter(Order.status.in_(status_list))
        
        if order_no:
            query = query.filter(Order.order_no.like(f"%{order_no}%"))
        
        if contact_name:
            query = query.filter(Order.contact_name.like(f"%{contact_name}%"))
        
        if contact_phone:
            query = query.filter(Order.contact_phone.like(f"%{contact_phone}%"))
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        if date_start:
            try:
                start_date = datetime.strptime(date_start, '%Y-%m-%d')
                query = query.filter(Order.created_at >= start_date)
            except ValueError:
                pass
        
        if date_end:
            try:
                end_date = datetime.strptime(date_end, '%Y-%m-%d')
                # 设置为当天的最后一秒
                end_date = end_date.replace(hour=23, minute=59, second=59)
                query = query.filter(Order.created_at <= end_date)
            except ValueError:
                pass
        
        # 应用排序
        query = query.order_by(desc(Order.created_at))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for order in paginate.items:
            order_data = order.to_dict()
            
            # 获取用户信息
            user = User.query.get(order.user_id)
            if user:
                order_data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'phone': user.phone
                }
            
            # 获取订单项数量
            order_data['item_count'] = order.items.count()
            
            items.append(order_data)
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="获取订单列表成功"
        ))
    
    @staticmethod
    @admin_order_bp.route('/<string:order_no>', methods=['GET'])
    @jwt_required()
    @admin_required
    def get_order_detail(order_no):
        """
        获取订单详情
        ---
        tags:
          - 管理员-订单管理
        parameters:
          - name: order_no
            in: path
            required: true
            type: string
            description: 订单号
        """
        # 查询订单
        order = Order.query.filter_by(order_no=order_no).first()
        if not order:
            return jsonify(error_response("订单不存在")), 404
        
        # 准备响应数据
        result = order.to_dict()
        
        # 获取用户信息
        user = User.query.get(order.user_id)
        if user:
            result['user'] = {
                'id': user.id,
                'username': user.username,
                'phone': user.phone,
                'email': user.email
            }
        
        # 获取订单项
        items = [item.to_dict() for item in order.items]
        result['items'] = items
        
        return jsonify(success_response("获取订单详情成功", result))
    
    @staticmethod
    @admin_order_bp.route('/<string:order_no>/complete', methods=['POST'])
    @jwt_required()
    @admin_required
    def complete_order(order_no):
        """
        完成订单
        ---
        tags:
          - 管理员-订单管理
        parameters:
          - name: order_no
            in: path
            required: true
            type: string
            description: 订单号
        """
        # 查询订单
        order = Order.query.filter_by(order_no=order_no).first()
        if not order:
            return jsonify(error_response("订单不存在")), 404
        
        # 验证订单状态
        if order.status != 2:  # 只能完成已支付的订单
            return jsonify(error_response(f"订单状态不允许完成，当前状态: {order.get_status_text()}")), 403
        
        try:
            # 更新订单状态
            order.status = 3  # 已完成
            order.complete_time = datetime.now()
            
            db.session.commit()
            
            # 记录管理员活动
            record_admin_activity(
                admin_id=g.admin_id,
                action="complete_order",
                module="order",
                target_id=order.id
            )
            
            return jsonify(success_response("订单完成成功"))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"完成订单失败: {str(e)}")
            return jsonify(error_response("完成订单失败，服务器错误")), 500
    
    @staticmethod
    @admin_order_bp.route('/<string:order_no>/cancel', methods=['POST'])
    @jwt_required()
    @admin_required
    def cancel_order(order_no):
        """
        取消订单
        ---
        tags:
          - 管理员-订单管理
        parameters:
          - name: order_no
            in: path
            required: true
            type: string
            description: 订单号
          - name: body
            in: body
            required: true
            schema:
              required:
                - reason
              properties:
                reason:
                  type: string
                  description: 取消原因
        """
        # 查询订单
        order = Order.query.filter_by(order_no=order_no).first()
        if not order:
            return jsonify(error_response("订单不存在")), 404
        
        # 验证订单状态
        if order.status not in [1, 2]:  # 只能取消待支付或已支付的订单
            return jsonify(error_response(f"订单状态不允许取消，当前状态: {order.get_status_text()}")), 403
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['reason']
        validation_result = validate_required(data, required_fields)
        if validation_result:
            return jsonify(error_response(f"缺少必填字段: {validation_result}")), 400
            
        reason = data.get('reason')
        
        try:
            # 更新订单状态
            order.status = 4  # 已取消
            order.cancel_time = datetime.now()
            order.cancel_reason = reason
            
            # 如果订单已支付，则进行退款处理
            if order.status == 2:
                # 模拟退款成功
                # 实际应用中，这里应该调用退款接口，并在退款回调中更新退款信息
                order.refund_time = datetime.now()
                order.refund_amount = order.amount
                
                # 更新门票销售数量
                for item in order.items:
                    ticket = Ticket.query.get(item.ticket_id)
                    if ticket and ticket.sold_count >= item.quantity:
                        ticket.sold_count -= item.quantity
            
            db.session.commit()
            
            # 记录管理员活动
            record_admin_activity(
                admin_id=g.admin_id,
                action="cancel_order",
                module="order",
                target_id=order.id,
                remarks=reason
            )
            
            return jsonify(success_response("订单取消成功"))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"取消订单失败: {str(e)}")
            return jsonify(error_response("取消订单失败，服务器错误")), 500
    
    @staticmethod
    @admin_required
    def get_order_statistics():
        """
        获取订单统计数据
        ---
        tags:
          - 管理员-订单管理
        parameters:
          - name: start_date
            in: query
            type: string
            description: 开始日期 (YYYY-MM-DD)
          - name: end_date
            in: query
            type: string
            description: 结束日期 (YYYY-MM-DD)
          - name: type
            in: query
            type: string
            enum: [daily, monthly]
            default: daily
            description: 统计类型，按日/按月
        """
        # 获取参数
        start_date_str = request.args.get('start_date', '')
        end_date_str = request.args.get('end_date', '')
        stat_type = request.args.get('type', 'daily')
        
        # 默认统计最近30天
        today = datetime.now().date()
        
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                start_date = today - timedelta(days=29)
                
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                end_date = today
        except ValueError:
            return jsonify(error_response("日期格式错误")), 400
        
        # 检查日期范围
        if start_date > end_date:
            return jsonify(error_response("开始日期不能大于结束日期")), 400
        
        # 构建统计数据查询
        result = {
            'total_orders': 0,        # 总订单数
            'total_amount': 0,        # 总金额
            'paid_orders': 0,         # 已支付订单数
            'paid_amount': 0,         # 已支付金额
            'cancelled_orders': 0,    # 已取消订单数
            'cancelled_amount': 0,    # 已取消金额
            'completed_orders': 0,    # 已完成订单数
            'completed_amount': 0,    # 已完成金额
            'series': []              # 时间序列数据
        }
        
        # 获取统计周期内的总体数据
        try:
            # 查询周期范围内的订单总数和总金额
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # 所有订单
            total_stats = db.session.query(
                func.count(Order.id), 
                func.sum(Order.amount)
            ).filter(
                Order.created_at.between(start_datetime, end_datetime)
            ).first()
            
            result['total_orders'] = total_stats[0] or 0
            result['total_amount'] = float(total_stats[1]) if total_stats[1] else 0
            
            # 已支付订单
            paid_stats = db.session.query(
                func.count(Order.id), 
                func.sum(Order.amount)
            ).filter(
                Order.created_at.between(start_datetime, end_datetime),
                Order.status.in_([2, 3])  # 已支付、已完成
            ).first()
            
            result['paid_orders'] = paid_stats[0] or 0
            result['paid_amount'] = float(paid_stats[1]) if paid_stats[1] else 0
            
            # 已取消订单
            cancelled_stats = db.session.query(
                func.count(Order.id), 
                func.sum(Order.amount)
            ).filter(
                Order.created_at.between(start_datetime, end_datetime),
                Order.status == 4  # 已取消
            ).first()
            
            result['cancelled_orders'] = cancelled_stats[0] or 0
            result['cancelled_amount'] = float(cancelled_stats[1]) if cancelled_stats[1] else 0
            
            # 已完成订单
            completed_stats = db.session.query(
                func.count(Order.id), 
                func.sum(Order.amount)
            ).filter(
                Order.created_at.between(start_datetime, end_datetime),
                Order.status == 3  # 已完成
            ).first()
            
            result['completed_orders'] = completed_stats[0] or 0
            result['completed_amount'] = float(completed_stats[1]) if completed_stats[1] else 0
            
            # 生成时间序列数据
            if stat_type == 'monthly':
                # 按月统计
                series_data = AdminOrderController._get_monthly_statistics(start_date, end_date)
            else:
                # 按日统计
                series_data = AdminOrderController._get_daily_statistics(start_date, end_date)
            
            result['series'] = series_data
            
            return jsonify(success_response("获取订单统计数据成功", result))
            
        except Exception as e:
            current_app.logger.error(f"获取订单统计数据失败: {str(e)}")
            return jsonify(error_response("获取订单统计数据失败，服务器错误")), 500
    
    @staticmethod
    def _get_daily_statistics(start_date, end_date):
        """获取按日统计数据"""
        result = []
        current_date = start_date
        
        while current_date <= end_date:
            start_datetime = datetime.combine(current_date, datetime.min.time())
            end_datetime = datetime.combine(current_date, datetime.max.time())
            
            # 查询当日数据
            daily_stats = db.session.query(
                func.count(Order.id),
                func.sum(Order.amount),
                func.count(Order.id).filter(Order.status.in_([2, 3])),
                func.sum(Order.amount).filter(Order.status.in_([2, 3]))
            ).filter(
                Order.created_at.between(start_datetime, end_datetime)
            ).first()
            
            result.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total_orders': daily_stats[0] or 0,
                'total_amount': float(daily_stats[1]) if daily_stats[1] else 0,
                'paid_orders': daily_stats[2] or 0,
                'paid_amount': float(daily_stats[3]) if daily_stats[3] else 0
            })
            
            current_date += timedelta(days=1)
        
        return result
    
    @staticmethod
    def _get_monthly_statistics(start_date, end_date):
        """获取按月统计数据"""
        result = []
        
        # 确定起始年月
        start_year, start_month = start_date.year, start_date.month
        end_year, end_month = end_date.year, end_date.month
        
        current_year, current_month = start_year, start_month
        
        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            # 获取当月第一天和最后一天
            _, last_day = calendar.monthrange(current_year, current_month)
            
            month_start = datetime(current_year, current_month, 1)
            month_end = datetime(current_year, current_month, last_day, 23, 59, 59)
            
            # 如果月份超出了指定范围，则调整
            if month_start.date() < start_date:
                month_start = datetime.combine(start_date, datetime.min.time())
            
            if month_end.date() > end_date:
                month_end = datetime.combine(end_date, datetime.max.time())
            
            # 查询当月数据
            monthly_stats = db.session.query(
                func.count(Order.id),
                func.sum(Order.amount),
                func.count(Order.id).filter(Order.status.in_([2, 3])),
                func.sum(Order.amount).filter(Order.status.in_([2, 3]))
            ).filter(
                Order.created_at.between(month_start, month_end)
            ).first()
            
            result.append({
                'date': f"{current_year}-{current_month:02d}",
                'total_orders': monthly_stats[0] or 0,
                'total_amount': float(monthly_stats[1]) if monthly_stats[1] else 0,
                'paid_orders': monthly_stats[2] or 0,
                'paid_amount': float(monthly_stats[3]) if monthly_stats[3] else 0
            })
            
            # 移动到下一个月
            if current_month == 12:
                current_year += 1
                current_month = 1
            else:
                current_month += 1
        
        return result 