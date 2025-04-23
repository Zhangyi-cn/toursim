import re
from datetime import datetime, date
from flask import request


def is_empty(value):
    """
    检查值是否为空
    :param value: 待检查的值
    :return: 是否为空
    """
    if value is None:
        return True
    
    if isinstance(value, str) and value.strip() == '':
        return True
    
    if isinstance(value, (list, dict, tuple)) and len(value) == 0:
        return True
    
    return False


def is_valid_email(email):
    """
    验证邮箱格式
    :param email: 邮箱
    :return: 是否有效
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone):
    """
    验证手机号格式（中国大陆手机号）
    :param phone: 手机号
    :return: 是否有效
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def is_valid_password(password):
    """
    验证密码强度
    :param password: 密码
    :return: 是否有效
    """
    # 至少6位密码
    return password and len(password) >= 6


def is_valid_username(username):
    """
    验证用户名
    :param username: 用户名
    :return: 是否有效
    """
    # 4-20位，字母、数字、下划线
    pattern = r'^[a-zA-Z0-9_]{4,20}$'
    return bool(re.match(pattern, username))


def is_valid_date(date_str, format='%Y-%m-%d'):
    """
    验证日期格式
    :param date_str: 日期字符串
    :param format: 日期格式
    :return: 是否有效
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except (ValueError, TypeError):
        return False


def validate_required(data, fields):
    """
    验证必填字段
    :param data: 待验证的数据字典
    :param fields: 必填字段列表
    :return: (是否通过验证, 错误信息)
    """
    errors = {}
    
    for field in fields:
        if field not in data or is_empty(data[field]):
            errors[field] = f"{field} 不能为空"
    
    return len(errors) == 0, errors


def validate_required_fields(data, fields):
    """
    验证必填字段，返回错误信息
    :param data: 待验证的数据字典
    :param fields: 必填字段列表
    :return: 错误信息，如果验证通过则返回None
    """
    missing_fields = []
    
    for field in fields:
        if field not in data or is_empty(data[field]):
            missing_fields.append(field)
    
    if missing_fields:
        return f"缺少必填字段: {', '.join(missing_fields)}"
    
    return None


def get_page_params(default_page=1, default_size=20, max_size=100):
    """
    获取分页参数
    :param default_page: 默认页码
    :param default_size: 默认每页记录数
    :param max_size: 最大每页记录数
    :return: (page, per_page)
    """
    try:
        page = int(request.args.get('page', default_page))
        if page < 1:
            page = default_page
    except (ValueError, TypeError):
        page = default_page
    
    try:
        per_page = int(request.args.get('per_page', default_size))
        if per_page < 1:
            per_page = default_size
        elif per_page > max_size:
            per_page = max_size
    except (ValueError, TypeError):
        per_page = default_size
    
    return page, per_page


def get_date_range_params(start_param='start_date', end_param='end_date', format='%Y-%m-%d'):
    """
    获取日期范围参数
    :param start_param: 开始日期参数名
    :param end_param: 结束日期参数名
    :param format: 日期格式
    :return: (start_date, end_date) 如果未提供则为None
    """
    start_str = request.args.get(start_param)
    end_str = request.args.get(end_param)
    
    start_date = None
    end_date = None
    
    if start_str and is_valid_date(start_str, format):
        start_date = datetime.strptime(start_str, format).date()
    
    if end_str and is_valid_date(end_str, format):
        end_date = datetime.strptime(end_str, format).date()
    
    return start_date, end_date


def convert_to_date(date_str, format='%Y-%m-%d'):
    """
    转换字符串为日期对象
    :param date_str: 日期字符串
    :param format: 日期格式
    :return: 日期对象，转换失败返回None
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, format).date()
    except (ValueError, TypeError):
        return None


def validate_params(data, validations):
    """
    验证多种类型的参数
    
    :param data: 待验证的数据字典
    :param validations: 验证规则字典，格式如下：
        {
            'field_name': {
                'required': True|False,
                'type': 'string|int|float|email|phone|date|...',
                'min': 最小值(数字)/最小长度(字符串),
                'max': 最大值(数字)/最大长度(字符串),
                'format': 日期格式(如果type为date),
                'custom': 自定义验证函数,
                'message': 自定义错误信息
            }
        }
    :return: (是否通过验证, 错误信息)
    """
    errors = {}
    
    for field, rules in validations.items():
        # 检查必填
        if rules.get('required', False) and (field not in data or is_empty(data[field])):
            errors[field] = rules.get('message', f"{field} 不能为空")
            continue
        
        # 如果字段不存在且非必填，跳过后续验证
        if field not in data or is_empty(data[field]):
            continue
        
        value = data[field]
        
        # 类型验证
        if 'type' in rules:
            type_name = rules['type']
            
            # 字符串类型
            if type_name == 'string' and not isinstance(value, str):
                errors[field] = rules.get('message', f"{field} 必须是字符串")
                continue
            
            # 整数类型
            elif type_name == 'int':
                try:
                    value = int(value)
                    data[field] = value  # 更新为转换后的值
                except (ValueError, TypeError):
                    errors[field] = rules.get('message', f"{field} 必须是整数")
                    continue
            
            # 浮点数类型
            elif type_name == 'float':
                try:
                    value = float(value)
                    data[field] = value  # 更新为转换后的值
                except (ValueError, TypeError):
                    errors[field] = rules.get('message', f"{field} 必须是数字")
                    continue
            
            # 邮箱类型
            elif type_name == 'email' and not is_valid_email(value):
                errors[field] = rules.get('message', f"{field} 不是有效的邮箱格式")
                continue
            
            # 手机号类型
            elif type_name == 'phone' and not is_valid_phone(value):
                errors[field] = rules.get('message', f"{field} 不是有效的手机号格式")
                continue
            
            # 日期类型
            elif type_name == 'date':
                format_str = rules.get('format', '%Y-%m-%d')
                if not is_valid_date(value, format_str):
                    errors[field] = rules.get('message', f"{field} 不是有效的日期格式")
                    continue
                else:
                    # 转换为日期对象
                    data[field] = convert_to_date(value, format_str)
        
        # 最小值/长度验证
        if 'min' in rules:
            min_val = rules['min']
            
            if isinstance(value, int) or isinstance(value, float):
                if value < min_val:
                    errors[field] = rules.get('message', f"{field} 不能小于 {min_val}")
                    continue
            elif isinstance(value, str):
                if len(value) < min_val:
                    errors[field] = rules.get('message', f"{field} 长度不能小于 {min_val}个字符")
                    continue
        
        # 最大值/长度验证
        if 'max' in rules:
            max_val = rules['max']
            
            if isinstance(value, int) or isinstance(value, float):
                if value > max_val:
                    errors[field] = rules.get('message', f"{field} 不能大于 {max_val}")
                    continue
            elif isinstance(value, str):
                if len(value) > max_val:
                    errors[field] = rules.get('message', f"{field} 长度不能超过 {max_val}个字符")
                    continue
        
        # 自定义验证
        if 'custom' in rules and callable(rules['custom']):
            custom_func = rules['custom']
            is_valid, error_msg = custom_func(value)
            
            if not is_valid:
                errors[field] = rules.get('message', error_msg)
                continue
    
    return len(errors) == 0, errors 


def is_valid_content(content, min_length=1, max_length=5000):
    """
    验证内容是否有效
    :param content: 内容字符串
    :param min_length: 最小长度
    :param max_length: 最大长度
    :return: 是否有效
    """
    if not content or not isinstance(content, str):
        return False
    
    content_length = len(content.strip())
    return min_length <= content_length <= max_length 