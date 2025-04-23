from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.response import success_response, error_response
from controllers.attraction_controller import attraction_bp
from controllers.travel_guide_controller import travel_guide_bp
from controllers.auth_controller import auth_bp
from controllers.category_controller import category_bp
from controllers.like_controller import like_bp
from controllers.collection_controller import collection_bp
from controllers.recommendation_controller import recommendation_bp
from controllers.user_controller import user_bp

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 注册子蓝图
api_bp.register_blueprint(attraction_bp, url_prefix='/attractions')
api_bp.register_blueprint(travel_guide_bp, url_prefix='/guides')
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(category_bp, url_prefix='/categories')
api_bp.register_blueprint(like_bp, url_prefix='/likes')
api_bp.register_blueprint(collection_bp, url_prefix='/collections')
api_bp.register_blueprint(recommendation_bp, url_prefix='/recommendations')
api_bp.register_blueprint(user_bp, url_prefix='/user')

# API状态检查
@api_bp.route('/status', methods=['GET'])
def api_status():
    return jsonify(success_response("API服务正常运行"))

# 错误处理
@api_bp.errorhandler(404)
def handle_404(e):
    return jsonify(error_response("接口不存在", 404)), 404

@api_bp.errorhandler(500)
def handle_500(e):
    return jsonify(error_response("服务器内部错误", 500)), 500 