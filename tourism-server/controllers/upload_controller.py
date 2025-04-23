from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import os
from werkzeug.utils import secure_filename
import uuid
import time
from datetime import datetime

from utils.response import success_response, error_response
from utils.auth import get_current_user

# 创建蓝图
upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'],
    'video': ['mp4', 'avi', 'mov', 'wmv'],
    'audio': ['mp3', 'wav', 'ogg']
}

def allowed_file(filename, file_type=None):
    """检查文件是否是允许的扩展名"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type and file_type in ALLOWED_EXTENSIONS:
        return ext in ALLOWED_EXTENSIONS[file_type]
    
    # 如果未指定类型，则检查所有允许的扩展名
    for allowed_exts in ALLOWED_EXTENSIONS.values():
        if ext in allowed_exts:
            return True
    
    return False

def get_file_type(filename):
    """根据文件名获取文件类型"""
    if '.' not in filename:
        return None
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    
    return None

def generate_filename(original_filename):
    """生成唯一的文件名"""
    if '.' not in original_filename:
        return str(uuid.uuid4())
    
    name, ext = original_filename.rsplit('.', 1)
    timestamp = int(time.time())
    random_str = str(uuid.uuid4()).split('-')[0]
    
    return f"{timestamp}_{random_str}.{ext}"

@upload_bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def upload():
    """通用上传入口"""
    if request.method == 'OPTIONS':
        return '', 204
        
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify(error_response("未找到文件")), 400
    
    file = request.files['file']
    file_type = request.form.get('type', 'file')  # 可以指定上传类型：image, file, document等
    
    # 根据类型调用对应的处理函数
    if file_type == 'image':
        return upload_image()
    else:
        return upload_file()

@upload_bp.route('/image', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def upload_image():
    """上传图片"""
    if request.method == 'OPTIONS':
        return '', 204
        
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify(error_response("未找到文件")), 400
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify(error_response("文件名为空")), 400
    
    # 检查文件类型
    if not allowed_file(file.filename, 'image'):
        return jsonify(error_response("不支持的文件类型，请上传图片文件")), 400
    
    # 获取用户ID
    user = get_current_user()
    if not user:
        return jsonify(error_response("用户未认证")), 401
    
    # 获取保存目录，默认为images
    folder = request.form.get('folder', 'images')
    
    # 确保目录存在
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # 生成安全的文件名
    original_filename = secure_filename(file.filename)
    filename = generate_filename(original_filename)
    
    # 保存文件
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # 生成URL路径
    url_path = f"/static/uploads/{folder}/{filename}"
    
    # 返回结果
    return jsonify(success_response("上传成功", {
        "url": url_path,
        "filename": filename,
        "original_name": original_filename,
        "file_type": get_file_type(original_filename),
        "size": os.path.getsize(filepath),
        "uploaded_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }))


@upload_bp.route('/file', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def upload_file():
    """上传通用文件"""
    if request.method == 'OPTIONS':
        return '', 204
        
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify(error_response("未找到文件")), 400
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify(error_response("文件名为空")), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify(error_response("不支持的文件类型")), 400
    
    # 获取用户ID
    user = get_current_user()
    if not user:
        return jsonify(error_response("用户未认证")), 401
    
    # 获取保存目录，默认为files
    folder = request.form.get('folder', 'files')
    
    # 确保目录存在
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # 生成安全的文件名
    original_filename = secure_filename(file.filename)
    filename = generate_filename(original_filename)
    
    # 保存文件
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # 生成URL路径
    url_path = f"/static/uploads/{folder}/{filename}"
    
    # 返回结果
    return jsonify(success_response("上传成功", {
        "url": url_path,
        "filename": filename,
        "original_name": original_filename,
        "file_type": get_file_type(original_filename),
        "size": os.path.getsize(filepath),
        "uploaded_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }))


@upload_bp.route('/multiple', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def upload_multiple_files():
    """上传多个文件"""
    if request.method == 'OPTIONS':
        return '', 204
        
    # 检查是否有文件
    if 'files[]' not in request.files:
        return jsonify(error_response("未找到文件")), 400
    
    files = request.files.getlist('files[]')
    
    if len(files) == 0:
        return jsonify(error_response("没有选择文件")), 400
    
    # 获取用户ID
    user = get_current_user()
    if not user:
        return jsonify(error_response("用户未认证")), 401
    
    # 获取保存目录，默认为files
    folder = request.form.get('folder', 'files')
    
    # 确保目录存在
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    result = []
    for file in files:
        # 检查文件名是否为空
        if file.filename == '':
            continue
        
        # 检查文件类型
        if not allowed_file(file.filename):
            continue
        
        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        filename = generate_filename(original_filename)
        
        # 保存文件
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # 生成URL路径
        url_path = f"/static/uploads/{folder}/{filename}"
        
        # 添加到结果
        result.append({
            "url": url_path,
            "filename": filename,
            "original_name": original_filename,
            "file_type": get_file_type(original_filename),
            "size": os.path.getsize(filepath),
            "uploaded_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    if len(result) == 0:
        return jsonify(error_response("没有成功上传任何文件")), 400
    
    return jsonify(success_response(f"成功上传{len(result)}个文件", result)) 