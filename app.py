from flask import Flask, render_template, redirect, url_for, flash, session, request
from models import db, User, Server
from forms import LoginForm, RegisterForm
from utils import hash_password, verify_password
from functools import wraps
from flask_migrate import Migrate
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SECRET_KEY'] = "devops"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'cmdb.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录！')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


@app.route("/")
@login_required
def index():
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and verify_password(user.password_hash, form.password.data):
            session['user_id'] = user.id
            flash('登录成功！')
            return redirect(url_for('index'))
        flash('用户名或密码错误！')
    return render_template('login.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('用户已存在！')
            return render_template('register.html', form=form)
        new_user = User(username=form.username.data, password_hash=hash_password(form.password.data))
        db.session.add(new_user)
        db.session.commit()
        flash("注册成功，请登录!")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('已退出登录！')
    return redirect(url_for('login'))


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
    return render_template('server_add.html')


@app.route('/server/edit/<int:server_id>', methods=['GET', 'POST'])
@login_required
def server_edit(server_id):
    server = Server.query.filter_by(id=server_id, user_id=session['user_id']).first_or_404()
    if request.method == 'POST':
        server.hostname = request.form.get('hostname')
        server.ip = request.form.get('ip')
        server.os_type = request.form.get('os_type')
        server.desc = request.form.get('desc')
        db.session.commit()
        flash('修改成功！')
        return redirect(url_for('server_list'))
    return render_template('server_edit.html', server=server)


@app.route('/server/delete/<int:server_id>')
@login_required
def server_delete(server_id):
    server = Server.query.filter_by(id=server_id, user_id=session['user_id']).first_or_404()
    db.session.delete(server)
    db.session.commit()
    flash('删除成功！')
    return redirect(url_for('server_list'))
