# -*- coding: utf-8 -*-
"""
订单管理模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import random
from .database import Base

class Order(Base):
    """
    订单模型
    """
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer = Column(String(100), nullable=False, comment='客户名称')
    vehicle_model = Column(String(50), nullable=False, comment='车型')
    quantity = Column(Integer, nullable=False, comment='数量')
    due_date = Column(DateTime, nullable=False, comment='交期')
    status = Column(String(20), nullable=False, default='NEW', comment='状态')
    vin_prefix = Column(String(10), nullable=True, comment='VIN前缀')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联关系
    production_plans = relationship("ProductionPlan", back_populates="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, customer='{self.customer}', model='{self.vehicle_model}')>"
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'customer': self.customer,
            'vehicle_model': self.vehicle_model,
            'quantity': self.quantity,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'status': self.status,
            'vin_prefix': self.vin_prefix,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    @staticmethod
    def create_sample_data(db, count=200):
        """
        创建示例订单数据
        """
        # 客户名称列表
        customers = [
            '比亚迪汽车', '特斯拉中国', '蔚来汽车', '理想汽车', '小鹏汽车',
            '长城汽车', '吉利汽车', '奇瑞汽车', '江淮汽车', '北汽新能源',
            '广汽埃安', '上汽荣威', '东风岚图', '长安深蓝', '零跑汽车'
        ]
        
        # 车型列表
        vehicle_models = [
            'Model 3', 'Model Y', 'ES6', 'ES8', '理想ONE', '理想L9',
            'P7', 'P5', '欧拉好猫', '欧拉黑猫', '汉EV', '唐EV',
            '秦PLUS EV', '宋PLUS EV', '元PLUS', '海豚', '海豹'
        ]
        
        # VIN前缀列表
        vin_prefixes = ['LHG', 'LSG', 'LNB', 'LFP', 'LGB', 'LDC', 'LFA', 'LFB']
        
        # 状态列表
        statuses = ['NEW', 'REVIEW', 'COMPLETED']
        
        orders = []
        for i in range(count):
            # 随机生成交期（未来30-90天）
            due_date = datetime.now() + timedelta(days=random.randint(30, 90))
            
            order = Order(
                customer=random.choice(customers),
                vehicle_model=random.choice(vehicle_models),
                quantity=random.randint(1, 50),
                due_date=due_date,
                status=random.choice(statuses),
                vin_prefix=random.choice(vin_prefixes)
            )
            orders.append(order)
        
        # 批量插入
        db.add_all(orders)
        print(f"已创建 {count} 条示例订单数据")
