# -*- coding: utf-8 -*-
"""
生产计划视图
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from src.services.production_service import ProductionService
from src.services.order_service import OrderService
from src.models.database import session_factory
from src.config import PRODUCTION_STATUS
import plotly.graph_objects as go
import plotly.utils
import json

# 创建蓝图
production_bp = Blueprint('production', __name__, url_prefix='/production')

@production_bp.route('/')
def page_production_list():
    """
    生产计划列表页面
    """
    try:
        db = session_factory()
        production_service = ProductionService(db)
        
        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        
        # 获取生产计划列表
        result = production_service.get_plans(page=page, per_page=per_page, search=search)
        
        # 获取统计信息
        stats = production_service.get_production_statistics()
        
        return render_template('production/list.html', 
                             plans=result['plans'],
                             pagination=result,
                             search=search,
                             stats=stats,
                             status_options=PRODUCTION_STATUS)
    except Exception as e:
        flash(f'获取生产计划列表失败: {str(e)}', 'error')
        return render_template('production/list.html', plans=[], pagination={}, search='', stats={}, status_options=PRODUCTION_STATUS)
    finally:
        db.close()

@production_bp.route('/create', methods=['GET', 'POST'])
def page_production_create():
    """
    创建生产计划页面
    """
    try:
        db = session_factory()
        production_service = ProductionService(db)
        order_service = OrderService(db)
        
        if request.method == 'GET':
            # 获取所有订单
            orders = order_service.get_orders(page=1, per_page=1000)['orders']
            return render_template('production/form.html', 
                                 plan=None, 
                                 orders=orders,
                                 status_options=PRODUCTION_STATUS)
        
        # 获取表单数据
        plan_data = {
            'plan_code': request.form.get('plan_code'),
            'order_id': int(request.form.get('order_id', 0)),
            'line': request.form.get('line'),
            'start_time': request.form.get('start_time'),
            'end_time': request.form.get('end_time'),
            'status': request.form.get('status', 'PLANNED')
        }
        
        # 创建生产计划
        plan = production_service.create_plan(plan_data)
        
        flash('生产计划创建成功', 'success')
        return redirect(url_for('production.page_production_list'))
        
    except Exception as e:
        flash(f'创建生产计划失败: {str(e)}', 'error')
        return redirect(url_for('production.page_production_create'))
    finally:
        db.close()

@production_bp.route('/<int:plan_id>/edit', methods=['GET', 'POST'])
def page_production_edit(plan_id):
    """
    编辑生产计划页面
    """
    try:
        db = session_factory()
        production_service = ProductionService(db)
        order_service = OrderService(db)
        
        if request.method == 'GET':
            plan = production_service.get_plan_by_id(plan_id)
            if not plan:
                flash('生产计划不存在', 'error')
                return redirect(url_for('production.page_production_list'))
            
            # 获取所有订单
            orders = order_service.get_orders(page=1, per_page=1000)['orders']
            
            return render_template('production/form.html', 
                                 plan=plan.to_dict(), 
                                 orders=orders,
                                 status_options=PRODUCTION_STATUS)
        
        # 获取表单数据
        plan_data = {
            'plan_code': request.form.get('plan_code'),
            'order_id': int(request.form.get('order_id', 0)),
            'line': request.form.get('line'),
            'start_time': request.form.get('start_time'),
            'end_time': request.form.get('end_time'),
            'status': request.form.get('status')
        }
        
        # 更新生产计划
        plan = production_service.update_plan(plan_id, plan_data)
        if not plan:
            flash('生产计划不存在', 'error')
            return redirect(url_for('production.page_production_list'))
        
        flash('生产计划更新成功', 'success')
        return redirect(url_for('production.page_production_list'))
        
    except Exception as e:
        flash(f'更新生产计划失败: {str(e)}', 'error')
        return redirect(url_for('production.page_production_edit', plan_id=plan_id))
    finally:
        db.close()

@production_bp.route('/<int:plan_id>/delete', methods=['POST'])
def page_production_delete(plan_id):
    """
    删除生产计划
    """
    try:
        db = session_factory()
        production_service = ProductionService(db)
        
        success = production_service.delete_plan(plan_id)
        if success:
            flash('生产计划删除成功', 'success')
        else:
            flash('生产计划不存在', 'error')
        
        return redirect(url_for('production.page_production_list'))
        
    except Exception as e:
        flash(f'删除生产计划失败: {str(e)}', 'error')
        return redirect(url_for('production.page_production_list'))
    finally:
        db.close()

@production_bp.route('/<int:plan_id>/status', methods=['POST'])
def page_production_update_status(plan_id):
    """
    更新生产计划状态
    """
    try:
        db = session_factory()
        production_service = ProductionService(db)
        
        status = request.form.get('status')
        if not status:
            flash('请选择状态', 'error')
            return redirect(url_for('production.page_production_list'))
        
        plan = production_service.update_plan_status(plan_id, status)
        if plan:
            flash('生产计划状态更新成功', 'success')
        else:
            flash('生产计划不存在', 'error')
        
        return redirect(url_for('production.page_production_list'))
        
    except Exception as e:
        flash(f'更新生产计划状态失败: {str(e)}', 'error')
        return redirect(url_for('production.page_production_list'))
    finally:
        db.close()

@production_bp.route('/generate/<int:order_id>', methods=['POST'])
def page_production_generate(order_id):
    """
    自动生成生产计划
    """
    try:
        db = session_factory()
        production_service = ProductionService(db)
        
        # 生成生产计划
        plan = production_service.generate_production_plan(order_id)
        
        flash('生产计划生成成功', 'success')
        return redirect(url_for('production.page_production_list'))
        
    except Exception as e:
        flash(f'生成生产计划失败: {str(e)}', 'error')
        return redirect(url_for('production.page_production_list'))
    finally:
        db.close()

@production_bp.route('/gantt')
def page_production_gantt():
    """
    生产计划统计页面
    """
    try:
        db = session_factory()
        production_service = ProductionService(db)
        
        # 获取所有生产计划
        result = production_service.get_plans(page=1, per_page=1000)
        plans = result['plans']
        
        # 创建统计图表
        charts = create_gantt_chart(plans)
        
        return render_template('production/gantt.html', 
                             status_chart=charts.get('status_chart', ''),
                             line_chart=charts.get('line_chart', ''),
                             plans=plans)
        
    except Exception as e:
        flash(f'获取统计图表失败: {str(e)}', 'error')
        return render_template('production/gantt.html', 
                             status_chart='', 
                             line_chart='', 
                             plans=[])
    finally:
        db.close()

def create_gantt_chart(plans):
    """
    创建生产计划状态分布图（使用matplotlib柱状图）
    """
    try:
        from src.utils.matplotlib_charts import MatplotlibCharts
        from src.utils.status_mapping import StatusMapping
        
        if not plans:
            return {'status_chart': '', 'line_chart': ''}
        
        # 按状态和生产线统计
        status_stats = {}
        line_stats = {}
        
        for plan in plans:
            status = plan['status']
            line = plan['line']
            
            # 统计状态分布
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1
            
            # 统计生产线分布
            if line not in line_stats:
                line_stats[line] = 0
            line_stats[line] += 1
        
        # 翻译状态为中文，生产线保持英文
        translated_status_stats = StatusMapping.translate_status_dict(status_stats)
        translated_line_stats = StatusMapping.translate_line_dict(line_stats)
        
        # 分别创建两个图表
        status_chart = MatplotlibCharts.create_bar_chart(
            title='按状态分布',
            data=translated_status_stats
        )
        
        line_chart = MatplotlibCharts.create_bar_chart(
            title='按生产线分布',
            data=translated_line_stats
        )
        
        return {
            'status_chart': status_chart,
            'line_chart': line_chart
        }
        
    except Exception as e:
        print(f"创建生产计划图表失败: {e}")
        return {'status_chart': '', 'line_chart': ''}

@production_bp.route('/api/statistics')
def api_production_statistics():
    """
    生产统计API
    """
    try:
        db = session_factory()
        production_service = ProductionService(db)
        
        stats = production_service.get_production_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
