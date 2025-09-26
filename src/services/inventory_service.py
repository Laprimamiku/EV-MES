# -*- coding: utf-8 -*-
"""
库存管理业务逻辑服务
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models.inventory_model import InventoryItem

class InventoryService:
    """
    库存管理服务类
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_item(self, item_data: Dict) -> InventoryItem:
        """
        创建新库存物料
        """
        try:
            # 检查物料编码是否已存在
            existing_item = self.db.query(InventoryItem).filter(
                InventoryItem.part_code == item_data.get('part_code')
            ).first()
            
            if existing_item:
                raise ValueError("物料编码已存在")
            
            # 创建库存物料对象
            item = InventoryItem(
                part_code=item_data.get('part_code'),
                name=item_data.get('name'),
                spec=item_data.get('spec'),
                quantity=item_data.get('quantity', 0),
                location=item_data.get('location')
            )
            
            # 生成二维码
            item.generate_qrcode()
            
            # 保存到数据库
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            
            return item
        except Exception as e:
            self.db.rollback()
            raise Exception(f"创建库存物料失败: {str(e)}")
    
    def get_item_by_id(self, item_id: int) -> Optional[InventoryItem]:
        """
        根据ID获取库存物料
        """
        return self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    
    def get_item_by_code(self, part_code: str) -> Optional[InventoryItem]:
        """
        根据物料编码获取库存物料
        """
        return self.db.query(InventoryItem).filter(InventoryItem.part_code == part_code).first()
    
    def get_items(self, page: int = 1, per_page: int = 20, search: str = None) -> Dict:
        """
        获取库存物料列表（分页）
        """
        query = self.db.query(InventoryItem)
        
        # 物料名称或编码模糊搜索
        if search:
            query = query.filter(
                or_(
                    InventoryItem.name.like(f'%{search}%'),
                    InventoryItem.part_code.like(f'%{search}%')
                )
            )
        
        # 总数
        total = query.count()
        
        # 分页查询
        items = query.order_by(InventoryItem.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'items': [item.to_dict() for item in items],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def update_item(self, item_id: int, item_data: Dict) -> Optional[InventoryItem]:
        """
        更新库存物料信息
        """
        try:
            item = self.get_item_by_id(item_id)
            if not item:
                return None
            
            # 检查物料编码是否与其他记录冲突
            if 'part_code' in item_data and item_data['part_code'] != item.part_code:
                existing_item = self.db.query(InventoryItem).filter(
                    InventoryItem.part_code == item_data['part_code'],
                    InventoryItem.id != item_id
                ).first()
                
                if existing_item:
                    raise ValueError("物料编码已存在")
            
            # 更新字段
            if 'part_code' in item_data:
                item.part_code = item_data['part_code']
            if 'name' in item_data:
                item.name = item_data['name']
            if 'spec' in item_data:
                item.spec = item_data['spec']
            if 'quantity' in item_data:
                item.quantity = item_data['quantity']
            if 'location' in item_data:
                item.location = item_data['location']
            
            # 重新生成二维码
            item.generate_qrcode()
            
            self.db.commit()
            self.db.refresh(item)
            
            return item
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新库存物料失败: {str(e)}")
    
    def delete_item(self, item_id: int) -> bool:
        """
        删除库存物料
        """
        try:
            item = self.get_item_by_id(item_id)
            if not item:
                return False
            
            self.db.delete(item)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"删除库存物料失败: {str(e)}")
    
    def update_quantity(self, item_id: int, quantity: int) -> Optional[InventoryItem]:
        """
        更新库存数量
        """
        try:
            item = self.get_item_by_id(item_id)
            if not item:
                return None
            
            item.quantity = quantity
            self.db.commit()
            self.db.refresh(item)
            
            return item
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新库存数量失败: {str(e)}")
    
    def get_inventory_statistics(self) -> Dict:
        """
        获取库存统计信息
        """
        total_items = self.db.query(InventoryItem).count()
        total_quantity = self.db.query(InventoryItem).with_entities(
            InventoryItem.quantity
        ).all()
        
        total_quantity_sum = sum([item.quantity for item in total_quantity])
        
        # 按物料类型统计
        part_types = {}
        items = self.db.query(InventoryItem).all()
        for item in items:
            prefix = item.part_code[:3] if len(item.part_code) >= 3 else 'OTHER'
            if prefix not in part_types:
                part_types[prefix] = {'count': 0, 'quantity': 0}
            part_types[prefix]['count'] += 1
            part_types[prefix]['quantity'] += item.quantity
        
        return {
            'total_items': total_items,
            'total_quantity': total_quantity_sum,
            'part_types': part_types
        }
