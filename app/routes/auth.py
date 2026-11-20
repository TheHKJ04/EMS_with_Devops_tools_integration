from flask import Blueprint, request, redirect, url_for, render_template, session, flash, current_app
from app.models.employee import Employee
from app.models import db
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id') and session.get('is_admin') is True:
        return redirect(url_for('home.home'))
    if session.get('user_id') and session.get('is_admin') is False:
        return redirect(url_for('employee.employee_portal'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        admin_hash = current_app.config.get('ADMIN_PASSWORD_HASH')
        if (email == current_app.config.get('ADMIN_EMAIL') and admin_hash
                and check_password_hash(admin_hash, password)):
            session['user_id'] = 'admin'
            session['user_name'] = 'Administrator'
            session['is_admin'] = True
            flash('Admin login successful', 'success')
            return redirect(url_for('home.home'))

        flash('Invalid admin credentials', 'danger')

    return render_template('login.html')


@auth_bp.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    if session.get('user_id') and session.get('is_admin') is True:
        return redirect(url_for('home.home'))
    if session.get('user_id') and session.get('is_admin') is False:
        return redirect(url_for('employee.employee_portal'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        employee = Employee.query.filter_by(email=email).first()
        password_ok = False
        if employee and employee.password_hash:
            try:
                password_ok = check_password_hash(employee.password_hash, password)
            except (ValueError, TypeError):
                # Transitional support for legacy plaintext rows: upgrade only after
                # a successful match. Remaining rows require a controlled data migration.
                password_ok = employee.password_hash == password
                if password_ok:
                    employee.password_hash = generate_password_hash(password)
                    db.session.commit()

        if employee and password_ok:
            session['user_id'] = employee.id
            session['user_name'] = employee.name
            session['is_admin'] = False
            flash('Employee login successful', 'success')
            return redirect(url_for('employee.employee_portal'))
        flash('Invalid employee credentials', 'danger')

    return render_template('employee_login.html')


@auth_bp.route('/logout',methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/signup')
def signup():
    flash('Admin sign-up is disabled. Please use the admin login form.', 'info')
    return redirect(url_for('auth.login'))
