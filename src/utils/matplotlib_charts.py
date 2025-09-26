"""
使用matplotlib生成中文图表的工具模块
"""
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免tkinter线程问题
import matplotlib.pyplot as plt
import base64
import io
from typing import Dict, List, Any

# 设置中文字体
import platform
if platform.system() == 'Windows':
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
else:
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['figure.facecolor'] = 'white'
matplotlib.rcParams['axes.facecolor'] = 'white'


class MatplotlibCharts:
    """使用matplotlib生成图表的工具类"""
    
    @staticmethod
    def create_bar_chart(title: str, data: Dict[str, int], colors: List[str] = None) -> str:
        """
        创建柱状图并返回base64编码的图片
        
        Args:
            title: 图表标题
            data: 数据字典 {key: value}
            colors: 颜色列表
            
        Returns:
            base64编码的图片字符串
        """
        if not data:
            return ''
        
        if colors is None:
            colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']
        
        # 创建图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(data.keys(), data.values(), color=colors[0])
        
        # 设置标题和标签
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('分类', fontsize=12)
        plt.ylabel('数量', fontsize=12)
        
        # 旋转x轴标签
        plt.xticks(rotation=45)
        
        # 在柱子上显示数值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        # 调整布局
        plt.tight_layout()
        
        # 转换为base64
        return MatplotlibCharts._fig_to_base64()
    
    @staticmethod
    def create_double_bar_chart(title: str, data1: Dict[str, int], data2: Dict[str, int], 
                               name1: str, name2: str, colors: List[str] = None) -> str:
        """
        创建双柱状图并返回base64编码的图片
        
        Args:
            title: 图表标题
            data1: 第一组数据
            data2: 第二组数据
            name1: 第一组数据名称
            name2: 第二组数据名称
            colors: 颜色列表
            
        Returns:
            base64编码的图片字符串
        """
        if not data1 and not data2:
            return ''
        
        if colors is None:
            colors = ['#5470c6', '#91cc75']
        
        # 获取所有键
        all_keys = set(data1.keys()) | set(data2.keys())
        keys = list(all_keys)
        
        # 获取对应的值
        values1 = [data1.get(key, 0) for key in keys]
        values2 = [data2.get(key, 0) for key in keys]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # 第一个子图
        bars1 = ax1.bar(keys, values1, color=colors[0])
        ax1.set_title(f'{name1}分布', fontsize=14, fontweight='bold')
        ax1.set_ylabel('数量', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        
        # 在柱子上显示数值
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        # 第二个子图
        bars2 = ax2.bar(keys, values2, color=colors[1])
        ax2.set_title(f'{name2}分布', fontsize=14, fontweight='bold')
        ax2.set_ylabel('数量', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        
        # 在柱子上显示数值
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        # 设置总标题
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # 调整布局
        plt.tight_layout()
        
        # 转换为base64
        return MatplotlibCharts._fig_to_base64()
    
    @staticmethod
    def create_pie_chart(title: str, data: Dict[str, int], colors: List[str] = None) -> str:
        """
        创建饼图并返回base64编码的图片
        
        Args:
            title: 图表标题
            data: 数据字典 {key: value}
            colors: 颜色列表
            
        Returns:
            base64编码的图片字符串
        """
        if not data:
            return ''
        
        if colors is None:
            colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']
        
        # 过滤掉值为0的数据
        filtered_data = {k: v for k, v in data.items() if v > 0}
        
        if not filtered_data:
            return ''
        
        # 创建图表
        plt.figure(figsize=(8, 8))
        
        # 创建饼图
        wedges, texts, autotexts = plt.pie(
            filtered_data.values(), 
            labels=filtered_data.keys(),
            autopct='%1.1f%%',
            colors=colors[:len(filtered_data)],
            startangle=90
        )
        
        # 设置标题
        plt.title(title, fontsize=16, fontweight='bold')
        
        # 调整布局
        plt.tight_layout()
        
        # 转换为base64
        return MatplotlibCharts._fig_to_base64()
    
    @staticmethod
    def create_line_chart(title: str, data: Dict[str, int], colors: List[str] = None) -> str:
        """
        创建折线图并返回base64编码的图片
        
        Args:
            title: 图表标题
            data: 数据字典 {key: value}
            colors: 颜色列表
            
        Returns:
            base64编码的图片字符串
        """
        if not data:
            return ''
        
        if colors is None:
            colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        
        # 排序数据
        sorted_data = dict(sorted(data.items()))
        
        # 创建折线图
        plt.plot(list(sorted_data.keys()), list(sorted_data.values()), 
                marker='o', linewidth=2, markersize=6, color=colors[0])
        
        # 设置标题和标签
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('时间', fontsize=12)
        plt.ylabel('数量', fontsize=12)
        
        # 旋转x轴标签
        plt.xticks(rotation=45)
        
        # 在点上显示数值
        for x, y in sorted_data.items():
            plt.text(x, y + 0.1, f'{y}', ha='center', va='bottom')
        
        # 添加网格
        plt.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 转换为base64
        return MatplotlibCharts._fig_to_base64()
    
    @staticmethod
    def _fig_to_base64() -> str:
        """
        将matplotlib图表转换为base64字符串
        
        Returns:
            base64编码的图片字符串
        """
        # 保存到内存缓冲区
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        
        # 转换为base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 清理
        plt.close()
        buffer.close()
        
        return f"data:image/png;base64,{image_base64}"
