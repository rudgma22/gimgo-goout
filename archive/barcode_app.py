from flask import Flask, request, jsonify, render_template, redirect, url_for
import pandas as pd
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import base64
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# 엑셀 파일 경로
excel_file_path = '../students.xlsx'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///log.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    barcode = db.Column(db.String(100))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))


with app.app_context():
    db.create_all()


def load_students():
    """엑셀 파일을 읽고 데이터프레임을 반환합니다."""
    return pd.read_excel(excel_file_path, dtype={'barcode': str, 'out date/time': str, 'in date/time': str})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    img_data = base64.b64decode(data['image'])
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # 이미지 전처리
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray)
    if barcodes:
        barcode = barcodes[0].data.decode('utf-8')
        return jsonify({'barcode': barcode})
    return jsonify({'error': 'No barcode found'})


@app.route('/check-authorization', methods=['POST'])
def check_authorization():
    df = load_students()  # 데이터베이스 업데이트
    data = request.json
    barcode = data.get('barcode')
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 바코드로 학생 정보 찾기
    student = df[df['barcode'] == barcode]

    if not student.empty:
        student_info = student.iloc[0]
        out_time_str = student_info['out date/time'].replace('T', ' ')
        in_time_str = student_info['in date/time'].replace('T', ' ')

        # 초 단위를 제거하여 시간 비교
        out_time = datetime.strptime(out_time_str[:16], '%Y-%m-%d %H:%M')
        in_time = datetime.strptime(in_time_str[:16], '%Y-%m-%d %H:%M')

        current_time = datetime.strptime(now, '%Y-%m-%d %H:%M')

        if out_time <= current_time <= in_time:
            message = f"{student_info['name']}은/는 외출이 가능합니다."
            status = '외출 가능'
        else:
            message = f"{student_info['name']}은/는 외출이 불가능합니다. 허용된 시간: {out_time_str} ~ {in_time_str}"
            status = '외출 불가능'
        registered = True
    else:
        message = "등록되지 않은 학생입니다."
        status = '등록되지 않음'
        registered = False

    log_entry = Log(name=student_info['name'], barcode=barcode, status=status)
    db.session.add(log_entry)
    db.session.commit()

    return jsonify(message=message, registered=registered, barcode=barcode)


@app.route('/result/<barcode>')
def result(barcode):
    df = load_students()  # 데이터베이스 업데이트
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 바코드로 학생 정보 찾기
    student = df[df['barcode'] == barcode]

    if not student.empty:
        student_info = student.iloc[0]
        out_time_str = student_info['out date/time'].replace('T', ' ')
        in_time_str = student_info['in date/time'].replace('T', ' ')

        # 초 단위를 제거하여 시간 비교
        out_time = datetime.strptime(out_time_str[:16], '%Y-%m-%d %H:%M')
        in_time = datetime.strptime(in_time_str[:16], '%Y-%m-%d %H:%M')

        current_time = datetime.strptime(now, '%Y-%m-%d %H:%M')

        if out_time <= current_time <= in_time:
            message = f"{student_info['name']}은/는 외출이 가능합니다."
        else:
            message = f"{student_info['name']}은/는 외출이 불가능합니다. 허용된 시간: {out_time_str} ~ {in_time_str}"
    else:
        message = "등록되지 않은 학생입니다."

    return render_template('result.html', message=message)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/monthly-stats')
def monthly_stats():
    stats = db.session.query(
        func.strftime('%Y-%m', Log.date_time).label('month'),
        func.count(Log.id).label('count')
    ).group_by('month').all()

    labels = [row.month for row in stats]
    data = [row.count for row in stats]

    return jsonify(labels=labels, data=data)


@app.route('/api/class-stats')
def class_stats():
    df = load_students()
    logs = db.session.query(Log).all()

    class_counts = {cls: 0 for cls in df['class'].unique()}
    for log in logs:
        student_class = df[df['barcode'] == log.barcode]['class'].values[0]
        if student_class in class_counts:
            class_counts[student_class] += 1

    labels = list(class_counts.keys())
    data = list(class_counts.values())

    return jsonify(labels=labels, data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
