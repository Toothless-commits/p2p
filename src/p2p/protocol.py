import struct 
import json 
from config import ENCODING

def Encoding_Message(msg):
    json_msg = json.dumps(msg.encode(ENCODING))
    json_length = len(json_msg)
    header = struct.pack('!I',json_length)
    return header+json_msg

def Decoding_Message(conn,n):
    data = b''
    while len(data)<n:
        packet = conn.recv(n-len(data))
        if not packet : 
            raise ConnectionError
        data +=packet

    return data


def Read_Message(conn):
    head = Decoding_Message(conn,4)

    length = struct.unpack('!I',head)[0]

    message = Decoding_Message(conn,length)

    return json.dumps(message)


    