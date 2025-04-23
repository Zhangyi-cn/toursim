"""
支付相关工具函数
用于处理订单支付、查询和退款操作
"""
import random
import time
from datetime import datetime
import uuid
from flask import current_app


def create_payment(order_no, amount, pay_method, description="旅游景点门票"):
    """
    创建支付订单
    
    Args:
        order_no (str): 订单号
        amount (float): 支付金额
        pay_method (str): 支付方式 'alipay', 'wechat', 'balance'
        description (str): 商品描述
        
    Returns:
        dict: 支付结果
    """
    # 模拟支付
    current_app.logger.info(f"创建支付订单: 订单号 {order_no}, 金额 {amount}, 支付方式 {pay_method}")
    
    # 生成支付流水号
    pay_no = str(uuid.uuid4()).replace('-', '')[:16].upper()
    
    # 返回支付结果
    return {
        'success': True,
        'pay_no': pay_no,
        'order_no': order_no,
        'amount': amount,
        'pay_method': pay_method,
        'pay_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'SUCCESS'
    }


def query_payment(order_no=None, pay_no=None):
    """
    查询支付状态
    
    Args:
        order_no (str, optional): 订单号
        pay_no (str, optional): 支付流水号
        
    Returns:
        dict: 支付状态信息
    """
    if not order_no and not pay_no:
        raise ValueError("订单号和支付流水号不能同时为空")
    
    # 模拟查询支付状态
    current_app.logger.info(f"查询支付状态: 订单号 {order_no}, 支付流水号 {pay_no}")
    
    # 随机模拟成功或处理中状态
    status = random.choice(['SUCCESS', 'PROCESSING'])
    
    # 返回查询结果
    return {
        'success': True,
        'order_no': order_no,
        'pay_no': pay_no or str(uuid.uuid4()).replace('-', '')[:16].upper(),
        'status': status,
        'pay_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': '支付成功' if status == 'SUCCESS' else '支付处理中'
    }


def refund_payment(order_no, refund_amount, refund_reason="用户取消订单"):
    """
    申请退款
    
    Args:
        order_no (str): 订单号
        refund_amount (float): 退款金额
        refund_reason (str): 退款原因
        
    Returns:
        dict: 退款结果
    """
    # 模拟退款
    current_app.logger.info(f"申请退款: 订单号 {order_no}, 退款金额 {refund_amount}, 原因 {refund_reason}")
    
    # 生成退款流水号
    refund_no = 'R' + str(uuid.uuid4()).replace('-', '')[:15].upper()
    
    # 返回退款结果
    return {
        'success': True,
        'order_no': order_no,
        'refund_no': refund_no,
        'refund_amount': refund_amount,
        'refund_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'SUCCESS',
        'message': '退款成功'
    } 