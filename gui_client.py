import tkinter as tk
from tkinter import messagebox
import client
#ai generated gui , socket process procedd in client.py
BG_MAIN = "#FAF6F0"
BG_HEADER = "#5F7464"
BG_SIDE = "#E8EFEA"
BG_CHAT = "#FFFFFF"
ACCENT_PINK = "#D98A9C"
ACCENT_DARK = "#C26D80"
TEXT_DARK = "#2C3531"
TEXT_LIGHT = "#FFFFFF"

is_mobile_mode = False
selected_target = "All (Public)"
login_error_shown = False

root = tk.Tk()
root.title("Multi-User Chat Application")
root.geometry("780x500")
root.configure(bg=BG_MAIN)
root.resizable(False, False)


def append_chat(text, tag="pub"):
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, text + "\n", tag)
    chat_display.see(tk.END)
    chat_display.config(state=tk.DISABLED)


def update_user_header(username):
    root.title(f"Chat - {username}")
    status_label.config(text=f"Connected as: {username}")


def show_main_chat(username):
    update_user_header(username)
    login_frame.place_forget()
    build_layout()


def refresh_user_list(users):
    names = ["All (Public)"] + users
    user_listbox.delete(0, tk.END)
    for n in names:
        user_listbox.insert(tk.END, n)
    online_label.config(text=f"Online ({len(users)})")


def set_target(name):
    global selected_target
    selected_target = name
    if name == "All (Public)":
        target_indicator.config(text="Sending to: All (Public)", fg=BG_HEADER)
    else:
        target_indicator.config(text=f"Private to: {name}", fg=ACCENT_DARK)


def receive_from_client(code, time, messeage):
    root.after(0, process_incoming, code, time, messeage)


def process_incoming(code, time, messeage):
    global login_error_shown
    if code == "1":
        login_error_shown = False
        assigned_name = messeage.replace("Username ", "").replace(" register.", "").strip()
        if not assigned_name:
            assigned_name = entry_name.get().strip()
        show_main_chat(assigned_name)
        append_chat(f"[{time}] {messeage}", "sys")
    elif code == "2":
        append_chat(f"[{time}] {messeage}", "pub")
    elif code == "3":
        append_chat(f"[{time}] [PRIVATE] {messeage}", "priv")
    elif code == "4":
        if "Username changed to " in messeage:
            new_assigned = messeage.replace("Username changed to ", "").rstrip(".").strip()
            if new_assigned:
                update_user_header(new_assigned)
        append_chat(f"[{time}] {messeage}", "sys")
    elif code == "6":
        users = messeage.replace("Online users: ", "").split(",")
        clean_users = [u.strip() for u in users if u.strip()]
        refresh_user_list(clean_users)
    elif code in ("Error", "Eror", "Closed"):
        if login_frame.winfo_ismapped():
            if code in ("Error", "Eror"):
                login_error_shown = True
                messagebox.showerror("Error", messeage)
            elif code == "Closed" and not login_error_shown:
                messagebox.showerror("Connection Error", messeage)
        else:
            append_chat(f"[{time}] [{code}] {messeage}", "err")


client.gui_sender = receive_from_client


def handle_connect(event=None):
    global login_error_shown
    login_error_shown = False
    name = entry_name.get().strip()
    ip = entry_ip.get().strip()
    port_str = entry_port.get().strip()
    if not name:
        messagebox.showerror("Error", "Username cannot be empty.")
        return
    if port_str.isdigit():
        client.connectServer(name, ip, int(port_str))
    else:
        messagebox.showerror("Error", "Port must be a number.")


def connect_via_relay():
    entry_port.delete(0, tk.END)
    entry_port.insert(0, "38390")
    handle_connect()


def handle_send(event=None):
    msg = msg_entry.get().strip()
    if not msg:
        return
    msg_entry.delete(0, tk.END)

    if selected_target == "All (Public)":
        client.sendGenMessage(msg)
    else:
        client.sendprivateMessage(selected_target, msg)


def handle_change_name():
    new_n = new_name_entry.get().strip()
    if new_n:
        client.changeUsername(new_n)
        new_name_entry.delete(0, tk.END)


