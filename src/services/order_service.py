# -*- coding: utf-8 -*-
"""
订单管理业务逻辑服务
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models.order_model import Order
from src.config import ORDER_STATUS

class OrderService:
    """
    订单管理服务类
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_order(self, order_data: Dict) -> Order:
        """
        创建新订单
        """
        try:
            # 创建订单对象
            order = Order(
                customer=order_data.get('customer'),
                vehicle_model=order_data.get('vehicle_model'),
                quantity=order_data.get('quantity'),
                due_date=datetime.strptime(order_data.get('due_date'), '%Y-%m-%d'),
                status=order_data.get('status', 'NEW'),
                vin_prefix=order_data.get('vin_prefix')
            )
            
            # 保存到数据库
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            return order
        except Exception as e:
            self.db.rollback()
            raise Exception(f"创建订单失败: {str(e)}")
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        根据ID获取订单
        """
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_orders(self, page: int = 1, per_page: int = 20, search: str = None) -> Dict:
        """
        获取订单列表（分页）
        """
        query = self.db.query(Order)
        
        # 客户名称模糊搜索
        if search:
            query = query.filter(Order.customer.like(f'%{search}%'))
        
        # 总数
        total = query.count()
        
        # 分页查询
        orders = query.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'orders': [order.to_dict() for order in orders],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def update_order(self, order_id: int, order_data: Dict) -> Optional[Order]:
        """
        更新订单信息
        """
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return None
            
            # 更新字段
            if 'customer' in order_data:
                order.customer = order_data['customer']
            if 'vehicle_model' in order_data:
                order.vehicle_model = order_data['vehicle_model']
            if 'quantity' in order_data:
                order.quantity = order_data['quantity']
            if 'due_date' in order_data:
                order.due_date = datetime.strptime(order_data['due_date'], '%Y-%m-%d')
            if 'status' in order_data:
                order.status = order_data['status']
            if 'vin_prefix' in order_data:
                order.vin_prefix = order_data['vin_prefix']
            
            order.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(order)
            
            return order
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新订单失败: {str(e)}")
    
    def delete_order(self, order_id: int) -> bool:
        """
        删除订单
        """
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return False
            
            self.db.delete(order)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"删除订单失败: {str(e)}")
    
    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """
        更新订单状态
        """
        if status not in ORDER_STATUS:
            raise ValueError(f"无效的状态: {status}")
        
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return None
            
            order.status = status
            order.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(order)
            
            return order
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新订单状态失败: {str(e)}")
    
    def get_order_statistics(self) -> Dict:
        """
        获取订单统计信息
        """
        total_orders = self.db.query(Order).count()
        new_orders = self.db.query(Order).filter(Order.status == 'NEW').count()
        review_orders = self.db.query(Order).filter(Order.status == 'REVIEW').count()
        completed_orders = self.db.query(Order).filter(Order.status == 'COMPLETED').count()
        
        return {
            'total': total_orders,
            'new': new_orders,
            'review': review_orders,
            'completed': completed_orders,
            'completion_rate': round(completed_orders / total_orders * 100, 2) if total_orders > 0 else 0
        }
