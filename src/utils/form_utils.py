"""
表单工具模块
提供通用的表单处理功能
"""
from typing import Dict, Any, Optional
from datetime import datetime


class FormUtils:
    """表单工具类"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, str]:
        """
        验证必填字段
        
        Args:
            data: 表单数据
            required_fields: 必填字段列表
            
        Returns:
            错误信息字典
        """
        errors = {}
        
        for field in required_fields:
            if not data.get(field) or str(data.get(field)).strip() == '':
                errors[field] = f'{field}不能为空'
        
        return errors
    
    @staticmethod
    def validate_numeric_fields(data: Dict[str, Any], numeric_fields: List[str]) -> Dict[str, str]:
        """
        验证数值字段
        
        Args:
            data: 表单数据
            numeric_fields: 数值字段列表
            
        Returns:
            错误信息字典
        """
        errors = {}
        
        for field in numeric_fields:
            value = data.get(field)
            if value is not None and value != '':
                try:
                    float(value)
                    if float(value) < 0:
                        errors[field] = f'{field}不能为负数'
                except (ValueError, TypeError):
                    errors[field] = f'{field}必须是有效数字'
        
        return errors
    
    @staticmethod
    def validate_date_fields(data: Dict[str, Any], date_fields: List[str]) -> Dict[str, str]:
        """
        验证日期字段
        
        Args:
            data: 表单数据
            date_fields: 日期字段列表
            
        Returns:
            错误信息字典
        """
        errors = {}
        
        for field in date_fields:
            value = data.get(field)
            if value is not None and value != '':
                try:
                    datetime.strptime(str(value), '%Y-%m-%d')
                except ValueError:
                    try:
                        datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        errors[field] = f'{field}日期格式不正确'
        
        return errors
    
    @staticmethod
    def clean_form_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理表单数据
        
        Args:
            data: 原始表单数据
            
        Returns:
            清理后的表单数据
        """
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                cleaned_data[key] = value.strip()
            elif value is not None:
                cleaned_data[key] = value
        
        return cleaned_data
    
    @staticmethod
    def format_errors(errors: Dict[str, str]) -> str:
        """
        格式化错误信息
        
        Args:
            errors: 错误信息字典
            
        Returns:
            格式化的错误信息字符串
        """
        if not errors:
            return ''
        
        error_list = [f"{field}: {message}" for field, message in errors.items()]
        return "; ".join(error_list)
