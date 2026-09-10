from p2p.connections import *
from p2p.protocol import *
import threading

peer = {}
lock = threading.Lock()

def Handle_Client(conn,addr):
    while True : 
        try :
            Message = Read_Message(conn)
            Type = Message["type"]

            if Type =="register":
                peer_id = Message["peer_id"]


                with lock:
                    if peer_id not in peer :
                        peer[peer_id] = {
                            "peer_id" : peer_id, 
                            "name" : Message["name"], 
                            "IP" : addr[0], 
                            "Port" : Message["Port"]
                        }

            elif Type == "Get Peers":

                with lock :
                    peer_list = list(peer)

                Msg = {"type" : "Peer List", 
                       "peers" : peer_list}

                conn.sendall(Decoding_Message(Msg))
        except Exception as e : 
            print(f"Error : {e}")

conn,addr = Start_Server()

