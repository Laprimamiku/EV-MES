# -*- coding: utf-8 -*-
"""
生产计划业务逻辑服务
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from src.models.production_model import ProductionPlan
from src.models.order_model import Order
from src.config import PRODUCTION_STATUS

class ProductionService:
    """
    生产计划服务类
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plan(self, plan_data: Dict) -> ProductionPlan:
        """
        创建新生产计划
        """
        try:
            # 检查计划编号是否已存在
            existing_plan = self.db.query(ProductionPlan).filter(
                ProductionPlan.plan_code == plan_data.get('plan_code')
            ).first()
            
            if existing_plan:
                raise ValueError("计划编号已存在")
            
            # 检查订单是否存在
            order = self.db.query(Order).filter(Order.id == plan_data.get('order_id')).first()
            if not order:
                raise ValueError("订单不存在")
            
            # 解析时间格式（支持多种格式）
            start_time_str = plan_data.get('start_time')
            end_time_str = plan_data.get('end_time')
            
            # 尝试解析时间，支持多种格式
            start_time = self._parse_datetime(start_time_str)
            end_time = self._parse_datetime(end_time_str)
            
            # 创建生产计划对象
            plan = ProductionPlan(
                plan_code=plan_data.get('plan_code'),
                order_id=plan_data.get('order_id'),
                line=plan_data.get('line'),
                start_time=start_time,
                end_time=end_time,
                status=plan_data.get('status', 'PLANNED')
            )
            
            # 检查时间冲突
            if self._check_time_conflict(plan):
                raise ValueError("该时间段生产线已被占用")
            
            # 保存到数据库
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
            
            return plan
        except Exception as e:
            self.db.rollback()
            raise Exception(f"创建生产计划失败: {str(e)}")
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """
        解析时间字符串，支持多种格式
        """
        if not datetime_str:
            raise ValueError("时间不能为空")
        
        # 支持的格式列表
        formats = [
            '%Y-%m-%dT%H:%M',      # ISO格式：2025-09-13T08:30
            '%Y-%m-%dT%H:%M:%S',   # ISO格式：2025-09-13T08:30:00
            '%Y-%m-%d %H:%M:%S',   # 标准格式：2025-09-13 08:30:00
            '%Y-%m-%d %H:%M',      # 简化格式：2025-09-13 08:30
            '%Y-%m-%d',            # 日期格式：2025-09-13
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"无法解析时间格式: {datetime_str}")
    
    def _check_time_conflict(self, plan: ProductionPlan) -> bool:
        """
        检查时间冲突（简单实现）
        """
        # 查询同一生产线在相同时间段是否有其他计划
        conflicting_plans = self.db.query(ProductionPlan).filter(
            and_(
                ProductionPlan.line == plan.line,
                ProductionPlan.id != plan.id,
                ProductionPlan.status != 'CANCELLED',
                or_(
                    and_(
                        ProductionPlan.start_time <= plan.start_time,
                        ProductionPlan.end_time > plan.start_time
                    ),
                    and_(
                        ProductionPlan.start_time < plan.end_time,
                        ProductionPlan.end_time >= plan.end_time
                    ),
                    and_(
                        ProductionPlan.start_time >= plan.start_time,
                        ProductionPlan.end_time <= plan.end_time
                    )
                )
            )
        ).count()
        
        return conflicting_plans > 0
    
    def get_plan_by_id(self, plan_id: int) -> Optional[ProductionPlan]:
        """
        根据ID获取生产计划
        """
        return self.db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    
    def get_plans(self, page: int = 1, per_page: int = 20, search: str = None) -> Dict:
        """
        获取生产计划列表（分页）
        """
        query = self.db.query(ProductionPlan).join(Order)
        
        # 计划编号或订单客户名称模糊搜索
        if search:
            query = query.filter(
                or_(
                    ProductionPlan.plan_code.like(f'%{search}%'),
                    Order.customer.like(f'%{search}%')
                )
            )
        
        # 总数
        total = query.count()
        
        # 分页查询
        plans = query.order_by(ProductionPlan.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'plans': [plan.to_dict() for plan in plans],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def update_plan(self, plan_id: int, plan_data: Dict) -> Optional[ProductionPlan]:
        """
        更新生产计划信息
        """
        try:
            plan = self.get_plan_by_id(plan_id)
            if not plan:
                return None
            
            # 检查计划编号是否与其他记录冲突
            if 'plan_code' in plan_data and plan_data['plan_code'] != plan.plan_code:
                existing_plan = self.db.query(ProductionPlan).filter(
                    ProductionPlan.plan_code == plan_data['plan_code'],
                    ProductionPlan.id != plan_id
                ).first()
                
                if existing_plan:
                    raise ValueError("计划编号已存在")
            
            # 更新字段
            if 'plan_code' in plan_data:
                plan.plan_code = plan_data['plan_code']
            if 'order_id' in plan_data:
                plan.order_id = plan_data['order_id']
            if 'line' in plan_data:
                plan.line = plan_data['line']
            if 'start_time' in plan_data:
                plan.start_time = self._parse_datetime(plan_data['start_time'])
            if 'end_time' in plan_data:
                plan.end_time = self._parse_datetime(plan_data['end_time'])
            if 'status' in plan_data:
                plan.status = plan_data['status']
            
            # 检查时间冲突
            if self._check_time_conflict(plan):
                raise ValueError("该时间段生产线已被占用")
            
            plan.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(plan)
            
            return plan
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新生产计划失败: {str(e)}")
    
    def delete_plan(self, plan_id: int) -> bool:
        """
        删除生产计划
        """
        try:
            plan = self.get_plan_by_id(plan_id)
            if not plan:
                return False
            
            self.db.delete(plan)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"删除生产计划失败: {str(e)}")
    
    def update_plan_status(self, plan_id: int, status: str) -> Optional[ProductionPlan]:
        """
        更新生产计划状态
        """
        if status not in PRODUCTION_STATUS:
            raise ValueError(f"无效的状态: {status}")
        
        try:
            plan = self.get_plan_by_id(plan_id)
            if not plan:
                return None
            
            plan.status = status
            plan.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(plan)
            
            return plan
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新生产计划状态失败: {str(e)}")
    
    def generate_production_plan(self, order_id: int) -> ProductionPlan:
        """
        自动生成生产计划（简单贪心算法）
        """
        try:
            # 获取订单信息
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ValueError("订单不存在")
            
            # 获取可用生产线
            lines = ['Line-A', 'Line-B', 'Line-C', 'Line-D', 'Line-E']
            
            # 计算生产时间（根据数量估算）
            production_hours = order.quantity * 2  # 每台车2小时
            
            # 寻找最早可用的时间段
            start_time = datetime.now() + timedelta(days=1)  # 明天开始
            best_line = None
            best_start = None
            
            for line in lines:
                # 获取该生产线的最新计划
                latest_plan = self.db.query(ProductionPlan).filter(
                    and_(
                        ProductionPlan.line == line,
                        ProductionPlan.status != 'CANCELLED'
                    )
                ).order_by(ProductionPlan.end_time.desc()).first()
                
                if not latest_plan:
                    # 生产线空闲，使用默认开始时间
                    best_line = line
                    best_start = start_time
                    break
                else:
                    # 从最新计划结束后开始
                    candidate_start = latest_plan.end_time + timedelta(hours=1)
                    if candidate_start > start_time:
                        best_line = line
                        best_start = candidate_start
                        break
            
            if not best_line:
                raise ValueError("所有生产线都被占用")
            
            # 生成计划编号
            plan_code = f"PLAN{datetime.now().strftime('%Y%m%d')}{order_id:04d}"
            
            # 计算结束时间
            end_time = best_start + timedelta(hours=production_hours)
            
            # 创建生产计划
            plan = ProductionPlan(
                plan_code=plan_code,
                order_id=order_id,
                line=best_line,
                start_time=best_start,
                end_time=end_time,
                status='PLANNED'
            )
            
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
            
            return plan
        except Exception as e:
            self.db.rollback()
            raise Exception(f"生成生产计划失败: {str(e)}")
    
    def get_production_statistics(self) -> Dict:
        """
        获取生产统计信息
        """
        total_plans = self.db.query(ProductionPlan).count()
        planned_plans = self.db.query(ProductionPlan).filter(ProductionPlan.status == 'PLANNED').count()
        in_progress_plans = self.db.query(ProductionPlan).filter(ProductionPlan.status == 'IN_PROGRESS').count()
        completed_plans = self.db.query(ProductionPlan).filter(ProductionPlan.status == 'COMPLETED').count()
        cancelled_plans = self.db.query(ProductionPlan).filter(ProductionPlan.status == 'CANCELLED').count()
        
        return {
            'total': total_plans,
            'planned': planned_plans,
            'in_progress': in_progress_plans,
            'completed': completed_plans,
            'cancelled': cancelled_plans,
            'completion_rate': round(completed_plans / total_plans * 100, 2) if total_plans > 0 else 0
        }
