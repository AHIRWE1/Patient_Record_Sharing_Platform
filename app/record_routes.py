from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import MedicalRecord, Patient, AuditLog
from app.auth import doctor_required, staff_required
from datetime import datetime

record_bp = Blueprint('records', __name__, template_folder='templates', url_prefix='/records')

@record_bp.route('/')
@login_required
def records():
    hospital_id = current_user.hospital_id
    patients = Patient.query.filter_by(hospital_id=hospital_id).order_by(Patient.name).all()
    return render_template('records.html', patients=patients)

@record_bp.route('/add/<int:patient_id>', methods=['GET', 'POST'])
@login_required
@doctor_required
def add_record(patient_id):
    patient = Patient.query.filter_by(id=patient_id, hospital_id=current_user.hospital_id).first_or_404()
    
    if request.method == 'POST':
        record = MedicalRecord(
            patient_id=patient_id,
            diagnosis=request.form.get('diagnosis', ''),
            tests=request.form.get('tests', ''),
            treatment=request.form.get('treatment', ''),
            clinical_notes=request.form.get('clinical_notes', ''),
            doctor_id=current_user.id
        )
        db.session.add(record)
        db.session.commit()
        
        # Log
        log = AuditLog(
            user_id=current_user.id,
            action='RECORD_ADDED',
            details=f'Patient {patient.name} ID:{patient_id}'
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Medical record added successfully!', 'success')
        return redirect(url_for('patients.patient_detail', patient_id=patient_id))
    
    return render_template('add_record.html', patient=patient)

@record_bp.route('/view/<int:patient_id>')
@login_required
def view_records(patient_id):
    patient = Patient.query.filter_by(id=patient_id, hospital_id=current_user.hospital_id).first_or_404()
    records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.timestamp.desc()).all()
    return render_template('view_records.html', patient=patient, records=records)

