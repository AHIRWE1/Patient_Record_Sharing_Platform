from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func, UniqueConstraint

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='hospital', lazy=True, cascade='all, delete-orphan')
    patients = db.relationship('Patient', backref='hospital', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Hospital {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'staff', 'doctor'
    
    # Relationships
    medical_records = db.relationship('MedicalRecord', backref='doctor', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_hospital_role(self):
        return f'{self.role}@{self.hospital.name}'
    
    def __repr__(self):
        return f'<User {self.username} - {self.role}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    national_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('hospital_id', 'national_id', name='uq_patient_hospital_national_id'),
    )

    # Relationships
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True, cascade='all, delete-orphan')
    share_requests = db.relationship('ShareRequest', backref='patient', lazy=True)

    def __repr__(self):
        return f'<Patient {self.name} - {self.national_id}>'

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    tests = db.Column(db.Text)
    treatment = db.Column(db.Text)
    clinical_notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<MedicalRecord {self.id} for Patient {self.patient_id}>'

class ShareRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    to_hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)

    from_hospital = db.relationship('Hospital', foreign_keys=[from_hospital_id], backref='outgoing_share_requests')
    to_hospital = db.relationship('Hospital', foreign_keys=[to_hospital_id], backref='incoming_share_requests')

    def __repr__(self):
        return f'<ShareRequest {self.id}: {self.status}>'

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'

