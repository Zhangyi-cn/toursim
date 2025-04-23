from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from extensions import db, migrate
from config import Config
from utils.cache import init_cache
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 初始化CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 86400  # 预检请求的结果可以缓存24小时
        }
    })
    
    # 添加OPTIONS请求的全局处理，确保每个路由都能处理OPTIONS请求
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        # 这个函数会处理所有路径的OPTIONS请求
        response = app.make_default_options_response()
        return response
        
    # 确保跨域请求得到正确响应
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
        return response
    
    db.init_app(app)
    migrate.init_app(app, db)
    init_cache(app)  # 初始化缓存
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 注册蓝图
    from routes.api import api_bp
    from routes.admin import admin_bp
    from routes.public import public_bp
    from controllers.system_controller import system_bp
    from controllers import (
        auth_bp, user_bp, attraction_bp, guide_bp,
        note_bp, comment_bp, upload_bp, category_bp
    )
    
    # 注册基础蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    # 将admin_bp直接注册到/api/admin路径下，不再使用代理
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # 继续注册其他蓝图
    app.register_blueprint(public_bp, url_prefix='/public')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    
    # 注册功能蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(attraction_bp, url_prefix='/api/attractions')
    app.register_blueprint(guide_bp, url_prefix='/api/guides')
    app.register_blueprint(note_bp, url_prefix='/api/notes')
    app.register_blueprint(comment_bp, url_prefix='/api/comments')
    app.register_blueprint(upload_bp)  # 已在蓝图中定义了url_prefix
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    
    # 应用ProxyFix中间件
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
