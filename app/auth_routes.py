from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Hospital, AuditLog
from app.auth import admin_required, staff_required
import uuid

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/register_hospital', methods=['GET', 'POST'])
def register_hospital():
    if request.method == 'POST':
        name = request.form['hospital_name']
        username = request.form['username']
        password = request.form['password']
        
        if not name or not username or not password:
            flash('All fields are required.', 'danger')
            return render_template('register_hospital.html')

        if Hospital.query.filter_by(name=name).first():
            flash('A hospital with that name is already registered.', 'danger')
            return render_template('register_hospital.html')

        if User.query.filter_by(username=username).first():
            flash('That admin username is already taken. Please choose another.', 'danger')
            return render_template('register_hospital.html')

        # Create hospital
        hospital = Hospital(name=name)
        db.session.add(hospital)
        db.session.flush()  # Get ID
        
        # Create admin user
        user = User(
            hospital_id=hospital.id,
            username=username,
            role='admin'
        )
        user.set_password(password)
        db.session.add(user)
        
        db.session.commit()
        
        # Log
        log = AuditLog(user_id=user.id, action='HOSPITAL_REGISTER', details=f'Hospital: {name}')
        db.session.add(log)
        db.session.commit()
        
        flash('Hospital registered! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register_hospital.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            log = AuditLog(user_id=user.id, action='LOGIN', details=f'User: {username}')
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('dashboard.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log = AuditLog(user_id=current_user.id, action='LOGOUT', details='User logged out')
    db.session.add(log)
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('landing.html')

