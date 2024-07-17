from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models import db, User

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        if role == 'student':
            name = request.form.get('student_name')
            grade = request.form.get('grade')
            user_class = request.form.get('class') if grade != '기타' else None
            student_id = request.form.get('student_id')
            barcode = request.form.get('barcode')
        else:
            name = request.form.get('teacher_name')
            grade = request.form.get('teacher_grade')
            user_class = request.form.get('teacher_class') if grade != '기타' else None
            student_id = None
            barcode = None

        if role == 'student' and not barcode:
            flash('학생은 바코드 정보를 입력해야 합니다.', 'error')
            return redirect(url_for('register.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(
            username=username,
            password=hashed_password,
            user_class=user_class,
            role=role,
            barcode=barcode
        )

        db.session.add(new_user)
        db.session.commit()

        flash('회원가입이 완료되었습니다. 이제 로그인하세요.', 'success')
        return redirect(url_for('login.login'))

    return render_template('register.html')
