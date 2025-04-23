#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from app import app, db

def parse_args():
    parser = argparse.ArgumentParser(description='Tourism API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', default=5000, type=int, help='Port to bind to')
    parser.add_argument('--env', default='development', 
                      choices=['development', 'testing', 'production'],
                      help='Environment to run in')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def init_db():
    """初始化数据库"""
    print("初始化数据库...")
    with app.app_context():
        db.create_all()
    print("数据库初始化完成!")

if __name__ == '__main__':
    args = parse_args()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = args.env
    
    # 是否初始化数据库
    if args.init_db:
        init_db()
    
    # 启动服务器
    debug = args.debug or args.env == 'development'
    print(f"启动旅游平台API服务，环境: {args.env}, 调试模式: {'启用' if debug else '禁用'}")
    print(f"服务运行在 http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=debug) 