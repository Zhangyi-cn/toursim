import os
import uuid
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

def generate_unique_filename(original_filename):
    """生成唯一的文件名
    格式: yyyyMMdd_uuid前8位_原文件扩展名
    """
    # 获取文件扩展名
    ext = os.path.splitext(original_filename)[1]
    # 生成新文件名：日期_uuid前8位
    new_filename = f"{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}{ext}"
    return new_filename

def create_rename_log(log_dir):
    """创建重命名日志文件
    Returns:
        str: 日志文件路径
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f'rename_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    with open(log_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', '原文件名', '新文件名', '状态', '错误信息'])
    return log_file

def rename_file(old_path, new_filename):
    """重命名文件
    Args:
        old_path: 原文件完整路径
        new_filename: 新文件名（不含路径）
    Returns:
        new_path: 新文件完整路径
    """
    if not os.path.exists(old_path):
        return None
        
    # 获取目录路径
    directory = os.path.dirname(old_path)
    # 新文件完整路径
    new_path = os.path.join(directory, new_filename)
    
    try:
        # 如果新文件已存在，先生成一个新的文件名
        while os.path.exists(new_path):
            new_filename = generate_unique_filename(new_filename)
            new_path = os.path.join(directory, new_filename)
        
        # 重命名文件
        os.rename(old_path, new_path)
        return new_path
    except Exception as e:
        print(f"重命名文件失败: {str(e)}")
        return None

def check_files_exist(base_path, items):
    """预检查所有文件是否存在
    Args:
        base_path: 图片根目录
        items: 数据库记录列表
    Returns:
        tuple: (存在文件数, 不存在文件数, 不存在文件列表)
    """
    exist_count = 0
    not_exist_count = 0
    not_exist_files = []
    
    for item in items:
        if not item.cover_image:
            continue
            
        old_filename = item.cover_image.split('/')[-1]
        old_path = os.path.join(base_path, old_filename)
        
        if os.path.exists(old_path):
            exist_count += 1
        else:
            not_exist_count += 1
            not_exist_files.append((item.id, old_filename))
            
    return exist_count, not_exist_count, not_exist_files

def batch_rename_images(base_path, model, db_session):
    """批量重命名图片并更新数据库
    Args:
        base_path: 图片根目录
        model: 数据库模型类
        db_session: 数据库会话
    Returns:
        tuple: (成功数, 失败数, 日志文件路径)
    """
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(base_path), 'logs')
    log_file = create_rename_log(log_dir)
    
    try:
        # 获取所有记录
        items = model.query.all()
        total = len(items)
        print(f"总共需要处理 {total} 条记录")
        
        # 预检查文件是否存在
        exist_count, not_exist_count, not_exist_files = check_files_exist(base_path, items)
        print(f"文件检查结果: 存在 {exist_count} 个，不存在 {not_exist_count} 个")
        
        if not_exist_count > 0:
            print("以下文件不存在:")
            for item_id, filename in not_exist_files:
                print(f"ID: {item_id}, 文件名: {filename}")
            
        # 询问是否继续
        response = input("是否继续执行重命名操作？(y/n): ")
        if response.lower() != 'y':
            print("操作已取消")
            return 0, 0, log_file
            
        success_count = 0
        fail_count = 0
        
        # 打开日志文件
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            for index, item in enumerate(items, 1):
                if not item.cover_image:
                    continue
                    
                try:
                    # 原文件完整路径
                    old_filename = item.cover_image.split('/')[-1]
                    old_path = os.path.join(base_path, old_filename)
                    
                    # 如果原文件不存在，记录错误并继续
                    if not os.path.exists(old_path):
                        writer.writerow([item.id, old_filename, '', '失败', '原文件不存在'])
                        fail_count += 1
                        continue
                    
                    # 生成新文件名
                    new_filename = generate_unique_filename(old_filename)
                    
                    # 重命名文件
                    new_path = rename_file(old_path, new_filename)
                    if new_path:
                        # 更新数据库中的文件路径
                        item.cover_image = f"attractions/{new_filename}"
                        writer.writerow([item.id, old_filename, new_filename, '成功', ''])
                        success_count += 1
                    else:
                        writer.writerow([item.id, old_filename, new_filename, '失败', '重命名失败'])
                        fail_count += 1
                    
                    # 每100条记录提交一次事务
                    if index % 100 == 0:
                        db_session.commit()
                        print(f"已处理: {index}/{total}")
                
                except Exception as e:
                    writer.writerow([item.id, old_filename, '', '失败', str(e)])
                    fail_count += 1
                    
        # 最后提交事务
        db_session.commit()
        print(f"处理完成: 成功 {success_count} 条，失败 {fail_count} 条")
        return success_count, fail_count, log_file
        
    except Exception as e:
        print(f"批量重命名失败: {str(e)}")
        db_session.rollback()
        return 0, 0, log_file 