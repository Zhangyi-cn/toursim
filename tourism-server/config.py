import os


class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传文件大小限制为16MB

    # 数据库配置 zaajy571
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://root:zaajy571@localhost/tourism'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 内存缓存配置
    CACHE_TYPE = 'SimpleCache'  # 使用Python字典作为缓存存储
    CACHE_DEFAULT_TIMEOUT = 300  # 默认缓存过期时间(秒)
    CACHE_THRESHOLD = 1000  # SimpleCache最大项目数

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24小时token有效期

    # CORS配置
    CORS_ORIGINS = '*'


class DevelopmentConfig(Config):
    DEBUG = True
    # 可以添加开发环境特定配置


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    # 生产环境特定配置
    DEBUG = False

    # 连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 