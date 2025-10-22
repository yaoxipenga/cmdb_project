# cmdb_project
Flask CMDB练手项目

🧩 项目整体结构

Flask 框架：作为 Web 框架，处理路由、请求、渲染模板等。

SQLAlchemy ORM：作为数据库模型框架，负责与 SQLite 数据库交互，保存和读取数据。

Flask-Migrate：用于数据库迁移（用于修改数据库结构时自动处理变动）。

Flask-Session：用来管理用户登录状态，基于会话管理。

🧩 开发步骤和核心功能
1. 数据库模型设计（models.py）

我们首先定义了数据库的结构，主要涉及两张表：

User（用户表）：存储用户名、密码和角色等。

Server（服务器表）：存储服务器的相关信息（如：主机名、IP、操作系统、描述等），同时关联 user_id，来确定每个服务器属于哪个用户。

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

2. 用户身份验证功能（登录、注册、登出）

用户通过 LoginForm 进行登录，表单提交后验证用户信息（通过哈希密码匹配）。

用户通过 RegisterForm 注册新账号，验证用户名是否重复，成功后存入数据库。

使用 Flask 的 session 存储用户的登录状态，保证每次请求都可以识别当前登录的用户。

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and verify_password(user.password_hash, form.password.data):
            session['user_id'] = user.id
            flash('登录成功！')
            return redirect(url_for('index'))

3. 用户权限控制（login_required）

在一些敏感页面（如：服务器管理页面），我们使用了 @login_required 装饰器，确保只有登录的用户才能访问。

如果用户未登录，系统会跳转到登录页面。

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录！')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated

4. 增删改查操作（服务器管理）

添加服务器：用户在表单中填写服务器信息，提交后保存到数据库中，并将该服务器与当前用户 (user_id) 关联。

查看服务器列表：只有当前用户的服务器才会显示出来，防止不同用户看到彼此的服务器。

编辑服务器：通过 user_id 过滤，确保用户只能编辑自己的服务器。

删除服务器：同样通过 user_id 过滤，删除属于该用户的服务器。

@app.route('/server/list')
@login_required
def server_list():
    user_id = session.get('user_id')
    servers = Server.query.filter_by(user_id=user_id).all()
    return render_template('server_list.html', servers=servers)

@app.route('/server/add', methods=['GET', 'POST'])
@login_required
def server_add():
    if request.method == 'POST':
        new_server = Server(
            hostname=request.form['hostname'],
            ip=request.form['ip'],
            os_type=request.form['os_type'],
            desc=request.form['desc'],
            user_id=session['user_id']
        )
        db.session.add(new_server)
        db.session.commit()
        flash('添加成功!')
        return redirect(url_for('server_list'))

5. 用户权限隔离（防止越权）

权限隔离：通过 filter_by(user_id=session['user_id']) 保证每个用户只能操作自己的服务器，防止了越权访问。

进一步防止越权：在编辑和删除操作时，通过 filter_by(id=server_id, user_id=session['user_id']) 限制只有自己的服务器才可以编辑和删除。

@app.route('/server/edit/<int:server_id>', methods=['GET', 'POST'])
@login_required
def server_edit(server_id):
    server = Server.query.filter_by(id=server_id, user_id=session['user_id']).first_or_404()

🧩 关键步骤总结

数据库设计：确定了 User 和 Server 两张表及其字段，确保每个服务器与用户一一关联。

身份验证：通过 Flask session 来管理登录状态，LoginForm 和 RegisterForm 进行表单验证。

权限控制：使用 login_required 装饰器保护路由，防止未登录的用户访问。

增删改查操作：实现服务器的增删改查，确保每个用户只能管理自己的服务器。

权限隔离：在 edit 和 delete 操作中使用 user_id 校验，防止越权。