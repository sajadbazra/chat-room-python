import argparse
import json
import os
import queue
import socket
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

ENC = "utf-8"
BUFFER = 8192

class ClientNet:
    def __init__(self, host, port, user_id, inbox_queue: queue.Queue):
        self.host = host
        self.port = port
        self.user_id = user_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.reader = None
        self.running = False
        self.inbox = inbox_queue
        self.lock = threading.Lock()

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.reader = self.sock.makefile("r", encoding=ENC)
        self._send({"type": "register", "user_id": self.user_id})

        line = self.reader.readline()
        if not line:
            raise RuntimeError("No response from server")
        msg = json.loads(line.strip())
        if not (msg.get("type") == "register" and msg.get("ok")):
            reason = msg.get("reason", "unknown")
            raise RuntimeError(f"Register failed: {reason}")
        self.running = True
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def close(self):
        self.running = False
        try:
            self._send({"type": "logout"})
        except Exception:
            pass
        try:
            if self.reader:
                self.reader.close()
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass

    def _send(self, obj):
        data = (json.dumps(obj) + "\n").encode(ENC)
        with self.lock:
            self.sock.sendall(data)

    def send_chat(self, text: str):
        if text:
            self._send({"type": "chat", "text": text})

    def send_pm(self, to_user: str, text: str):
        if to_user and text:
            self._send({"type": "pm", "to": to_user, "text": text})

    def request_users(self):
        self._send({"type": "list"})
    """
    Copyright (c) 2025 sajjadbazra
    """
    def _recv_loop(self):
        try:
            while self.running:
                line = self.reader.readline()
                if not line:
                    break
                try:
                    msg = json.loads(line.strip())
                    self.inbox.put(msg)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            self.inbox.put({"type": "system", "text": f"خطا در ارتباط: {e}"})
        finally:
            self.inbox.put({"type": "disconnect"})


class LoginDialog:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("ورود به چت")
        self.top.geometry("300x150")
        self.user = None

        ttk.Label(self.top, text="نام کاربری:").pack(pady=10)
        self.entry = ttk.Entry(self.top)
        self.entry.pack(pady=5)
        self.entry.focus()

        btn = ttk.Button(self.top, text="ورود", command=self._on_ok)
        btn.pack(pady=10)

        self.top.protocol("WM_DELETE_WINDOW", root.destroy)

    def _on_ok(self):
        u = self.entry.get().strip()
        if not u:
            messagebox.showerror("خطا", "لطفاً نام کاربری وارد کنید")
            return
        self.user = u
        self.top.destroy()


class ChatGUI:
    def __init__(self, net):
        self.net = net
        self.root = tk.Tk()
        self.root.title(f"چت بات — {self.net.user_id}")
        self.root.geometry("900x560")
        self.root.configure(bg="#fef6e4")

        self._set_style()
        self._build_widgets()
        self._connect_signals()
        self.inbox = net.inbox

        self.history_path = os.path.join("history", f"{self.net.user_id}.jsonl")
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)

        self.root.after(100, self._poll_inbox)
        self.root.after(400, self.net.request_users)

    def _set_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#fef6e4", foreground="#5c4033", font=("Segoe UI", 10))
        style.configure("TButton", background="#ff914d", foreground="white", font=("Segoe UI", 10, "bold"), padding=6)
    """
    Copyright (c) 2025 sajjadbazra
    """
    def _build_widgets(self):
        self.txt = tk.Text(self.root, state=tk.DISABLED, wrap=tk.WORD,
                           bg="#fffdf8", fg="#333", font=("Segoe UI", 11))
        self.txt.pack(fill="both", expand=True, padx=8, pady=8)

        self.entry = ttk.Entry(self.root, font=("Segoe UI", 11))
        self.entry.pack(fill="x", padx=8, pady=4)
        self.entry.bind("<Return>", self._on_send)

        self.btn = ttk.Button(self.root, text="ارسال", command=self._on_send)
        self.btn.pack(pady=4)

    def _append(self, text: str, tag=None):
        self.txt.configure(state=tk.NORMAL)
        self.txt.insert(tk.END, text + "\n", tag)
        self.txt.configure(state=tk.DISABLED)
        self.txt.see(tk.END)

    def _on_send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        if text.startswith('@') and ' ' in text:
            to_user, msg = text[1:].split(' ', 1)
            self.net.send_pm(to_user, msg)
            self._append(f"[PM -> {to_user}] {msg}")
        else:
            self.net.send_chat(text)
            self._append(f"[//] {text}")
        self.entry.delete(0, tk.END)
    """
    Copyright (c) 2025 sajjadbazra
    """
    def _poll_inbox(self):
        try:
            while True:
                msg = self.inbox.get_nowait()
                self._handle_msg(msg)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_inbox)

    def _handle_msg(self, msg: dict):
        t = msg.get("type")
        if t == "system":
            self._append(f"* {msg.get('text','')} *")
        elif t == "chat":
            ts = self._fmt_ts(msg.get("ts"))
            self._append(f"[{ts}] {msg.get('from')}: {msg.get('text','')}")
        elif t == "pm":
            ts = self._fmt_ts(msg.get("ts"))
            self._append(f"[{ts}] [PM] {msg.get('from')} → شما: {msg.get('text','')}")
        elif t == "disconnect":
            self._append("* ارتباط با سرور قطع شد *")

    def _fmt_ts(self, ts):
        try:
            return datetime.fromtimestamp(ts).strftime("%H:%M:%S")
        except Exception:
            return "--:--:--"

    def _connect_signals(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        try:
            self.net.close()
        finally:
            self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    p = argparse.ArgumentParser(description="Tkinter Chat Client")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5050)
    args = p.parse_args()

    root = tk.Tk()
    root.withdraw()
    dlg = LoginDialog(root)
    root.wait_window(dlg.top)

    if not dlg.user:
        return

    inbox = queue.Queue()
    net = ClientNet(args.host, args.port, dlg.user, inbox)
    try:
        net.connect()
    except Exception as e:
        messagebox.showerror("Connection error", str(e))
        return

    gui = ChatGUI(net)
    gui.run()


if __name__ == "__main__":
    main()
