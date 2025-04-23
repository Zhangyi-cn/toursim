from flask import request
from collections import OrderedDict


class Pagination:
    """
    分页类，用于保存分页信息
    """
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = self.compute_pages()
        self.has_prev = page > 1
        self.has_next = page < self.pages
        
    def compute_pages(self):
        """计算总页数"""
        if self.per_page == 0:
            return 0
        return max(1, (self.total + self.per_page - 1) // self.per_page)
    
    def prev_page(self):
        """获取上一页页码"""
        if not self.has_prev:
            return None
        return self.page - 1
    
    def next_page(self):
        """获取下一页页码"""
        if not self.has_next:
            return None
        return self.page + 1
    
    def to_dict(self):
        """转换为字典"""
        return {
            'total': self.total,
            'pages': self.pages,
            'page': self.page,
            'per_page': self.per_page,
            'has_prev': self.has_prev,
            'has_next': self.has_next,
            'prev_page': self.prev_page(),
            'next_page': self.next_page()
        }


def paginate_query(query, page=None, per_page=None):
    """
    对查询结果进行分页
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码(从1开始)
        per_page: 每页记录数
    
    Returns:
        Pagination: 分页对象
    """
    if page is None:
        page = request.args.get('page', 1, type=int)
    if per_page is None:
        per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # 确保页码大于0
    page = max(1, page)
    # 确保每页记录数大于0
    per_page = max(1, per_page)
    
    try:
        # 计算总记录数
        total = query.count()
        
        # 应用分页
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        
        # 返回分页对象
        return Pagination(items, page, per_page, total)
    except Exception as e:
        # 处理查询失败的情况
        from flask import current_app
        current_app.logger.error(f"分页查询失败: {str(e)}")
        return Pagination([], page, per_page, 0)

# 添加别名
paginate = paginate_query 