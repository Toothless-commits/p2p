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

            if not Check(conn) :
                add_to_peer(conn,peer)

        except Exception as e : 
            print(f"Error : {e}")

s = Start_Server()

Handle_Client(s)