def handle_exit():
    client.dissconnect()
    root.destroy()


def on_select_user(event):
    sel = user_listbox.curselection()
    if sel:
        set_target(user_listbox.get(sel[0]))


def toggle_view_mode():
    global is_mobile_mode
    is_mobile_mode = not is_mobile_mode
    build_layout()


def build_layout():
    header_bar.place_forget()
    side_panel.place_forget()
    chat_panel.place_forget()

    if not is_mobile_mode:
        root.geometry("780x500")
        mode_btn.config(text="Phone View")
        header_bar.place(x=0, y=0, width=780, height=45)
        status_label.place(x=15, y=12)
        mode_btn.place(x=605, y=9, width=90, height=27)
        exit_btn.place(x=705, y=9, width=60, height=27)

        side_panel.place(x=10, y=55, width=200, height=435)
        online_label.place(x=10, y=8)
        user_listbox.place(x=10, y=32, width=180, height=320)
        new_name_entry.place(x=10, y=362, width=115, height=26)
        rename_btn.place(x=130, y=362, width=60, height=26)
        hint_label.place(x=10, y=398)

        chat_panel.place(x=220, y=55, width=550, height=435)
        chat_display.place(x=0, y=0, width=550, height=355)
        target_indicator.place(x=2, y=360)
        msg_entry.place(x=0, y=385, width=460, height=38)
        send_btn.place(x=468, y=385, width=82, height=38)
    else:
        root.geometry("360x560")
        mode_btn.config(text="PC View")
        header_bar.place(x=0, y=0, width=360, height=42)
        status_label.place(x=10, y=11)
        mode_btn.place(x=215, y=8, width=72, height=26)
        exit_btn.place(x=295, y=8, width=55, height=26)

        side_panel.place(x=10, y=48, width=340, height=115)
        online_label.place(x=8, y=4)
        user_listbox.place(x=8, y=24, width=195, height=82)
        new_name_entry.place(x=212, y=26, width=118, height=26)
        rename_btn.place(x=212, y=58, width=118, height=26)
        hint_label.place(x=212, y=88)

        chat_panel.place(x=10, y=170, width=340, height=380)
        chat_display.place(x=0, y=0, width=340, height=305)
        target_indicator.place(x=2, y=310)
        msg_entry.place(x=0, y=335, width=265, height=36)
        send_btn.place(x=272, y=335, width=68, height=36)


header_bar = tk.Frame(root, bg=BG_HEADER)
status_label = tk.Label(header_bar, text="Connected", bg=BG_HEADER, fg=TEXT_LIGHT, font=("Segoe UI", 10, "bold"))
mode_btn = tk.Button(header_bar, text="Phone View", bg=BG_SIDE, fg=TEXT_DARK, font=("Segoe UI", 8, "bold"), relief="flat", command=toggle_view_mode)
exit_btn = tk.Button(header_bar, text="Exit", bg=ACCENT_DARK, fg=TEXT_LIGHT, font=("Segoe UI", 8, "bold"), relief="flat", command=handle_exit)

side_panel = tk.Frame(root, bg=BG_SIDE, highlightbackground="#D0DDD4", highlightthickness=1)
online_label = tk.Label(side_panel, text="Online (0)", bg=BG_SIDE, fg=TEXT_DARK, font=("Segoe UI", 9, "bold"))
user_listbox = tk.Listbox(side_panel, bg=BG_CHAT, fg=TEXT_DARK, font=("Segoe UI", 9), selectbackground=ACCENT_PINK, relief="flat", exportselection=False)
user_listbox.bind("<<ListboxSelect>>", on_select_user)

new_name_entry = tk.Entry(side_panel, bg=BG_CHAT, fg=TEXT_DARK, font=("Segoe UI", 9), relief="flat")
rename_btn = tk.Button(side_panel, text="Rename", bg=BG_HEADER, fg=TEXT_LIGHT, font=("Segoe UI", 8, "bold"), relief="flat", command=handle_change_name)
hint_label = tk.Label(side_panel, text="Click user for DM", bg=BG_SIDE, fg="#687A6E", font=("Segoe UI", 8))

