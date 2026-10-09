"""
AKITDA Event & Member Management Suite 2026
Main Application Launcher & Desktop Control Panel
"""

import sys
import os
import threading
import time
import webbrowser
import socket
import subprocess

import db
import server

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def run_server_thread():
    try:
        server.start_server(5000)
    except Exception as e:
        print("Server error:", e)

def launch_gui(local_url, network_url):
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        print("Tkinter not available. Running in console mode.")
        return False

    root = tk.Tk()
    root.title("AKITDA Event Suite 2026 - Control Panel")
    root.geometry("560x520")
    root.resizable(False, False)
    root.configure(bg="#0f172a") # Slate-900

    # Header
    header_frame = tk.Frame(root, bg="#1e293b", padx=20, pady=16)
    header_frame.pack(fill=tk.X)

    title_lbl = tk.Label(
        header_frame,
        text="AKITDA Event & Member Suite 2026",
        font=("Segoe UI", 15, "bold"),
        fg="#ffffff",
        bg="#1e293b"
    )
    title_lbl.pack(anchor="w")

    subtitle_lbl = tk.Label(
        header_frame,
        text="All Kerala IT Dealers Association • General Body 10th Dec 2026",
        font=("Segoe UI", 9),
        fg="#94a3b8",
        bg="#1e293b"
    )
    subtitle_lbl.pack(anchor="w")

    # Status Box
    status_frame = tk.Frame(root, bg="#1e293b", padx=15, pady=12, highlightthickness=1, highlightbackground="#334155")
    status_frame.pack(fill=tk.X, padx=20, pady=15)

    status_indicator = tk.Label(
        status_frame,
        text="🟢 SERVER STATUS: RUNNING (PORT 5000)",
        font=("Segoe UI", 10, "bold"),
        fg="#22c55e", # Emerald
        bg="#1e293b"
    )
    status_indicator.pack(anchor="w")

    # URL links
    url_frame = tk.Frame(status_frame, bg="#1e293b")
    url_frame.pack(fill=tk.X, pady=(6, 0))

    tk.Label(url_frame, text="• Local Machine: ", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b").grid(row=0, column=0, sticky="w")
    local_btn = tk.Label(url_frame, text=local_url, font=("Segoe UI", 9, "bold", "underline"), fg="#38bdf8", bg="#1e293b", cursor="hand2")
    local_btn.grid(row=0, column=1, sticky="w")
    local_btn.bind("<Button-1>", lambda e: webbrowser.open(local_url))

    tk.Label(url_frame, text="• Local Network: ", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b").grid(row=1, column=0, sticky="w")
    net_btn = tk.Label(url_frame, text=network_url, font=("Segoe UI", 9, "bold", "underline"), fg="#fb923c", bg="#1e293b", cursor="hand2")
    net_btn.grid(row=1, column=1, sticky="w")
    net_btn.bind("<Button-1>", lambda e: webbrowser.open(network_url))

    note_lbl = tk.Label(
        status_frame,
        text="💡 Mobile phones & other PCs on the same WiFi can access using the Network URL.",
        font=("Segoe UI", 8),
        fg="#cbd5e1",
        bg="#1e293b"
    )
    note_lbl.pack(anchor="w", pady=(6, 0))

    # Module Buttons Container
    btn_frame = tk.Frame(root, bg="#0f172a", padx=20)
    btn_frame.pack(fill=tk.BOTH, expand=True)

    def make_btn(parent, text, url_path, bg_color="#2563eb", fg_color="#ffffff"):
        target = f"{local_url}{url_path}" if url_path else local_url
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg=fg_color,
            activebackground="#ea580c",
            activeforeground="#ffffff",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda: webbrowser.open(target)
        )
        return btn

    btn_hub = make_btn(btn_frame, "🌐  OPEN ALL-IN-ONE WEB PORTAL", "", bg_color="#ea580c")
    btn_hub.pack(fill=tk.X, pady=(4, 6))

    grid_btns = tk.Frame(btn_frame, bg="#0f172a")
    grid_btns.pack(fill=tk.X, pady=2)
    grid_btns.columnconfigure(0, weight=1)
    grid_btns.columnconfigure(1, weight=1)

    btn_scan = make_btn(grid_btns, "⚡  Thermal Badge Scanner", "/scan", bg_color="#334155")
    btn_scan.grid(row=0, column=0, padx=(0, 4), pady=3, sticky="ew")

    btn_reg = make_btn(grid_btns, "📝  Registration Desk", "/register", bg_color="#334155")
    btn_reg.grid(row=0, column=1, padx=(4, 0), pady=3, sticky="ew")

    btn_passes = make_btn(grid_btns, "🎫  Passes Issued", "/passes", bg_color="#2563eb")
    btn_passes.grid(row=1, column=0, padx=(0, 4), pady=3, sticky="ew")

    btn_viewer = make_btn(grid_btns, "📊  Attendance Viewer", "/viewer", bg_color="#334155")
    btn_viewer.grid(row=1, column=1, padx=(4, 0), pady=3, sticky="ew")

    btn_renewal = make_btn(grid_btns, "💳  Membership Renewal", "/renewal", bg_color="#334155")
    btn_renewal.grid(row=2, column=0, columnspan=2, padx=0, pady=3, sticky="ew")

    def export_csv_action():
        webbrowser.open(f"{local_url}/api/export/csv")

    btn_export = tk.Button(
        btn_frame,
        text="📥  Export Scanned Attendance to CSV (.csv)",
        font=("Segoe UI", 9, "bold"),
        bg="#059669",
        fg="#ffffff",
        bd=0,
        pady=8,
        cursor="hand2",
        command=export_csv_action
    )
    btn_export.pack(fill=tk.X, pady=(6, 10))

    # Footer
    footer_frame = tk.Frame(root, bg="#0f172a", padx=20, pady=8)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

    def on_exit():
        if messagebox.askokcancel("Exit AKITDA Suite", "Do you want to stop the AKITDA event server and exit?"):
            root.destroy()
            os._exit(0)

    btn_exit = tk.Button(
        footer_frame,
        text="🛑 Stop Server & Exit",
        font=("Segoe UI", 9),
        bg="#dc2626",
        fg="#ffffff",
        bd=0,
        pady=4,
        padx=12,
        cursor="hand2",
        command=on_exit
    )
    btn_exit.pack(side=tk.RIGHT)

    copy_lbl = tk.Label(
        footer_frame,
        text="AKITDA Ernakulam • 193 Members Loaded",
        font=("Segoe UI", 8),
        fg="#64748b",
        bg="#0f172a"
    )
    copy_lbl.pack(side=tk.LEFT)

    root.protocol("WM_DELETE_WINDOW", on_exit)
    root.mainloop()
    return True

def main():
    # 1. Initialize SQLite Database and import Excel members
    db.init_db()

    # 2. Start HTTP Server in background thread
    server_thread = threading.Thread(target=run_server_thread, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    local_ip = get_lan_ip()
    local_url = "http://localhost:5000"
    network_url = f"http://{local_ip}:5000"

    print("\n" + "=" * 60)
    print("  AKITDA Event & Member Suite 2026 Started! (10 Dec 2026)")
    print(f"  * Local:   {local_url}")
    print(f"  * Network: {network_url}")
    print("=" * 60 + "\n")

    # 3. Automatically open browser to the portal
    webbrowser.open(local_url)

    # 4. Launch Desktop GUI Control Panel
    gui_launched = launch_gui(local_url, network_url)

    if not gui_launched:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

if __name__ == '__main__':
    main()
