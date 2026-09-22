import socket
from p2p.config import DISCOVERY_HOST,DISCOVERY_PORT

def Reuse_Socket(s):
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    

def Make_Connection():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    return s 


def Bind(s,HOST,PORT):
    s.bind((HOST,PORT))

def Listen(s):
    s.listen()

def Connect(s):
    conn, addr = s.accept()

    return conn,addr


def Start_Server(HOST = DISCOVERY_HOST,PORT=DISCOVERY_PORT):
    s = Make_Connection()
    Reuse_Socket(s)
    Bind(s,HOST,PORT)
    Listen(s)
    conn,addr =Connect(s)
    return conn,addr