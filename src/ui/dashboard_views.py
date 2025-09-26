# -*- coding: utf-8 -*-
"""
仪表板视图
"""
from flask import Blueprint, render_template, jsonify
from src.utils.db_decorators import with_database_and_services
import plotly.graph_objects as go
import plotly.utils
import json

# 创建蓝图
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@with_database_and_services
def page_dashboard(db, services):
    """
    仪表板主页面
    """
    try:
        # 获取统计数据
        order_stats = services['order_service'].get_order_statistics()
        inventory_stats = services['inventory_service'].get_inventory_statistics()
        production_stats = services['production_service'].get_production_statistics()
        
        # 创建图表
        order_chart = create_order_completion_chart(order_stats)
        inventory_chart = create_inventory_radar_chart(inventory_stats)
        production_chart = create_production_gantt_chart(services['production_service'])
        
        return render_template('dashboard/index.html',
                             order_stats=order_stats,
                             inventory_stats=inventory_stats,
                             production_stats=production_stats,
                             order_chart=order_chart,
                             inventory_chart=inventory_chart,
                             production_chart=production_chart)
        
    except Exception as e:
        return render_template('dashboard/index.html',
                             order_stats={},
                             inventory_stats={},
                             production_stats={},
                             order_chart='',
                             inventory_chart='',
                             production_chart='')

def create_order_completion_chart(order_stats):
    """
    创建订单完成率饼图
    """
    try:
        labels = ['新建', '审核中', '已完成']
        values = [order_stats.get('new', 0), order_stats.get('review', 0), order_stats.get('completed', 0)]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='订单完成率分布',
            height=400,
            showlegend=True
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"创建订单完成率饼图失败: {e}")
        return ''

def create_inventory_radar_chart(inventory_stats):
    """
    创建库存雷达图
    """
    try:
        part_types = inventory_stats.get('part_types', {})
        
        if not part_types:
            return ''
        
        # 准备雷达图数据
        categories = list(part_types.keys())
        quantities = [part_types[cat]['quantity'] for cat in categories]
        counts = [part_types[cat]['count'] for cat in categories]
        
        # 标准化数据（0-100）
        max_quantity = max(quantities) if quantities else 1
        max_count = max(counts) if counts else 1
        
        normalized_quantities = [q / max_quantity * 100 for q in quantities]
        normalized_counts = [c / max_count * 100 for c in counts]
        
        fig = go.Figure()
        
        # 添加数量雷达图
        fig.add_trace(go.Scatterpolar(
            r=normalized_quantities,
            theta=categories,
            fill='toself',
            name='库存数量',
            line_color='blue'
        ))
        
        # 添加种类数量雷达图
        fig.add_trace(go.Scatterpolar(
            r=normalized_counts,
            theta=categories,
            fill='toself',
            name='物料种类',
            line_color='red'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title='库存物料分布雷达图',
            height=400,
            showlegend=True
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"创建库存雷达图失败: {e}")
        return ''

def create_production_gantt_chart(production_service):
    """
    创建生产计划状态分布图（使用matplotlib柱状图）
    """
    try:
        from src.utils.matplotlib_charts import MatplotlibCharts
        from src.utils.status_mapping import StatusMapping
        
        # 获取生产计划数据
        result = production_service.get_plans(page=1, per_page=100)
        plans = result['plans']
        
        if not plans:
            return ''
        
        # 只按状态统计
        status_stats = {}
        
        for plan in plans:
            status = plan['status']
            
            # 统计状态分布
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1
        
        # 翻译状态为中文
        translated_status_stats = StatusMapping.translate_status_dict(status_stats)
        
        # 使用matplotlib创建单柱状图
        return MatplotlibCharts.create_bar_chart(
            title='生产计划状态分布',
            data=translated_status_stats
        )
    except Exception as e:
        print(f"创建生产计划图表失败: {e}")
        return ''

@dashboard_bp.route('/api/order-stats')
@with_database_and_services
def api_order_stats(db, services):
    """
    订单统计API
    """
    try:
        stats = services['order_service'].get_order_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/inventory-stats')
@with_database_and_services
def api_inventory_stats(db, services):
    """
    库存统计API
    """
    try:
        stats = services['inventory_service'].get_inventory_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/production-stats')
@with_database_and_services
def api_production_stats(db, services):
    """
    生产统计API
    """
    try:
        stats = services['production_service'].get_production_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
