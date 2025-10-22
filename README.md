# cmdb_project
Flask CMDB练手项目

整体架构概述

这个项目的核心目的是实现一个基于 Flask 的服务器管理系统（CMDB），用户可以进行登录、注册、管理服务器等操作。代码中涉及到 身份验证、权限控制、数据库操作 等关键部分。整体架构包括：

Flask 路由与视图函数：负责请求的处理和响应。

数据库设计（SQLAlchemy）：用于存储用户和服务器的数据。

表单处理（Flask-WTF）：用于处理用户输入的数据。

权限管理（Session & 自定义装饰器）：确保用户只能操作自己的服务器数据。

模板渲染（Jinja2）：呈现前端页面。

代码结构
- app.py                     # Flask应用的主文件
- models.py                  # 数据库模型，定义数据库表结构
- forms.py                   # 表单定义，用于处理用户输入
- utils.py                   # 实用工具函数（如哈希密码等）
- templates/                 # 存放 HTML 模板的目录
    - login.html
    - register.html
    - index.html
    - server_list.html
    - server_add.html
    - server_edit.html
- migrations/                # 数据库迁移目录（Flask-Migrate）

每个部分的功能
1. Flask 应用和路由配置 (app.py)

Flask 是一个轻量级的 Web 框架，主要用来处理 Web 请求和响应。在这个文件中，我们定义了所有的路由以及如何处理用户请求。

主要路由：

/: 主页路由，要求用户登录后才能访问（通过 login_required 装饰器保护）。

/login: 登录页面，用户通过表单输入用户名和密码进行登录。

/register: 注册页面，用户可以注册新账号。

/logout: 退出登录，清除会话信息。

/server/list: 显示用户自己的服务器列表。

/server/add: 添加新服务器。

/server/edit/<int:server_id>: 编辑服务器信息。

/server/delete/<int:server_id>: 删除服务器。

2. 数据库模型 (models.py)

数据库模型定义了我们需要存储的数据结构。我们使用 SQLAlchemy 来管理与数据库的交互。

User 模型：

存储用户的 username 和 password_hash，还可以存储用户的角色信息（role），在本项目中角色默认是 user，可以后期扩展为管理员等角色。

用户与服务器表之间是 一对多 的关系，一个用户可以管理多个服务器。

Server 模型：

存储服务器的 hostname、ip、os_type 和 desc 信息。

每个服务器通过 user_id 与用户关联，确保每个服务器只能被相关的用户操作。

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default='user')  # 角色字段

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    os_type = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='servers')

3. 表单处理与数据验证（forms.py）

在 Flask 中，Flask-WTF 提供了一个很方便的表单处理机制，包括数据验证、CSRF 保护等。在这个文件中，我们定义了 LoginForm 和 RegisterForm，并通过它们来验证用户的输入。

主要表单：

LoginForm: 包含 username 和 password 两个字段，进行用户登录验证。

RegisterForm: 包含 username 和 password 两个字段，进行用户注册。

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

4. 权限管理 (login_required 装饰器)

为了确保只有登录的用户才能访问某些页面，我们使用了一个自定义的装饰器 login_required。它会检查当前会话是否有 user_id，如果没有，则重定向到登录页面。如果用户登录了，才允许访问被保护的页面。

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录！')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

5. 服务器管理（增删改查）
1. 服务器列表 (server_list):

显示当前用户的服务器，过滤条件是 user_id。每个用户只能看到自己添加的服务器。

2. 添加服务器 (server_add):

用户填写表单，输入服务器信息，保存到数据库，并与当前登录用户关联（user_id）。

3. 编辑服务器 (server_edit):

用户编辑自己添加的服务器。通过 server_id 和 user_id 检查是否是当前用户的服务器，防止越权编辑。

4. 删除服务器 (server_delete):

删除当前用户的服务器，同样通过 server_id 和 user_id 防止删除其他用户的服务器。

6. 前端页面渲染（templates 目录）

Flask 使用 Jinja2 模板引擎来渲染 HTML 页面。我们在 templates/ 目录下创建了各种 HTML 页面，如登录页、注册页、服务器管理页等。

登录页 (login.html)、注册页 (register.html)：提供用户输入表单。

服务器列表页 (server_list.html)：显示当前用户的服务器。

服务器添加页 (server_add.html) 和编辑页 (server_edit.html)：提供表单让用户编辑或添加服务器。

<!-- login.html -->
<form method="POST">
    {{ form.hidden_tag() }}
    {{ form.username.label }} {{ form.username() }}
    {{ form.password.label }} {{ form.password() }}
    <button type="submit">Login</button>
</form>

设计原因与思路

分层架构：

models.py 负责定义数据库和数据结构。

app.py 负责处理用户请求，路由和业务逻辑。

forms.py 负责表单验证和数据输入。

templates/ 负责渲染前端界面。

权限控制：

使用 session 管理用户登录状态，保证每个请求都能识别当前用户。

通过 login_required 装饰器保护敏感页面，防止未登录用户访问。

在增删改查操作中，加入 user_id 校验，确保用户只能操作自己的数据。

Flask-Migrate：用于数据库迁移，简化了数据库表结构的更新，避免手动修改数据库结构。

SQLAlchemy 关系映射：通过 user_id 将 Server 和 User 两个模型关联，确保每个服务器都归某个用户管理。

总结

整体架构中，主要是通过 Flask 路由处理用户请求，SQLAlchemy 管理数据库，Flask-WTF 处理表单验证，Flask-Migrate 管理数据库迁移，最后通过 session 和装饰器来处理权限控制，确保每个用户只能看到自己的数据。