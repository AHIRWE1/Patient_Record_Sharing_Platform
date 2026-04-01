from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Patient, MedicalRecord, AuditLog
from app.auth import staff_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

patient_bp = Blueprint('patients', __name__, template_folder='templates', url_prefix='/patients')

@patient_bp.route('/')
@patient_bp.route('/list')
@login_required
def patients():
    hospital_id = current_user.hospital_id
    search = request.args.get('search', '')
    
    query = Patient.query.filter_by(hospital_id=hospital_id)
    if search:
        query = query.filter(
            or_(
                Patient.name.ilike(f'%{search}%'),
                Patient.national_id.ilike(f'%{search}%')
            )
        )
    
    patients_list = query.order_by(Patient.created_at.desc()).all()
    return render_template('patients.html', patients=patients_list, search=search)

@patient_bp.route('/register', methods=['GET', 'POST'])
@login_required
@staff_required
def register_patient():
    if request.method == 'POST':
        name = request.form['name']
        dob_str = request.form['dob']
        gender = request.form['gender']
        national_id = request.form['national_id']

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            if dob >= datetime.today().date():
                flash('Invalid date format. Please enter a valid date of birth (must be in the past).', 'danger')
                return render_template('register_patient.html')
        except ValueError:
            flash('Invalid date format. Please enter a valid date.', 'danger')
            return render_template('register_patient.html')
        
        # Check duplicate national ID (hospital-specific)
        if Patient.query.filter_by(hospital_id=current_user.hospital_id, national_id=national_id).first():
            flash('Patient with this National ID already exists.', 'danger')
            return render_template('register_patient.html')
        
        patient = Patient(
            hospital_id=current_user.hospital_id,
            name=name,
            dob=dob,
            gender=gender,
            national_id=national_id
        )
        db.session.add(patient)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('A patient with this National ID is already registered at your hospital.', 'danger')
            return render_template('register_patient.html')

        log = AuditLog(
            user_id=current_user.id,
            action='PATIENT_REGISTER',
            details=f'Patient: {name} (ID: {national_id})'
        )
        db.session.add(log)
        db.session.commit()

        flash('Patient registered successfully!', 'success')
        return redirect(url_for('patients.patients'))
    
    return render_template('register_patient.html')

@patient_bp.route('/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    patient = Patient.query.filter_by(id=patient_id, hospital_id=current_user.hospital_id).first_or_404()
    records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.timestamp.desc()).all()
    return render_template('patient_detail.html', patient=patient, records=records)

@patient_bp.route('/api/search')
@login_required
def search_patients():
    search = request.args.get('q', '')
    hospital_id = current_user.hospital_id
    
    patients = Patient.query.filter(
        Patient.hospital_id == hospital_id,
        or_(
            Patient.name.ilike(f'%{search}%'),
            Patient.national_id.ilike(f'%{search}%')
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'national_id': p.national_id
    } for p in patients])

