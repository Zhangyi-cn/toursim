import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions=None):
    """
    检查文件扩展名是否允许
    :param filename: 文件名
    :param allowed_extensions: 允许的扩展名列表，默认为图片
    :return: 是否允许
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_filename(filename):
    """
    生成唯一的文件名
    格式: yyyyMMdd_uuid前8位_原文件扩展名
    :param filename: 原始文件名
    :return: 新的文件名
    """
    # 获取文件扩展名
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    # 生成新文件名：日期_uuid前8位
    new_filename = f"{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
    
    if ext:
        new_filename = f"{new_filename}.{ext}"
        
    return new_filename


def get_upload_path(folder=None):
    """
    获取上传路径
    :param folder: 子目录，如 'images', 'avatars' 等
    :return: 上传路径
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # 按年月分目录
    date_folder = datetime.now().strftime('%Y%m')
    
    if folder:
        path = os.path.join(upload_folder, folder, date_folder)
    else:
        path = os.path.join(upload_folder, date_folder)
    
    # 确保目录存在
    if not os.path.exists(path):
        os.makedirs(path)
        
    return path


def save_file(file, folder=None, allowed_extensions=None):
    """
    保存上传的文件
    :param file: 上传的文件对象
    :param folder: 子目录
    :param allowed_extensions: 允许的扩展名列表
    :return: 保存的文件URL路径，失败返回None
    """
    if not file:
        return None
    
    filename = secure_filename(file.filename)
    
    if not allowed_file(filename, allowed_extensions):
        return None
    
    # 生成唯一文件名
    new_filename = generate_filename(filename)
    
    # 获取保存路径
    save_path = get_upload_path(folder)
    
    # 完整的文件保存路径
    file_path = os.path.join(save_path, new_filename)
    
    try:
        file.save(file_path)
        
        # 生成相对于上传根目录的路径，用于URL
        upload_root = current_app.config['UPLOAD_FOLDER']
        relative_path = os.path.relpath(file_path, upload_root)
        
        # 将路径分隔符统一为 '/'
        relative_path = relative_path.replace('\\', '/')
        
        return relative_path
    except Exception as e:
        current_app.logger.error(f"文件保存失败: {str(e)}")
        return None


def save_image(image, folder='images'):
    """
    保存图片文件
    :param image: 上传的图片文件对象
    :param folder: 子目录，默认为 'images'
    :return: 保存的图片URL路径，失败返回None
    """
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return save_file(image, folder, allowed_extensions)


def delete_file(file_path):
    """
    删除文件
    :param file_path: 文件相对路径
    :return: 是否删除成功
    """
    try:
        upload_root = current_app.config['UPLOAD_FOLDER']
        full_path = os.path.join(upload_root, file_path)
        
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"文件删除失败: {str(e)}")
        return False 