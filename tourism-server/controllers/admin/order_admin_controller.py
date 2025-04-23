from datetime import datetime
from flask import request, jsonify
from extensions import db
from models.order import Order
from utils.response import success_response, error_response
from utils.pagination import paginate


class OrderAdminController:
    """订单管理控制器"""

    @staticmethod
    def get_orders():
        """获取订单列表"""
        try:
            # 获取查询参数
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            keyword = request.args.get('keyword', '')
            status = request.args.get('status', None)
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)

            # 构建查询
            query = Order.query

            # 按状态筛选
            if status is not None:
                query = query.filter(Order.status == int(status))

            # 按日期范围筛选
            if start_date:
                query = query.filter(Order.created_at >= start_date)
            if end_date:
                query = query.filter(Order.created_at <= end_date)

            # 按关键词搜索（订单号或用户名）
            if keyword:
                query = query.filter(
                    db.or_(
                        Order.order_no.like(f'%{keyword}%'),
                        Order.user_name.like(f'%{keyword}%')
                    )
                )

            # 按创建时间倒序排序
            query = query.order_by(Order.created_at.desc())

            # 分页
            pagination = paginate(query, page, per_page)
            
            # 转换为字典
            orders = [order.to_dict() for order in pagination.items]
            
            return success_response(data={
                'items': orders,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            })
            
        except Exception as e:
            return error_response(str(e))

    @staticmethod
    def get_order(order_id):
        """获取订单详情"""
        try:
            order = Order.query.get(order_id)
            if not order:
                return error_response('订单不存在')
            
            return success_response(data=order.to_dict())
            
        except Exception as e:
            return error_response(str(e))

    @staticmethod
    def refund_order(order_id):
        """退款处理"""
        try:
            # 获取参数
            reason = request.json.get('reason')
            if not reason:
                return error_response('请提供退款原因')

            # 查询订单
            order = Order.query.get(order_id)
            if not order:
                return error_response('订单不存在')

            # 检查订单状态
            if order.status not in [1, 2]:  # 1=待使用，2=已使用
                return error_response('当前订单状态不支持退款')

            # 更新订单状态为已退款
            order.status = 4  # 4=已退款
            order.refund_reason = reason
            order.refund_time = datetime.now()
            db.session.commit()

            return success_response(data=order.to_dict())

        except Exception as e:
            db.session.rollback()
            return error_response(str(e))

    @staticmethod
    def get_statistics():
        """获取订单统计数据"""
        try:
            # 获取查询参数
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)

            # 构建查询
            query = Order.query

            # 按日期范围筛选
            if start_date:
                query = query.filter(Order.created_at >= start_date)
            if end_date:
                query = query.filter(Order.created_at <= end_date)

            # 统计各状态订单数量
            status_stats = db.session.query(
                Order.status,
                db.func.count(Order.id).label('count'),
                db.func.sum(Order.amount).label('amount')
            ).group_by(Order.status).all()

            # 转换为字典
            stats = {
                'total_orders': query.count(),
                'total_amount': float(query.with_entities(db.func.sum(Order.amount)).scalar() or 0),
                'status_stats': [{
                    'status': status,
                    'count': count,
                    'amount': float(amount or 0)
                } for status, count, amount in status_stats]
            }

            return success_response(data=stats)

        except Exception as e:
            return error_response(str(e)) 