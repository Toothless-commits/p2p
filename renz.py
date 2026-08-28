import socket  
import threading
import struct 
import json

HOST ='0.0.0.0'
PORT = 5000
client_lock = threading.Lock()

def encd_msg(msg):
    json_msg = json.dumps(msg)
    json_bytes = json_msg.encode("utf-8")
    header = struct.pack("!I",len(json_bytes))
    return header+json_bytes

def decd_msg(conn,size):
    data = b""
    while len(data)<size :
        packet = conn.recv(size-len(data))
        if not packet : 
            raise ConnectionError
        data+=packet

    return data

def get_msg(conn):
    head = decd_msg(conn,4)
    length = struct.unpack("!I",head)[0]

    msg = decd_msg(conn,length).decode("utf-8")
    return json.loads(msg)


peers = {}


def send_to_peer(peer_id):

    with client_lock:
        peer = peers[peer_id]

        if not peer :return 

        connection = peer["Connection"]

        peer_list =[]
        for id,peer in  peers.items():
            peer_list.append({
                "peer_id":id, 
                "Name":peer["Name"], 
                "IP" : peer["IP"],
                "PORT" : peer["PORT"]
            })
        
    connection.sendall(encd_msg({
        "type":"peer_list", 
        "peers":peer_list
    }))

def Handle_Incoming_Request(conn,addr):

    while True:
        try : 
            msg = get_msg(conn)
            peer_id = msg.get("peer_id")
        except ConnectionError as e :
            print(f"Error : {e}")
            break
        except Exception as e : 
            print(f"Error : {e}")
            break            


        if msg.get("type")=="register":
            with client_lock:
                handle = Handle_Peer(conn,peer_id,msg.get("name"),addr[0],msg.get("port")) 

            if not handle :
                conn.sendall(encd_msg("You are already registered"))
                    
        elif msg.get("type")=="get_peers":
            send_to_peer(peer_id)

        elif msg.get("type")=="unregister":
                Remove_Peer(peer_id)

   

    conn.close()
    
    
def Remove_Peer(peer_id):
    with client_lock:
        peers.pop(peer_id,None)

def Handle_Peer(conn,peer_id,name,ip,port):

        if peer_id and ip and port and peer_id  not in peers:
            peers[peer_id]= {
                "Connection" : conn,
                "Name" : name, 
                "IP" : ip, 
                "PORT" : port
            }
            return True
        else :
            return False

    


def Start_Server():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((HOST,PORT))

    while True : 
        conn,addr = s.accept(); 
        t1 = threading.Thread(target=(Handle_Incoming_Request),args=(conn,addr,))
        t1.daemon=True
        t1.start()


if __name__ == '__main__':
    Start_Server()