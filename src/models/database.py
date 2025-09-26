# -*- coding: utf-8 -*-
"""
数据库初始化和事务管理
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
import os
from src.config import DATABASE_URI, BASE_DIR

# 确保数据库目录存在
db_path = os.path.join(BASE_DIR, 'data')
os.makedirs(db_path, exist_ok=True)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URI,
    poolclass=StaticPool,
    connect_args={'check_same_thread': False},
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session_factory = scoped_session(SessionLocal)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """
    获取数据库会话
    """
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    初始化数据库表结构
    """
    # 导入所有模型以确保表被创建
    from .order_model import Order
    from .inventory_model import InventoryItem
    from .production_model import ProductionPlan
    
    # 创建所有表（如果不存在）
    Base.metadata.create_all(bind=engine)

