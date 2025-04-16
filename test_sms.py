from sms_client import SMSClient
import logging
import sys

# Configure logging to show more details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('test_sms')

def test_sms_sending():
    # Create SMS client instance
    client = SMSClient(
        host='45.61.157.94',  # Updated SMPP server IP
        port=20003,  # HTTP Port
        account='XQB250213A',  # Updated username
        password='ABD55DBB'  # Updated auth password
    )
    
    logger.info(f"Created SMS client with account: {client.account}")
    
    # Test sending a single SMS
    test_number = '521234567890'  # Replace with your test number
    test_message = 'Test message from Quantum Hub SMS'
    
    logger.info(f"Sending test message to {test_number}")
    logger.info(f"Message content: {test_message}")
    
    success, result = client.send_sms(
        numbers=test_number,
        content=test_message,
        mmstitle="Test Message"
    )
    
    if success:
        logger.info("Test message sent successfully")
        logger.info(f"Response: {result}")
        
        # If we have message IDs, try to get the report
        if result.get('array'):
            message_id = result['array'][0][1]
            logger.info(f"Getting report for message ID: {message_id}")
            
            report_success, report_result = client.get_report(message_id)
            if report_success:
                logger.info(f"Report: {report_result}")
            else:
                logger.error(f"Failed to get report: {report_result}")
    else:
        logger.error(f"Failed to send test message: {result}")

if __name__ == '__main__':
    logger.info("Starting SMS sending test...")
    test_sms_sending() 