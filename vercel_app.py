from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
import json
from supabase import create_client, Client
import requests
import smpplib.gsm
import smpplib.client
import smpplib.consts

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add a global variable to track system balance
system_balance = 1000.0  # Initial balance in euros
DEFAULT_SMS_RATE = float(os.getenv('DEFAULT_SMS_RATE', 0.05))  # Default cost per SMS in euros

# Initialize SMPP client
def get_smpp_client():
    """Get a configured SMPP client"""
    try:
        client = smpplib.client.Client(os.getenv('SMPP_HOST'), int(os.getenv('SMPP_PORT')))
        client.connect()
        client.bind_transceiver(system_id=os.getenv('SMPP_USERNAME'), password=os.getenv('SMPP_PASSWORD'))
        return client
    except Exception as e:
        logger.error(f"SMPP connection error: {str(e)}")
        return None

# User class definition - uses Supabase instead of SQLAlchemy
class User(UserMixin):
    def __init__(self, id, username, email, password, credits, is_admin, sms_rate, role):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.credits = credits
        self.is_admin = is_admin
        self.sms_rate = sms_rate
        self.role = role

    @staticmethod
    def get(user_id):
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        if response.data and len(response.data) > 0:
            user_data = response.data[0]
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                credits=user_data['credits'],
                is_admin=user_data['is_admin'],
                sms_rate=user_data['sms_rate'],
                role=user_data['role']
            )
        return None

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_sms_rate(self):
        """Get the user's SMS rate"""
        return self.sms_rate if not self.is_admin else DEFAULT_SMS_RATE

# Message class for Supabase
class Message:
    @staticmethod
    def create(user_id, numbers, content, status='pending', message_id=None, cost=0.0):
        data = {
            'user_id': user_id,
            'numbers': numbers,
            'content': content,
            'status': status,
            'message_id': message_id,
            'created_at': datetime.utcnow().isoformat(),
            'cost': cost
        }
        response = supabase.table('messages').insert(data).execute()
        return response.data[0] if response.data else None

    @staticmethod
    def get_user_messages(user_id):
        response = supabase.table('messages').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data if response.data else []

    @staticmethod
    def get_recent_messages(limit=10):
        response = supabase.table('messages').select('*').order('created_at', desc=True).limit(limit).execute()
        return response.data if response.data else []

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Helper functions for system balance
def get_system_balance():
    """Get the system balance from Supabase"""
    response = supabase.table('system_settings').select('value').eq('key', 'system_balance').execute()
    if response.data and len(response.data) > 0:
        return float(response.data[0]['value'])
    return 1000.0  # Default value

def update_system_balance(amount):
    """Update the system balance in Supabase"""
    current_balance = get_system_balance()
    new_balance = current_balance + amount
    
    # Check if record exists
    response = supabase.table('system_settings').select('*').eq('key', 'system_balance').execute()
    
    if response.data and len(response.data) > 0:
        # Update existing record
        supabase.table('system_settings').update({'value': str(new_balance)}).eq('key', 'system_balance').execute()
    else:
        # Create new record
        supabase.table('system_settings').insert({'key': 'system_balance', 'value': str(new_balance)}).execute()
    
    return new_balance

