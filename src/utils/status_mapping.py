"""
状态映射工具模块
提供状态和生产线的中英文映射
"""

# 状态映射字典
STATUS_MAPPING = {
    'PLANNED': '已计划',
    'IN_PROGRESS': '进行中', 
    'COMPLETED': '已完成',
    'CANCELLED': '已取消'
}

# 订单状态映射字典
ORDER_STATUS_MAPPING = {
    'NEW': '新建',
    'REVIEW': '审核中',
    'COMPLETED': '已完成'
}

# 生产线映射字典（保持英文）
LINE_MAPPING = {
    'Line-A': 'Line-A',
    'Line-B': 'Line-B', 
    'Line-C': 'Line-C',
    'Line-D': 'Line-D',
    'Line-E': 'Line-E'
}

class StatusMapping:
    """状态映射工具类"""
    
    @staticmethod
    def translate_status(status: str) -> str:
        """
        翻译状态为中文
        
        Args:
            status: 英文状态
            
        Returns:
            中文状态
        """
        return STATUS_MAPPING.get(status, status)
    
    @staticmethod
    def translate_line(line: str) -> str:
        """
        翻译生产线（保持英文）
        
        Args:
            line: 生产线名称
            
        Returns:
            生产线名称
        """
        return LINE_MAPPING.get(line, line)
    
    @staticmethod
    def translate_status_dict(data: dict) -> dict:
        """
        翻译状态字典
        
        Args:
            data: 状态数据字典
            
        Returns:
            翻译后的状态字典
        """
        return {StatusMapping.translate_status(k): v for k, v in data.items()}
    
    @staticmethod
    def translate_line_dict(data: dict) -> dict:
        """
        翻译生产线字典
        
        Args:
            data: 生产线数据字典
            
        Returns:
            翻译后的生产线字典
        """
        return {StatusMapping.translate_line(k): v for k, v in data.items()}
    
    @staticmethod
    def translate_order_status(status: str) -> str:
        """
        翻译订单状态为中文
        
        Args:
            status: 英文订单状态
            
        Returns:
            中文订单状态
        """
        return ORDER_STATUS_MAPPING.get(status, status)
    
    @staticmethod
    def translate_order_status_dict(data: dict) -> dict:
        """
        翻译订单状态字典
        
        Args:
            data: 订单状态数据字典
            
        Returns:
            翻译后的订单状态字典
        """
        return {StatusMapping.translate_order_status(k): v for k, v in data.items()}
