from flask import Blueprint, render_template, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Patient, MedicalRecord, ShareRequest, AuditLog, func
from app.auth import admin_required
from datetime import datetime, timedelta

dash_bp = Blueprint('dashboard', __name__, template_folder='templates')

@dash_bp.route('/dashboard')
@login_required
def dashboard():
    hospital_id = current_user.hospital_id
    
    # Stats
    total_patients = Patient.query.filter_by(hospital_id=hospital_id).count()
    total_records = MedicalRecord.query.join(Patient).filter(Patient.hospital_id == hospital_id).count()
    recent_activity = AuditLog.query.filter(
        AuditLog.user_id == current_user.id,
        AuditLog.timestamp > datetime.utcnow() - timedelta(days=7)
    ).order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    # Shared records count (for hospital)
    outgoing_shares = ShareRequest.query.filter_by(from_hospital_id=hospital_id, status='approved').count()
    incoming_shares = ShareRequest.query.filter_by(to_hospital_id=hospital_id, status='approved').count()
    
    context = {
        'total_patients': total_patients,
        'total_records': total_records,
        'outgoing_shares': outgoing_shares,
        'incoming_shares': incoming_shares,
        'recent_activity': recent_activity
    }
    
    return render_template('dashboard.html', **context)

@dash_bp.route('/stats/api')
@login_required
def stats_api():
    hospital_id = current_user.hospital_id
    stats = {
        'patients': Patient.query.filter_by(hospital_id=hospital_id).count(),
        'records': MedicalRecord.query.join(Patient).filter(Patient.hospital_id == hospital_id).count(),
        'activity_last_7d': AuditLog.query.filter(
            AuditLog.timestamp > datetime.utcnow() - timedelta(days=7)
        ).count()
    }
    return jsonify(stats)