# SMS sending function
def send_sms(numbers, content):
    """Send SMS using SMPP"""
    try:
        gateway_type = os.getenv('SMS_GATEWAY_TYPE', 'smpp')
        
        if gateway_type.lower() == 'smpp':
            client = get_smpp_client()
            if not client:
                logger.error("Failed to connect to SMPP server")
                return False, {'error': 'SMPP connection failed'}
            
            # Format the destination number
            if numbers.startswith('+'):
                numbers = numbers[1:]  # Remove + if present
            
            # Format the SMS content for GSM encoding
            parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(content)
            
            # Generate a unique message ID
            message_id = f'msg_{datetime.now().timestamp()}'
            
            # Send the message
            for part in parts:
                pdu = client.send_message(
                    source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
                    source_addr=os.getenv('SMS_SENDER_ID', 'SMSHub'),
                    dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                    destination_addr=numbers,
                    short_message=part,
                    data_coding=encoding_flag,
                    esm_class=msg_type_flag,
                    registered_delivery=True,
                )
                logger.info(f"SMS sent with PDU ID: {pdu.sequence}")
            
            # Unbind and disconnect
            client.unbind()
            client.disconnect()
            
            return True, {'message_id': message_id, 'status': 'sent'}
        else:
            # Use HTTP API as fallback
            api_url = os.getenv('SMS_API_URL', 'http://45.61.157.94:20003/send')
            
            payload = {
                'username': os.getenv('SMPP_USERNAME'),
                'password': os.getenv('SMPP_PASSWORD'),
                'to': numbers,
                'text': content,
                'from': os.getenv('SMS_SENDER_ID', 'SMSHub')
            }
            
            response = requests.post(api_url, json=payload)
            success = response.status_code == 200
            
            try:
                result = response.json()
            except:
                result = {'status': 'sent' if success else 'failed'}
                
            return success, result
            
    except Exception as e:
        logger.error(f"SMS sending error: {str(e)}")
        return False, {'error': str(e)}

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        response = supabase.table('users').select('*').eq('username', username).execute()
        if response.data and len(response.data) > 0:
            user_data = response.data[0]
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                credits=user_data['credits'],
                is_admin=user_data['is_admin'],
                sms_rate=user_data['sms_rate'],
                role=user_data['role']
            )
            
            if user.check_password(password):
                login_user(user)
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get user's messages
    messages = Message.get_user_messages(current_user.id)
    
    # Calculate statistics (simplified for Vercel deployment)
    total_messages = len(messages)
    successful_messages = len([m for m in messages if m['status'] == 'success'])
    failed_messages = len([m for m in messages if m['status'] == 'failed'])
    total_cost = sum(message['cost'] for message in messages)
    
    return render_template('dashboard.html', 
                         messages=messages,
                         user=current_user,
                         total_messages=total_messages,
                         successful_messages=successful_messages,
                         failed_messages=failed_messages,
                         total_cost=total_cost)

@app.route('/send_sms', methods=['POST'])
@login_required
def send_sms_route():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    try:
        country_code = request.form.get('country_code', '+52').strip()
        phone_number = request.form.get('phone_number', '').strip()
        content = request.form.get('content', '').strip()
        
        if not phone_number or not content:
            flash('Please provide both phone number and message content', 'error')
            return redirect(url_for('send_sms_page'))
        
        # Format the phone number
        if country_code == '+52':
            formatted_number = '52' + phone_number
        else:
            formatted_number = country_code.replace('+', '') + phone_number
        
        # Calculate cost
        cost = current_user.sms_rate
        
        if current_user.credits < cost:
            flash('Insufficient credits', 'error')
            return redirect(url_for('send_sms_page'))
        
        # Send SMS
        success, result = send_sms(formatted_number, content)
        
        # Create message record
        Message.create(
            user_id=current_user.id,
            numbers=formatted_number,
            content=content,
            status='success' if success else 'failed',
            message_id=result.get('message_id'),
            cost=cost if success else 0
        )
        
        # Update user credits only if successful
        if success:
            # Update user credits in Supabase
            supabase.table('users').update({
                'credits': current_user.credits - cost
            }).eq('id', current_user.id).execute()
            
            # Update system balance
            update_system_balance(cost)
            
            flash('SMS sent successfully', 'success')
        else:
            flash(f'Failed to send SMS: {result.get("error", "Unknown error")}', 'error')
            
        return redirect(url_for('send_sms_page'))
        
    except Exception as e:
        logger.error(f"SMS sending error: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('send_sms_page'))

@app.route('/send_sms_page')
@login_required
def send_sms_page():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return render_template('send_sms.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Serverless-friendly health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# For local development
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), debug=os.getenv('FLASK_ENV') != 'production') 