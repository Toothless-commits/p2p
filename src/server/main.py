from p2p.connections import *
from p2p.protocol import *
from server.state import * 
from server.discovery import *
import threading

peer = PeerState()
lock = threading.Lock()

def Handle_Client(s):
    while True : 
        try :
            conn,addr = discovery(s)

            msg = Read_Message(conn)

            type = msg["type"]
            p_id = msg["peer_id"]
            
            if type == "connect" :
                with lock :
                    add_to_peer(p_id,conn,peer)

            elif type == "disconnect":
                remove(p_id,peer)

            elif type == "peer list":
                with lock :
                    peer_list = dict(peer)
                msg = {"type":"Peer List", 
                       "peers" : list(peer_list.keys())}
                conn.sendall(Encoding_Message(msg))
        except Exception as e : 
            print(f"Error : {e}")



s = Make_Connection()

Handle_Client(s)




