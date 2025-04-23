from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

# 数据库初始化函数
def init_db(app):
    """初始化数据库"""
    with app.app_context():
        db.create_all() 