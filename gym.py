from flask import Flask, jsonify, request, g, render_template
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

db = SQLAlchemy(app)

MEMBERSHIP_PLANS = ['Basic', 'Premium', 'Monthly', 'Yearly']
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'
active_tokens = set()

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    plan = db.Column(db.String(50), nullable=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'), nullable=True)
    payments = db.relationship('Payment', backref='member', lazy=True)
    attendance = db.relationship('Attendance', backref='member', lazy=True)

class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    members = db.relationship('Member', backref='trainer', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'amount': self.amount,
            'status': self.status,
            'recorded_at': self.recorded_at.isoformat()
        }

with app.app_context():
    db.create_all()


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        if not token or token not in active_tokens:
            return jsonify({'error': 'Unauthorized'}), 401
        g.admin = ADMIN_USERNAME
        return func(*args, **kwargs)
    return wrapper


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if data.get('username') == ADMIN_USERNAME and data.get('password') == ADMIN_PASSWORD:
        token = str(uuid.uuid4())
        active_tokens.add(token)
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/')
def home():
    return jsonify({'message': 'Welcome to ACEest Fitness & Gym Management System'})


@app.route('/ui')
def ui():
    return render_template('index.html')


@app.route('/members', methods=['GET', 'POST'])
@require_auth
def members_route():
    if request.method == 'GET':
        search = request.args.get('search', '').strip().lower()
        plan = request.args.get('plan', '').strip()

        query = Member.query
        if search:
            query = query.filter(Member.name.ilike(f'%{search}%'))
        if plan:
            query = query.filter(Member.plan == plan)

        members = query.all()
        return jsonify([{
            'id': m.id,
            'name': m.name,
            'email': m.email,
            'plan': m.plan,
            'trainer': m.trainer.name if m.trainer else None
        } for m in members])

    body = request.get_json() or {}
    name = body.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400

    member = Member(
        name=name,
        email=body.get('email'),
        plan=body.get('plan') if body.get('plan') in MEMBERSHIP_PLANS else None
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({'id': member.id, 'name': member.name, 'email': member.email, 'plan': member.plan}), 201


@app.route('/members/<int:member_id>', methods=['DELETE'])
@require_auth
def delete_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted'})


@app.route('/members/<int:member_id>/assign_trainer', methods=['PUT'])
@require_auth
def assign_trainer(member_id):
    data = request.get_json() or {}
    trainer_id = data.get('trainer_id')
    member = Member.query.get(member_id)
    trainer = Trainer.query.get(trainer_id)
    if not member or not trainer:
        return jsonify({'error': 'Member or trainer not found'}), 404
    member.trainer = trainer
    db.session.commit()
    return jsonify({'message': f'Trainer {trainer.name} assigned to member {member.name}'})


@app.route('/members/<int:member_id>/assign_plan', methods=['PUT'])
@require_auth
def assign_plan(member_id):
    data = request.get_json() or {}
    plan = data.get('plan')
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    if plan not in MEMBERSHIP_PLANS:
        return jsonify({'error': 'Invalid plan'}), 400
    member.plan = plan
    db.session.commit()
    return jsonify({'message': f'Plan {plan} assigned to member {member.name}'})


@app.route('/trainers', methods=['GET', 'POST'])
@require_auth
def trainers_route():
    if request.method == 'GET':
        trainers = Trainer.query.all()
        return jsonify([{'id': t.id, 'name': t.name, 'email': t.email} for t in trainers])

    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400

    trainer = Trainer(name=name, email=data.get('email'))
    db.session.add(trainer)
    db.session.commit()
    return jsonify({'id': trainer.id, 'name': trainer.name, 'email': trainer.email}), 201


@app.route('/attendance', methods=['POST'])
@require_auth
def mark_attendance():
    data = request.get_json() or {}
    member_id = data.get('member_id')
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'error': 'Member not found'}), 404

    attend = Attendance(member=member)
    db.session.add(attend)
    db.session.commit()
    return jsonify({'message': 'Attendance marked', 'member_id': member_id, 'timestamp': attend.timestamp.isoformat()}), 201


@app.route('/attendance/<int:member_id>', methods=['GET'])
@require_auth
def attendance_history(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'error': 'Member not found'}), 404

    records = Attendance.query.filter_by(member_id=member_id).order_by(Attendance.timestamp.desc()).all()
    return jsonify([{'id': r.id, 'timestamp': r.timestamp.isoformat()} for r in records])


@app.route('/bmi', methods=['POST'])
@require_auth
def bmi():
    data = request.get_json() or {}
    height = data.get('height')
    weight = data.get('weight')
    if not height or not weight or height <= 0:
        return jsonify({'error': 'Valid height and weight required'}), 400

    bmi_value = weight / (height * height)
    if bmi_value < 18.5:
        category = 'Underweight'
    elif bmi_value < 25:
        category = 'Normal weight'
    elif bmi_value < 30:
        category = 'Overweight'
    else:
        category = 'Obesity'

    return jsonify({'bmi': round(bmi_value, 2), 'category': category})


@app.route('/payments', methods=['POST'])
@require_auth
def create_payment():
    data = request.get_json() or {}
    member_id = data.get('member_id')
    amount = data.get('amount')
    status = data.get('status', 'paid')

    if not member_id or amount is None:
        return jsonify({'error': 'member_id and amount are required'}), 400

    member = Member.query.get(member_id)
    if not member:
        return jsonify({'error': 'Member not found'}), 404

    payment = Payment(member=member, amount=amount, status=status)
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.to_dict()), 201


@app.route('/payments/<int:member_id>', methods=['GET'])
@require_auth
def get_payments(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'error': 'Member not found'}), 404

    payments = Payment.query.filter_by(member_id=member_id).order_by(Payment.recorded_at.desc()).all()
    total_paid = sum(p.amount for p in payments if p.status == 'paid')
    total_pending = sum(p.amount for p in payments if p.status != 'paid')

    return jsonify({
        'member_id': member_id,
        'payments': [p.to_dict() for p in payments],
        'total_paid': total_paid,
        'total_pending': total_pending
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
