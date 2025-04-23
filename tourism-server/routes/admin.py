from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.response import success_response, error_response
from utils.auth import admin_required
from controllers.admin.admin_controller import AdminController
from controllers.admin.attraction_admin_controller import AttractionAdminController
from controllers.admin.user_admin_controller import UserAdminController
from controllers.admin.system_admin_controller import SystemAdminController
from controllers.admin.guide_admin_controller import GuideAdminController
from controllers.admin.note_admin_controller import NoteAdminController
from controllers.admin.tag_admin_controller import TagAdminController
from controllers.admin.comment_admin_controller import CommentAdminController
from controllers.admin.order_admin_controller import OrderAdminController
from controllers.admin.ticket_admin_controller import TicketAdminController
from controllers.admin.user_controller import admin_user_bp
from controllers.admin.order_controller import admin_order_bp
from controllers.admin.comment_controller import admin_comment_bp
from controllers.admin.stats_controller import admin_stats_bp
from controllers.admin.banner_admin_controller import BannerAdminController

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__)

# 管理员登录相关路由
admin_bp.route('/login', methods=['POST'])(AdminController.login)
admin_bp.route('/logout', methods=['POST'])(jwt_required()(AdminController.logout))
admin_bp.route('/profile', methods=['GET'])(admin_required()(AdminController.get_profile))
admin_bp.route('/password', methods=['PUT'])(admin_required()(AdminController.change_password))
admin_bp.route('/dashboard', methods=['GET'])(admin_required()(AdminController.get_dashboard))

# 用户管理路由
admin_bp.route('/users', methods=['GET'])(admin_required()(UserAdminController.get_users))
admin_bp.route('/users', methods=['POST'])(admin_required()(UserAdminController.create_user))
admin_bp.route('/users/<int:user_id>', methods=['GET'])(admin_required()(UserAdminController.get_user))
admin_bp.route('/users/<int:user_id>', methods=['PUT'])(admin_required()(UserAdminController.update_user))
admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])(admin_required()(UserAdminController.update_user_status))
admin_bp.route('/users/<int:user_id>/reset_password', methods=['POST'])(admin_required()(UserAdminController.reset_password))

# 景点管理路由
admin_bp.route('/attractions', methods=['GET'])(admin_required()(AttractionAdminController.get_attractions))
admin_bp.route('/attractions', methods=['POST'])(admin_required()(AttractionAdminController.create_attraction))
admin_bp.route('/attractions/<int:attraction_id>', methods=['GET'])(admin_required()(AttractionAdminController.get_attraction))
admin_bp.route('/attractions/<int:attraction_id>', methods=['PUT'])(admin_required()(AttractionAdminController.update_attraction))
admin_bp.route('/attractions/<int:attraction_id>', methods=['DELETE'])(admin_required()(AttractionAdminController.delete_attraction))
admin_bp.route('/attractions/upload/image', methods=['POST'])(admin_required()(AttractionAdminController.upload_image))
admin_bp.route('/attractions/categories', methods=['GET'], endpoint='attraction_categories')(admin_required()(AttractionAdminController.get_categories))
admin_bp.route('/attractions/categories', methods=['POST'], endpoint='attraction_create_category')(admin_required()(AttractionAdminController.create_category))
admin_bp.route('/attractions/categories/<int:category_id>', methods=['PUT'], endpoint='attraction_update_category')(admin_required()(AttractionAdminController.update_category))
admin_bp.route('/attractions/categories/<int:category_id>', methods=['DELETE'], endpoint='attraction_delete_category')(admin_required()(AttractionAdminController.delete_category))

# 旅游攻略管理路由
admin_bp.route('/guides', methods=['GET'])(admin_required()(GuideAdminController.get_guides))
admin_bp.route('/guides', methods=['POST'])(admin_required()(GuideAdminController.create_guide))
admin_bp.route('/guides/<int:guide_id>', methods=['GET'])(admin_required()(GuideAdminController.get_guide))
admin_bp.route('/guides/<int:guide_id>', methods=['PUT'])(admin_required()(GuideAdminController.update_guide))
admin_bp.route('/guides/<int:guide_id>', methods=['DELETE'])(admin_required()(GuideAdminController.delete_guide))

# 攻略分类管理路由
admin_bp.route('/guides/categories', methods=['GET'], endpoint='guide_categories')(admin_required()(GuideAdminController.get_categories))
admin_bp.route('/guides/categories', methods=['POST'], endpoint='guide_create_category')(admin_required()(GuideAdminController.create_category))
admin_bp.route('/guides/categories/<int:category_id>', methods=['PUT'], endpoint='guide_update_category')(admin_required()(GuideAdminController.update_category))
admin_bp.route('/guides/categories/<int:category_id>', methods=['DELETE'], endpoint='guide_delete_category')(admin_required()(GuideAdminController.delete_category))

