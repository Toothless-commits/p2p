import socket
import struct
import json
import threading
import secrets
import string

peers = {}

def decd_msg(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            raise ConnectionError
        data += packet
    return data

def get_msg(conn):
        head = decd_msg(conn, 4)
        length = struct.unpack('!I', head)[0]
        data = decd_msg(conn, length).decode('utf-8')
        return json.loads(data)

def encd_msg(msg):
    json_msg = json.dumps(msg)
    json_data = json_msg.encode('utf-8')
    header = struct.pack('!I', len(json_data))
    return header + json_data

def handle_peer(conn):
        peer_name = None
        try : 
             while True:

                msg = get_msg(conn)
                peer_name = msg.get("unique_id")
                name = msg.get("name")
                if peer_name not in peers:
                    peers[peer_name] = conn
                print("Name",name,":",msg.get("content"))
        except ConnectionError as e : 
            print (f"Error : {e}")
        finally:
            if peer_name : 
                peers.pop(peer_name,None)
            conn.close()
        

def send_conn(conn,name,unique_id):
    msg = input("Enter the message: ")
    send = {"unique_id": unique_id, "name": name, "content": msg}
    conn.sendall(encd_msg(send))

def listner(s):
   
        while True:
            try:
                conn, addr = s.accept()
                t1 = threading.Thread(target=handle_peer, args=(conn,))
                t1.daemon = True
                t1.start()
            except Exception as e :
                print(f"Error {e}")

def connect(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))   
    return s

def start_peer(my_port, peer_ip=None, peer_port=None,Name=None,unique_id=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', my_port))  
    s.listen()

    t1 = threading.Thread(target=listner, args=(s,))
    t1.daemon = True
    t1.start()

    if peer_ip and peer_port:
        conn = connect(peer_ip, peer_port)
        t2 = threading.Thread(target=handle_peer, args=(conn,))
        t2.daemon = True
        t2.start()
        while True:
         send_conn(conn,Name,unique_id)   
    else:
        while True:
            pass

def peer():
    name = input("Enter your name")
    alpha = string.ascii_uppercase + string.ascii_letters
    unique_id = ''.join(secrets.choice(alpha) for _ in range (6))
    my_port = int(input("Enter your port: "))
    join = input("Connect to existing peer (y/n)? ")
    if join == 'y':
        peer_ip = input("Peer IP: ")
        peer_port = int(input("Port: "))
        start_peer(my_port, peer_ip, peer_port,name,unique_id)
    else:
        start_peer(my_port,Name = name,unique_id=unique_id)

peer()