chat_panel = tk.Frame(root, bg=BG_MAIN)
chat_display = tk.Text(chat_panel, bg=BG_CHAT, fg=TEXT_DARK, font=("Segoe UI", 9), state=tk.DISABLED, relief="flat", padx=8, pady=8, highlightbackground="#E2DCD5", highlightthickness=1)
chat_display.tag_config("sys", foreground="#5F7464", font=("Segoe UI", 9, "italic"))
chat_display.tag_config("priv", foreground="#B8526B", font=("Segoe UI", 9, "bold"))
chat_display.tag_config("err", foreground="#C93B3B", font=("Segoe UI", 9, "bold"))
chat_display.tag_config("pub", foreground="#2C3531")

target_indicator = tk.Label(chat_panel, text="Sending to: All (Public)", bg=BG_MAIN, fg=BG_HEADER, font=("Segoe UI", 8, "bold"))
msg_entry = tk.Entry(chat_panel, bg=BG_CHAT, fg=TEXT_DARK, font=("Segoe UI", 10), relief="flat", highlightbackground="#D5CBBF", highlightthickness=1)
msg_entry.bind("<Return>", handle_send)
send_btn = tk.Button(chat_panel, text="Send", bg=ACCENT_PINK, fg=TEXT_LIGHT, font=("Segoe UI", 9, "bold"), relief="flat", command=handle_send)

login_frame = tk.Frame(root, bg=BG_MAIN)
login_frame.place(x=0, y=0, relwidth=1, relheight=1)

login_card = tk.Frame(login_frame, bg=BG_SIDE, highlightbackground="#C5D3C9", highlightthickness=1)
login_card.place(relx=0.5, rely=0.5, anchor="center", width=320, height=330)

tk.Label(login_card, text="Chat Login", bg=BG_SIDE, fg=BG_HEADER, font=("Segoe UI", 14, "bold")).pack(pady=(15, 10))

tk.Label(login_card, text="Nickname:", bg=BG_SIDE, fg=TEXT_DARK, font=("Segoe UI", 9)).pack(anchor="w", padx=35)
entry_name = tk.Entry(login_card, font=("Segoe UI", 10), bg=BG_CHAT, relief="flat")
entry_name.pack(fill="x", padx=35, pady=(2, 8), ipady=4)

tk.Label(login_card, text="Server IP:", bg=BG_SIDE, fg=TEXT_DARK, font=("Segoe UI", 9)).pack(anchor="w", padx=35)
entry_ip = tk.Entry(login_card, font=("Segoe UI", 10), bg=BG_CHAT, relief="flat")
entry_ip.insert(0, client.host)
entry_ip.pack(fill="x", padx=35, pady=(2, 8), ipady=4)

tk.Label(login_card, text="TCP Port:", bg=BG_SIDE, fg=TEXT_DARK, font=("Segoe UI", 9)).pack(anchor="w", padx=35)
entry_port = tk.Entry(login_card, font=("Segoe UI", 10), bg=BG_CHAT, relief="flat")
entry_port.insert(0, str(client.port))
entry_port.pack(fill="x", padx=35, pady=(2, 12), ipady=4)

for e in (entry_name, entry_ip, entry_port):
    e.bind("<Return>", handle_connect)

connect_btn = tk.Button(login_card, text="Connect to Server", bg=ACCENT_PINK, fg=TEXT_LIGHT, font=("Segoe UI", 10, "bold"), relief="flat", command=handle_connect)
connect_btn.pack(fill="x", padx=35, ipady=4)

relay_btn = tk.Button(login_card, text="Connect via Relay (38390)", bg=ACCENT_DARK, fg=TEXT_LIGHT, font=("Segoe UI", 9, "bold"), relief="flat", command=connect_via_relay)
relay_btn.pack(fill="x", padx=35, pady=(6, 0), ipady=4)

root.protocol("WM_DELETE_WINDOW", handle_exit)
entry_name.focus_set()
root.mainloop()
