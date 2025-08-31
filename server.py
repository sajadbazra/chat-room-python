import argparse
import json
import re
import socket
import ssl
import threading
import time
from typing import Dict, Tuple, Optional

ENC = "utf-8"
MAX_LINE = 4096
SOCKET_TIMEOUT = 15
BACKLOG = 100

USER_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


def recv_line(sock: socket.socket, max_len: int = MAX_LINE, timeout: int = SOCKET_TIMEOUT) -> Optional[str]:

    sock.settimeout(timeout)
    buf = bytearray()
    try:
        while True:
            b = sock.recv(1)
            if not b:
                return None
            if b == b"\n":
                break
            buf += b
            if len(buf) > max_len:
                raise ValueError("line too long")
    except socket.timeout:
        raise
    return buf.decode(ENC, errors="replace")


def json_dumps_line(obj: dict) -> bytes:
    return (json.dumps(obj, ensure_ascii=False) + "\n").encode(ENC)


class ChatServer:
    def __init__(self, host: str, port: int, cert: Optional[str] = None, key: Optional[str] = None):
        self.host = host
        self.port = port
        self.cert = cert
        self.key = key

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients_lock = threading.Lock()
        # user_id {"sock": sock, "addr": (ip,port), "send_lock": Lock}
        self.clients: Dict[str, Dict] = {}

        self.running = threading.Event()
        self.running.clear()

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(BACKLOG)

        if self.cert and self.key:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_COMPRESSION
            context.load_cert_chain(certfile=self.cert, keyfile=self.key)
            self.sock = context.wrap_socket(self.sock, server_side=True)
            print(f"[SERVER] Listening (TLS) on {self.host}:{self.port}")
        else:
            print(f"[SERVER] Listening on {self.host}:{self.port} (NO TLS)")

        self.running.set()
        threading.Thread(target=self._accept_loop, daemon=True).start()

        try:
            while self.running.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self.running.clear()
            with self.clients_lock:
                for uid, meta in list(self.clients.items()):
                    try:
                        meta["sock"].close()
                    except Exception:
                        pass
                self.clients.clear()
            try:
                self.sock.close()
            except Exception:
                pass

    def _accept_loop(self):
        while self.running.is_set():
            try:
                csock, caddr = self.sock.accept()
                csock.settimeout(SOCKET_TIMEOUT)
                threading.Thread(target=self._handle_client, args=(csock, caddr), daemon=True).start()
            except OSError:
                break
            except Exception as e:
                print(f"[SERVER] accept error: {e}")


    def _handle_client(self, csock: socket.socket, caddr: Tuple[str, int]):
        user_id: Optional[str] = None
        try:
            line = recv_line(csock)
            if line is None:
                return
            try:
                msg = json.loads(line.strip())
            except json.JSONDecodeError:
                self._send_raw(csock, {"type": "error", "error": "bad_json"})
                return

            if msg.get("type") != "register" or not msg.get("user_id"):
                self._send_raw(csock, {"type": "error", "error": "register_required"})
                return

            requested = str(msg["user_id"]).strip()
            if not USER_RE.match(requested):
                self._send_raw(csock, {"type": "register", "ok": False, "reason": "invalid_user"})
                return

            with self.clients_lock:
                if requested in self.clients:
                    self._send_raw(csock, {"type": "register", "ok": False, "reason": "user_taken"})
                    return
                self.clients[requested] = {
                    "sock": csock,
                    "addr": caddr,
                    "send_lock": threading.Lock(),
                }
                user_id = requested

            self._send_raw(csock, {"type": "register", "ok": True, "user_id": user_id})
            self._broadcast_system(f"{user_id} پیوست.")
            self._broadcast_users()

            while True:
                try:
                    line = recv_line(csock)
                except socket.timeout:
                    continue
                if line is None:
                    break
                try:
                    data = json.loads(line.strip())
                except json.JSONDecodeError:
                    self._send_to_user(user_id, {"type": "error", "error": "bad_json"})
                    continue

                dtype = data.get("type")

                if dtype == "chat":
                    text = str(data.get("text", "")).strip()
                    if not text:
                        continue
                    if len(text.encode(ENC)) > MAX_LINE:
                        text = text.encode(ENC)[:MAX_LINE].decode(ENC, errors="ignore")
                    payload = {
                        "type": "chat",
                        "from": user_id,
                        "text": text,
                        "ts": time.time(),
                    }
                    self._broadcast(payload, exclude=user_id)

                elif dtype == "pm":
                    to_user = str(data.get("to", "")).strip()
                    text = str(data.get("text", "")).strip()
                    if not to_user or not USER_RE.match(to_user) or not text:
                        self._send_to_user(user_id, {"type": "pm_ack", "to": to_user, "delivered": False, "reason": "invalid"})
                        continue
                    if len(text.encode(ENC)) > MAX_LINE:
                        text = text.encode(ENC)[:MAX_LINE].decode(ENC, errors="ignore")
                    payload = {
                        "type": "pm",
                        "from": user_id,
                        "to": to_user,
                        "text": text,
                        "ts": time.time(),
                    }
                    sent = self._send_to(to_user, payload)
                    ack = {"type": "pm_ack", "to": to_user, "delivered": sent, "ts": time.time()}
                    self._send_to_user(user_id, ack)

                elif dtype == "list":
                    self._send_to_user(user_id, {"type": "users", "users": self._user_list(), "ts": time.time()})

                elif dtype == "logout":
                    break

                else:
                    self._send_to_user(user_id, {"type": "error", "error": "unknown_type"})

        except Exception as e:
            print(f"[SERVER] Error with {caddr}: {e}")
        finally:
            if user_id:
                with self.clients_lock:
                    self.clients.pop(user_id, None)
                self._broadcast_system(f"{user_id} رفتش.")
                self._broadcast_users()
            try:
                csock.close()
            except Exception:
                pass

    def _send_raw(self, sock: socket.socket, obj: dict) -> bool:
        try:
            data = json_dumps_line(obj)
            if len(data) > MAX_LINE:
                data = json_dumps_line({"type": "error", "error": "message_too_long"})
            sock.sendall(data)
            return True
        except Exception:
            return False

    def _send_to_user(self, user_id: Optional[str], obj: dict) -> bool:
        if not user_id:
            return False
        with self.clients_lock:
            meta = self.clients.get(user_id)
        if not meta:
            return False
        try:
            data = json_dumps_line(obj)
            if len(data) > MAX_LINE:
                data = json_dumps_line({"type": "error", "error": "message_too_long"})
            with meta["send_lock"]:
                meta["sock"].sendall(data)
            return True
        except Exception:
            return False

    def _send_to(self, user_id: str, obj: dict) -> bool:
        with self.clients_lock:
            meta = self.clients.get(user_id)
        if not meta:
            return False
        try:
            data = json_dumps_line(obj)
            if len(data) > MAX_LINE:
                data = json_dumps_line({"type": "error", "error": "message_too_long"})
            with meta["send_lock"]:
                meta["sock"].sendall(data)
            return True
        except Exception:
            return False

    def _broadcast(self, obj: dict, exclude: Optional[str] = None):
        with self.clients_lock:
            items = list(self.clients.items())

        to_remove = []
        for uid, meta in items:
            if exclude and uid == exclude:
                continue
            try:
                data = json_dumps_line(obj)
                if len(data) > MAX_LINE:
                    data = json_dumps_line({"type": "error", "error": "message_too_long"})
                with meta["send_lock"]:
                    meta["sock"].sendall(data)
            except Exception:
                to_remove.append(uid)
        if to_remove:
            with self.clients_lock:
                for uid in to_remove:
                    self.clients.pop(uid, None)

    def _broadcast_system(self, text: str):
        self._broadcast({"type": "system", "text": text, "ts": time.time()})

    def _user_list(self):
        with self.clients_lock:
            return sorted(list(self.clients.keys()))

    def _broadcast_users(self):
        self._broadcast({"type": "users", "users": self._user_list(), "ts": time.time()})

    def stop(self):
        self.running.clear()
        try:
            self.sock.close()
        except Exception:
            pass

def start_server(host="127.0.0.1", port=5050, cert: Optional[str] = None, key: Optional[str] = None):
    ChatServer(host, port, cert, key).start()


def main():
    p = argparse.ArgumentParser(description="Simple multi-user chat server (fixed)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5050)
    p.add_argument("--cert", default=None, help="")
    p.add_argument("--key", default=None, help="")
    args = p.parse_args()

    ChatServer(args.host, args.port, cert=args.cert, key=args.key).start()


if __name__ == "__main__":
    main()