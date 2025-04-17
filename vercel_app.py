from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
import json
import sys

# Configure logging first thing to capture any startup errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Log important environment information
logger.info(f"Python version: {sys.version}")
logger.info(f"Starting Vercel serverless function")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

try:
    from supabase import create_client, Client
    import requests
    import smpplib.gsm
    import smpplib.client
    import smpplib.consts
    logger.info("All libraries imported successfully")
except Exception as e:
    logger.error(f"Error importing libraries: {str(e)}")
    raise

# Log important environment variables (without sensitive values)
logger.info(f"SUPABASE_URL set: {'SUPABASE_URL' in os.environ}")
logger.info(f"SMPP_HOST set: {'SMPP_HOST' in os.environ}")
logger.info(f"SMS_GATEWAY_TYPE: {os.getenv('SMS_GATEWAY_TYPE', 'not set')}")
logger.info(f"SMS_SENDER_ID: {os.getenv('SMS_SENDER_ID', 'not set')}")

# Initialize Supabase client
try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    logger.info(f"Initializing Supabase client with URL: {supabase_url[:20]}...")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase URL or key is missing")
        raise ValueError("Supabase URL or key is missing")
        
    supabase: Client = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Supabase client: {str(e)}")
    # Don't raise here, allow app to initialize even with Supabase error

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
logger.info("Flask app initialized")

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
        # Log the SMPP connection details
        logger.info(f"Connecting to SMPP server: {os.getenv('SMPP_HOST')}:{os.getenv('SMPP_PORT')}")
        
        # Create client instance
        client = smpplib.client.Client(
            os.getenv('SMPP_HOST', '45.61.157.94'), 
            int(os.getenv('SMPP_PORT', '20002'))
        )
        
        # Set timeouts
        client.set_message_sent_handler(
            lambda pdu: logger.info(f"SMS message sent with PDU sequence {pdu.sequence}")
        )
        
        # Connect to the server
        logger.info("Attempting SMPP connection...")
        client.connect()
        logger.info("SMPP connection successful, binding...")
        
        # Bind to the server
        client.bind_transceiver(
            system_id=os.getenv('SMPP_USERNAME', 'XQB250213A'), 
            password=os.getenv('SMPP_PASSWORD', 'ABD55DBB')
        )
        logger.info("SMPP bind successful")
        
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
        logger.info(f"Using SMS gateway type: {gateway_type}")
        
        if gateway_type.lower() == 'smpp':
            # Log attempt to send SMS
            logger.info(f"Attempting to send SMS to {numbers} via SMPP")
            
            # Get SMPP client
            client = get_smpp_client()
            if not client:
                logger.error("Failed to connect to SMPP server")
                # Try HTTP fallback
                logger.info("Trying HTTP fallback for SMS delivery")
                return send_sms_http(numbers, content)
            
            # Format the destination number
            if numbers.startswith('+'):
                numbers = numbers[1:]  # Remove + if present
            
            # Ensure number is in international format
            if not numbers.startswith('52') and len(numbers) < 10:
                numbers = '52' + numbers
                
            logger.info(f"Formatted destination number: {numbers}")
            
            # Format the SMS content for GSM encoding
            try:
                parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(content)
                logger.info(f"Message split into {len(parts)} parts")
            except Exception as e:
                logger.error(f"Error encoding message: {str(e)}")
                # If encoding fails, send as unicode
                parts = [content.encode('utf-16-be')]
                encoding_flag = smpplib.consts.SMPP_ENCODING_ISO10646
                msg_type_flag = 0
                logger.info("Using unicode encoding for message")
            
            # Generate a unique message ID
            message_id = f'msg_{datetime.now().timestamp()}'
            
            # Send the message
            success = True
            for part in parts:
                try:
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
                    logger.info(f"SMS part sent with PDU ID: {pdu.sequence}")
                except Exception as e:
                    logger.error(f"Error sending message part: {str(e)}")
                    success = False
            
            # Unbind and disconnect
            try:
                client.unbind()
                client.disconnect()
                logger.info("SMPP connection closed")
            except Exception as e:
                logger.error(f"Error closing SMPP connection: {str(e)}")
            
            if success:
                return True, {'message_id': message_id, 'status': 'sent'}
            else:
                # Try HTTP fallback
                logger.info("SMPP delivery failed, trying HTTP fallback")
                return send_sms_http(numbers, content)
        else:
            # Use HTTP API directly
            return send_sms_http(numbers, content)
            
    except Exception as e:
        logger.error(f"SMS sending error: {str(e)}")
        # Try HTTP fallback as last resort
        try:
            return send_sms_http(numbers, content)
        except Exception as e2:
            logger.error(f"HTTP fallback also failed: {str(e2)}")
            return False, {'error': f"Both SMPP and HTTP delivery failed: {str(e2)}"}

