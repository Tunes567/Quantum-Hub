from smpp_client import SMPPClient
import logging
import sys

# Configure logging to show more details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('test_smpp')

def test_smpp_connection():
    # Create SMPP client instance
    client = SMPPClient(
        host='85.239.241.134',
        port=20002,
        system_id='MX-Route',  # Exact username
        password='MX-Route'    # Exact password
    )
    
    logger.info(f"Created SMPP client with system_id: {client.system_id}")
    logger.info(f"Password length: {len(client.password)} characters")
    
    # Try to connect and bind
    logger.info("Attempting to connect and bind...")
    if client.connect():
        logger.info("Successfully connected and bound to SMPP server")
        
        # Try to send a test message
        test_number = '521234567890'  # Replace with your test number
        test_message = 'Test message from Quantum Hub SMS'
        
        logger.info(f"Sending test message to {test_number}")
        logger.info(f"Message content: {test_message}")
        
        success, result = client.send_message(
            source_addr='QUANTUMHUB',
            destination_addr=test_number,
            message=test_message
        )
        
        if success:
            logger.info("Test message sent successfully")
        else:
            logger.error(f"Failed to send test message: {result}")
        
        # Disconnect
        client.disconnect()
    else:
        logger.error("Failed to connect to SMPP server")

if __name__ == '__main__':
    logger.info("Starting SMPP connection test...")
    test_smpp_connection() 