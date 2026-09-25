from p2p.config import * 
from p2p.connections import * 
from p2p.protocol import * 
from server.state import * 
import threading

lock = threading.Lock()


def discovery(s):
    conn,addr = Connect(s)
    return conn,addr

def Check(conn,peers):

    msg = Read_Message(conn)

    p_id = msg["peer_id"]

    for peer_in in peers : 
        if p_id == peer_in:
            return True
        else :
            return False

def add_to_peer(conn,peer):
    msg = 
    peer[peer_id]=conn