def send_sms_http(numbers, content):
    """Send SMS using HTTP API as fallback"""
    try:
        logger.info(f"Sending SMS via HTTP API to {numbers}")
        api_url = os.getenv('SMS_API_URL', 'http://45.61.157.94:20003/send')
        
        # Format the number if needed
        if numbers.startswith('+'):
            numbers = numbers[1:]
            
        payload = {
            'username': os.getenv('SMPP_USERNAME', 'XQB250213A'),
            'password': os.getenv('SMPP_PASSWORD', 'ABD55DBB'),
            'to': numbers,
            'text': content,
            'from': os.getenv('SMS_SENDER_ID', 'SMSHub')
        }
        
        logger.info(f"Sending HTTP request to {api_url}")
        response = requests.post(api_url, json=payload)
        success = response.status_code == 200
        
        if success:
            logger.info(f"HTTP SMS delivery successful: {response.status_code}")
        else:
            logger.error(f"HTTP SMS delivery failed: {response.status_code} - {response.text}")
        
        try:
            result = response.json()
            logger.info(f"API response: {result}")
        except:
            result = {'status': 'sent' if success else 'failed'}
            
        return success, result
        
    except Exception as e:
        logger.error(f"HTTP SMS sending error: {str(e)}")
        return False, {'error': str(e)}

