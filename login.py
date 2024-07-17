from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models import db, User

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User.query.filter_by(username=username, role=role).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            session['user_class'] = user.user_class
            session['role'] = user.role

            if role == 'student':
                return redirect(url_for('outing.student_home'))
            else:
                return redirect(url_for('outing.class_page', class_name=user.user_class))

        flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
        return redirect(url_for('login.login'))

    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_class', None)
    session.pop('role', None)
    return redirect(url_for('login.login'))

@login_bp.route('/', methods=['GET'])
def home_page():
    if 'username' in session:
        if session['role'] == 'student':
            return redirect(url_for('outing.student_home'))
        else:
            return redirect(url_for('outing.class_page', class_name=session['user_class']))
    return redirect(url_for('login.login'))
