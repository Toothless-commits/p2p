from p2p.config import * 
from p2p.protocol import * 
from p2p.connections import * 
from node.state import PeerState
import threading 

lock = threading.Lock()
peers = PeerState()

def connect_to_new_peer (info,conn):
    IP = info["IP"]
    Port = info["Port"]

    try :
        conn.connect((IP,Port))
        peers[info["peer_id"]]=conn
    except :
        raise ConnectionRefusedError
        

def incoming(conn):
    try : 
        while True : 
            Recieved_Message = Read_Message(conn)
            type = Recieved_Message["Type"]

            if type == "Peer List":
                list = Recieved_Message["peers"]

                for peer_id in list : 
                    if peer_id not in peers:
                        connect_to_new_peer(peers[peer_id],conn)

    except Exception as e :
        print(f"Error : {e}")



def start_server():

    IP = input("Enter your ip address")
    Host = int(input("Enter your port number"))
    conn,addr = Start_Server(IP,Host)

    conn.connect((DISCOVERY_HOST,DISCOVERY_PORT))
    peers["Server"] =conn

    t1 = threading.Thread(target=(incoming),args=(conn,))
    t1.daemon=True
    t1.start()


