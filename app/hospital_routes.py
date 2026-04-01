from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, AuditLog
from app.auth import admin_required

hospital_bp = Blueprint('hospitals', __name__, template_folder='templates', url_prefix='/hospital')

@hospital_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.filter_by(hospital_id=current_user.hospital_id).all()
    return render_template('manage_users.html', users=users)

@hospital_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('add_user.html')
        
        user = User(
            hospital_id=current_user.hospital_id,
            username=username,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        log = AuditLog(user_id=current_user.id, action='USER_ADDED', details=f'{username} ({role})')
        db.session.add(log)
        db.session.commit()
        
        flash('User added successfully!', 'success')
        return redirect(url_for('hospitals.manage_users'))
    
    return render_template('add_user.html')

@hospital_bp.route('/audit')
@login_required
@admin_required
def audit_logs():
    hospital_user_ids = [u.id for u in User.query.filter_by(hospital_id=current_user.hospital_id).all()]
    logs = AuditLog.query.filter(AuditLog.user_id.in_(hospital_user_ids)).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('audit_logs.html', logs=logs)

