from src.p2p.config import * 
from src.p2p.protocol import * 
from src.p2p.connections import * 
from node.state import PeerState
import uuid
import threading 

lock = threading.Lock()
peers = PeerState()

def connect_to_new_peer (p_id,ip,port,peers):
    try :
        s = Make_Connection()
        s.connect((ip,port))
        s.sendall("Connection Successfull")
        peers[p_id]=s
    except :
        raise ConnectionRefusedError
        

def incoming(IP,Port):
    print("start")
    try : 
        while True : 
            s= Start_Server(IP,Port)
            conn,addr = s.accept()
            Recieved_Message = Read_Message(conn)
            type = Recieved_Message["Type"]

            if type == "Peer List":
                list = Recieved_Message["peer_list"]
                for peer_id , info in list.items():
                    if peer_id not in peers :
                        connect_to_new_peer(peer_id,info["ip"],info["port"],peers)
            else :
                print(Recieved_Message)

    except Exception as e :
        print(f"Error : {e}")

def outgoing():
    print("start")
    try :
        while True:
            choice = input("1.Get peer's list \n 2.Direct Msg")
            if choice == "1" :
                with lock:
                    conn = peers["Server"]

                conn.sendall(Encoding_Message("Get Peers"))

            # elif choice == "2" :
            #     peer_id = input("Enter the peer_id you wanna message")

            #     for peer in peers :
            #         if peer_id == peer :
            #             with lock :
            #                 conn = peers[peer_id]
            #                 break
            #         else :
            #             print("Enter correct peer_id")


            #     message = input("Enter the message you wanna send")

            #     conn.sendall(Encoding_Message(message))
    except Exception as e: 
        print(f"Error : {e}")


def start_server():

    p_id = uuid.uuid4()
    print("start")
    IP = input("Enter your ip address").strip()
    Port = int(input("Enter your port number"))
    s = Make_Connection()
    s.connect((DISCOVERY_HOST,DISCOVERY_PORT))
    peers["Server"] =s
    s.sendall(Encoding_Message({"type":"Register", 
                                "peer_id":str(p_id),
                                "ip":IP, 
                                "Port":Port
                                }))
    t1 = threading.Thread(target=(incoming),args=(IP,Port))
    t2 = threading.Thread(target=(outgoing),args=())
    t1.daemon=True
    t2.daemon=True
    t1.start()
    t2.start()
