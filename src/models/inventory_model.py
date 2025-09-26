# -*- coding: utf-8 -*-
"""
库存管理模型
"""
from sqlalchemy import Column, Integer, String, Float, Text
from datetime import datetime
import random
import qrcode
import os
from .database import Base
from src.config import QRCODE_DIR

class InventoryItem(Base):
    """
    库存物料模型
    """
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    part_code = Column(String(50), unique=True, nullable=False, comment='物料编码')
    name = Column(String(100), nullable=False, comment='物料名称')
    spec = Column(String(200), nullable=True, comment='规格型号')
    quantity = Column(Integer, nullable=False, default=0, comment='库存数量')
    location = Column(String(50), nullable=True, comment='存放位置')
    created_at = Column(String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='创建时间')
    
    def __repr__(self):
        return f"<InventoryItem(id={self.id}, part_code='{self.part_code}', name='{self.name}')>"
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'part_code': self.part_code,
            'name': self.name,
            'spec': self.spec,
            'quantity': self.quantity,
            'location': self.location,
            'created_at': self.created_at,
            'qrcode_path': self.get_qrcode_path()
        }
    
    def get_qrcode_path(self):
        """
        获取二维码文件路径
        """
        return f"qrcodes/{self.part_code}.png"
    
    def generate_qrcode(self):
        """
        生成二维码图片
        """
        try:
            # 创建二维码内容（包含物料信息）
            qr_content = f"物料编码: {self.part_code}\n物料名称: {self.name}\n规格: {self.spec}\n库存: {self.quantity}"
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # 创建二维码图片
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 保存二维码图片
            qr_path = os.path.join(QRCODE_DIR, f"{self.part_code}.png")
            img.save(qr_path)
            
            return True
        except Exception as e:
            print(f"生成二维码失败: {e}")
            return False
    
    @staticmethod
    def create_sample_data(db, count=500):
        """
        创建示例库存数据
        """
        # 硬编码的库存数据
        hardcoded_items = [
            {'part_code': 'BAT1001', 'name': '动力电池包', 'spec': '100kWh-磷酸铁锂', 'quantity': 150, 'location': 'A区-01'},
            {'part_code': 'BAT1002', 'name': '动力电池包', 'spec': '150kWh-三元锂', 'quantity': 200, 'location': 'A区-02'},
            {'part_code': 'MOT2001', 'name': '永磁同步电机', 'spec': '200kW-前驱', 'quantity': 80, 'location': 'B区-01'},
            {'part_code': 'MOT2002', 'name': '永磁同步电机', 'spec': '150kW-后驱', 'quantity': 120, 'location': 'B区-02'},
            {'part_code': 'CTL3001', 'name': '电机控制器', 'spec': 'IGBT-V1.0', 'quantity': 100, 'location': 'C区-01'},
            {'part_code': 'CTL3002', 'name': '电池管理系统', 'spec': 'BMS-V2.1', 'quantity': 90, 'location': 'C区-02'},
            {'part_code': 'BOD4001', 'name': '车身框架', 'spec': '铝合金-轻量化', 'quantity': 50, 'location': 'D区-01'},
            {'part_code': 'BOD4002', 'name': '车门总成', 'spec': '钢制-标准型', 'quantity': 200, 'location': 'D区-02'},
            {'part_code': 'INT5001', 'name': '仪表盘总成', 'spec': '12.3寸-液晶', 'quantity': 180, 'location': 'E区-01'},
            {'part_code': 'INT5002', 'name': '座椅总成', 'spec': '真皮-电动调节', 'quantity': 160, 'location': 'E区-02'},
            {'part_code': 'EXT6001', 'name': '前大灯总成', 'spec': 'LED-矩阵式', 'quantity': 300, 'location': 'F区-01'},
            {'part_code': 'EXT6002', 'name': '后尾灯总成', 'spec': 'LED-贯穿式', 'quantity': 280, 'location': 'F区-02'},
            {'part_code': 'SFT7001', 'name': '车载系统软件', 'spec': 'Android-12.0', 'quantity': 1, 'location': 'G区-01'},
            {'part_code': 'SFT7002', 'name': '自动驾驶软件', 'spec': 'L2级-ADAS', 'quantity': 1, 'location': 'G区-02'},
            {'part_code': 'HWD8001', 'name': '线束总成', 'spec': '高压-400V', 'quantity': 250, 'location': 'H区-01'},
            {'part_code': 'HWD8002', 'name': '充电接口', 'spec': 'CCS2-快充', 'quantity': 180, 'location': 'H区-02'},
            {'part_code': 'SEN9001', 'name': '毫米波雷达', 'spec': '77GHz-前向', 'quantity': 120, 'location': 'I区-01'},
            {'part_code': 'SEN9002', 'name': '摄像头模组', 'spec': '8MP-环视', 'quantity': 200, 'location': 'I区-02'},
            {'part_code': 'CHG1001', 'name': '车载充电器', 'spec': '11kW-AC', 'quantity': 150, 'location': 'J区-01'},
            {'part_code': 'INV1001', 'name': 'DC-DC转换器', 'spec': '3kW-双向', 'quantity': 140, 'location': 'J区-02'},
        ]
        
        items = []
        
        # 添加硬编码数据
        for item_data in hardcoded_items:
            item = InventoryItem(
                part_code=item_data['part_code'],
                name=item_data['name'],
                spec=item_data['spec'],
                quantity=item_data['quantity'],
                location=item_data['location']
            )
            
            # 尝试生成二维码，失败也不影响数据插入
            try:
                item.generate_qrcode()
            except Exception as e:
                print(f"生成二维码失败 {item.part_code}: {e}")
            
            items.append(item)
        
        # 生成随机数据补充到指定数量
        part_prefixes = ['BAT', 'MOT', 'CTL', 'BOD', 'INT', 'EXT', 'SFT', 'HWD']
        part_names = [
            '电池包', '电机', '控制器', '车身', '内饰', '外饰', '软件', '硬件',
            '传感器', '线束', '充电器', '逆变器', '冷却系统', '制动系统', '转向系统'
        ]
        specs = [
            '100kWh', '150kW', 'V1.0', '铝合金', '碳纤维', '钢制', 'V2.1', 'V3.0',
            'Type-A', 'Type-B', 'Type-C', '标准型', '加强型', '轻量化', '高性能'
        ]
        locations = [
            'A区-01', 'A区-02', 'A区-03', 'B区-01', 'B区-02', 'B区-03',
            'C区-01', 'C区-02', 'C区-03', 'D区-01', 'D区-02', 'D区-03'
        ]
        
        for i in range(len(hardcoded_items), count):
            # 生成物料编码
            prefix = random.choice(part_prefixes)
            part_code = f"{prefix}{random.randint(1000, 9999)}"
            
            # 生成物料名称
            name = random.choice(part_names)
            
            # 生成规格
            spec = f"{random.choice(specs)}-{random.randint(1, 9)}"
            
            # 生成库存数量
            quantity = random.randint(0, 1000)
            
            # 生成存放位置
            location = random.choice(locations)
            
            item = InventoryItem(
                part_code=part_code,
                name=name,
                spec=spec,
                quantity=quantity,
                location=location
            )
            
            # 尝试生成二维码，失败也不影响数据插入
            try:
                item.generate_qrcode()
            except Exception as e:
                print(f"生成二维码失败 {item.part_code}: {e}")
            
            items.append(item)
        
        # 批量插入
        db.add_all(items)
        print(f"已创建 {count} 条示例库存数据（包含 {len(hardcoded_items)} 条硬编码数据）")
