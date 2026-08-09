import json 
import threading 
import struct 
import socket

HOST = '127.0.0.1'
PORT = 5001

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
    json_mgs = json.dumps(msg)
    json_data = json_mgs.encode('utf-8')
    header = struct.pack('!I', len(json_data))
    return header + json_data

def incoming_msg(conn):
    while True:
        try:
            msg = get_msg(conn)
            msg_type = msg.get("type")

            if msg_type == "dm":
                msg_sender = msg.get("sender")
                msg_content = msg.get("message") # Fixed to match server's "message" key
                print(f"\n[DM] {msg_sender}: {msg_content}")

            elif msg_type == "system":
                msg_content = msg.get("message") # Fixed to match server's "message" key
                print(f"\n{msg_content}")

            elif msg_type == "chat":
                msg_content = msg.get("content")
                print(f"\n{msg_content}")
        except Exception:
            print("\n[-] Disconnected from server.")
            break

def outgoing_msg(conn, user):
    while True:
        try:
            choice = input("Enter the type of msg:\n 1. Chat\n 2. DM\nChoice: ").strip()

            if choice == "2" or choice.lower() == "dm":
                receiver = input("Enter the name of receiver: ")
                content = input("Enter the contents of the message: ")
                msg = {
                    "type": "dm", 
                    "sender": user, 
                    "reciever": receiver, 
                    "content": content
                }
                conn.sendall(encd_msg(msg))
            else:
                content = input("Enter the contents of the message: ")
                msg = {
                    "type": "chat",
                    "sender": user,
                    "content": content
                }
                conn.sendall(encd_msg(msg))
        except Exception:
            break

def start_server():
    name = input("Enter your username: ").strip()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    initial_msg = {
        "username": name
    }
    s.sendall(encd_msg(initial_msg))

    t1 = threading.Thread(target=incoming_msg, args=(s,))
    t1.daemon = True
    t1.start()

    outgoing_msg(s, name)

if __name__ == '__main__':
    start_server()