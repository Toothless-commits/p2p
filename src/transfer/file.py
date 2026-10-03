from pathlib import Path
import hashlib

SHARED = Path("Shared").resolve()
OK, NOT_FOUND, DENIED = b"\x00", b"\x01", b"\x10"
CHUNK = 64 * 1024


def file_hash(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        while chunk := f.read(64 * 1024):
            h.update(chunk)
    return h.digest()


def file_send(p, conn):
    with p.open("rb") as f:
        while chunk := f.read(CHUNK):
            conn.sendall(chunk)


def file_load(path, conn):
    p = (SHARED / path).resolve()
    if not p.is_relative_to(SHARED):
        conn.sendall(DENIED)
        return False

    try:
        s1 = p.stat().st_size
    except (PermissionError, FileNotFoundError, IsADirectoryError):
        conn.sendall(DENIED)
        return False
    try:
        digest = file_hash(p)
    except (FileNotFoundError, IsADirectoryError):
        conn.sendall(NOT_FOUND)
        return False
    except PermissionError:
        conn.sendall(DENIED)
        return False

    s2 = p.stat().st_size

    if s1 != s2:
        conn.sendall(DENIED)
        return False

    header = OK + s2.to_bytes(8, "big")
    conn.sendall(header)
    try:
        file_send(p, conn)
        conn.sendall(digest)
        return True
    except Exception as e:
        print(f"Error : {e}")

    return False


def recv_exact(conn, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("peer closed mid transfer")

        buf += chunk

    return bytes(buf)


def receive_file(conn, dest: Path) -> bool:
    status = recv_exact(conn, 1)
    if status != OK:
        return False
    size = int.from_bytes(recv_exact(conn, 8), "big")

    h = hashlib.sha256()
    remaining = size
    with dest.open("wb") as f:
        while remaining:
            chunk = conn.recv(min(CHUNK, remaining))
            if not chunk:
                raise ConnectionError
            h.update(chunk)
            f.write(chunk)
            remaining -= len(chunk)

    expected = recv_exact(conn, 32)

    if h.digest() != expected:
        dest.unlink(missing_ok=True)
        return False

    return True
