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
indent = "    "

def subgroup (group,  indent):
    indent = indent + "    "
    print (indent , group)
    for group_segment in group.children:
        if isinstance(group_segment, Group):
            subgroup (group_segment)
        else: 
            print(indent_seg, indent ,group_segment)
            for attribute in group_segment.children:
                print(indent_fld, indent ,attribute, attribute.value)

def show_message(msg):

    indent_seg = "    "
    indent_fld = "        "
    print(msg.children[1])
    for segment in msg.children:
        if isinstance(segment, Segment):
            print(indent + str(segment) + str(len(segment.children)))
            for attribute in segment.children:
                print(indent_fld, indent, attribute, attribute.value)
        elif isinstance(segment, Group):
            for group in segment.children:
                print(indent,group)
                for group_segment in group.children:
                    if isinstance(group_segment, Group): 
                        subgroup(group_segment, indent)
                    else:
                        print(indent_seg, indent ,group_segment)
                        for attribute in group_segment.children:
                            print(indent_fld, indent, attribute, attribute.value)

def send_hl7_message(message, host, port):
    """Sends an HL7 message to the specified host and port."""

    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the serv
    try:
        s.connect((host, port))
    except Exception as e:
        print("Error connecting to server: "+str(e))
        return
    
    # Encode the HL7 message to ER7 format
    # encoded_message = message.to_er7()
    # s.sendall(encoded_message.encode('utf-8'))
    
    encoded_message = message.to_mllp().encode('utf-8')
    #print(encoded_message)
    s.sendall(encoded_message)
    

    # Receive the response (if any)
    response = s.recv(1024)

    r_msg = parse_message(response.decode('utf-8'))
    print('Acknowledgement Code: '+r_msg.msa.msa_1.value)
    #print(r_msg.to_er7())
    #print(r_msg.to_mllp())
    #print(r_msg.msh.msh_2)
    #show_message(r_msg)

    # Close the socket
    s.close()
    

def main():

    parser = argparse.ArgumentParser(description='Send HL7 message')
    parser.add_argument('-a', '--addr', help='destination IP address', type=str, required=True)
    parser.add_argument('-p', '--port', help='Port number for server', type=int, required=True)
    parser.add_argument('-i', '--input_message', help='File with message to send', type=str, required=True)
    args = parser.parse_args()

    with open(args.input_message, 'r') as file:
        dat = file.readlines()
    dat = ''.join(dat).replace('\n', '\r')
    msg = parse_message(dat)

    print("Sending to "+args.addr+ ":" + str(args.port))
    send_hl7_message(msg, args.addr, args.port)

if __name__=="__main__":
    sys.exit(main())