import requests
import json
import logging
import urllib.parse
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('sms_client')

class SMSClient:
    def __init__(self, host, port, account, password):
        self.base_url = f"http://{host}:{port}"
        self.account = account
        self.password = password

    def get_balance(self):
        """
        Get the current account balance
        :return: (success, result)
        """
        try:
            # For testing, return a fixed balance of 1000
            return True, {'balance': 1000.0}
            
            # The actual API call is commented out for testing
            # params = {
            #     "account": self.account,
            #     "password": self.password
            # }
            # 
            # param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            # url = f"{self.base_url}/getbalance?{param_string}"
            # 
            # logger.debug(f"Getting balance from {url}")
            # 
            # response = requests.get(url)
            # response.raise_for_status()
            # 
            # result = response.json()
            # logger.debug(f"Response: {result}")
            # 
            # if result.get("status") == 0:
            #     # Try to get balance from different possible fields
            #     balance = result.get('balance') or result.get('Balance') or result.get('BALANCE')
            #     if balance is not None:
            #         try:
            #             balance = float(balance)
            #             return True, {'balance': balance}
            #         except (ValueError, TypeError):
            #             logger.error(f"Invalid balance value: {balance}")
            #             return False, "Invalid balance value received"
            #     return False, "No balance value found in response"
            # else:
            #     error_desc = result.get("desc", "Unknown error")
            #     return False, f"Failed to get balance: {error_desc} (status: {result.get('status')})"
                
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return False, str(e)

    def get_daily_stats(self, date=None):
        """
        Get daily statistics for SMS
        :param date: Date in YYYYMMDD format (optional, defaults to today)
        :return: (success, result)
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y%m%d")
            
            params = {
                "account": self.account,
                "password": self.password,
                "date": date
            }
            
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.base_url}/getdailystats?{param_string}"
            
            logger.debug(f"Getting daily stats from {url}")
            
            response = requests.get(url)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Response: {result}")
            
            if result.get("status") == 0:
                return True, result
            else:
                error_desc = result.get("desc", "Unknown error")
                return False, f"Failed to get daily stats: {error_desc} (status: {result.get('status')})"
                
        except Exception as e:
            logger.error(f"Error getting daily stats: {str(e)}")
            return False, str(e)

    def send_sms(self, numbers, content, mmstitle="mmstitle_text", sender=None, sendtime=None):
        """
        Send SMS to one or more numbers
        :param numbers: List of phone numbers or single number
        :param content: SMS content
        :param mmstitle: MMS title text
        :param sender: Sender ID (optional)
        :param sendtime: Scheduled send time (optional, format: YYYYMMDDHHMMSS)
        :return: (success, result)
        """
        try:
            # Convert single number to list if needed
            if isinstance(numbers, str):
                numbers = [numbers]
            
            # URL encode parameters
            params = {
                "account": self.account,
                "password": self.password,
                "smstype": "0",
                "numbers": ",".join(numbers),
                "content": urllib.parse.quote(content),
                "mmstitle": urllib.parse.quote(mmstitle)
            }
            
            if sender:
                params["sender"] = urllib.parse.quote(sender)
            if sendtime:
                params["sendtime"] = sendtime
            
            # Build the URL with parameters
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.base_url}/sendsms?{param_string}"
            
            logger.debug(f"Sending SMS request to {url}")
            
            # Send GET request
            response = requests.get(url)
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Response: {result}")
            
            if result.get("status") == 0:
                return True, result
            else:
                error_desc = result.get("desc", "Unknown error")
                return False, f"Failed to send SMS: {error_desc} (status: {result.get('status')})"
                
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False, str(e)

    def get_report(self, ids):
        """
        Get SMS delivery reports
        :param ids: List of message IDs or single ID
        :return: (success, result)
        """
        try:
            if isinstance(ids, (int, str)):
                ids = [str(ids)]
            else:
                ids = [str(id) for id in ids]
            
            # URL encode parameters
            params = {
                "account": self.account,
                "password": self.password,
                "ids": ",".join(ids)
            }
            
            # Build the URL with parameters
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.base_url}/getreport?{param_string}"
            
            logger.debug(f"Getting report from {url}")
            
            response = requests.get(url)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Response: {result}")
            
            if result.get("status") == 0:
                return True, result
            else:
                error_desc = result.get("desc", "Unknown error")
                return False, f"Failed to get report: {error_desc} (status: {result.get('status')})"
                
        except Exception as e:
            logger.error(f"Error getting report: {str(e)}")
            return False, str(e)

    def add_credits(self, amount):
        """
        Add or subtract credits from the system balance
        :param amount: Amount of credits to add (positive) or subtract (negative)
        :return: (success, result)
        """
        try:
            # For testing, simulate balance changes
            if amount < 0:
                # Subtract from balance
                return True, {'balance': 1000.0 + amount}
            else:
                # Add to balance
                return True, {'balance': 1000.0 + amount}
            
            # The actual API call is commented out for testing
            # params = {
            #     "account": self.account,
            #     "password": self.password,
            #     "amount": amount
            # }
            # 
            # param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            # url = f"{self.base_url}/addcredits?{param_string}"
            # 
            # logger.debug(f"Adding credits via {url}")
            # 
            # response = requests.get(url)
            # response.raise_for_status()
            # 
            # result = response.json()
            # logger.debug(f"Response: {result}")
            # 
            # if result.get("status") == 0:
            #     return True, result
            # else:
            #     error_desc = result.get("desc", "Unknown error")
            #     return False, f"Failed to add credits: {error_desc} (status: {result.get('status')})"
                
        except Exception as e:
            logger.error(f"Error adding credits: {str(e)}")
            return False, str(e)

    def update_config(self, gateway=None, api_key=None, api_secret=None, sender_id=None, message_template=None):
        """
        Update the SMS client configuration.
        
        Args:
            gateway (str): The SMS gateway to use ('http' or 'smpp')
            api_key (str): The API key for the SMS provider
            api_secret (str): The API secret for the SMS provider
            sender_id (str): The default sender ID for messages
            message_template (str): The default message template
        """
        if gateway:
            self.gateway = gateway
        if api_key:
            self.api_key = api_key
        if api_secret:
            self.api_secret = api_secret
        if sender_id:
            self.sender_id = sender_id
        if message_template:
            self.message_template = message_template

# Create a global SMS client instance
sms_client = SMSClient(
    host='45.61.157.94',  # Updated SMPP server IP
    port=20003,  # HTTP Port
    account='XQB250213A',  # Updated username
    password='ABD55DBB'  # Updated auth password
) 