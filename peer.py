import struct 
import threading 
import json 
import uuid 
import socket

peers={}

def decd_msg(conn,length):
    data =b""
    while len(data)<length:
        packet = conn.recv(length-len(data))
        if not packet : 
            raise ConnectionError
        data+=packet

    return data

def get_msg(conn):
    head = decd_msg(conn,4)
    length = struct.unpack('!I',head)[0]

    message = decd_msg(conn,length)

    return json.loads(message)

def encd_msg(message):
    json_message= json.dumps(message)
    json_length = len(json_message)
    head = struct.pack("!I",json_length)
    return head+json_message.encode('utf-8')


def incoming_message(conn):
    while True:
        try :
            message = get_msg(conn)
            print(message.get("content"))
        except Exception as e:
            print(f"Error : {e}")


def connect_to_peer (s):
    while True : 
        conn,addr = s.accept()

        if addr[0] not in peers:
            peers[addr[0]]=conn

        t2 = threading.Thread(target=(incoming_message),args=(conn))
        t2.daemon=True 
        t2.start()


def server(IP,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(("0.0.0.0","5000"))
    peer_id = uuid.uuid4()
    name = input("Enter you name(make it anonymus)")
    msg = {"type":"register", 
           "name":name, 
           "port":port}
    s.sendall(encd_msg(msg))
    
def start_server():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    IP = input("Enter your ip")
    port = int(input("Enter your port"))

    s.bind((IP,port))
    s.listen()

    #giving info to the server after connecting first time 
    server()

    t1 = threading.Thread(target=(connect_to_peer),args=(s,))
    t1.daemon=True 
    t1.start()





