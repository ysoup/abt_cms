from flask import session


# 菜单相关内容， 在需要时调用，会生成菜单相关数据
def menu_html(request):
    current_url = request.path
    menu_list = session.get('menu_list')
    pass