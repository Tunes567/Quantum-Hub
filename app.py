from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from sms_client import sms_client, SMSClient
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Database configuration - use PostgreSQL in production, SQLite for development
if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add a global variable to track system balance
system_balance = 1000.0  # Initial balance in euros
DEFAULT_SMS_RATE = float(os.getenv('DEFAULT_SMS_RATE', 0.05))  # Default cost per SMS in euros

# Message model for tracking SMS
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    numbers = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    message_id = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cost = db.Column(db.Float, default=0.0)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    credits = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)
    sms_rate = db.Column(db.Float, default=DEFAULT_SMS_RATE)  # Custom rate per SMS
    role = db.Column(db.String(20), default='user')  # Add role field
    messages = db.relationship('Message', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_sms_rate(self):
        """Get the user's SMS rate"""
        return self.sms_rate if not self.is_admin else DEFAULT_SMS_RATE

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_system_balance():
    """Get the real system balance in euros"""
    global system_balance
    return system_balance

def update_system_balance(amount):
    """Update the system balance in euros"""
    global system_balance
    system_balance += amount
    return system_balance

def euros_to_credits(euros, rate):
    """Convert euros to SMS credits based on rate"""
    return int(euros / rate)

def credits_to_euros(credits, rate):
    """Convert SMS credits to euros based on rate"""
    return credits * rate

def get_system_stats():
    """Get system-wide statistics"""
    success, result = sms_client.get_daily_stats()
    if success:
        return {
            'total_sent': result.get('success', 0),
            'total_failed': result.get('fail', 0),
            'total_cost': result.get('billcnt', 0)
        }
    return {'total_sent': 0, 'total_failed': 0, 'total_cost': 0}

# Create all database tables
with app.app_context():
    # Only drop tables in development to avoid data loss in production
    if os.getenv('FLASK_ENV') != 'production':
        db.drop_all()  # Drop all existing tables
    
    db.create_all()  # Create new tables
    
    # Create admin user if not exists
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(
            username=admin_username,
            email=admin_email,
            is_admin=True,
            credits=1000.0
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/request_demo', methods=['GET', 'POST'])
def request_demo():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        phone = request.form['phone']
        message = request.form['message']
        
        # Here you would typically send an email notification to admin
        flash('Demo request received. We will contact you soon!')
        return redirect(url_for('index'))
    
    return render_template('request_demo.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    users = User.query.filter_by(is_admin=False).all()
    system_stats = get_system_stats()
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html',
                         users=users,
                         system_balance=get_system_balance(),
                         system_stats=system_stats,
                         recent_messages=recent_messages,
                         sms_rate=DEFAULT_SMS_RATE)

@app.route('/admin/user/<int:user_id>/messages')
@login_required
def view_user_messages(user_id):
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    messages = Message.query.filter_by(user_id=user_id).order_by(Message.created_at.desc()).all()
    
    return render_template('user_messages.html',
                         user=user,
                         messages=messages)

@app.route('/admin/create_user', methods=['POST'])
@login_required
def admin_create_user():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    credits = float(request.form.get('credits', 0))
    sms_rate = float(request.form.get('sms_rate', 0.05))
    role = request.form.get('role', 'user')
    
    if not all([username, email, password]):
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Check if username or email already exists
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if User.query.filter_by(email=email).first():
        flash('Email already exists', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Check system balance
    current_balance = get_system_balance()
    if current_balance < credits:
        flash('Insufficient system balance', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Create new user
        user = User(
            username=username,
            email=email,
            credits=credits,
            sms_rate=sms_rate,
            role=role
        )
        user.set_password(password)
        
        # Update system balance
        update_system_balance(-credits)
        
        db.session.add(user)
        db.session.commit()
        flash(f'User {username} created successfully with {credits} credits', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating user: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_credits/<int:user_id>', methods=['POST'])
@login_required
def add_credits(user_id):
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    try:
        user = User.query.get_or_404(user_id)
        amount = float(request.form.get('amount', 0))
        
        if amount <= 0:
            flash('Invalid amount', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Check system balance
        current_balance = get_system_balance()
        if current_balance < amount:
            flash('Insufficient system balance', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Update user's credits
        user.credits += amount
        
        # Update system balance
        update_system_balance(-amount)
        
        db.session.commit()
        flash(f'Successfully added {amount} credits to {user.username}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding credits: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/send_sms', methods=['POST'])
@login_required
def admin_send_sms():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    numbers = request.form.get('numbers', '').strip()
    content = request.form.get('content', '').strip()
    schedule = request.form.get('schedule')
    
    if not numbers or not content:
        flash('Please provide both phone numbers and message content', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Send SMS through client
        success, result = sms_client.send_sms(numbers, content)
        
        # Create message record
        message = Message(
            user_id=current_user.id,
            numbers=numbers,
            content=content,
            status='success' if success else 'failed',
            cost=0.0  # Admin messages don't cost credits
        )
        
        db.session.add(message)
        db.session.commit()
        
        if success:
            flash('SMS sent successfully', 'success')
        else:
            flash(f'Failed to send SMS: {result}', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error sending SMS: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get user's messages
    messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.created_at.desc()).all()
    
    # Calculate basic statistics
    total_messages = len(messages)
    successful_messages = len([m for m in messages if m.status == 'success'])
    failed_messages = len([m for m in messages if m.status == 'failed'])
    total_cost = sum(message.cost for message in messages)
    
    # Calculate hourly statistics (last 24 hours)
    now = datetime.utcnow()
    hourly_stats = {i: {'success': 0, 'failed': 0, 'count_success': 0, 'count_failed': 0} 
                   for i in range(24)}
    
    for message in messages:
        if (now - message.created_at) <= timedelta(hours=24):
            hour = message.created_at.hour
            if message.status == 'success':
                hourly_stats[hour]['success'] += 1
                hourly_stats[hour]['count_success'] += len(message.numbers.split(','))
            else:
                hourly_stats[hour]['failed'] += 1
                hourly_stats[hour]['count_failed'] += len(message.numbers.split(','))
    
    hourly_success = [hourly_stats[i]['success'] for i in range(24)]
    hourly_failed = [hourly_stats[i]['failed'] for i in range(24)]
    hourly_count_success = [hourly_stats[i]['count_success'] for i in range(24)]
    hourly_count_failed = [hourly_stats[i]['count_failed'] for i in range(24)]
    
    # Calculate monthly statistics (last 12 months)
    monthly_stats = {i: {'success': 0, 'failed': 0, 'count_success': 0, 'count_failed': 0} 
                    for i in range(12)}
    
    for message in messages:
        if (now - message.created_at) <= timedelta(days=365):
            month = (now.month - message.created_at.month) % 12
            if message.status == 'success':
                monthly_stats[month]['success'] += 1
                monthly_stats[month]['count_success'] += len(message.numbers.split(','))
            else:
                monthly_stats[month]['failed'] += 1
                monthly_stats[month]['count_failed'] += len(message.numbers.split(','))
    
    monthly_success = [monthly_stats[i]['success'] for i in range(12)]
    monthly_failed = [monthly_stats[i]['failed'] for i in range(12)]
    monthly_count_success = [monthly_stats[i]['count_success'] for i in range(12)]
    monthly_count_failed = [monthly_stats[i]['count_failed'] for i in range(12)]
    
    # Calculate daily statistics (last 30 days)
    daily_stats = {i: {'success': 0, 'failed': 0, 'count_success': 0, 'count_failed': 0} 
                  for i in range(30)}
    
    for message in messages:
        if (now - message.created_at) <= timedelta(days=30):
            day = (now.date() - message.created_at.date()).days
            if day < 30:
                if message.status == 'success':
                    daily_stats[day]['success'] += 1
                    daily_stats[day]['count_success'] += len(message.numbers.split(','))
                else:
                    daily_stats[day]['failed'] += 1
                    daily_stats[day]['count_failed'] += len(message.numbers.split(','))
    
    daily_success = [daily_stats[i]['success'] for i in range(30)]
    daily_failed = [daily_stats[i]['failed'] for i in range(30)]
    daily_count_success = [daily_stats[i]['count_success'] for i in range(30)]
    daily_count_failed = [daily_stats[i]['count_failed'] for i in range(30)]
    
    return render_template('dashboard.html', 
                         messages=messages,
                         user=current_user,
                         total_messages=total_messages,
                         successful_messages=successful_messages,
                         failed_messages=failed_messages,
                         total_cost=total_cost,
                         hourly_success=hourly_success,
                         hourly_failed=hourly_failed,
                         hourly_count_success=hourly_count_success,
                         hourly_count_failed=hourly_count_failed,
                         monthly_success=monthly_success,
                         monthly_failed=monthly_failed,
                         monthly_count_success=monthly_count_success,
                         monthly_count_failed=monthly_count_failed,
                         daily_success=daily_success,
                         daily_failed=daily_failed,
                         daily_count_success=daily_count_success,
                         daily_count_failed=daily_count_failed)

@app.route('/send_sms', methods=['POST'])
@login_required
def send_sms():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    try:
        country_code = request.form.get('country_code', '+52').strip()  # Get with +
        phone_number = request.form.get('phone_number', '').strip()
        content = request.form.get('content', '').strip()
        
        if not phone_number or not content:
            flash('Please provide both phone number and message content', 'error')
            return redirect(url_for('send_sms_page'))
        
        # Format the phone number - remove + for Mexico
        if country_code == '+52':
            formatted_number = '52' + phone_number
        else:
            formatted_number = country_code + phone_number
        
        # Calculate cost
        cost = current_user.sms_rate
        
        if current_user.credits < cost:
            flash('Insufficient credits', 'error')
            return redirect(url_for('send_sms_page'))
        
        try:
            # Send SMS through client
            success, result = sms_client.send_sms(formatted_number, content)
            
            # Create message record
            message = Message(
                user_id=current_user.id,
                numbers=formatted_number,
                content=content,
                status='success' if success else 'failed',
                cost=cost if success else 0
            )
            
            # Update user credits only if successful
            if success:
                current_user.credits -= cost
                update_system_balance(cost)
            
            db.session.add(message)
            db.session.commit()
            
            if success:
                flash('SMS sent successfully', 'success')
            else:
                flash(f'Failed to send SMS: {result}', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error sending SMS: {str(e)}', 'error')
        
        return redirect(url_for('send_sms_page'))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('send_sms_page'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/add_system_credits', methods=['POST'])
@login_required
def add_system_credits():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    try:
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method')
        transaction_id = request.form.get('transaction_id')
        
        if amount <= 0:
            flash('Invalid amount', 'error')
            return redirect(url_for('admin_dashboard'))
        
        if payment_method == 'bank_transfer' and not transaction_id:
            flash('Transaction ID is required for bank transfers', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Update system balance
        update_system_balance(amount)
        
        flash(f'Successfully added {amount} credits to system balance', 'success')
        
    except Exception as e:
        flash(f'Error adding system credits: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_settings', methods=['POST'])
@login_required
def update_system_settings():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        default_sms_rate = float(request.form.get('default_sms_rate', 0.0))
        sms_gateway = request.form.get('sms_gateway', 'http')
        api_key = request.form.get('api_key')
        api_secret = request.form.get('api_secret')
        sender_id = request.form.get('sender_id')
        message_template = request.form.get('message_template')

        # Update SMS client configuration
        sms_client.update_config(
            gateway=sms_gateway,
            api_key=api_key,
            api_secret=api_secret,
            sender_id=sender_id,
            message_template=message_template
        )

        # Update default SMS rate
        sms_rate = default_sms_rate

        flash('System settings updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating system settings: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/send_sms_page')
@login_required
def send_sms_page():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return render_template('send_sms.html', user=current_user)

@app.route('/bulk_sms_page')
@login_required
def bulk_sms_page():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return render_template('bulk_sms.html', user=current_user)

@app.route('/send_bulk_sms', methods=['POST'])
@login_required
def send_bulk_sms():
    try:
        country_code = request.form.get('country_code', '+52').strip()  # Get with +
        content = request.form.get('content', '').strip()
        
        # Get numbers from either textarea or file
        numbers = []
        if 'numbers_file' in request.files and request.files['numbers_file'].filename:
            file = request.files['numbers_file']
            numbers_text = file.read().decode('utf-8')
            numbers = [n.strip() for n in numbers_text.split('\n') if n.strip()]
        else:
            numbers_text = request.form.get('numbers', '').strip()
            numbers = [n.strip() for n in numbers_text.split('\n') if n.strip()]

        # Validate and format numbers
        formatted_numbers = []
        for number in numbers:
            # Remove any non-digit characters
            clean_number = ''.join(filter(str.isdigit, number))
            
            # If number already has country code, use it as is
            if len(clean_number) > 10:
                formatted_numbers.append(clean_number)
            # If it's a 10-digit number, add the country code
            elif len(clean_number) == 10:
                # Remove + for Mexico when sending
                if country_code == '+52':
                    formatted_numbers.append('52' + clean_number)
                else:
                    formatted_numbers.append(country_code + clean_number)
            else:
                flash(f'Invalid number format: {number}', 'error')
                continue

        if not formatted_numbers:
            flash('No valid phone numbers provided', 'error')
            return redirect(url_for('bulk_sms_page'))

        if not content:
            flash('Message content is required', 'error')
            return redirect(url_for('bulk_sms_page'))

        # Calculate total cost
        total_cost = len(formatted_numbers) * current_user.sms_rate
        if total_cost > current_user.credits:
            flash('Insufficient credits for bulk SMS', 'error')
            return redirect(url_for('bulk_sms_page'))

        # Send messages and track success/failure
        success_count = 0
        failed_numbers = []
        
        for number in formatted_numbers:
            try:
                # Send SMS using your SMS gateway
                success, result = sms_client.send_sms(number, content)
                
                # Create message record
                message = Message(
                    user_id=current_user.id,
                    numbers=number,
                    content=content,
                    status='sent' if success else 'failed',
                    cost=current_user.sms_rate if success else 0
                )
                db.session.add(message)
                
                if success:
                    success_count += 1
                else:
                    failed_numbers.append(number)
                    logger.error(f"Failed to send SMS to {number}: {result}")
                    
            except Exception as e:
                failed_numbers.append(number)
                logger.error(f"Error sending SMS to {number}: {str(e)}")
                continue

        # Update user credits only for successful messages
        current_user.credits -= (success_count * current_user.sms_rate)
        update_system_balance(success_count * current_user.sms_rate)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error in bulk SMS: {str(e)}")
            flash('Error saving message records', 'error')
            return redirect(url_for('bulk_sms_page'))

        # Show results
        if success_count == len(formatted_numbers):
            flash(f'Successfully sent {success_count} messages', 'success')
        else:
            flash(f'Sent {success_count} messages. Failed to send to: {", ".join(failed_numbers)}', 'warning')

        return redirect(url_for('bulk_sms_page'))

    except Exception as e:
        logger.error(f"Bulk SMS error: {str(e)}")
        flash(f'Error sending bulk SMS: {str(e)}', 'error')
        return redirect(url_for('bulk_sms_page'))

@app.route('/user/add_credits', methods=['POST'])
@login_required
def user_add_credits():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    try:
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method')
        
        if amount <= 0:
            flash('Invalid amount', 'error')
            return redirect(url_for('dashboard'))
        
        if not payment_method:
            flash('Please select a payment method', 'error')
            return redirect(url_for('dashboard'))
        
        # Here you would typically integrate with a payment gateway
        # For now, we'll just simulate a successful payment
        
        # Update user's credits
        current_user.credits += amount
        
        db.session.commit()
        flash(f'Successfully added {amount} credits to your account', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding credits: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

# For production use with Gunicorn
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), debug=os.getenv('FLASK_ENV') != 'production') 