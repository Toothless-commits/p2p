import socket
from config import DISCOVERY_HOST,DISCOVERY_PORT

def Reuse_Socket(s):
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    

def Make_Connection():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    return s 


def Bind(s):
    s.bind((DISCOVERY_HOST,DISCOVERY_PORT))

def Listen(s):
    s.listen()

def Connect(s):
    conn, addr = s.accept()

    return conn,addr


def Start_Server():
    s = Make_Connection()
    Reuse_Socket(s)
    Bind(s)
    Listen(s)
    conn,addr =Connect(s)
    return conn,addr