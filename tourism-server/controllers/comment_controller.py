from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Comment, Attraction, TravelNote
from models.user import User
from app import db
from utils.response import success_response, error_response
from utils.auth import login_required
from utils.validator import get_page_params
from utils.pagination import paginate_query

comment_bp = Blueprint('comment', __name__)


class CommentController:
    """评论控制器"""
    
    @staticmethod
    @comment_bp.route('/<string:target_type>/<int:target_id>', methods=['POST'])
    @jwt_required()
    def add_comment(target_type, target_id):
        """
        添加评论
        ---
        tags:
          - 评论
        parameters:
          - name: target_type
            in: path
            required: true
            type: string
            enum: [attraction, guide, note]
            description: 目标类型
          - name: target_id
            in: path
            required: true
            type: integer
            description: 目标ID
          - name: body
            in: body
            required: true
            schema:
              required:
                - content
              properties:
                content:
                  type: string
                  description: 评论内容
                parent_id:
                  type: integer
                  description: 父评论ID(回复评论时使用)
                images:
                  type: array
                  items:
                    type: string
                  description: 图片地址列表
        """
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证参数
        content = data.get('content')
        parent_id = data.get('parent_id')
        images = data.get('images', [])
        
        if not content or not content.strip():
            return jsonify(error_response("评论内容不能为空")), 400
        
        # 检查目标是否存在
        target = None
        if target_type == 'attraction':
            target = Attraction.query.get(target_id)
        elif target_type == 'guide':
            target = TravelGuide.query.get(target_id)
        elif target_type == 'note':
            target = TravelNote.query.get(target_id)
        else:
            return jsonify(error_response(f"不支持的目标类型: {target_type}")), 400
        
        if not target:
            return jsonify(error_response("目标不存在")), 404
        
        # 检查父评论是否存在
        if parent_id:
            parent_comment = Comment.query.get(parent_id)
            if not parent_comment:
                return jsonify(error_response("父评论不存在")), 404
            
            # 验证父评论是否属于同一目标
            if parent_comment.content_type != target_type or parent_comment.content_id != target_id:
                return jsonify(error_response("父评论不属于该目标")), 400
        
        # 创建评论
        try:
            # 创建评论记录
            comment = Comment(
                user_id=user_id,
                content_type=target_type,
                content_id=target_id,
                content=content,
                parent_id=parent_id,
                images=images
            )
            db.session.add(comment)
            
            # 更新目标评论数
            if hasattr(target, 'comments'):
                target.comments = target.comments + 1
            
            db.session.commit()
            
            # 返回创建后的评论
            return jsonify(success_response("添加评论成功", comment.to_dict(with_user=True)))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"添加评论失败: {str(e)}")), 500
    
    @staticmethod
    @comment_bp.route('/<int:comment_id>', methods=['DELETE'])
    @jwt_required()
    def delete_comment(comment_id):
        """
        删除评论
        ---
        tags:
          - 评论
        parameters:
          - name: comment_id
            in: path
            required: true
            type: integer
            description: 评论ID
        """
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify(error_response("用户不存在")), 404
        
        # 查询评论
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify(error_response("评论不存在")), 404
        
        # 添加调试输出
        print(f"\n===== 删除评论调试 =====")
        print(f"评论ID: {comment_id}")
        print(f"当前用户ID: {user_id}, 类型: {type(user_id)}")
        print(f"评论所有者ID: {comment.user_id}, 类型: {type(comment.user_id)}")
        print(f"当前用户是否管理员: {getattr(current_user, 'is_admin', False)}")
        
        # 尝试安全类型转换进行比较
        try:
            user_id_int = int(user_id)
            comment_user_id_int = int(comment.user_id)
            print(f"转换后ID匹配检查: {comment_user_id_int == user_id_int}")
            is_owner = comment_user_id_int == user_id_int
        except (ValueError, TypeError):
            print("ID类型转换失败，使用原始值比较")
            is_owner = comment.user_id == user_id
        
        # 验证权限
        if not is_owner and not getattr(current_user, 'is_admin', False):
            print("权限检查失败，拒绝删除评论")
            return jsonify(error_response("无权删除该评论")), 403
        
        try:
            # 获取目标对象，用于更新评论计数
            target = None
            if comment.content_type == 'attraction':
                target = Attraction.query.get(comment.content_id)
            elif comment.content_type == 'guide':
                target = TravelGuide.query.get(comment.content_id)
            elif comment.content_type == 'note':
                target = TravelNote.query.get(comment.content_id)
            
            # 递归删除所有子评论
            child_comments = Comment.query.filter_by(parent_id=comment_id).all()
            child_count = len(child_comments)
            
            for child in child_comments:
                db.session.delete(child)
            
            # 删除当前评论
            db.session.delete(comment)
            
            # 更新目标评论数
            if target and hasattr(target, 'comments'):
                target.comments = max(0, target.comments - (1 + child_count))
            
            db.session.commit()
            
            return jsonify(success_response("删除评论成功"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"删除评论失败: {str(e)}")), 500
    
    @staticmethod
    @comment_bp.route('/<string:target_type>/<int:target_id>', methods=['GET'])
    def get_comments(target_type, target_id):
        """获取评论列表
        
        Args:
            target_type: 目标类型(attraction, guide, note)
            target_id: 目标ID
            
        Returns:
            评论列表
        """
        try:
            # 支持两种参数格式：直接参数和params[param]格式
            params = request.args.to_dict()
            
            # 获取分页参数
            page_param = params.get('page', '1')
            per_page_param = params.get('per_page', '10')
            parent_id_param = params.get('parent_id')
            
            # 检查是否使用params[param]格式
            if 'params[page]' in params:
                page_param = params.get('params[page]', '1')
            if 'params[per_page]' in params:
                per_page_param = params.get('params[per_page]', '10')
            if 'params[parent_id]' in params:
                parent_id_param = params.get('params[parent_id]')
            
            # 转换为整数
            try:
                page = int(page_param)
                per_page = int(per_page_param)
                parent_id = int(parent_id_param) if parent_id_param else None
            except (ValueError, TypeError):
                page = 1
                per_page = 10
                parent_id = None
            
            # 打印调试信息
            print(f"\n===== 评论列表API调试 =====")
            print(f"类型: {target_type}, ID: {target_id}, 页码: {page}, 每页: {per_page}, 父ID: {parent_id}")
            print(f"原始参数: {params}")

            # 构建查询
            query = Comment.query.filter(
                Comment.content_id == target_id,
                Comment.content_type == target_type
            )

            # 父评论ID过滤
            if parent_id is not None:
                if parent_id == 0:  # 前端传0表示获取顶级评论
                    query = query.filter(Comment.parent_id.is_(None))
                    print("查询顶级评论")
                else:
                    query = query.filter(Comment.parent_id == parent_id)
                    print(f"查询子评论，父ID={parent_id}")
            
            # 按创建时间降序排序并分页
            query = query.order_by(Comment.created_at.desc())
            pagination = paginate_query(query, page, per_page)
            
            # 转换为字典列表
            comment_list = [c.to_dict(with_user=True) for c in pagination.items]
            print(f"查询到{len(comment_list)}条评论")
            
            return success_response(data={
                'items': comment_list,
                'pagination': pagination.to_dict()
            }, message="获取评论列表成功")
        except Exception as e:
            current_app.logger.error(f"获取评论列表错误: {str(e)}")
            print(f"获取评论列表错误: {str(e)}")
            return error_response(message=f"获取评论列表失败: {str(e)}")
    
    @staticmethod
    @comment_bp.route('/comments/target', methods=['GET'])
    def get_target_comments():
        """获取目标评论列表
        
        Args:
            target_type: 目标类型(attraction, guide, note)
            target_id: 目标ID
            parent_id: 父评论ID
            
        Returns:
            评论列表
        """
        try:
            # 获取参数
            target_type = request.args.get('target_type')
            target_id = request.args.get('target_id', type=int)
            parent_id = request.args.get('parent_id', type=int)
            
            # 验证参数
            if not target_type or not target_id:
                return jsonify(error_response("缺少必要参数")), 400
            
            # 检查目标是否存在
            target = None
            if target_type == 'attraction':
                target = Attraction.query.get(target_id)
            elif target_type == 'guide':
                target = TravelGuide.query.get(target_id)
            elif target_type == 'note':
                target = TravelNote.query.get(target_id)
            
            if not target:
                return jsonify(error_response("目标不存在")), 404
            
            # 获取评论
            paginate = Comment.get_target_comments(
                content_id=target_id,
                content_type=target_type,
                parent_id=parent_id,
                page=page,
                per_page=per_page
            )
            
            # 准备响应数据
            items = []
            for comment in paginate.items:
                comment_data = comment.to_dict()
                
                # 检查当前用户是否点赞
                if current_user:
                    comment_data['is_liked'] = Comment.is_liked(
                        user_id=current_user.id,
                        comment_id=comment.id
                    )
                else:
                    comment_data['is_liked'] = False
                
                # 获取回复数量
                if parent_id is None:
                    replies_count = Comment.query.filter_by(
                        parent_id=comment.id,
                        status=1
                    ).count()
                    comment_data['replies_count'] = replies_count
                
                items.append(comment_data)
            
            return jsonify(pagination_response(
                items=items,
                total=paginate.total,
                page=page,
                per_page=per_page,
                message="获取评论成功"
            ))
        except Exception as e:
            current_app.logger.error(f"获取评论列表错误: {str(e)}")
            return error_response(message=f"获取评论列表失败: {str(e)}")
    
    @staticmethod
    @comment_bp.route('/user/comments', methods=['GET'])
    @jwt_required()
    def get_user_comments():
        """
        获取用户评论
        ---
        tags:
          - 评论
        parameters:
          - name: target_type
            in: query
            type: string
            enum: [attraction, note, guide]
            description: 目标类型
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        current_user = get_current_user()
        if not current_user:
            return jsonify(error_response("用户未找到")), 404
        
        # 获取分页参数
        page, per_page = get_page_params()
        
        # 获取过滤参数
        target_type = request.args.get('target_type')
        
        # 构建查询
        query = Comment.query.filter_by(user_id=current_user.id)
        
        # 应用过滤条件
        if target_type and target_type in ['attraction', 'note', 'guide']:
            query = query.filter_by(content_type=target_type)
        
        # 只获取一级评论
        query = query.filter(Comment.parent_id.is_(None))
        
        # 应用排序
        query = query.order_by(desc(Comment.created_at))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for comment in paginate.items:
            comment_data = comment.to_dict()
            
            # 获取目标信息
            if comment.content_type == 'attraction':
                target = Attraction.query.get(comment.content_id)
                if target:
                    comment_data['target'] = target.to_dict(with_details=False)
            elif comment.content_type == 'note':
                target = TravelNote.query.get(comment.content_id)
                if target:
                    comment_data['target'] = target.to_dict(with_details=False)
            elif comment.content_type == 'guide':
                target = TravelGuide.query.get(comment.content_id)
                if target:
                    comment_data['target'] = target.to_dict(with_details=False)
            
            # 获取回复数量
            replies_count = Comment.query.filter_by(
                parent_id=comment.id,
                status=1
            ).count()
            comment_data['replies_count'] = replies_count
            
            items.append(comment_data)
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="获取用户评论成功"
        )) 