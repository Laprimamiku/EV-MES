# -*- coding: utf-8 -*-
"""
订单管理视图
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from src.services.order_service import OrderService
from src.models.database import session_factory
from src.config import ORDER_STATUS
from src.utils.matplotlib_charts import MatplotlibCharts
from src.utils.status_mapping import StatusMapping

# 创建蓝图
order_bp = Blueprint('order', __name__, url_prefix='/order')

@order_bp.route('/')
def page_order_list():
    """
    订单列表页面
    """
    try:
        db = session_factory()
        order_service = OrderService(db)
        
        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        
        # 获取订单列表
        result = order_service.get_orders(page=page, per_page=per_page, search=search)
        
        # 获取统计信息
        stats = order_service.get_order_statistics()
        
        return render_template('order/list.html', 
                             orders=result['orders'],
                             pagination=result,
                             search=search,
                             stats=stats,
                             status_options=ORDER_STATUS)
    except Exception as e:
        flash(f'获取订单列表失败: {str(e)}', 'error')
        return render_template('order/list.html', orders=[], pagination={}, search='', stats={}, status_options=ORDER_STATUS)
    finally:
        db.close()

@order_bp.route('/create', methods=['GET', 'POST'])
def page_order_create():
    """
    创建订单页面
    """
    if request.method == 'GET':
        return render_template('order/form.html', order=None, status_options=ORDER_STATUS)
    
    try:
        db = session_factory()
        order_service = OrderService(db)
        
        # 获取表单数据
        order_data = {
            'customer': request.form.get('customer'),
            'vehicle_model': request.form.get('vehicle_model'),
            'quantity': int(request.form.get('quantity', 0)),
            'due_date': request.form.get('due_date'),
            'status': request.form.get('status', 'NEW'),
            'vin_prefix': request.form.get('vin_prefix')
        }
        
        # 创建订单
        order = order_service.create_order(order_data)
        
        flash('订单创建成功', 'success')
        return redirect(url_for('order.page_order_list'))
        
    except Exception as e:
        flash(f'创建订单失败: {str(e)}', 'error')
        return render_template('order/form.html', order=None, status_options=ORDER_STATUS)
    finally:
        db.close()

@order_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
def page_order_edit(order_id):
    """
    编辑订单页面
    """
    try:
        db = session_factory()
        order_service = OrderService(db)
        
        if request.method == 'GET':
            order = order_service.get_order_by_id(order_id)
            if not order:
                flash('订单不存在', 'error')
                return redirect(url_for('order.page_order_list'))
            
            return render_template('order/form.html', order=order.to_dict(), status_options=ORDER_STATUS)
        
        # 获取表单数据
        order_data = {
            'customer': request.form.get('customer'),
            'vehicle_model': request.form.get('vehicle_model'),
            'quantity': int(request.form.get('quantity', 0)),
            'due_date': request.form.get('due_date'),
            'status': request.form.get('status'),
            'vin_prefix': request.form.get('vin_prefix')
        }
        
        # 更新订单
        order = order_service.update_order(order_id, order_data)
        if not order:
            flash('订单不存在', 'error')
            return redirect(url_for('order.page_order_list'))
        
        flash('订单更新成功', 'success')
        return redirect(url_for('order.page_order_list'))
        
    except Exception as e:
        flash(f'更新订单失败: {str(e)}', 'error')
        return redirect(url_for('order.page_order_edit', order_id=order_id))
    finally:
        db.close()

@order_bp.route('/<int:order_id>/delete', methods=['POST'])
def page_order_delete(order_id):
    """
    删除订单
    """
    try:
        db = session_factory()
        order_service = OrderService(db)
        
        success = order_service.delete_order(order_id)
        if success:
            flash('订单删除成功', 'success')
        else:
            flash('订单不存在', 'error')
        
        return redirect(url_for('order.page_order_list'))
        
    except Exception as e:
        flash(f'删除订单失败: {str(e)}', 'error')
        return redirect(url_for('order.page_order_list'))
    finally:
        db.close()

@order_bp.route('/<int:order_id>/status', methods=['POST'])
def page_order_update_status(order_id):
    """
    更新订单状态
    """
    try:
        db = session_factory()
        order_service = OrderService(db)
        
        status = request.form.get('status')
        if not status:
            flash('请选择状态', 'error')
            return redirect(url_for('order.page_order_list'))
        
        order = order_service.update_order_status(order_id, status)
        if order:
            flash('订单状态更新成功', 'success')
        else:
            flash('订单不存在', 'error')
        
        return redirect(url_for('order.page_order_list'))
        
    except Exception as e:
        flash(f'更新订单状态失败: {str(e)}', 'error')
        return redirect(url_for('order.page_order_list'))
    finally:
        db.close()

@order_bp.route('/charts')
def page_order_charts():
    """
    订单统计图表页面
    """
    try:
        db = session_factory()
        order_service = OrderService(db)
        
        # 获取所有订单
        result = order_service.get_orders(page=1, per_page=1000)
        orders = result['orders']
        
        # 创建统计图表
        charts = create_order_charts(orders)
        
        return render_template('order/charts.html', 
                             status_chart=charts.get('status_chart', ''),
                             customer_chart=charts.get('customer_chart', ''),
                             orders=orders)
        
    except Exception as e:
        flash(f'获取统计图表失败: {str(e)}', 'error')
        return render_template('order/charts.html', 
                             status_chart='', 
                             customer_chart='', 
                             orders=[])
    finally:
        db.close()

def create_order_charts(orders):
    """
    创建订单统计图表
    """
    try:
        if not orders:
            print("订单数据为空")
            return {'status_chart': '', 'customer_chart': ''}
        
        print(f"开始处理 {len(orders)} 条订单数据")
        
        # 按状态统计
        status_stats = {}
        customer_stats = {}
        
        for order in orders:
            status = order.get('status', '')
            customer = order.get('customer', '')
            
            # 统计状态分布
            if status:
                if status not in status_stats:
                    status_stats[status] = 0
                status_stats[status] += 1
            
            # 统计客户分布
            if customer:
                if customer not in customer_stats:
                    customer_stats[customer] = 0
                customer_stats[customer] += 1
        
        print(f"状态统计: {status_stats}")
        print(f"客户统计: {customer_stats}")
        
        # 翻译状态为中文
        translated_status_stats = StatusMapping.translate_order_status_dict(status_stats)
        
        # 取前10个客户
        top_customers = dict(sorted(customer_stats.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # 创建图表
        status_chart = ''
        customer_chart = ''
        
        if translated_status_stats:
            status_chart = MatplotlibCharts.create_pie_chart(
                title='订单状态分布',
                data=translated_status_stats
            )
            print("状态图表生成成功")
        
        if top_customers:
            customer_chart = MatplotlibCharts.create_bar_chart(
                title='客户订单数量TOP10',
                data=top_customers
            )
            print("客户图表生成成功")
        
        return {
            'status_chart': status_chart,
            'customer_chart': customer_chart
        }
        
    except Exception as e:
        print(f"创建订单图表失败: {e}")
        import traceback
        traceback.print_exc()
        return {'status_chart': '', 'customer_chart': ''}

@order_bp.route('/api/statistics')
def api_order_statistics():
    """
    订单统计API
    """
    try:
        db = session_factory()
        order_service = OrderService(db)
        
        stats = order_service.get_order_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
