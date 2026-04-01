from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app import db
from app.models import ShareRequest, Patient, Hospital, AuditLog, MedicalRecord
from app.auth import staff_required

share_bp = Blueprint('shares', __name__, template_folder='templates', url_prefix='/share')

@share_bp.route('/records')
@login_required
@staff_required
def share():
    my_hospital_id = current_user.hospital_id
    patients = Patient.query.filter_by(hospital_id=my_hospital_id).all()
    other_hospitals = Hospital.query.filter(Hospital.id != my_hospital_id).all()

    # Incoming requests
    incoming = ShareRequest.query.filter_by(to_hospital_id=my_hospital_id).order_by(ShareRequest.requested_at.desc()).all()

    return render_template('share.html', patients=patients, incoming=incoming, other_hospitals=other_hospitals)

@share_bp.route('/request', methods=['POST'])
@login_required
@staff_required
def request_share():
    patient_id = request.form.get('patient_id', type=int)
    if not patient_id:
        flash('Please select a patient.', 'danger')
        return redirect(url_for('shares.share'))
    patient = Patient.query.filter_by(id=patient_id, hospital_id=current_user.hospital_id).first_or_404()
    target_hospital_name = request.form['target_hospital']
    
    target_hospital = Hospital.query.filter_by(name=target_hospital_name).first()
    if not target_hospital:
        flash('Target hospital not found.', 'danger')
        return redirect(url_for('shares.share'))
    
    # Check if request exists
    existing = ShareRequest.query.filter_by(
        from_hospital_id=current_user.hospital_id,
        to_hospital_id=target_hospital.id,
        patient_id=patient_id
    ).first()
    
    if existing:
        if existing.status == 'pending':
            flash('Share request already pending.', 'warning')
        else:
            existing.status = 'pending'
            existing.requested_at = datetime.now(timezone.utc)
        db.session.commit()
    else:
        share_request = ShareRequest(
            from_hospital_id=current_user.hospital_id,
            to_hospital_id=target_hospital.id,
            patient_id=patient_id
        )
        db.session.add(share_request)
        db.session.commit()
        
        log = AuditLog(
            user_id=current_user.id,
            action='SHARE_REQUEST_SENT',
            details=f'Patient {patient.name} to {target_hospital.name}'
        )
        db.session.add(log)
        db.session.commit()
    
    flash('Share request sent successfully!', 'success')
    return redirect(url_for('shares.share'))

@share_bp.route('/approve/<int:request_id>')
@login_required
@staff_required
def approve_share(request_id):
    request_share = ShareRequest.query.get_or_404(request_id)
    if request_share.to_hospital_id != current_user.hospital_id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('shares.share'))
    
    request_share.status = 'approved'
    request_share.approved_at = datetime.now(timezone.utc)
    db.session.commit()
    
    log = AuditLog(
        user_id=current_user.id,
        action='SHARE_REQUEST_APPROVED',
        details=f'Request {request_id}'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Share request approved!', 'success')
    return redirect(url_for('shares.share'))

@share_bp.route('/reject/<int:request_id>')
@login_required
@staff_required
def reject_share(request_id):
    request_share = ShareRequest.query.get_or_404(request_id)
    if request_share.to_hospital_id != current_user.hospital_id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('shares.share'))

    request_share.status = 'rejected'
    db.session.commit()

    log = AuditLog(
        user_id=current_user.id,
        action='SHARE_REQUEST_REJECTED',
        details=f'Request {request_id}'
    )
    db.session.add(log)
    db.session.commit()

    flash('Share request rejected.', 'info')
    return redirect(url_for('shares.share'))

@share_bp.route('/view_shared/<int:patient_id>')
@login_required
def view_shared_record(patient_id):
    # Check if has approved share access
    share = ShareRequest.query.filter_by(
        patient_id=patient_id,
        to_hospital_id=current_user.hospital_id,
        status='approved'
    ).first()
    
    if not share:
        flash('No access to this patient record.', 'danger')
        return redirect(url_for('shares.share'))
    
    patient = Patient.query.get_or_404(patient_id)
    records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.timestamp.desc()).all()
    
    return render_template('view_shared_record.html', patient=patient, records=records, share=share)

