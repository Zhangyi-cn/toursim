def success_response(message="操作成功", data=None, code=200):
    """
    统一成功响应格式
    :param message: 成功消息
    :param data: 返回数据
    :param code: 状态码
    :return: 响应字典
    """
    response = {
        "code": code,
        "message": message,
        "success": True
    }
    
    if data is not None:
        response["data"] = data
        
    return response


def error_response(message="操作失败", code=400, errors=None):
    """
    统一错误响应格式
    :param message: 错误消息
    :param code: 状态码
    :param errors: 详细错误信息
    :return: 响应字典
    """
    response = {
        "code": code,
        "message": message,
        "success": False
    }
    
    if errors:
        response["errors"] = errors
        
    return response


def pagination_response(items=None, total=None, page=None, per_page=None, message="获取数据成功", extras=None, data=None):
    """
    统一分页响应格式
    :param items: 分页数据列表
    :param total: 总记录数
    :param page: 当前页码
    :param per_page: 每页记录数
    :param message: 成功消息
    :param extras: 额外数据
    :param data: 直接提供完整的数据对象(优先级高于其他参数)
    :return: 分页响应字典
    """
    if data is not None:
        # 如果直接提供了data，则使用它
        return success_response(message, data)
    
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    response_data = {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
    }
    
    # 添加额外数据
    if extras:
        response_data.update(extras)
    
    return success_response(message, response_data) 