from hl7apy.parser import parse_message
from hl7apy.mllp import AbstractHandler
from hl7apy.mllp import AbstractErrorHandler
from hl7apy.mllp import UnsupportedMessageType
from hl7apy.mllp import MLLPServer
from hl7apy.core import Message

import sys
import argparse
import os

def handle_message(msg):

    # Process the received HL7 message here
    print("Received HL7 message:")
    print(msg.to_er7())

    # Create an ACK message
    ack = Message("ACK")
    ack.msh.msh_9 = "ACK"
    ack.msh.msh_10 = msg.msh.msh_10
    ack.msh.msh_11 = "P"
    ack.msa.msa_1 = "AA"
    ack.msa.msa_2 = msg.msh.msh_10

    return ack.to_er7()

class ErrorHandler(AbstractErrorHandler):
    def reply(self):
        if isinstance(self.exc, UnsupportedMessageType):
            # return your custom response for unsupported message
            print("Unsupported message type")
            print( self.exc )
        else:
            # return your custom response for general errors
            print("Unknown error")

class ORUHandler(AbstractHandler):
    def __init__(self, msg, config):
        super(ORUHandler, self).__init__(msg)
        self.config = config

    def reply(self):
        print("Received ORU Message")
        msg = parse_message(self.incoming_message)

        if self.config.get('archive') is not None:
            if os.path.exists(self.config.get('archive')):
                stamp = msg.msh.msh_7.value
                id = msg.msh.msh_10.value
                fname=os.path.join(self.config.get('archive'),str(stamp) + "_" + id + ".hl7")
                print("Archiving message to: " + fname)
                with open(fname, "w") as text_file:
                    #text_file.write(msg.to_er7().encode('utf-8'))
                    print()
                    text_file.write(str(msg.to_mllp()))
        # do something with the message

        # Create an ACK message
        ack = Message("ACK")
        ack.msh.msh_9 = "ACK"
        ack.msh.msh_3 = str(self.config.get('sending_application'))
        ack.msh.msh_4 = str(self.config.get('sending_facility'))
        ack.msh.msh_10 = msg.msh.msh_10
        ack.msh.msh_11 = "P"
        ack.msa.msa_1 = "AA"
        ack.msa.msa_2 = msg.msh.msh_10
        ack.msa.msa_3 = "Success"

        #print("Returning response")
        #print( ack.to_mllp() )
        #print( ack.to_er7() )
        
        # populate the message
        #return ack.to_mllp()
    
        return ack.to_er7()
    
def main():

    parser = argparse.ArgumentParser(description='Apply lung segmentation models to a CT volume')
    parser.add_argument('-p', '--port', help='Port number for server', type=int, required=False, default=2575)
    parser.add_argument('-o', '--output', help='Archive directory', type=str, required=False, default=None)
    parser.add_argument('-f', '--facility', help='Sending facility name', type=str, required=False, default='Sending Facility')
    parser.add_argument('-a', '--application', help='Sending application name', type=str, required=False, default='Sending Application')
    args = parser.parse_args()

    config={ 'archive' : args.output,
            'sending_application' : args.application,
            'sending_facility' : args.facility }

    handlers = { 'ORU^R01': (ORUHandler,config), 'ERR' : (ErrorHandler,) }

    print("Opening on port: " + str(args.port))


    

    server = MLLPServer('localhost', args.port, handlers)
    server.serve_forever()

if __name__=="__main__":
    sys.exit(main())