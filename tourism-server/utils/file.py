import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

# 允许的图片类型
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def get_file_extension(filename):
    """
    获取文件扩展名
    :param filename: 文件名
    :return: 扩展名（小写）
    """
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def generate_unique_filename(filename):
    """
    生成唯一文件名
    :param filename: 原始文件名
    :return: 唯一文件名
    """
    ext = get_file_extension(filename)
    unique_filename = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}"
    if ext:
        unique_filename = f"{unique_filename}.{ext}"
    return unique_filename


def ensure_directory_exists(directory):
    """
    确保目录存在，不存在则创建
    :param directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_upload_path(upload_dir):
    """
    获取上传路径
    :param upload_dir: 上传目录
    :return: 完整上传路径
    """
    base_dir = current_app.config.get('UPLOAD_FOLDER', 'static')
    upload_path = os.path.join(base_dir, upload_dir)
    ensure_directory_exists(upload_path)
    return upload_path


def upload_file(file, upload_dir, filename=None, allowed_extensions=None):
    """
    上传文件
    :param file: 文件对象
    :param upload_dir: 上传目录
    :param filename: 指定文件名，为空则自动生成
    :param allowed_extensions: 允许的扩展名列表
    :return: 文件名
    """
    # 验证文件类型
    if allowed_extensions:
        file_ext = get_file_extension(file.filename)
        if file_ext not in allowed_extensions:
            raise ValueError(f"文件类型不允许: {file_ext}")
    
    # 获取安全的文件名
    if not filename:
        filename = generate_unique_filename(secure_filename(file.filename))
    
    # 获取上传路径
    upload_path = get_upload_path(upload_dir)
    
    # 保存文件
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    
    return filename


def delete_file(filepath):
    """
    删除文件
    :param filepath: 文件路径
    :return: 是否成功
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"删除文件失败: {str(e)}")
        return False


def allowed_file(filename, allowed_extensions=None):
    """
    检查文件类型是否允许
    :param filename: 文件名
    :param allowed_extensions: 允许的扩展名集合
    :return: 是否允许
    """
    if not allowed_extensions:
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_image(file, directory='images'):
    """
    保存图片文件
    :param file: 文件对象
    :param directory: 保存目录
    :return: 文件URL
    """
    if not file:
        raise ValueError("未上传文件")
        
    if not allowed_file(file.filename):
        raise ValueError("不支持的文件类型")
        
    filename = upload_file(file, directory, allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
    return os.path.join(directory, filename) 