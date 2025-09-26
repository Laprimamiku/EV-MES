# -*- coding: utf-8 -*-
"""
库存管理视图
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from src.services.inventory_service import InventoryService
from src.models.database import session_factory
import os
from src.config import QRCODE_DIR
from src.utils.matplotlib_charts import MatplotlibCharts
from src.utils.status_mapping import StatusMapping

# 创建蓝图
inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
def page_inventory_list():
    """
    库存列表页面
    """
    try:
        db = session_factory()
        inventory_service = InventoryService(db)
        
        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        
        # 获取库存列表
        result = inventory_service.get_items(page=page, per_page=per_page, search=search)
        
        # 获取统计信息
        stats = inventory_service.get_inventory_statistics()
        
        return render_template('inventory/list.html', 
                             items=result['items'],
                             pagination=result,
                             search=search,
                             stats=stats)
    except Exception as e:
        flash(f'获取库存列表失败: {str(e)}', 'error')
        return render_template('inventory/list.html', items=[], pagination={}, search='', stats={})
    finally:
        db.close()

@inventory_bp.route('/create', methods=['GET', 'POST'])
def page_inventory_create():
    """
    创建库存物料页面
    """
    if request.method == 'GET':
        return render_template('inventory/form.html', item=None)
    
    try:
        db = session_factory()
        inventory_service = InventoryService(db)
        
        # 获取表单数据
        item_data = {
            'part_code': request.form.get('part_code'),
            'name': request.form.get('name'),
            'spec': request.form.get('spec'),
            'quantity': int(request.form.get('quantity', 0)),
            'location': request.form.get('location')
        }
        
        # 创建库存物料
        item = inventory_service.create_item(item_data)
        
        flash('库存物料创建成功', 'success')
        return redirect(url_for('inventory.page_inventory_list'))
        
    except Exception as e:
        flash(f'创建库存物料失败: {str(e)}', 'error')
        return render_template('inventory/form.html', item=None)
    finally:
        db.close()

@inventory_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
def page_inventory_edit(item_id):
    """
    编辑库存物料页面
    """
    try:
        db = session_factory()
        inventory_service = InventoryService(db)
        
        if request.method == 'GET':
            item = inventory_service.get_item_by_id(item_id)
            if not item:
                flash('库存物料不存在', 'error')
                return redirect(url_for('inventory.page_inventory_list'))
            
            return render_template('inventory/form.html', item=item.to_dict())
        
        # 获取表单数据
        item_data = {
            'part_code': request.form.get('part_code'),
            'name': request.form.get('name'),
            'spec': request.form.get('spec'),
            'quantity': int(request.form.get('quantity', 0)),
            'location': request.form.get('location')
        }
        
        # 更新库存物料
        item = inventory_service.update_item(item_id, item_data)
        if not item:
            flash('库存物料不存在', 'error')
            return redirect(url_for('inventory.page_inventory_list'))
        
        flash('库存物料更新成功', 'success')
        return redirect(url_for('inventory.page_inventory_list'))
        
    except Exception as e:
        flash(f'更新库存物料失败: {str(e)}', 'error')
        return redirect(url_for('inventory.page_inventory_edit', item_id=item_id))
    finally:
        db.close()

@inventory_bp.route('/<int:item_id>/delete', methods=['POST'])
def page_inventory_delete(item_id):
    """
    删除库存物料
    """
    try:
        db = session_factory()
        inventory_service = InventoryService(db)
        
        success = inventory_service.delete_item(item_id)
        if success:
            flash('库存物料删除成功', 'success')
        else:
            flash('库存物料不存在', 'error')
        
        return redirect(url_for('inventory.page_inventory_list'))
        
    except Exception as e:
        flash(f'删除库存物料失败: {str(e)}', 'error')
        return redirect(url_for('inventory.page_inventory_list'))
    finally:
        db.close()

@inventory_bp.route('/<int:item_id>/qrcode')
def page_inventory_qrcode(item_id):
    """
    查看二维码
    """
    try:
        db = session_factory()
        inventory_service = InventoryService(db)
        
        item = inventory_service.get_item_by_id(item_id)
        if not item:
            flash('库存物料不存在', 'error')
            return redirect(url_for('inventory.page_inventory_list'))
        
        # 检查二维码文件是否存在
        qr_path = os.path.join(QRCODE_DIR, f"{item.part_code}.png")
        if not os.path.exists(qr_path):
            # 重新生成二维码
            item.generate_qrcode()
        
        return send_file(qr_path, mimetype='image/png')
        
    except Exception as e:
        flash(f'获取二维码失败: {str(e)}', 'error')
        return redirect(url_for('inventory.page_inventory_list'))
    finally:
        db.close()

@inventory_bp.route('/<int:item_id>/quantity', methods=['POST'])
def page_inventory_update_quantity(item_id):
    """
    更新库存数量
    """
    try:
        db = session_factory()
        inventory_service = InventoryService(db)
        
        quantity = int(request.form.get('quantity', 0))
        if quantity < 0:
            flash('库存数量不能为负数', 'error')
            return redirect(url_for('inventory.page_inventory_list'))
        
        item = inventory_service.update_quantity(item_id, quantity)
        if item:
            flash('库存数量更新成功', 'success')
        else:
            flash('库存物料不存在', 'error')
        
        return redirect(url_for('inventory.page_inventory_list'))
        
    except Exception as e:
        flash(f'更新库存数量失败: {str(e)}', 'error')
        return redirect(url_for('inventory.page_inventory_list'))
    finally:
        db.close()

@inventory_bp.route('/charts')
def page_inventory_charts():
    """
    库存统计图表页面
    """
    try:
        db = session_factory()
        inventory_service = InventoryService(db)
        
        # 获取所有库存物料
        result = inventory_service.get_items(page=1, per_page=1000)
        items = result['items']
        
        # 创建统计图表
        charts = create_inventory_charts(items)
        
        return render_template('inventory/charts.html', 
                             location_chart=charts.get('location_chart', ''),
                             quantity_chart=charts.get('quantity_chart', ''),
                             category_chart=charts.get('category_chart', ''),
                             items=items)
        
    except Exception as e:
        flash(f'获取统计图表失败: {str(e)}', 'error')
        return render_template('inventory/charts.html', 
                             location_chart='', 
                             quantity_chart='', 
                             category_chart='', 
                             items=[])
    finally:
        db.close()

def create_inventory_charts(items):
    """
    创建库存统计图表
    """
    try:
        if not items:
            print("库存数据为空")
            return {'location_chart': '', 'quantity_chart': '', 'category_chart': ''}
        
        print(f"开始处理 {len(items)} 条库存数据")
        
        # 按位置统计
        location_stats = {}
        quantity_stats = {}
        category_stats = {}
        
        for item in items:
            location = item.get('location', '') or '未分配'
            quantity = item.get('quantity', 0)
            part_code = item.get('part_code', '')
            
            # 统计位置分布
            if location not in location_stats:
                location_stats[location] = 0
            location_stats[location] += 1
            
            # 统计数量分布（按数量区间）
            if quantity >= 100:
                qty_range = '100+'
            elif quantity >= 50:
                qty_range = '50-99'
            elif quantity >= 20:
                qty_range = '20-49'
            elif quantity >= 10:
                qty_range = '10-19'
            else:
                qty_range = '0-9'
            
            if qty_range not in quantity_stats:
                quantity_stats[qty_range] = 0
            quantity_stats[qty_range] += 1
            
            # 统计类别分布（按零件代码前缀）
            if part_code and len(part_code) >= 2:
                category = part_code[:2]
            else:
                category = '其他'
            
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        print(f"位置统计: {location_stats}")
        print(f"数量统计: {quantity_stats}")
        print(f"类别统计: {category_stats}")
        
        # 创建图表
        location_chart = ''
        quantity_chart = ''
        category_chart = ''
        
        if location_stats:
            location_chart = MatplotlibCharts.create_bar_chart(
                title='库存位置分布',
                data=location_stats
            )
            print("位置图表生成成功")
        
        if quantity_stats:
            quantity_chart = MatplotlibCharts.create_pie_chart(
                title='库存数量分布',
                data=quantity_stats
            )
            print("数量图表生成成功")
        
        if category_stats:
            category_chart = MatplotlibCharts.create_bar_chart(
                title='零件类别分布',
                data=category_stats
            )
            print("类别图表生成成功")
        
        return {
            'location_chart': location_chart,
            'quantity_chart': quantity_chart,
            'category_chart': category_chart
        }
        
    except Exception as e:
        print(f"创建库存图表失败: {e}")
        import traceback
        traceback.print_exc()
        return {'location_chart': '', 'quantity_chart': '', 'category_chart': ''}

@inventory_bp.route('/api/statistics')
def api_inventory_statistics():
    """
    库存统计API
    """
    try:
        db = session_factory()
        inventory_service = InventoryService(db)
        
        stats = inventory_service.get_inventory_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
