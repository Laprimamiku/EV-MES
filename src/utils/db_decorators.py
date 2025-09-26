"""
数据库装饰器工具模块
用于简化数据库连接和会话管理
"""
from functools import wraps
from src.models.database import session_factory
from src.services.order_service import OrderService
from src.services.inventory_service import InventoryService
from src.services.production_service import ProductionService


def with_database_session(func):
    """
    数据库会话装饰器
    自动管理数据库连接的创建和关闭
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = None
        try:
            db = session_factory()
            # 将数据库会话作为第一个参数传递给原函数
            return func(db, *args, **kwargs)
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if db:
                db.close()
    return wrapper


def with_services(func):
    """
    服务装饰器
    自动创建所有服务实例
    """
    @wraps(func)
    def wrapper(db, *args, **kwargs):
        # 创建服务实例
        services = {
            'order_service': OrderService(db),
            'inventory_service': InventoryService(db),
            'production_service': ProductionService(db)
        }
        # 将服务作为关键字参数传递给原函数
        return func(db, services=services, *args, **kwargs)
    return wrapper


def with_database_and_services(func):
    """
    组合装饰器：数据库会话 + 服务
    """
    return with_database_session(with_services(func))


class DatabaseContext:
    """
    数据库上下文管理器
    用于手动管理数据库连接
    """
    
    def __init__(self):
        self.db = None
        self.services = {}
    
    def __enter__(self):
        self.db = session_factory()
        self.services = {
            'order_service': OrderService(self.db),
            'inventory_service': InventoryService(self.db),
            'production_service': ProductionService(self.db)
        }
        return self.db, self.services
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        if self.db:
            self.db.close()
