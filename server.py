import threading 
import struct 
import json 
import sys 
import socket

HOST = '127.0.0.1'
PORT = 5001

clients = {}
client_lock = threading.Lock()
def decd_msg(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            raise ConnectionError
        data += packet
    return data

def get_msg(conn) -> dict:
    head = decd_msg(conn, 4)
    length = struct.unpack('!I', head)[0]
    json_data = decd_msg(conn, length).decode('utf-8')
    return json.loads(json_data)

def encd_msg(msg):
    json_msg = json.dumps(msg)
    json_bytes = json_msg.encode('utf-8')
    header = struct.pack('!I', len(json_bytes))
    return header + json_bytes

def broadcast(conn, data_dict):
    payload = encd_msg(data_dict)
    with client_lock :
        client_list = list(clients.items())

    for user, client_conn in client_list:
        if client_conn != conn:
            try:
                 client_conn.sendall(payload)
            except Exception as e:
                with client_lock:
                    if user in clients:
                        del clients[user]

def handle_client(conn):
    username = None
    try:
        # 1. Handle initial connection handshake (get username)
        initial_msg = get_msg(conn)
        username = initial_msg.get("username")
        with client_lock :
            if username and username not in clients:
                clients[username] = conn
                print(f"[*] Username: {username} has connected")
            else:
                conn.close()
                return

        broadcast(conn,{
              "type":"chat", 
              "content":f"[*]{username} has joined the chat room"
              })

        # 2. Main loop for handling incoming messages
        while True:
            msg = get_msg(conn)  # CRITICAL: Fetch next message inside loop
            msg_type = msg.get("type")

            if msg_type == "chat":
                sender = msg.get("sender")
                content = msg.get("content")
                message = f"[*]{sender}:{content}"
                broadcast(conn, {
                    "type": "chat", 
                    "content": message
                })  

            elif msg_type == "dm":
                sender = msg.get("sender")
                receiver = msg.get("reciever")
                content = msg.get("content")
                dm_msg = {
                    "type": "dm", 
                    "sender": sender, 
                    "message": content
                }
                with client_lock:
                    reciever_conn = clients.get(receiver)

                if reciever_conn:
                    reciever_conn.sendall(encd_msg(dm_msg))

    except Exception:
        pass

    # 3. Cleanup on disconnect
    with client_lock:
        if username and username in clients:
            del clients[username]
    
    broadcast(conn, {
        "type": "system",
        "message": f"{username} has left the chat"
    })

    conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((HOST, PORT))
    s.listen()
    print(f"[*] Server listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn,))
            thread.daemon = True
            thread.start()
    except Exception as e:
        pass

if __name__ == '__main__':
    start_server()
