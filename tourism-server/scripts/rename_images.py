import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app import create_app
from extensions import db
from models.attraction import Attraction
from models.travel_guide import TravelGuide
from models.travel_note import TravelNote
from utils.file_utils import batch_rename_images

def main():
    """批量重命名图片文件"""
    # 创建应用实例
    app = create_app()
    
    # 在应用上下文中执行操作
    with app.app_context():
        # 图片根目录
        static_dir = os.path.join(project_root, 'static', 'images')
        
        # 重命名景点图片
        print("\n=== 开始处理景点图片 ===")
        attractions_dir = os.path.join(static_dir, 'attractions')
        success, fail, log_file = batch_rename_images(attractions_dir, Attraction, db.session)
        if log_file:
            print(f"处理完成: 成功 {success} 条，失败 {fail} 条")
            print(f"日志文件: {log_file}")
        
        # 重命名攻略图片
        print("\n=== 开始处理攻略图片 ===")
        guides_dir = os.path.join(static_dir, 'guides')
        success, fail, log_file = batch_rename_images(guides_dir, TravelGuide, db.session)
        if log_file:
            print(f"处理完成: 成功 {success} 条，失败 {fail} 条")
            print(f"日志文件: {log_file}")
        
        # 重命名游记图片
        print("\n=== 开始处理游记图片 ===")
        notes_dir = os.path.join(static_dir, 'notes')
        success, fail, log_file = batch_rename_images(notes_dir, TravelNote, db.session)
        if log_file:
            print(f"处理完成: 成功 {success} 条，失败 {fail} 条")
            print(f"日志文件: {log_file}")

if __name__ == '__main__':
    main() 