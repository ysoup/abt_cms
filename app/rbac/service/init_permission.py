

def init_permission(user, request, session):
    permission_url_list = []

    roles = user.roles
    for role in roles:
        permissions = role.role_pers
        for permission in permissions:
            if permission and permission.per_group:
                data = {}
                data['permission_menu_id'] = permission.per_group.gp_menu.id        # 权限所属菜单id
                data['permission_menu_title'] = permission.per_group.gp_menu.title  # 权限所属菜单title
                data['permission_gp_id'] = permission.per_group.id                  # 权限所属分组id
                data['permission_gp_caption'] = permission.per_group.caption        # 权限所属分组caption
                data['url_title'] = permission.title                                # 权限title
                data['per_url'] = permission.url                                    # 权限名称对应的url
                data['url_code'] = permission.code                                  # 权限名称对应的code
                data['menu_gp'] = permission.per_menu_gp                            # 若为None，则为menu选项。
                permission_url_list.append(data)

    # 一个用户可能涉及多个角色，角色对应的权限url可能会重复，需要去重。
    new_permission_url_list = []
    for permission_url_dic in permission_url_list:
        if permission_url_dic not in new_permission_url_list:
            new_permission_url_list.append(permission_url_dic)
    permission_url_list = new_permission_url_list
    print('init_permission28===permission_url_list', permission_url_list)

    l = [{'permission_menu_id':1, 'permission_menu_title':'菜单一',
          'permission_gp_id':1, 'permission_gp_caption':'用户信息',
          'url_title':'用户列表', 'per_url':'/userinfo/', 'url_code':'list'}]

    # 1. 页面添加、编辑、删除 显示相关
    # Ps: test_permission_dic = {'1': {'code': [], 'per_url': []}, '2': {'code': [], 'per_url': []}}
    show_per_dic = {}
    for each_dic in permission_url_list:
        if each_dic['permission_gp_id'] in show_per_dic:
            show_per_dic[each_dic['permission_gp_id']]['code'].append(each_dic['url_code'])
            show_per_dic[each_dic['permission_gp_id']]['per_url'].append(each_dic['per_url'])
        else:
            show_per_dic[each_dic['permission_gp_id']] = {'code':[each_dic['url_code'], ],
                                                          'per_url':[each_dic['per_url']]}
    print('show_per_dic44===', show_per_dic)
    session['show_per_dic'] = show_per_dic

    # 2. 页面菜单相关
    # Ps: menu_list = [{'menu_id':1, 'menu_title':'菜单一', 'url_title':'用户列表', 'per_url':'/userinfo/', 'menu_gp':None, 'active':False, }]
    menu_list = []
    for dic in permission_url_list:
        if not dic['menu_gp']:
            data = {}
            data['menu_id'] = dic['permission_menu_id']            # 菜单id
            data['menu_title'] = dic['permission_menu_title']      # 菜单title
            data['permission_menu_gp'] = dic['menu_gp']            # 属于哪个菜单组下
            data['active'] = False
            menu_list.append(data)
    session['menu_list'] = menu_list