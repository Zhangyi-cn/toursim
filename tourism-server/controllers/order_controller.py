from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Order, OrderItem, Ticket, Attraction
from app import db
from utils.response import success_response, error_response
from utils.auth import login_required

order_bp = Blueprint('order', __name__)


class OrderController:
    """订单控制器"""
    
    @staticmethod
    @order_bp.route('', methods=['POST'])
    @login_required
    def create_order():
        """
        创建订单
        ---
        tags:
          - 订单
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - attraction_id
                - ticket_id
                - quantity
                - visit_date
                - visitor_name
                - visitor_phone
              properties:
                attraction_id:
                  type: integer
                  description: 景点ID
                ticket_id:
                  type: integer
                  description: 门票ID
                quantity:
                  type: integer
                  description: 数量
                visit_date:
                  type: string
                  format: date
                  description: 游玩日期(YYYY-MM-DD)
                visitor_name:
                  type: string
                  description: 游客姓名
                visitor_phone:
                  type: string
                  description: 游客手机号
                visitor_id_card:
                  type: string
                  description: 游客身份证号
                remark:
                  type: string
                  description: 备注
        """
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(error_response("用户不存在", 404)), 404
        
        # 获取请求数据
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['attraction_id', 'ticket_id', 'quantity', 'visit_date', 'visitor_name', 'visitor_phone']
        error = validate_required_fields(data, required_fields)
        if error:
            return jsonify(error_response(error)), 400
        
        # 验证景点存在
        attraction_id = data.get('attraction_id')
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify(error_response("景点不存在")), 404
        
        # 验证门票存在
        ticket_id = data.get('ticket_id')
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify(error_response("门票不存在")), 404
        
        # 验证门票属于该景点
        if ticket.attraction_id != attraction_id:
            # 如果门票不属于该景点，尝试查找景点已有门票
            existing_ticket = Ticket.query.filter_by(attraction_id=attraction_id).first()
            
            if existing_ticket:
                # 如果景点已有门票，使用已有的
                ticket = existing_ticket
                ticket_id = existing_ticket.id
            else:
                # 如果景点没有门票，自动创建一个测试门票
                try:
                    new_ticket = Ticket(
                        attraction_id=attraction_id,
                        name=f"{attraction.name}门票",
                        description=f"{attraction.name}的标准门票",
                        price=100.00,
                        original_price=120.00,
                        type=1,  # 普通票
                        notice="仅供测试使用",
                        valid_period="当天有效",
                        status=1  # 上架
                    )
                    
                    db.session.add(new_ticket)
                    db.session.commit()
                    
                    ticket = new_ticket
                    ticket_id = new_ticket.id
                    
                    current_app.logger.info(f"为景点{attraction_id}自动创建了门票{ticket_id}")
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"自动创建门票失败: {str(e)}")
                    return jsonify(error_response(f"创建门票失败: {str(e)}")), 500
        
        # 验证数量
        quantity = data.get('quantity')
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify(error_response("数量必须为正整数")), 400
        
        # 验证游玩日期
        visit_date = data.get('visit_date')
        try:
            visit_datetime = datetime.strptime(visit_date, '%Y-%m-%d')
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # 不能选择过去的日期
            if visit_datetime < today:
                return jsonify(error_response("不能选择过去的日期")), 400
            
            # 不能选择超过3个月的日期
            if visit_datetime > today + timedelta(days=90):
                return jsonify(error_response("不能选择3个月以后的日期")), 400
        except ValueError:
            return jsonify(error_response("游玩日期格式不正确，应为YYYY-MM-DD")), 400
        
        # 生成订单号
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        # 计算订单金额
        total_amount = ticket.price * quantity
        
        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user.id,
            amount=total_amount,
            status=0,  # 待支付
            contact_name=data.get('visitor_name'),
            contact_phone=data.get('visitor_phone'),
            visit_date=visit_datetime,
            remark=data.get('remark', ''),
            created_at=datetime.now()
        )
        
        try:
            db.session.add(order)
            db.session.flush()  # 获取订单ID
            
            # 创建订单项
            order_item = OrderItem(
                order_id=order.id,
                ticket_id=ticket_id,
                attraction_id=attraction_id,
                ticket_name=ticket.name,
                attraction_name=attraction.name,
                price=ticket.price,
                quantity=quantity,
                subtotal=total_amount
            )
            
            db.session.add(order_item)
            db.session.commit()
            
            # 返回创建的订单信息
            order_dict = order.to_dict()
            order_dict['items'] = [item.to_dict() for item in order.items]
            
            return jsonify(success_response("订单创建成功", order_dict)), 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"订单创建失败: {str(e)}")
            return jsonify(error_response(f"订单创建失败: {str(e)}")), 500
    
    @staticmethod
    @order_bp.route('', methods=['GET'])
    @login_required
    def get_orders():
        """
        获取订单列表
        ---
        tags:
          - 订单
        parameters:
          - name: page
            in: query
            type: integer
            required: false
            default: 1
            description: 页码
          - name: per_page
            in: query
            type: integer
            required: false
            default: 10
            description: 每页数量
          - name: status
            in: query
            type: integer
            required: false
            description: 订单状态（0:待支付，1:已支付, 2:已完成，3:已取消）
        """
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(error_response("用户不存在", 404)), 404
        
        # 获取查询参数
        page, per_page = get_page_params()
        status = request.args.get('status', type=int)
        
        # 构建查询
        query = Order.query.filter_by(user_id=user.id)
        
        # 根据状态筛选
        if status is not None:
            query = query.filter_by(status=status)
        
        # 分页查询
        orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
        
        # 准备响应数据
        order_list = [order.to_dict() for order in orders.items]
        
        # 返回结果
        return jsonify(pagination_response(
            order_list,
            orders.total,
            page,
            per_page
        ))
    
    @staticmethod
    @order_bp.route('/<string:order_no>', methods=['GET'])
    @login_required
    def get_order_detail(order_no):
        """
        获取订单详情
        ---
        tags:
          - 订单
        parameters:
          - name: order_no
            in: path
            type: string
            required: true
            description: 订单编号
        """
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(error_response("用户不存在", 404)), 404
        
        # 查询订单
        order = Order.query.filter_by(order_no=order_no, user_id=user.id).first()
        if not order:
            return jsonify(error_response("订单不存在")), 404
        
        # 返回订单详情
        return jsonify(success_response("获取订单详情成功", order.to_dict()))
    
    @staticmethod
    @order_bp.route('/<string:order_no>/cancel', methods=['PUT'])
    @login_required
    def cancel_order(order_no):
        """
        取消订单
        ---
        tags:
          - 订单
        parameters:
          - name: order_no
            in: path
            type: string
            required: true
            description: 订单编号
        """
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(error_response("用户不存在", 404)), 404
        
        # 查询订单
        order = Order.query.filter_by(order_no=order_no, user_id=user.id).first()
        if not order:
            return jsonify(error_response("订单不存在")), 404
        
        # 验证订单状态
        if order.status != 0:
            return jsonify(error_response("只有待支付状态的订单可以取消")), 400
        
        # 修改订单状态
        try:
            order.status = 3  # 已取消
            order.updated_at = datetime.now()
            db.session.commit()
            
            return jsonify(success_response("订单取消成功"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"订单取消失败: {str(e)}")
            return jsonify(error_response(f"订单取消失败: {str(e)}")), 500
    
    @staticmethod
    @order_bp.route('/<string:order_no>/pay', methods=['POST'])
    @login_required
    def pay_order(order_no):
        """
        支付订单
        ---
        tags:
          - 订单
        parameters:
          - name: order_no
            in: path
            type: string
            required: true
            description: 订单编号
        """
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(error_response("用户不存在", 404)), 404
        
        # 查询订单
        order = Order.query.filter_by(order_no=order_no, user_id=user.id).first()
        if not order:
            return jsonify(error_response("订单不存在")), 404
        
        # 验证订单状态
        if order.status != 0:
            return jsonify(error_response("只有待支付状态的订单可以支付")), 400
        
        # 模拟支付
        try:
            # 修改订单状态
            order.status = 1  # 已支付
            order.paid_at = datetime.now()
            order.updated_at = datetime.now()
            # 生成随机支付流水号
            order.pay_no = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
            
            db.session.commit()
            
            # 返回支付结果
            return jsonify(success_response("订单支付成功", {
                "pay_no": order.pay_no,
                "paid_at": order.paid_at.strftime('%Y-%m-%d %H:%M:%S')
            }))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"订单支付失败: {str(e)}")
            return jsonify(error_response(f"订单支付失败: {str(e)}")), 500
    
    @staticmethod
    def generate_order_no():
        """生成订单号"""
        now = datetime.now()
        return now.strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
    
    @staticmethod
    def generate_pay_no():
        """生成支付流水号"""
        return str(uuid.uuid4()).replace('-', '')[:16].upper() 