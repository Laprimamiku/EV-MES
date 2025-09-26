# -*- coding: utf-8 -*-
"""
生产计划模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import random
from .database import Base

class ProductionPlan(Base):
    """
    生产计划模型
    """
    __tablename__ = 'production_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_code = Column(String(50), unique=True, nullable=False, comment='计划编号')
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, comment='关联订单ID')
    line = Column(String(20), nullable=False, comment='生产线')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=False, comment='结束时间')
    status = Column(String(20), nullable=False, default='PLANNED', comment='状态')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联关系
    order = relationship("Order", back_populates="production_plans")
    
    def __repr__(self):
        return f"<ProductionPlan(id={self.id}, plan_code='{self.plan_code}', line='{self.line}')>"
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'plan_code': self.plan_code,
            'order_id': self.order_id,
            'line': self.line,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'order_info': self.order.to_dict() if self.order else None
        }
    
    @staticmethod
    def create_sample_data(db, count=100):
        """
        创建示例生产计划数据
        """
        # 导入Order模型
        from .order_model import Order
        
        # 获取所有订单
        orders = db.query(Order).all()
        if not orders:
            print("没有找到订单数据，无法创建生产计划")
            return
        
        print(f"找到 {len(orders)} 条订单数据，开始创建生产计划...")
        
        # 硬编码的生产计划数据
        current_date = datetime.now().strftime('%Y%m%d')
        hardcoded_plans = [
            {'plan_code': f'PLAN{current_date}001', 'line': 'Line-A', 'status': 'IN_PROGRESS', 'duration_hours': 48},
            {'plan_code': f'PLAN{current_date}002', 'line': 'Line-B', 'status': 'PLANNED', 'duration_hours': 72},
            {'plan_code': f'PLAN{current_date}003', 'line': 'Line-C', 'status': 'COMPLETED', 'duration_hours': 96},
            {'plan_code': f'PLAN{current_date}004', 'line': 'Line-D', 'status': 'IN_PROGRESS', 'duration_hours': 60},
            {'plan_code': f'PLAN{current_date}005', 'line': 'Line-E', 'status': 'PLANNED', 'duration_hours': 84},
            {'plan_code': f'PLAN{current_date}006', 'line': 'Line-A', 'status': 'CANCELLED', 'duration_hours': 36},
            {'plan_code': f'PLAN{current_date}007', 'line': 'Line-B', 'status': 'COMPLETED', 'duration_hours': 120},
            {'plan_code': f'PLAN{current_date}008', 'line': 'Line-C', 'status': 'PLANNED', 'duration_hours': 54},
            {'plan_code': f'PLAN{current_date}009', 'line': 'Line-D', 'status': 'IN_PROGRESS', 'duration_hours': 78},
            {'plan_code': f'PLAN{current_date}010', 'line': 'Line-E', 'status': 'PLANNED', 'duration_hours': 66},
        ]
        
        plans = []
        
        # 添加硬编码数据
        for i, plan_data in enumerate(hardcoded_plans):
            if i < len(orders):
                order = orders[i]
            else:
                order = random.choice(orders)
            
            # 生成开始时间（未来1-30天）
            start_time = datetime.now() + timedelta(days=random.randint(1, 30))
            
            # 生成结束时间
            end_time = start_time + timedelta(hours=plan_data['duration_hours'])
            
            plan = ProductionPlan(
                plan_code=plan_data['plan_code'],
                order_id=order.id,
                line=plan_data['line'],
                start_time=start_time,
                end_time=end_time,
                status=plan_data['status']
            )
            plans.append(plan)
        
        # 生成随机数据补充到指定数量
        lines = ['Line-A', 'Line-B', 'Line-C', 'Line-D', 'Line-E']
        statuses = ['PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
        
        for i in range(len(hardcoded_plans), count):
            # 随机选择订单
            order = random.choice(orders)
            
            # 生成计划编号
            plan_code = f"PLAN{datetime.now().strftime('%Y%m%d')}{i+1:04d}"
            
            # 随机选择生产线
            line = random.choice(lines)
            
            # 生成开始时间（未来1-30天）
            start_time = datetime.now() + timedelta(days=random.randint(1, 30))
            
            # 生成结束时间（开始时间后1-7天）
            duration_hours = random.randint(8, 168)  # 1天到7天
            end_time = start_time + timedelta(hours=duration_hours)
            
            # 随机选择状态
            status = random.choice(statuses)
            
            plan = ProductionPlan(
                plan_code=plan_code,
                order_id=order.id,
                line=line,
                start_time=start_time,
                end_time=end_time,
                status=status
            )
            plans.append(plan)
        
        # 批量插入
        db.add_all(plans)
        print(f"已创建 {count} 条示例生产计划数据（包含 {len(hardcoded_plans)} 条硬编码数据）")
