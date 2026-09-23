from src.p2p.config import * 
from src.p2p.protocol import * 
from src.p2p.connections import * 
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
                print(list)
                for peer_id in list : 
                    if peer_id not in peers:
                        connect_to_new_peer(peers[peer_id],conn)
            else :
                print(Recieved_Message)

    except Exception as e :
        print(f"Error : {e}")

def outgoing(conn,):
    try :
        while True:
            choice = input("1.Get peer's list \n 2.Direct Msg")
            if choice == "1" :
                with lock:
                    conn = peers["Server"]

                conn.sendall(Encoding_Message("Get Peers"))

            elif choice == "2" :
                peer_id = input("Enter the peer_id you wanna message")

                for peer in peers :
                    if peer_id == peer :
                        with lock :
                            conn = peers[peer_id]
                            break
                    else :
                        print("Enter correct peer_id")


                message = input("Enter the message you wanna send")

                conn.sendall(Encoding_Message(message))
    except Exception as e: 
        print(f"Error : {e}")


def start_server():

    IP = input("Enter your ip address").strip()
    Port = int(input("Enter your port number"))
    conn,addr = Start_Server(IP,Port)

    conn.connect((DISCOVERY_HOST,DISCOVERY_PORT))
    peers["Server"] =conn
    conn.sendall(Encoding_Message("Register"))

    t1 = threading.Thread(target=(incoming),args=(conn,))
    t2 = threading.Thread(target=(outgoing),args=(conn,))
    t1.daemon=True
    t2.daemon=True
    t1.start()
    t2.start()
