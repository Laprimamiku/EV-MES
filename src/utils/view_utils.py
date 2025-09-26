"""
视图工具模块
提供通用的视图功能和模板渲染
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from src.utils.db_decorators import with_database_and_services
from src.utils.pagination_utils import get_pagination_data


class BaseView:
    """
    基础视图类
    提供通用的CRUD操作模板
    """
    
    def __init__(self, service_name, template_dir, blueprint_name):
        self.service_name = service_name
        self.template_dir = template_dir
        self.blueprint_name = blueprint_name
    
    def list_view(self, search_fields=None, extra_data=None):
        """
        列表视图装饰器
        """
        def decorator(func):
            @with_database_and_services
            def wrapper(db, services, *args, **kwargs):
                try:
                    # 获取分页参数
                    page = int(request.args.get('page', 1))
                    per_page = int(request.args.get('per_page', 10))
                    search = request.args.get('search', '')
                    
                    # 获取服务
                    service = services[self.service_name]
                    
                    # 获取列表数据
                    result = service.get_items(page=page, per_page=per_page, search=search)
                    
                    # 获取统计信息
                    stats = service.get_statistics()
                    
                    # 准备模板数据
                    template_data = {
                        'items': result.get('items', []),
                        'pagination': result,
                        'search': search,
                        'stats': stats
                    }
                    
                    # 添加额外数据
                    if extra_data:
                        template_data.update(extra_data)
                    
                    # 调用原函数获取额外数据
                    if func:
                        extra_template_data = func(db, services, *args, **kwargs)
                        if extra_template_data:
                            template_data.update(extra_template_data)
                    
                    return render_template(f'{self.template_dir}/list.html', **template_data)
                    
                except Exception as e:
                    flash(f'获取列表失败: {str(e)}', 'error')
                    return render_template(f'{self.template_dir}/list.html', 
                                         items=[], 
                                         pagination={}, 
                                         search='', 
                                         stats={})
            return wrapper
        return decorator
    
    def create_view(self, form_fields, redirect_route):
        """
        创建视图装饰器
        """
        def decorator(func):
            @with_database_and_services
            def wrapper(db, services, *args, **kwargs):
                try:
                    if request.method == 'GET':
                        # 准备表单数据
                        template_data = {}
                        if func:
                            template_data = func(db, services, *args, **kwargs)
                        return render_template(f'{self.template_dir}/form.html', 
                                             item=None, **template_data)
                    
                    # 处理POST请求
                    service = services[self.service_name]
                    
                    # 获取表单数据
                    form_data = {}
                    for field in form_fields:
                        form_data[field] = request.form.get(field)
                    
                    # 创建记录
                    item = service.create_item(form_data)
                    
                    flash(f'{self.service_name.title()}创建成功', 'success')
                    return redirect(url_for(redirect_route))
                    
                except Exception as e:
                    flash(f'创建{self.service_name}失败: {str(e)}', 'error')
                    return redirect(url_for(f'{self.blueprint_name}.page_{self.service_name}_create'))
            return wrapper
        return decorator
    
    def edit_view(self, form_fields, redirect_route):
        """
        编辑视图装饰器
        """
        def decorator(func):
            @with_database_and_services
            def wrapper(db, services, item_id, *args, **kwargs):
                try:
                    service = services[self.service_name]
                    
                    if request.method == 'GET':
                        # 获取记录
                        item = service.get_item_by_id(item_id)
                        if not item:
                            flash(f'{self.service_name.title()}不存在', 'error')
                            return redirect(url_for(redirect_route))
                        
                        # 准备表单数据
                        template_data = {'item': item}
                        if func:
                            extra_data = func(db, services, item_id, *args, **kwargs)
                            if extra_data:
                                template_data.update(extra_data)
                        
                        return render_template(f'{self.template_dir}/form.html', **template_data)
                    
                    # 处理POST请求
                    # 获取表单数据
                    form_data = {}
                    for field in form_fields:
                        form_data[field] = request.form.get(field)
                    
                    # 更新记录
                    item = service.update_item(item_id, form_data)
                    
                    flash(f'{self.service_name.title()}更新成功', 'success')
                    return redirect(url_for(redirect_route))
                    
                except Exception as e:
                    flash(f'更新{self.service_name}失败: {str(e)}', 'error')
                    return redirect(url_for(f'{self.blueprint_name}.page_{self.service_name}_edit', 
                                          item_id=item_id))
            return wrapper
        return decorator
    
    def delete_view(self, redirect_route):
        """
        删除视图装饰器
        """
        def decorator(func):
            @with_database_and_services
            def wrapper(db, services, item_id, *args, **kwargs):
                try:
                    service = services[self.service_name]
                    
                    # 删除记录
                    success = service.delete_item(item_id)
                    
                    if success:
                        flash(f'{self.service_name.title()}删除成功', 'success')
                    else:
                        flash(f'{self.service_name.title()}不存在', 'error')
                    
                    return redirect(url_for(redirect_route))
                    
                except Exception as e:
                    flash(f'删除{self.service_name}失败: {str(e)}', 'error')
                    return redirect(url_for(redirect_route))
            return wrapper
        return decorator


def render_list_template(template_path, items, pagination, search='', stats=None, **extra_data):
    """
    渲染列表模板的通用函数
    """
    template_data = {
        'items': items,
        'pagination': pagination,
        'search': search,
        'stats': stats or {}
    }
    template_data.update(extra_data)
    return render_template(template_path, **template_data)


def handle_form_submission(service, form_fields, success_message, error_message, redirect_route):
    """
    处理表单提交的通用函数
    """
    try:
        # 获取表单数据
        form_data = {}
        for field in form_fields:
            form_data[field] = request.form.get(field)
        
        # 创建或更新记录
        if hasattr(service, 'create_item'):
            item = service.create_item(form_data)
        else:
            item = service.update_item(form_data)
        
        flash(success_message, 'success')
        return redirect(url_for(redirect_route))
        
    except Exception as e:
        flash(f'{error_message}: {str(e)}', 'error')
        return None
