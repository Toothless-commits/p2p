from p2p.config import * 
from p2p.connections import * 
from p2p.protocol import * 
from server.state import * 
import threading

lock = threading.Lock()


def discovery(s):
    conn,addr = Connect(s)
    return conn,addr

def add_to_peer(p_id,conn,peer,addr,port):
    peer[p_id]={"ip":addr[0],
                "port":port}

def remove(p_id,peer):
    del peer[p_id]