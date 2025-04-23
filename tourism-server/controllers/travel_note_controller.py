from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime
from sqlalchemy import desc, func, and_
import re
import os
from werkzeug.utils import secure_filename

from models import TravelNote, TravelNoteImage, NoteAttraction, Attraction
from models.tag import Tag, ContentTag
from models.user import User
from models.comment import Comment
from models.like import Like
from models.collection import Collection
from extensions import db, cache
from utils.response import success_response, error_response, pagination_response
from utils.auth import get_current_user, login_required
from utils.validator import get_page_params, validate_required, validate_params
from utils.file import upload_file
from utils.rich_content import extract_summary, extract_images
from utils.pagination import paginate_query
from utils.upload import allowed_file, save_file, save_image

note_bp = Blueprint('note', __name__, url_prefix='')


class TravelNoteController:
    """旅游游记控制器"""
    
    @staticmethod
    @note_bp.route('', methods=['GET'])
    def get_notes():
        """
        获取游记列表
        ---
        tags:
          - 旅游游记
        parameters:
          - name: keyword
            in: query
            type: string
            description: 关键词搜索(标题)
          - name: destination
            in: query
            type: string
            description: 目的地
          - name: user_id
            in: query
            type: integer
            description: 作者ID
          - name: sort
            in: query
            type: string
            enum: [newest, hottest, most_viewed, most_liked, most_collected]
            description: 排序方式(newest-最新,hottest-最热,most_viewed-最多浏览,most_liked-最多点赞,most_collected-最多收藏)
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        # 获取参数
        keyword = request.args.get('keyword', '').strip()
        destination = request.args.get('destination', '').strip()
        user_id = request.args.get('user_id', type=int)
        sort = request.args.get('sort', 'newest')
        page, per_page = get_page_params()
        
        # 构建查询
        query = TravelNote.query
        
        # 只返回已发布的游记
        query = query.filter(TravelNote.status == 1)
        
        # 应用过滤条件
        if keyword:
            query = query.filter(
                TravelNote.title.like(f'%{keyword}%')
            )
        
        if destination:
            query = query.filter(TravelNote.location.like(f'%{destination}%'))
        
        if user_id:
            query = query.filter(TravelNote.user_id == user_id)
        
        # 应用排序
        if sort == 'newest':
            query = query.order_by(desc(TravelNote.created_at))
        elif sort == 'hottest':
            # 热度综合排序 (浏览量 + 点赞数*2 + 收藏数*3 + 评论数*2)
            query = query.order_by(
                desc(TravelNote.views + TravelNote.likes*2 + TravelNote.collections*3 + TravelNote.comments*2)
            )
        elif sort == 'most_viewed':
            query = query.order_by(desc(TravelNote.views))
        elif sort == 'most_liked':
            query = query.order_by(desc(TravelNote.likes))
        elif sort == 'most_collected':
            query = query.order_by(desc(TravelNote.collections))
        else:
            # 默认按最新排序
            query = query.order_by(desc(TravelNote.created_at))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 获取当前用户ID(如果已登录)
        current_user_id = None
        try:
            if hasattr(request, 'user') and request.user:
                current_user_id = request.user.id
        except:
            pass
        
        # 准备响应数据
        items = []
        for note in paginate.items:
            note_data = note.to_dict(with_details=False)
            
            # 如果用户已登录，查询点赞和收藏状态
            if current_user_id:
                # 查询是否点赞
                like = Like.query.filter_by(
                    user_id=current_user_id,
                    target_type='note',
                    target_id=note.id
                ).first()
                note_data['is_liked'] = bool(like)
                
                # 查询是否收藏
                collection = Collection.query.filter_by(
                    user_id=current_user_id,
                    target_type='note',
                    target_id=note.id
                ).first()
                note_data['is_collected'] = bool(collection)
            
            items.append(note_data)
        
        # 获取所有目的地选项
        destinations = db.session.query(
            TravelNote.location
        ).filter(
            TravelNote.status == 1,
            TravelNote.location != None,
            TravelNote.location != ''
        ).distinct().all()
        destinations = [d[0] for d in destinations if d[0]]
        
        # 构建过滤选项
        filters = {
            'destinations': destinations
        }
        
        # 修改响应格式，同时支持标准格式(items)和新格式(notes)，以适配测试
        response_data = {
            'items': items,
            'notes': items,  # 兼容新格式
            'pagination': {
                'total': paginate.total,
                'page': page,
                'per_page': per_page,
                'total_pages': paginate.pages,
                'has_next': paginate.has_next,
                'has_prev': paginate.has_prev
            },
            'filters': filters
        }
        
        return jsonify(pagination_response(
            data=response_data,
            message="获取游记列表成功"
        ))
    
    @staticmethod
    @note_bp.route('/<int:note_id>', methods=['GET'])
    def get_note_detail(note_id):
        """
        获取游记详情
        ---
        tags:
          - 旅游游记
        parameters:
          - name: note_id
            in: path
            required: true
            type: integer
            description: 游记ID
        """
        # 查询游记
        note = TravelNote.query.get(note_id)
        if not note:
            return jsonify(error_response("游记不存在")), 404
        
        # 如果游记未发布且不是作者本人查看，则返回错误
        if note.status != 1:
            current_user_id = None
            try:
                if hasattr(request, 'user') and request.user:
                    current_user_id = request.user.id
            except:
                pass
            
            if not current_user_id or current_user_id != note.user_id:
                return jsonify(error_response("游记不存在或已下架")), 404
        
        # 增加浏览量
        note.views += 1
        db.session.commit()
        
        # 获取当前用户ID(如果已登录)
        current_user_id = None
        try:
            if hasattr(request, 'user') and request.user:
                current_user_id = request.user.id
        except:
            pass
        
        # 获取游记详情
        note_data = note.to_dict(with_details=True)
        
        # 如果用户已登录，查询点赞和收藏状态
        if current_user_id:
            # 查询是否点赞
            like = Like.query.filter_by(
                user_id=current_user_id,
                target_type='note',
                target_id=note.id
            ).first()
            note_data['is_liked'] = bool(like)
            
            # 查询是否收藏
            collection = Collection.query.filter_by(
                user_id=current_user_id,
                target_type='note',
                target_id=note.id
            ).first()
            note_data['is_collected'] = bool(collection)
        
        return jsonify(success_response("获取游记详情成功", note_data))
    
    @staticmethod
    @note_bp.route('', methods=['POST'])
    @login_required
    def create_note():
        """
        创建游记
        ---
        tags:
          - 旅游游记
        parameters:
          - name: body
            in: body
            required: true
            schema:
              properties:
                title:
                  type: string
                  description: 标题
                content:
                  type: string
                  description: 内容
                cover_image:
                  type: string
                  description: 封面图片
                summary:
                  type: string
                  description: 摘要
                destination:
                  type: string
                  description: 目的地
                trip_date:
                  type: string
                  format: date
                  description: 出行日期
                days:
                  type: integer
                  description: 出行天数
                companions:
                  type: string
                  description: 同行人
                cost:
                  type: string
                  description: 费用预算
                status:
                  type: integer
                  enum: [0, 1]
                  description: 状态(0-草稿,1-已发布)
        """
        # 获取请求数据
        data = request.get_json()
        
        # 校验参数
        required_fields = ['title', 'content']
        is_valid, errors = validate_required(data, required_fields)
        if not is_valid:
            return jsonify(error_response("缺少必要参数")), 400
        
        # 提取摘要
        summary = data.get('summary', '')
        if not summary and data.get('content'):
            summary = extract_summary(data['content'], max_length=250)  # 减少最大长度，留出安全边界
        # 确保summary不超过数据库字段长度
        summary = summary[:255] if summary else ''
        
        # 如果没有提供封面图片，则尝试从内容中提取第一张图片
        cover_image = data.get('cover_image', '')
        if not cover_image and data.get('content'):
            images = extract_images(data['content'])
            if images:
                cover_image = images[0]
        
        # 解析出行日期
        trip_date = None
        if data.get('trip_date'):
            try:
                trip_date = datetime.strptime(data['trip_date'], '%Y-%m-%d')
            except:
                pass
        
        # 创建游记
        note = TravelNote(
            title=data['title'],
            content=data['content'],
            description=summary,
            cover_image=cover_image,
            location=data.get('destination', ''),
            trip_start_date=trip_date,
            trip_days=data.get('days'),
            trip_cost=data.get('cost', ''),
            status=data.get('status', 0),
            user_id=request.user.id
        )
        
        try:
            # 保存到数据库
            db.session.add(note)
            db.session.commit()
            
            return jsonify(success_response("游记创建成功", {'note_id': note.id}))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"游记创建失败: {str(e)}")), 500
    
    @staticmethod
    @note_bp.route('/<int:note_id>', methods=['PUT'])
    @login_required
    def update_note(note_id):
        """
        更新游记
        ---
        tags:
          - 旅游游记
        parameters:
          - name: note_id
            in: path
            required: true
            type: integer
            description: 游记ID
          - name: body
            in: body
            required: true
            schema:
              properties:
                title:
                  type: string
                  description: 标题
                content:
                  type: string
                  description: 内容
                cover_image:
                  type: string
                  description: 封面图片
                summary:
                  type: string
                  description: 摘要
                destination:
                  type: string
                  description: 目的地
                trip_date:
                  type: string
                  format: date
                  description: 出行日期
                days:
                  type: integer
                  description: 出行天数
                cost:
                  type: string
                  description: 费用预算
                status:
                  type: integer
                  enum: [0, 1, 2]
                  description: 状态(0-草稿,1-已发布,2-已下架)
        """
        # 获取请求数据
        data = request.get_json()
        
        # 校验参数
        if not data:
            return jsonify(error_response("请求参数不能为空")), 400
        
        # 查询游记
        note = TravelNote.query.get(note_id)
        if not note:
            return jsonify(error_response("游记不存在")), 404
        
        # 验证权限
        if note.user_id != request.user.id:
            return jsonify(error_response("无权修改该游记")), 403
        
        # 解析出行日期
        trip_date = None
        if data.get('trip_date'):
            try:
                trip_date = datetime.strptime(data['trip_date'], '%Y-%m-%d')
            except:
                pass
        
        # 更新游记信息
        if 'title' in data:
            note.title = data['title']
        
        if 'content' in data:
            note.content = data['content']
            
            # 如果更新了内容，重新提取摘要
            if not data.get('summary'):
                note.description = extract_summary(data['content'], max_length=250)
                # 确保不超过数据库字段长度
                note.description = note.description[:255] if note.description else ''
            
            # 如果没有封面图片，从内容中提取
            if not note.cover_image and not data.get('cover_image'):
                images = extract_images(data['content'])
                if images:
                    note.cover_image = images[0]
        
        if 'summary' in data:
            note.description = data['summary'][:255] if data['summary'] else ''
        
        if 'cover_image' in data:
            note.cover_image = data['cover_image']
        
        if 'destination' in data:
            note.location = data['destination']
        
        if trip_date:
            note.trip_start_date = trip_date
        
        if 'days' in data:
            note.trip_days = data['days']
        
        if 'cost' in data:
            note.trip_cost = data['cost']
        
        if 'status' in data:
            note.status = data['status']
        
        try:
            db.session.commit()
            
            return jsonify(success_response("游记更新成功"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"游记更新失败: {str(e)}")), 500
    
    @staticmethod
    @note_bp.route('/<int:note_id>', methods=['DELETE'])
    @login_required
    def delete_note(note_id):
        """
        删除游记
        ---
        tags:
          - 旅游游记
        parameters:
          - name: note_id
            in: path
            required: true
            type: integer
            description: 游记ID
        """
        # 查询游记
        note = TravelNote.query.get(note_id)
        if not note:
            return jsonify(error_response("游记不存在")), 404
        
        # 验证权限
        if note.user_id != request.user.id:
            return jsonify(error_response("无权删除该游记")), 403
        
        try:
            # 删除游记
            db.session.delete(note)
            db.session.commit()
            
            return jsonify(success_response("游记删除成功"))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"游记删除失败: {str(e)}")), 500
    
    @staticmethod
    @note_bp.route('/my', methods=['GET'])
    @login_required
    def get_my_notes():
        """
        获取我的游记列表
        ---
        tags:
          - 旅游游记
        parameters:
          - name: status
            in: query
            type: integer
            enum: [0, 1, 2]
            description: 状态(0-草稿,1-已发布,2-已下架)
          - name: page
            in: query
            type: integer
            description: 页码
          - name: per_page
            in: query
            type: integer
            description: 每页数量
        """
        # 获取参数
        status = request.args.get('status', type=int)
        page, per_page = get_page_params()
        
        # 构建查询
        query = TravelNote.query.filter_by(user_id=request.user.id)
        
        # 按状态过滤
        if status is not None:
            query = query.filter_by(status=status)
        
        # 按创建时间倒序排序
        query = query.order_by(desc(TravelNote.created_at))
        
        # 执行分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 准备响应数据
        items = []
        for note in paginate.items:
            note_data = note.to_dict(with_details=False)
            items.append(note_data)
        
        return jsonify(pagination_response(
            items=items,
            total=paginate.total,
            page=page,
            per_page=per_page,
            message="获取我的游记列表成功"
        ))
    
    @staticmethod
    @note_bp.route('/upload/image', methods=['POST'])
    @login_required
    def upload_image():
        """
        上传游记图片
        ---
        tags:
          - 旅游游记
        parameters:
          - name: file
            in: formData
            required: true
            type: file
            description: 图片文件
        """
        if 'file' not in request.files:
            return jsonify(error_response("未找到上传文件")), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify(error_response("未选择文件")), 400
        
        # 验证文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify(error_response("不支持的文件类型")), 400
        
        try:
            # 上传文件
            upload_dir = 'uploads/notes'
            filename = upload_file(file, upload_dir)
            
            # 构建图片URL
            image_url = os.path.join('/static', upload_dir, filename)
            
            return jsonify(success_response("图片上传成功", {
                'url': image_url,
                'filename': filename
            }))
        except Exception as e:
            current_app.logger.error(f"图片上传失败: {str(e)}")
            return jsonify(error_response(f"图片上传失败: {str(e)}")), 500
    
    @staticmethod
    @note_bp.route('/<int:note_id>/feature', methods=['PUT', 'OPTIONS'])
    def feature_note(note_id):
        """
        设置游记为精选
        ---
        tags:
          - 旅游游记
        parameters:
          - name: note_id
            in: path
            required: true
            type: integer
            description: 游记ID
        """
        # 对于OPTIONS请求直接返回空响应，用于CORS预检
        if request.method == 'OPTIONS':
            return jsonify({})
        
        # JWT验证
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify(error_response("用户未登录或不存在")), 401
            if not user.is_admin:
                return jsonify(error_response("没有权限执行此操作")), 403
        except Exception as e:
            return jsonify(error_response(f"认证失败: {str(e)}")), 401
            
        # 查询游记
        note = TravelNote.query.get(note_id)
        if not note:
            return jsonify(error_response("游记不存在")), 404
            
        # 设置为精选
        note.featured = True
        note.featured_at = datetime.now()
        
        try:
            db.session.commit()
            return jsonify(success_response("设置精选成功", note.to_dict()))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"设置精选失败: {str(e)}")), 500
    
    @staticmethod
    @note_bp.route('/<int:note_id>/status', methods=['PUT', 'OPTIONS'])
    def update_note_status(note_id):
        """
        更新游记状态
        ---
        tags:
          - 旅游游记
        parameters:
          - name: note_id
            in: path
            required: true
            type: integer
            description: 游记ID
          - name: body
            in: body
            required: true
            schema:
              properties:
                status:
                  type: integer
                  enum: [0, 1, 2]
                  description: 状态(0-草稿,1-已发布,2-已下架)
        """
        # 对于OPTIONS请求直接返回空响应，用于CORS预检
        if request.method == 'OPTIONS':
            return jsonify({})
            
        # JWT验证
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify(error_response("用户未登录或不存在")), 401
            if not user.is_admin:
                return jsonify(error_response("没有权限执行此操作")), 403
        except Exception as e:
            return jsonify(error_response(f"认证失败: {str(e)}")), 401
        
        # 获取请求数据
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify(error_response("请求参数不能为空")), 400
            
        # 查询游记
        note = TravelNote.query.get(note_id)
        if not note:
            return jsonify(error_response("游记不存在")), 404
            
        # 更新状态
        note.status = data['status']
        note.updated_at = datetime.now()
        
        try:
            db.session.commit()
            return jsonify(success_response("更新游记状态成功", note.to_dict()))
        except Exception as e:
            db.session.rollback()
            return jsonify(error_response(f"更新游记状态失败: {str(e)}")), 500 