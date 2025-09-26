# -*- coding: utf-8 -*-
"""
EV-MES 系统配置文件
"""
import os

# 数据库配置
DATABASE_URI = 'sqlite:///data/ev_mes.db'

# 应用配置
SECRET_KEY = 'ev-mes-secret-key-2024'
DEBUG = True

# 文件路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
QRCODE_DIR = os.path.join(DATA_DIR, 'qrcodes')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(QRCODE_DIR, exist_ok=True)

# 业务常量
ORDER_STATUS = {
    'NEW': '新建',
    'REVIEW': '审核中', 
    'COMPLETED': '已完成'
}

PRODUCTION_STATUS = {
    'PLANNED': '已计划',
    'IN_PROGRESS': '进行中',
    'COMPLETED': '已完成',
    'CANCELLED': '已取消'
}


# 分页配置
DEFAULT_PAGE_SIZE = 10
