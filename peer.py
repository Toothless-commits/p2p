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
    while True:
        msg = get_msg(conn)
        peer_name = msg.get("unique_id")

        if peer_name not in peers:
            peers[peer_name] = conn
        print(msg.get("content"))

        

def send_conn(conn):
    name = input("Enter name: ")
    alpha = string.ascii_uppercase + string.digits
    unique_id = ''.join(secrets.choice(alpha) for _ in range(6))
    msg = input("Enter the message: ")
    send = {"unique_id": unique_id, "name": name, "content": msg}
    conn.sendall(encd_msg(send))

def listner(s):
    try:
        while True:
            conn, addr = s.accept()
            
            t1 = threading.Thread(target=handle_peer, args=(conn,))
            t1.daemon = True
            t1.start()
    except Exception as e:
        print(f"Error : {e}")

def connect(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))   
    return s

def start_peer(my_port, peer_ip=None, peer_port=None):
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
         send_conn(conn)   
    else:
        while True:
            pass

def peer():
    my_port = int(input("Enter your port: "))
    join = input("Connect to existing peer (y/n)? ")
    if join == 'y':
        peer_ip = input("Peer IP: ")
        peer_port = int(input("Port: "))
        start_peer(my_port, peer_ip, peer_port)
    else:
        start_peer(my_port)

peer()