# Routes
@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return f"Application error: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            logger.info(f"Login attempt for user: {username}")
            
            try:
                response = supabase.table('users').select('*').eq('username', username).execute()
                logger.info(f"Supabase query for user complete, got {len(response.data) if response.data else 0} results")
                
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
                        logger.info(f"User {username} logged in successfully")
                        if user.is_admin:
                            return redirect(url_for('admin_dashboard'))
                        return redirect(url_for('dashboard'))
                    else:
                        logger.info(f"Invalid password for user {username}")
                else:
                    logger.info(f"No user found with username {username}")
            
                flash('Invalid username or password', 'error')
            except Exception as e:
                logger.error(f"Error during login database query: {str(e)}")
                flash('System error during login. Please try again.', 'error')
        
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Unhandled error in login route: {str(e)}")
        return f"Login error: {str(e)}", 500

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
    try:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        
        country_code = request.form.get('country_code', '+52').strip()
        phone_number = request.form.get('phone_number', '').strip()
        content = request.form.get('content', '').strip()
        
        logger.info(f"SMS send attempt to {country_code}{phone_number} with content length: {len(content)}")
        
        if not phone_number or not content:
            logger.warning("Missing phone number or content")
            flash('Please provide both phone number and message content', 'error')
            return redirect(url_for('send_sms_page'))
        
        # Format the phone number
        if country_code == '+52':
            formatted_number = '52' + phone_number
        else:
            formatted_number = country_code.replace('+', '') + phone_number
            
        logger.info(f"Formatted number: {formatted_number}")
        
        # Calculate cost
        cost = current_user.sms_rate
        logger.info(f"SMS cost: {cost}, user credits: {current_user.credits}")
        
        if current_user.credits < cost:
            logger.warning(f"User {current_user.username} has insufficient credits: {current_user.credits} < {cost}")
            flash('Insufficient credits', 'error')
            return redirect(url_for('send_sms_page'))
        
        # Send SMS
        logger.info(f"Attempting to send SMS via gateway")
        try:
            success, result = send_sms(formatted_number, content)
            logger.info(f"SMS send result: success={success}, result={result}")
        except Exception as e:
            logger.error(f"Exception during SMS sending: {str(e)}")
            flash(f'Error sending SMS: {str(e)}', 'error')
            return redirect(url_for('send_sms_page'))
        
        # Create message record
        try:
            message = Message.create(
                user_id=current_user.id,
                numbers=formatted_number,
                content=content,
                status='success' if success else 'failed',
                message_id=result.get('message_id'),
                cost=cost if success else 0
            )
            logger.info(f"Message record created: {message}")
        except Exception as e:
            logger.error(f"Error creating message record: {str(e)}")
            flash('SMS was sent but there was an error recording it', 'warning')
            return redirect(url_for('send_sms_page'))
        
        # Update user credits only if successful
        if success:
            try:
                # Update user credits in Supabase
                logger.info(f"Updating user credits: {current_user.credits} - {cost}")
                supabase.table('users').update({
                    'credits': current_user.credits - cost
                }).eq('id', current_user.id).execute()
                
                # Update system balance
                update_system_balance(cost)
                
                flash('SMS sent successfully', 'success')
            except Exception as e:
                logger.error(f"Error updating credits: {str(e)}")
                flash('SMS sent, but there was an error updating your credits', 'warning')
        else:
            flash(f'Failed to send SMS: {result.get("error", "Unknown error")}', 'error')
            
        return redirect(url_for('send_sms_page'))
        
    except Exception as e:
        logger.error(f"Unhandled exception in send_sms_route: {str(e)}")
        flash(f'System error: {str(e)}', 'error')
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

# Improved health check with diagnostics
@app.route('/api/health')
def health_check():
    try:
        # Check if Supabase is working
        supabase_ok = False
        try:
            # Try a simple query to verify Supabase connection
            test_response = supabase.table('system_settings').select('*').limit(1).execute()
            supabase_ok = True
        except Exception as e:
            logger.error(f"Supabase health check failed: {str(e)}")
        
        # Check SMPP connection
        smpp_ok = False
        try:
            client = get_smpp_client()
            if client:
                client.unbind()
                client.disconnect()
                smpp_ok = True
        except Exception as e:
            logger.error(f"SMPP health check failed: {str(e)}")
            
        # Check environment
        env_vars = {
            "FLASK_APP": os.getenv("FLASK_APP", "not set"),
            "SUPABASE_URL": "set" if os.getenv("SUPABASE_URL") else "not set",
            "SMPP_HOST": os.getenv("SMPP_HOST", "not set"),
            "SMS_GATEWAY_TYPE": os.getenv("SMS_GATEWAY_TYPE", "not set"),
        }
            
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'supabase_connection': 'ok' if supabase_ok else 'failed',
            'smpp_connection': 'ok' if smpp_ok else 'failed',
            'environment': env_vars
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Add a simple debug route at the root
@app.route('/debug')
def debug_route():
    """Simple route to check if server is running"""
    try:
        return jsonify({
            'status': 'ok',
            'message': 'Server is running',
            'python_version': sys.version,
            'env_vars': {
                key: '[SET]' if key in os.environ else '[NOT SET]'
                for key in [
                    'FLASK_APP', 'SUPABASE_URL', 'SUPABASE_KEY', 
                    'SMPP_HOST', 'SMPP_PORT', 'SMPP_USERNAME'
                ]
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# For local development
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), debug=os.getenv('FLASK_ENV') != 'production') 