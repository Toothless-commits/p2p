import threading
import uuid

from src.p2p.config import *
from src.p2p.connections import *
from src.p2p.protocol import *

from node.state import PeerState
from transfer.file import *

from pathlib import Path

lock = threading.Lock()
peers = PeerState()

Download_DIR = Path.home() / "Downloads"


def connect_to_new_peer(p_id, ip, port, peers, my_id):
    try:
        s = Make_Connection()
        s.connect((ip, port))
        s.sendall(Encoding_Message({"type": "hello", "peer_id": my_id}))
        with lock:
            peers[p_id] = s
    except Exception as e:
        raise ConnectionRefusedError(f"Failed to connect to {p_id}: {e}") from e


def check(peers, peer_list, my_id):
    for peer_id, info in peer_list.items():
        if peer_id == my_id or peer_id in peers:
            continue
        try:
            connect_to_new_peer(peer_id, info["ip"], info["port"], peers, my_id)
            print(f"Connected to {peer_id}")
        except ConnectionRefusedError as e:
            print(f"Skipping {peer_id}: {e}")


def remove_peer_by_conn(conn):

    with lock:
        for pid, s in list(peers.items()):
            if s is conn:
                del peers[pid]
                break


def read_messages(conn, addr, my_id):
    try:
        while True:
            Recieved_Messages = Read_Message(conn)

            if not Recieved_Messages:
                break

            msg_type = Recieved_Messages["type"]

            if msg_type == "peer_list":
                check(peers, Recieved_Messages["peer_list"], my_id)

            elif msg_type == "chat":
                print(f"\n[{Recieved_Messages['peer_id']}] {Recieved_Messages['text']}")
            elif msg_type == "File":
                status = receive_file(conn, Download_DIR)
                if not status:
                    print("File Cannot be shared")
            else:
                print(Recieved_Messages)

    except Exception as e:
        print(f"Error : {e}")
    finally:
        remove_peer_by_conn(conn)
        conn.close()


def incoming(IP, Port, my_id):
    try:
        s = Start_Server(IP, Port)
        while True:
            conn, addr = s.accept()
            t = threading.Thread(
                target=read_messages, args=(conn, addr, my_id), daemon=True
            )
            t.start()
    except Exception as e:
        print(f"Error : {e}")


def outgoing(p_id):
    print("start")
    try:
        while True:
            choice = input("1.Get peer's list \n2.Direct Msg \n3.File Transfer\n")

            if choice == "1":
                with lock:
                    conn = peers["Server"]

                conn.sendall(Encoding_Message({"type": "peer_list", "peer_id": p_id}))
                response = Read_Message(conn)
                check(peers, response["peer_list"], p_id)
                print(response)

            elif choice == "2":
                peer_id = input("Enter the peer_id you wanna message \n").strip()

                if peer_id == "Server" or peer_id not in peers:
                    print("Enter correct peer_id")
                    continue

                with lock:
                    conn = peers[peer_id]

                message = input("Enter the message you wanna send \n")
                conn.sendall(
                    Encoding_Message({"type": "chat", "peer_id": p_id, "text": message})
                )
            elif choice == "3":
                peer_id = input("Enter the peer_id you wanna send the file\n").strip()

                if peer_id == "Server" or peer_id not in peers:
                    print("Enter Correct peer id")
                    continue

                with lock:
                    conn = peers[peer_id]

                path = input("Enter the path of the file rn")
                file_load(path, conn)

    except Exception as e:
        print(f"Error : {e}")


def start_server():
    p_id = str(uuid.uuid4())
    print("start")
    IP = input("Enter your ip address").strip()
    Port = int(input("Enter your port number"))
    s = Make_Connection()
    try:
        s.connect((DISCOVERY_HOST, DISCOVERY_PORT))
        peers["Server"] = s
        s.sendall(
            Encoding_Message(
                {"type": "connect", "peer_id": p_id, "ip": IP, "Port": Port}
            )
        )
        t1 = threading.Thread(target=incoming, args=(IP, Port, p_id))
        t2 = threading.Thread(target=outgoing, args=(p_id,))
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("Disconnecting")
        s.sendall(Encoding_Message({"type": "disconnect", "peer_id": p_id}))
    except Exception as e:
        print(f"Error : {e}")
