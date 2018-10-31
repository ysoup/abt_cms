from sqlalchemy.orm import relationship
from app import db
from datetime import *



class User(db.Model):
    """用户"""
    __bind_key__ = 'permission_manage'
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), unique=True, index=True)
    # username = db.Column(db.String(32), unique=True, index=True)
    # phone_no = db.Column(db.String(32), unique=True, index=True)
    password = db.Column(db.String(32))
    create_time = db.Column(db.DateTime, default=datetime.now)
    # roles与生成表结构无关，仅用于查询
    roles = relationship('Role', secondary='user2role', backref='role_users', passive_deletes=True)

    def __str__(self):
        return self.email


class Permission(db.Model):
    """权限"""
    __bind_key__ = 'permission_manage'
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(32))
    url = db.Column(db.String(64))
    code = db.Column(db.String(32), default='list')

    menu_gp = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=True)
    group= db.Column(db.Integer, db.ForeignKey('group.id'))

    # 仅用于查询,不会生成数据库实际字段
    roles = relationship('Role', secondary='role2permission', backref='role_pers', passive_deletes=True)
    per_menu_gp = relationship('Permission', remote_side=[id])  # 自关联
    per_group = relationship('Group', backref='group_per')      # 可通过permission.per_group拿到当前权限url所在的group对象

    def __str__(self):
        return self.url


class Menu(db.Model):
    """菜单"""
    __bind_key__ = 'permission_manage'
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(32), unique=True)

    def __str__(self):
        return self.title


class Group(db.Model):
    """url权限组"""
    __bind_key__ = 'permission_manage'
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caption = db.Column(db.String(32))
    menu = db.Column(db.Integer, db.ForeignKey('menu.id', ondelete='CASCADE', onupdate='CASCADE'))

    # 可通过权限组对象获取到所在菜单，backref可以通过menu对象获取到当前所属的权限组，下同。
    gp_menu = relationship('Menu', backref='menu_gp')

    def __str__(self):
        return self.caption


class Role(db.Model):
    """角色"""
    __bind_key__ = 'permission_manage'
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(32))

    permission = relationship('Permission', backref='per_roles', passive_deletes=True)
    users = relationship('User', secondary='user2role', backref='user_roles', passive_deletes=True)
    def __str__(self):
        return self.title

    def __repr__(self):
        return 'Role: %s'%self.title

# user2role = db.Table('user2role',
#                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#                      db.Column('role_id', db.Integer, db.ForeignKey('role.id')))
# role2permission = db.Table('role2permission',
#                            db.Column('role_id', db.Integer, db.ForeignKey('user.id')),
#                            db.Column('permission_id', db.Integer, db.ForeignKey('permission_id')))

class User2Role(db.Model):
    """用户M2M角色"""
    __bind_key__ = 'permission_manage'
    __tablename__ = 'user2role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE', onupdate='CASCADE'))

    def __str__(self):
        return 'user_id: %s, role_id: %s',(str(self.user_id), str(self.role_id))


class Role2Permission(db.Model):
    '''角色M2M权限'''
    __bind_key__ = 'permission_manage'
    __tablename__ = 'role2permission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE', onupdate='CASCADE'))
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', ondelete='CASCADE', onupdate='CASCADE'))

    def __str__(self):
        return 'role_id: %s, permission_id: %s',(str(self.role_id, str(self.permission_id)))
