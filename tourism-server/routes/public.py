from flask import Blueprint, jsonify, send_from_directory, current_app
from utils.response import success_response, error_response
from controllers.public_controller import get_banners

# 创建公共蓝图
public_bp = Blueprint('public', __name__)

# 静态文件服务
@public_bp.route('/uploads/<path:filename>', methods=['GET'])
def get_uploaded_file(filename):
    """获取上传的文件"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# 轮播图相关路由
public_bp.route('/banners', methods=['GET'])(get_banners)

# 健康检查
@public_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify(success_response("服务正常"))

# 错误处理
@public_bp.errorhandler(404)
def handle_404(e):
    return jsonify(error_response("接口不存在", 404)), 404

@public_bp.errorhandler(500)
def handle_500(e):
    return jsonify(error_response("服务器内部错误", 500)), 500 