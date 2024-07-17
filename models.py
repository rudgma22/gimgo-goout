from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    user_class = db.Column(db.String(50), nullable=False)
    barcode = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(50), nullable=False)

class OutingRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    student_name = db.Column(db.String(150), nullable=False)
    student_class = db.Column(db.String(50), nullable=False)
    barcode = db.Column(db.String(50), nullable=False)
    out_time = db.Column(db.String(50), nullable=False)
    in_time = db.Column(db.String(50), nullable=False)
    approved = db.Column(db.Boolean, default=False)
