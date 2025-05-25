from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import User
from werkzeug.security import generate_password_hash

# It's common to create forms in a separate forms.py file, but for simplicity,
# we'll handle form data directly in routes for now.

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # For POST request:
    # 1. Get username, email, password from request.form
    # 2. Check if user or email already exists
    # 3. Create new User object, set password (hashed)
    # 4. Add to db.session and commit
    # 5. Flash success message and redirect to login
    # For GET request:
    if request.method == 'GET':
        return render_template('register.html')

    # POST request logic (simplified for brevity - actual implementation would be more robust)
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not all([username, email, password, confirm_password]):
        flash('All fields are required.', 'error')
        return redirect(url_for('auth.register'))

    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('auth.register'))

    user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
    if user_exists:
        flash('Username or email already exists.', 'error')
        return redirect(url_for('auth.register'))

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    try:
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('auth.register'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard')) # Redirect if already logged in

    if request.method == 'GET':
        return render_template('login.html')

    # POST request logic
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash('Email and password are required.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)
        flash('Login successful!', 'success')
        # Attempt to redirect to 'next' page if provided by @login_required
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main_bp.dashboard'))
    else:
        flash('Invalid email or password.', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login')) # Or a public home page

# We would also need to create HTML templates (register.html, login.html)
# in an app/templates/ directory. For now, these routes return placeholders.