# 游记管理路由
admin_bp.route('/notes', methods=['GET'])(admin_required()(NoteAdminController.get_notes))
admin_bp.route('/notes/<int:note_id>', methods=['GET'])(admin_required()(NoteAdminController.get_note))
admin_bp.route('/notes/<int:note_id>/status', methods=['PUT'])(admin_required()(NoteAdminController.update_note_status))
admin_bp.route('/notes/<int:note_id>', methods=['DELETE'])(admin_required()(NoteAdminController.delete_note))
admin_bp.route('/notes/<int:note_id>/feature', methods=['PUT'])(admin_required()(NoteAdminController.feature_note))
admin_bp.route('/notes/<int:note_id>/unfeature', methods=['PUT'])(admin_required()(NoteAdminController.unfeature_note))

# 评论管理路由
admin_bp.route('/comments', methods=['GET'])(admin_required()(CommentAdminController.get_comments))
admin_bp.route('/comments/<int:comment_id>', methods=['GET'])(admin_required()(CommentAdminController.get_comment))
admin_bp.route('/comments/<int:comment_id>/status', methods=['PUT'])(admin_required()(CommentAdminController.update_comment_status))
admin_bp.route('/comments/<int:comment_id>', methods=['DELETE'])(admin_required()(CommentAdminController.delete_comment))
admin_bp.route('/comments/batch/status', methods=['PUT'])(admin_required()(CommentAdminController.batch_update_comment_status))
admin_bp.route('/comments/batch/delete', methods=['POST'])(admin_required()(CommentAdminController.batch_delete_comments))

# 标签管理路由
admin_bp.route('/tags', methods=['GET'])(admin_required()(TagAdminController.get_tags))
admin_bp.route('/tags', methods=['POST'])(admin_required()(TagAdminController.create_tag))
admin_bp.route('/tags/<int:tag_id>', methods=['PUT'])(admin_required()(TagAdminController.update_tag))
admin_bp.route('/tags/<int:tag_id>', methods=['DELETE'])(admin_required()(TagAdminController.delete_tag))
admin_bp.route('/tags/content', methods=['GET'])(admin_required()(TagAdminController.get_content_tags))
admin_bp.route('/tags/content', methods=['POST'])(admin_required()(TagAdminController.add_content_tag))
admin_bp.route('/tags/content/<int:content_tag_id>', methods=['DELETE'])(admin_required()(TagAdminController.delete_content_tag))

# 门票管理路由
admin_bp.route('/tickets', methods=['GET'])(admin_required()(TicketAdminController.get_tickets))
admin_bp.route('/tickets', methods=['POST'])(admin_required()(TicketAdminController.create_ticket))
admin_bp.route('/tickets/<int:ticket_id>', methods=['GET'])(admin_required()(TicketAdminController.get_ticket))
admin_bp.route('/tickets/<int:ticket_id>', methods=['PUT'])(admin_required()(TicketAdminController.update_ticket))
admin_bp.route('/tickets/<int:ticket_id>', methods=['DELETE'])(admin_required()(TicketAdminController.delete_ticket))
admin_bp.route('/tickets/<int:ticket_id>/status', methods=['PUT'])(admin_required()(TicketAdminController.update_ticket_status))

# 订单管理路由
admin_bp.route('/orders', methods=['GET'])(admin_required()(OrderAdminController.get_orders))
admin_bp.route('/orders/<int:order_id>', methods=['GET'])(admin_required()(OrderAdminController.get_order))
admin_bp.route('/orders/<int:order_id>/refund', methods=['POST'])(admin_required()(OrderAdminController.refund_order))
admin_bp.route('/orders/statistics', methods=['GET'])(admin_required()(OrderAdminController.get_statistics))

# 轮播图管理路由
admin_bp.route('/banners', methods=['GET'])(admin_required()(BannerAdminController.get_banners))
admin_bp.route('/banners', methods=['POST'])(admin_required()(BannerAdminController.create_banner))
admin_bp.route('/banners/<int:banner_id>', methods=['PUT'])(admin_required()(BannerAdminController.update_banner))
admin_bp.route('/banners/<int:banner_id>', methods=['DELETE'])(admin_required()(BannerAdminController.delete_banner))
admin_bp.route('/banners/<int:banner_id>/status', methods=['PUT'])(admin_required()(BannerAdminController.update_banner_status))
admin_bp.route('/banners/upload', methods=['POST'])(admin_required()(SystemAdminController.upload_banner))

# 注册订单控制器蓝图
admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')
admin_bp.register_blueprint(admin_order_bp, url_prefix='/orders')

# 注册后台评论管理
admin_bp.register_blueprint(admin_comment_bp, url_prefix='/comments')

# 注册后台统计
admin_bp.register_blueprint(admin_stats_bp, url_prefix='/stats')

# 通用错误处理
@admin_bp.errorhandler(404)
def handle_404(e):
    return jsonify(error_response("接口不存在", 404)), 404

@admin_bp.errorhandler(500)
def handle_500(e):
    return jsonify(error_response("服务器内部错误", 500)), 500 