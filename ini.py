from werkzeug.security import generate_password_hash
from student_management_app import db, User, app

# 애플리케이션 컨텍스트 내에서 데이터베이스 작업 수행
with app.app_context():
    # 데이터베이스 초기화
    db.drop_all()
    db.create_all()

    # 관리자 사용자 추가
    admin_username = "admin"
    admin_password = "admin_password"
    admin_class = "admin_class"  # 관리자는 모든 반을 관리할 수 있도록 설정
    admin_role = "teacher"

    hashed_admin_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
    admin_user = User(username=admin_username, password=hashed_admin_password, user_class=admin_class, role=admin_role)

    db.session.add(admin_user)
    db.session.commit()

    # 기본 학생 추가
    student_username = "student"
    student_password = "student_password"
    student_class = "1반"
    student_role = "student"
    student_barcode = "1234567890"  # 예제 바코드 정보

    hashed_student_password = generate_password_hash(student_password, method='pbkdf2:sha256')
    student_user = User(username=student_username, password=hashed_student_password, user_class=student_class, role=student_role, barcode=student_barcode)

    db.session.add(student_user)
    db.session.commit()

    print("Database initialized and default users created!")
