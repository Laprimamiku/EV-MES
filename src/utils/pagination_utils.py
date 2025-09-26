"""
分页工具模块
提供通用的分页功能
"""
from typing import Dict, Any, List
from math import ceil


class PaginationUtils:
    """分页工具类"""
    
    @staticmethod
    def create_pagination(page: int, per_page: int, total: int, 
                         search: str = '', base_url: str = '') -> Dict[str, Any]:
        """
        创建分页信息
        
        Args:
            page: 当前页码
            per_page: 每页显示数量
            total: 总记录数
            search: 搜索关键词
            base_url: 基础URL
            
        Returns:
            分页信息字典
        """
        pages = ceil(total / per_page) if total > 0 else 1
        has_prev = page > 1
        has_next = page < pages
        
        return {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None,
            'search': search,
            'base_url': base_url
        }
    
    @staticmethod
    def get_offset(page: int, per_page: int) -> int:
        """
        获取偏移量
        
        Args:
            page: 当前页码
            per_page: 每页显示数量
            
        Returns:
            偏移量
        """
        return (page - 1) * per_page
    
    @staticmethod
    def validate_page_params(page: int, per_page: int) -> tuple:
        """
        验证分页参数
        
        Args:
            page: 页码
            per_page: 每页显示数量
            
        Returns:
            验证后的页码和每页显示数量
        """
        # 确保页码至少为1
        page = max(1, page)
        
        # 限制每页显示数量范围
        per_page = max(1, min(100, per_page))
        
        return page, per_page
