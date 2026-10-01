from pathlib import Path 
import hashlib


def file_hash(p):
    h = hashlib.sha256()
    with p.open("rb") as f :
        while chunk := f.read(64*1024):
            h.update(chunk)
    return h.hexdigest()


def file_send(path,conn):
    data = file_hash(path)
    conn.sendall(data)


def file_load(path,conn):
    p = Path(path)

    try : 
        if not p.exists :
            print("File does not exist")
        else :
            file_send(path,conn)
    except Exception as e :
        print(f"Error : {e}")


