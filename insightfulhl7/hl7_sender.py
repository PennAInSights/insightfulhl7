from hl7apy.parser import parse_message
from hl7apy.mllp import AbstractHandler
from hl7apy.mllp import AbstractErrorHandler
from hl7apy.mllp import UnsupportedMessageType
from hl7apy.mllp import MLLPServer
import sys
import argparse
import socket
from hl7apy.core import Message
from hl7apy.core import Group, Segment
import logging

def send_hl7_message(message, host, port, logger=None):
    """Sends an HL7 message to the specified host and port."""
    if logger is not None:
        logger.info(f"Sending to {host}:{port}")

    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the serv
    try:
        s.connect((host, port))
    except Exception as e:
        if logger is not None:
            logger.error(f"Error connecting to server: {e}")
        return
    
    encoded_message = message.to_mllp().encode('utf-8')
    s.sendall(encoded_message)
    
    # Receive the response (if any)
    response = s.recv(1024)

    r_msg = parse_message(response.decode('utf-8'))
    if logger is not None:
        logger.info(f'Acknowledgement Code: {r_msg.msa.msa_1.value}')

    # Close the socket
    s.close()
    

def main():

    parser = argparse.ArgumentParser(description='Send HL7 message')
    parser.add_argument('-a', '--addr', help='destination IP address', type=str, required=True)
    parser.add_argument('-p', '--port', help='Port number for server', type=int, required=True)
    parser.add_argument('-i', '--input_message', help='File with message to send', type=str, required=True)
    parser.add_argument('-g', '--logging', type=str, help="Filename for logging output", default=None)
    args = parser.parse_args()

    # Setup logging
    logger = logging.getLogger("hl7_sender")
    logger.setLevel(logging.INFO)
    #if args.verbose:
    #    logger.setLevel(logging.DEBUG)
    #else:
    #    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if args.logging is not None:
        fileHandler = logging.FileHandler(args.logging)    
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

    with open(args.input_message, 'r') as file:
        dat = file.readlines()
        dat = ''.join(dat).replace('\n', '\r')
        msg = parse_message(dat)

    send_hl7_message(msg, args.addr, args.port, logger)

if __name__=="__main__":
    sys.exit(main())