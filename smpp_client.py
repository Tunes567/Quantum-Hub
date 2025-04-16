import smpplib.client
import smpplib.gsm
import smpplib.consts
import logging
import time
import socket

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('smpp_client')

class SMPPClient:
    def __init__(self, host, port, system_id, password):
        self.host = host
        self.port = port
        # Try to normalize the credentials
        self.system_id = system_id.strip().encode('ascii').decode('ascii')
        self.password = password.strip().encode('ascii').decode('ascii')
        self.client = None
        self.connected = False

    def test_connection(self):
        """Test if we can establish a TCP connection to the server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"TCP connection test failed: {str(e)}")
            return False

    def connect(self):
        try:
            logger.debug(f"Attempting to connect to SMPP server at {self.host}:{self.port}")
            
            # First test TCP connection
            if not self.test_connection():
                raise Exception("Cannot establish TCP connection to server")
            
            # Create SMPP client
            self.client = smpplib.client.Client(self.host, self.port)
            self.client.set_message_received_handler(self.handle_message)
            
            # Connect and bind
            logger.debug("Attempting to connect...")
            self.client.connect()
            
            logger.debug(f"Attempting to bind with system_id: '{self.system_id}' and password: '{self.password}'")
            # Try binding with different system types
            system_types = ['', 'SMPP', 'WWW']
            
            for system_type in system_types:
                try:
                    logger.debug(f"Trying bind with system_type: '{system_type}'")
                    bind_response = self.client.bind_transceiver(
                        system_id=self.system_id,
                        password=self.password,
                        system_type=system_type,
                        interface_version=0x34,  # SMPP version 3.4
                        addr_ton=0,
                        addr_npi=0,
                        address_range=''
                    )
                    
                    if bind_response.status == smpplib.consts.SMPP_ESME_ROK:
                        self.connected = True
                        logger.info(f"Successfully connected and bound to SMPP server with system_type: {system_type}")
                        return True
                except Exception as e:
                    logger.debug(f"Bind attempt with system_type '{system_type}' failed: {str(e)}")
                    continue
            
            raise Exception("All bind attempts failed")
            
        except Exception as e:
            logger.error(f"Failed to connect to SMPP server: {str(e)}")
            if self.client:
                try:
                    self.client.disconnect()
                except:
                    pass
            return False

    def disconnect(self):
        if self.client and self.connected:
            try:
                logger.debug("Attempting to unbind and disconnect from SMPP server")
                self.client.unbind()
                self.client.disconnect()
                self.connected = False
                logger.info("Successfully disconnected from SMPP server")
            except Exception as e:
                logger.error(f"Error disconnecting from SMPP server: {str(e)}")

    def send_message(self, source_addr, destination_addr, message):
        if not self.connected:
            logger.debug("Not connected to SMPP server, attempting to connect...")
            if not self.connect():
                return False, "Failed to connect to SMPP server"

        try:
            logger.debug(f"Preparing to send message to {destination_addr}")
            # Encode message parts if needed
            parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)
            logger.debug(f"Message split into {len(parts)} parts")
            
            for i, part in enumerate(parts, 1):
                logger.debug(f"Sending part {i}/{len(parts)}")
                response = self.client.send_message(
                    source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
                    source_addr_npi=smpplib.consts.SMPP_NPI_UNK,
                    source_addr=source_addr,
                    dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                    dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                    destination_addr=destination_addr,
                    short_message=part,
                    data_coding=encoding_flag,
                    esm_class=msg_type_flag,
                    registered_delivery=True
                )
                
                if response.status != smpplib.consts.SMPP_ESME_ROK:
                    raise Exception(f"Message send failed with status: {response.status}")
                
                # Add a small delay between parts
                time.sleep(0.1)
            
            logger.info(f"Successfully sent message to {destination_addr}")
            return True, "Message sent successfully"
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False, str(e)

    def handle_message(self, pdu):
        logger.info(f"Received message PDU: {pdu}")
        if pdu.command == 'deliver_sm_resp':
            logger.info("Message delivery confirmed")
        elif pdu.command == 'deliver_sm':
            logger.info(f"Received SMS: {pdu.short_message}")

# Create a global SMPP client instance with exact credentials
smpp_client = SMPPClient(
    host='85.239.241.134',
    port=20002,
    system_id='MX-Route',  # Exact username
    password='MX-Route'    # Exact password
) 