from flask_caching import Cache

# 创建缓存实例
cache = Cache(config={
    'CACHE_TYPE': 'simple',  # 使用简单的内存缓存
    'CACHE_DEFAULT_TIMEOUT': 300  # 默认缓存时间300秒
})

def init_cache(app):
    """初始化缓存配置"""
    cache.init_app(app)
    return cache 