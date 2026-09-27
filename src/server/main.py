from p2p.connections import *
from p2p.protocol import *
from server.state import * 
from server.discovery import *
import threading

peer = PeerState()
lock = threading.Lock()

def Handle_Client(conn,addr):
    while True : 
        try :

            msg = Read_Message(conn)

            if not msg :
                break

            msg_type = msg["type"]
            p_id = msg["peer_id"]
        
            
            if msg_type == "connect" :
                port = msg["Port"]
                with lock :
                    add_to_peer(p_id,peer,addr,port)

            elif msg_type == "disconnect":
                with lock :
                    remove(p_id,peer)
                break

            elif msg_type == "peer_list":
                with lock :
                    peer_list = dict(peer)
                msg = {"type":"peer_list", 
                       "peer_list" : peer_list}
                conn.sendall(Encoding_Message(msg))
        except Exception as e : 
            print(f"Error : {e}")

    conn.close()


def Accept_Loop(s):
    while True : 
        try : 
            conn , addr = discovery(s)
            t1 = threading.Thread(target=(Handle_Client),args=(conn,addr,))
            t1.start()
        except Exception as e :
            print(f"Error : {e}")

s = Make_Connection()
Reuse_Socket(s)
Bind(s,DEFAULT_PEER_HOST,DEFAULT_PEER_PORT)
Listen(s)

Accept_Loop(s)


