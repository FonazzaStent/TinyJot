"""TinyJot 1.4.2 - A WebDAV and encryption enabled notepad.
Copyright SymbolForm (C) 2023-2026

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. See <https://www.gnu.org/licenses/>."""

import base64
import os
import posixpath
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import webbrowser
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from tkinter.filedialog import askopenfilename, asksaveasfilename
import urllib3
from tkfontchooser import askfont

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Reusable pool manager
http = urllib3.PoolManager()


FAVICON_DATA = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAZxJREFUWIXt179rFkEQxvHPmICK6V4htipoGdTGRhQFSxWE/AdBS0sFwdrK0iog1jb2CoKClfgDU4gWKiRNCIIQBJGMzasEcvdm9/JeXgsfmOZ2dua7MztwG5lpktoz0eyYbluIiAHOYVAR7wceZ+b34h2ZucVwCqvIDvYGg6a4TRZNdyAinuEs7uNLRQXO4yLe4kJmrnWtwCpWSk+xad/12kq0XcIp/Kw4eZPm8DQiDo5y6nsK5vBkFMRujOEfiMZpah3DjnqBd5jZ9G3fEGIRV3oFyMz3w2R/FRHTWMfxpj29tyAzf2Gjbb2oAhFxCJdq8uJRZn7bzrG0BTM4jCj038B+jAcgMz/hVmHyKpW24CRuVsRN3M7Mj2MBwAfcrQCAryVOpS1Yx6tKgCKVtuAMHlTETVzOzKWxAGTmcxytAChWaQUO4LT2Mfw8nJR+AHAM10asv8S93gAy8zXmuyTYThP/K/4P8M8CrGE2Io7sNEFEnMDeYcytavm9vqPbo2SULdQ8TKZwA1cxu8MiLOMhFrMhWSPAbmril/A3Lo8hMwXmrDcAAAAASUVORK5CYII='


FOLDER_DATA = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAXpJREFUWIXtl7FKA0EQhr/RRBAxoAhaWYr4CCIWinkCURBLC3sLwcbawk4QwS6VvoE2PoBWFloEhEAsBEUQUUTP3+L2wpFccvE8uRQ3MNwycPt/uzvDzpoksrS+TNV7AaDQHDCzOWCaaLhX4FJSNTUCSQ0HKoBi3AP2gUL436RuQRKaWRk4A66AYyfWbEPAJjAFnADrkr5S2QFgy4mudiIGRhykHETxLzsQzoFg7MUAP5vZEnAOrACzZvbQxVq/gRtgV1Itage23aqWuyEHSvhH9Uh83oS9BpSCeRKXoaQXSRuSxiRZnONX1QEwCZSDeVrKEBg1s3lgIClcG/sAgvKd6ARwlLJwR4sCqAOnwGfKWkVgjdDq2wHsSKqkLA6AmVWBw3AsKgnf/0Pc2VtzIPPLKAfIAXKAHKCnADJ5oYQvo3v3XTSzC/wWKk3rBxbcuN6IhlqsYeCO37VXSfwWGGxpywHMbBy/N5xxxGmaB1wDe5KeGpr54zRrgB/90FZRdCs7PAAAAABJRU5ErkJggg=='



# --- WebDAV HTTP Client ---
class WebDAVClient:
    def __init__(self, base_url, username="", password=""):
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = "http://" + base_url
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password

        pass_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pass_mgr.add_password(None, self.base_url, username, password)
        auth_handler = urllib.request.HTTPBasicAuthHandler(pass_mgr)
        self.opener = urllib.request.build_opener(auth_handler)

    def _request(self, method, path, data=None, headers=None):
        url = self.base_url + path
        req = urllib.request.Request(url, data=data, method=method)
        if headers:
            for key, val in headers.items():
                req.add_header(key, val)
        try:
            return self.opener.open(req)
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP {e.code}: {e.reason}")

    def list_dir(self, path):
        headers = {"Depth": "1", "Content-Type": "application/xml"}
        body = (
            '<?xml version="1.0" encoding="utf-8" ?>'
            '<D:propfind xmlns:D="DAV:"><D:prop>'
            '<D:resourcetype/><D:displayname/>'
            '</D:prop></D:propfind>'
        ).encode('utf-8')
        
        response = self._request("PROPFIND", path, data=body, headers=headers)
        content = response.read()

        items = []
        root = ET.fromstring(content)
        prefix = "{DAV:}"

        for resp in root.findall(f"{prefix}response"):
            href = resp.find(f"{prefix}href").text
            is_dir = False
            propstat = resp.find(f"{prefix}propstat")
            if propstat is not None:
                prop = propstat.find(f"{prefix}prop")
                if prop is not None:
                    res_type = prop.find(f"{prefix}resourcetype")
                    if res_type is not None and res_type.find(f"{prefix}collection") is not None:
                        is_dir = True

            name = posixpath.basename(href.rstrip("/"))
            if not name:
                continue

            items.append({"name": name, "is_dir": is_dir, "path": href})

        return items

    def read_file_text(self, remote_path):
        res = self._request("GET", remote_path)
        return res.read().decode('utf-8', errors='replace')

    def write_file_text(self, remote_path, content):
        data = content.encode('utf-8')
        self._request("PUT", remote_path, data=data)

    def delete(self, path):
        self._request("DELETE", path)

    def rename(self, old_path, new_path):
        destination = self.base_url + new_path
        headers = {"Destination": destination, "Overwrite": "F"}
        self._request("MOVE", old_path, headers=headers)

    def mkdir(self, path):
        self._request("MKCOL", path)


# --- WebDAV Tkinter GUI Browser Module ---

class WebDAVBrowser(ttk.Frame):
    def __init__(self, parent, client: WebDAVClient, on_open_callback=None):
        super().__init__(parent)
        self.client = client
        self.on_open_callback = on_open_callback
        self.current_path = "/"
        self.selected_item = None

        # Caricamento e conservazione delle PhotoImage per evitare il Garbage Collector
        self.folder_img = tk.PhotoImage(data=FOLDER_DATA)
        self.file_img = tk.PhotoImage(data=FAVICON_DATA)

        self._build_ui()
        self.browse_dir(self.current_path)

    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=5)

        ttk.Button(toolbar, text="Open File", command=self.on_open).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Save Current Note Here", command=self.on_save_current).pack(side="left", padx=2)
        ttk.Button(toolbar, text="New Folder", command=self.on_new_folder).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Rename", command=self.on_rename).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Delete", command=self.on_delete).pack(side="left", padx=2)

        browser_frame = ttk.Frame(self)
        browser_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(browser_frame, bg="white", width=640, height=480)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        v_scrollbar = ttk.Scrollbar(browser_frame, orient="vertical", command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(browser_frame, orient="horizontal", command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=h_scrollbar.set)

        browser_frame.grid_rowconfigure(0, weight=1)
        browser_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Custom.TFrame", background="white")
        self.content_frame = ttk.Frame(self.canvas, style="Custom.TFrame")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

    def browse_dir(self, path="/"):
        self.current_path = path
        self.selected_item = None

        try:
            items = self.client.list_dir(path)
        except Exception as e:
            messagebox.showerror("WebDAV Error", f"Failed to list directory:\n{e}")
            return

        dirlist = []
        if self.current_path != "/":
            dirlist.append({"name": "..", "is_dir": True, "path": posixpath.dirname(self.current_path.rstrip("/"))})

        dirlist.extend(items)

        self.content_frame.destroy()
        style = ttk.Style()
        style.configure("Custom.TFrame", background="white")
        self.content_frame = ttk.Frame(self.canvas, style="Custom.TFrame")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        x, y = 0, 0
        for item in dirlist:
            # Selezione dell'oggetto PhotoImage in base al tipo di risorsa
            img_to_use = self.folder_img if item["is_dir"] else self.file_img

            # Label con la PhotoImage anziché con il testo emoji
            icon_label = tk.Label(self.content_frame, image=img_to_use, bg="white")
            caption_label = tk.Label(self.content_frame, text=item["name"], wraplength=74, bg="white")

            icon_label.grid(row=y, column=x, padx=5, pady=(5, 0))
            caption_label.grid(row=y + 1, column=x, padx=5, pady=(0, 5))

            for widget in (icon_label, caption_label):
                widget.bind("<Button-1>", lambda e, data=item, lb=icon_label: self._select_item(data, lb))
                widget.bind("<Double-Button-1>", lambda e, data=item: self._activate_item(data))

            x += 1
            if x > 7:
                x = 0
                y += 2

        self.content_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _select_item(self, item, widget):
        self.selected_item = item
        for child in self.content_frame.winfo_children():
            child.config(bg="white")
        widget.config(bg="#cce5ff")

    def _activate_item(self, item):
        if item["is_dir"]:
            target_path = item["path"] if item["name"] == ".." else posixpath.join(self.current_path, item["name"])
            if not target_path.endswith("/"):
                target_path += "/"
            self.browse_dir(target_path)
        else:
            if self.on_open_callback:
                file_path = posixpath.join(self.current_path, item["name"])
                self.on_open_callback(file_path)

    def on_open(self):
        if self.selected_item:
            self._activate_item(self.selected_item)
        else:
            messagebox.showinfo("Select Item", "Please select a file or directory first.")

    def on_save_current(self):
        remote_save_current_file(self.current_path)
        self.browse_dir(self.current_path)

    def on_new_folder(self):
        folder_name = simpledialog.askstring("New Folder", "Folder Name:")
        if folder_name:
            new_path = posixpath.join(self.current_path, folder_name) + "/"
            try:
                self.client.mkdir(new_path)
                self.browse_dir(self.current_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder:\n{e}")

    def on_rename(self):
        if not self.selected_item or self.selected_item["name"] == "..":
            messagebox.showwarning("Warning", "Select a valid item to rename.")
            return

        new_name = simpledialog.askstring("Rename", "New Name:", initialvalue=self.selected_item["name"])
        if new_name and new_name != self.selected_item["name"]:
            old_path = posixpath.join(self.current_path, self.selected_item["name"])
            new_path = posixpath.join(self.current_path, new_name)
            try:
                self.client.rename(old_path, new_path)
                self.browse_dir(self.current_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename item:\n{e}")

    def on_delete(self):
        if not self.selected_item or self.selected_item["name"] == "..":
            messagebox.showwarning("Warning", "Select an item to delete.")
            return

        if messagebox.askyesno("Confirm Delete", f"Delete '{self.selected_item['name']}'?"):
            target_path = posixpath.join(self.current_path, self.selected_item["name"])
            try:
                self.client.delete(target_path)
                self.browse_dir(self.current_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete item:\n{e}")
                
# --- Application State & Variables ---
try:
    import pyi_splash
    pyi_splash.close()
except Exception:
    pass

password = ''
server = 'ftp.host.com'
username = 'name@email.com'
fontname = 'Times'
fontsize = 12
filename = ''
txtfilename = ''
key = ''
saved = True
modified = False
current_remote_path = ''
browsewin = None
dav_client = None
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def read_config():
    global server, username, fontname, fontsize, saved, modified
    parameters = []
    if os.path.isfile('config.ini'):
        configfile = open("config.ini", 'r')
    else:
        parameterstring = 'ftp.host.com\nname@email.com\nTimes\n12'
        configfile = open("config.ini", 'w')
        configfile.write(parameterstring)
        configfile.close()
        configfile = open("config.ini", 'r')

    for n in range(0, 4):
        try:
            line = configfile.readline().rstrip('\n')
        except Exception:
            line = ''
        parameters.append(line)
    configfile.close()

    server = parameters[0]
    username = parameters[1]
    fontname = parameters[2] if parameters[2] else 'Times'
    try:
        fontsize = int(parameters[3])
    except Exception:
        fontsize = 12
    saved = True
    modified = False


def create_main_window():
    global top, root
    root = tk.Tk()
    top = root
    top.geometry("600x450")
    top.title("TinyJot")

    try:
        img=b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAAXNSR0IB2cksfwAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAATtQTFRFaRLG////QkJCq83gQkJCq83gQkJCxuT0yOb1QkJCq83ge42YbnyEYWtxQkJCUlhbz+v6lKWtg4+WR0lKcXp/W2BjSkxMQkJCQ4bJRojJRojKR4nKSEpLSYrKS0xNTIzLTIzMVVxfWZXOXWJlXZjPYJrPY5zQY53VZnF4Z6DWbKTYbaPSc4OMdH6CdKfUfrHfgJSgg5mlhLLXhLLYhbPXhpyohrTYh5SaiLjiirfZi6KwjLjZjrnaj7rZkau5lL3blrHAlr/bl8Dcmqqym7jIm8LcnMPcnq+4n8Xdn8nrocbeorO8osfeo8zspMjepcnfpc3tp8rfqM/uqbvFq83gq9Lvr9TxsNXxscbQtdnzttrzuM7ZuNv0ut31u971v9biv+D3w+P4xuX5yOf6y+n7zer8z+z80e791vH/ZZ/c0wAAAAF0Uk5TAEDm2GYAAAAJcEhZcwAADdcAAA3XAUIom3gAAAAHdElNRQfpCh0JOyQaPEdvAAAA8ElEQVQ4y62SMQvCMBCFy7vBxaK0CNXBQdHNrg6KLkWclA6CoCAO2vv/v8A0vWgSK6XgBwfh8sh74S4IKoDvcmgSnBGq5qC66KmaYmNdM98QcQddZoAoxI66yIjaCBaam1Kqfpblqg62AAIzk4UlWHJJhJ+CWpwXHonHgVzBMxVmwtETsOGTwLMYKVK+j4aCb6EzKMHPDI0WxVowYXNq+U2+Clvhy+IkrIS2Fk2z6I8NwPsY2QvDxiJW2zQrD0dn3MxmWDH2lFbDcgWCtnYX5tKzwXyCsd0IAy95kniNt0WhKVu5huozcP9cu7QW9HfBCykxbF/WiDKeAAAAAElFTkSuQmCC'
        favicon = tk.PhotoImage(data=img)
        root.wm_iconphoto(True, favicon)
    except Exception as e:
        print (e)

    root.protocol("WM_DELETE_WINDOW", QuitApp)


def configure():
    global configwin, pw_entry, user_entry, host_entry
    configwin = tk.Toplevel(top)
    configwin.geometry("493x140")
    configwin.resizable(0, 0)
    configwin.title("Configure WebDAV")

    host_label = Label(configwin, text="Hostname")
    host_label.place(x=20, y=19, height=19, width=64)
    v = tk.StringVar(value=server)
    host_entry = Entry(configwin, textvariable=v)
    host_entry.place(x=90, y=19, height=20, width=384)

    user_label = Label(configwin, text="Username")
    user_label.place(x=20, y=47, height=19, width=64)
    x = tk.StringVar(value=username)
    user_entry = Entry(configwin, textvariable=x)
    user_entry.place(x=90, y=47, height=20, width=384)

    pw_label = Label(configwin, text="Password")
    pw_label.place(x=25, y=75, height=21, width=54)
    j = tk.StringVar(value=password)
    pw_entry = Entry(configwin, show="*", textvariable=j)
    pw_entry.place(x=90, y=75, height=20, width=384)
    pw_entry.bind("<Return>", get_config)

    pw_button = Button(configwin, text="Save")
    pw_button.place(x=210, y=105, height=24, width=47)
    pw_button.bind("<Button-1>", get_config)

    cancel_button = Button(configwin, text="Cancel")
    cancel_button.place(x=290, y=105, height=24, width=47)
    cancel_button.bind("<Button-1>", config_cancel)
    pw_entry.focus_set()


def get_config(event=None):
    global password, server, username
    password = pw_entry.get()
    server = host_entry.get()
    username = user_entry.get()

    configfile = open("config.ini", 'w')
    configfile.writelines(server + "\n")
    configfile.writelines(username + "\n")
    configfile.writelines(fontname + "\n")
    configfile.writelines(str(fontsize) + "\n")
    configfile.close()

    configwin.destroy()
    read_config()


def config_cancel(event=None):
    configwin.destroy()


def create_textbox():
    global textbox
    textbox = Text(top)
    textbox.place(relx=0.0, rely=0.0, relheight=1.0, relwidth=0.97)
    scroll_1 = Scrollbar(top)
    scroll_1.pack(side=RIGHT, fill=Y)
    textbox.configure(yscrollcommand=scroll_1.set, wrap=WORD, undo=True, maxundo=50)
    textbox.configure(font=(fontname, fontsize))
    scroll_1.configure(command=textbox.yview)
    textbox.bind("<Key>", text_modified)


def create_menu():
    menubar = tk.Menu(top, tearoff=0)
    top.configure(menu=menubar)
    sub_menu = tk.Menu(top, tearoff=0)
    edit_menu = tk.Menu(top, tearoff=0)

    menubar.add_cascade(menu=sub_menu, label="File")
    sub_menu.add_command(label="New", command=new_file, accelerator="Alt+N")
    sub_menu.add_command(label="Open", command=open_file, accelerator="Alt+O")
    sub_menu.add_command(label="Save", command=Save, accelerator="Alt+S")
    sub_menu.add_command(label="Save as", command=Save_to_file, accelerator="Alt+A")
    sub_menu.add_command(label="WebDAV Browser", command=webdav_browse, accelerator="Alt+T")
    sub_menu.add_command(label="WebDAV Save", command=webdav_save_same_name, accelerator="Alt+W")
    sub_menu.add_command(label="WebDAV Configure", command=configure, accelerator="Alt+C")
    sub_menu.add_command(label="Encrypt/Decrypt", command=encrypt_pw, accelerator="Alt+E")
    sub_menu.add_command(label="Quit", command=QuitApp, accelerator="Alt+Q")

    menubar.add_cascade(menu=edit_menu, label="Edit")
    edit_menu.add_command(label="Undo", command=textbox.edit_undo, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Redo", command=textbox.edit_redo, accelerator="Ctrl+Y")
    edit_menu.add_command(label="Copy", command=lambda: textbox.event_generate("<<Copy>>"), accelerator="Ctrl+C")
    edit_menu.add_command(label="Paste", command=lambda: textbox.event_generate("<<Paste>>"), accelerator="Ctrl+V")
    edit_menu.add_command(label="Cut", command=lambda: textbox.event_generate("<<Cut>>"), accelerator="Ctrl+X")
    edit_menu.add_command(label="Font", command=font_size)
    edit_menu.add_command(label="Date and time", command=date_time, accelerator='Alt+D')
    edit_menu.add_command(label="Time", command=just_time, accelerator='Alt+I')

    top.bind_all("<Alt-n>", lambda e: new_file())
    top.bind_all("<Alt-o>", lambda e: open_file())
    top.bind_all("<Alt-s>", lambda e: Save())
    top.bind_all("<Alt-a>", lambda e: Save_to_file())
    top.bind_all("<Alt-t>", lambda e: webdav_browse())
    top.bind_all("<Alt-w>", lambda e: webdav_save_same_name())
    top.bind_all("<Alt-c>", lambda e: configure())
    top.bind_all("<Alt-e>", lambda e: encrypt_pw())
    top.bind_all("<Alt-q>", lambda e: QuitApp())
    top.bind_all("<Alt-d>", lambda e: date_time())
    top.bind_all("<Alt-i>", lambda e: just_time())

    about = tk.Menu(top, tearoff=0)
    menubar.add_cascade(menu=about, label="?")
    about.add_command(label="About", command=aboutbox)


# --- WebDAV Module Integration Functions ---
def webdav_browse():
    global browsewin, dav_client
    dav_client = WebDAVClient(server, username, password)

    browsewin = tk.Toplevel(root)
    browsewin.title("WebDAV File Manager")
    browsewin.geometry("680x520")

    browser = WebDAVBrowser(browsewin, client=dav_client, on_open_callback=webdav_open_remote_file)
    browser.pack(fill="both", expand=True)


def webdav_open_remote_file(file_path):
    global filename, current_remote_path, saved, modified

    clean_server = server.replace("https://", "").replace("http://", "").strip("/")
    clean_path = "/" + file_path.lstrip("/")
    url = f"https://{clean_server}{clean_path}"

    headers = urllib3.make_headers(basic_auth=f"{username}:{password}")
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TinyJot/1.0"
    
    temp_path = None
    try:
        response = http.request("GET", url, headers=headers, preload_content=False)

        if response.status != 200:
            messagebox.showerror(
                "WebDAV Error",
                f"Failed to fetch file. HTTP Status: {response.status}",
            )
            response.release_conn()
            return

        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".tmp") as temp_file:
            temp_path = temp_file.name
            for chunk in response.stream(8192):
                temp_file.write(chunk)

        response.release_conn()

        with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        if "browsewin" in globals() and browsewin and browsewin.winfo_exists():
            browsewin.destroy()

        if key != "":
            text = decrypt(text)

        textbox.delete(1.0, END)
        textbox.insert(INSERT, text)

        filename = os.path.basename(file_path)
        current_remote_path = clean_path
        top.title(f"TinyJot - WebDAV: {filename}")
        textbox.focus_set()

        saved = True
        modified = False

    except Exception as e:
        messagebox.showerror("WebDAV Error", f"Could not open remote file:\n{e}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def remote_save_current_file(target_folder_path):
    global current_remote_path, filename, saved, modified
    new_name = simpledialog.askstring("Save Remote File", "Enter Remote Filename:", initialvalue=filename or "note.txt")
    if not new_name:
        return

    if not new_name.endswith(".txt"):
        new_name += ".txt"

    raw_text = textbox.get(1.0, END).rstrip("\n")
    content_to_send = encrypt(raw_text) if key != '' else raw_text

    full_remote_path = posixpath.join(target_folder_path, new_name)
    clean_server = server.replace("https://", "").replace("http://", "").strip("/")
    clean_path = "/" + full_remote_path.lstrip("/")
    url = f"https://{clean_server}{clean_path}"

    headers = urllib3.make_headers(basic_auth=f"{username}:{password}")
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TinyJot/1.0"
    headers["Content-Type"] = "text/plain; charset=utf-8"

    try:
        response = http.request(
            "PUT",
            url,
            body=content_to_send.encode("utf-8"),
            headers=headers,
            retries=2
        )

        if response.status in (200, 201, 204):
            current_remote_path = clean_path
            filename = new_name
            top.title(f"TinyJot - WebDAV: {filename}")
            saved = True
            modified = False
            messagebox.showinfo("Success", "File successfully saved to WebDAV.")
        else:
            messagebox.showerror("WebDAV Error", f"Could not save file to WebDAV. HTTP Status: {response.status}")

    except Exception as e:
        messagebox.showerror("WebDAV Error", f"Could not save file to WebDAV:\n{e}")


def webdav_save_same_name():
    global current_remote_path, saved, modified
    if not current_remote_path:
        webdav_browse()
        return

    raw_text = textbox.get(1.0, END).rstrip("\n")
    content_to_send = encrypt(raw_text) if key != '' else raw_text

    clean_server = server.replace("https://", "").replace("http://", "").strip("/")
    clean_path = "/" + current_remote_path.lstrip("/")
    url = f"https://{clean_server}{clean_path}"

    headers = urllib3.make_headers(basic_auth=f"{username}:{password}")
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TinyJot/1.0"
    headers["Content-Type"] = "text/plain; charset=utf-8"

    try:
        response = http.request(
            "PUT",
            url,
            body=content_to_send.encode("utf-8"),
            headers=headers,
            retries=2
        )

        if response.status in (200, 201, 204):
            top.title(f"TinyJot - WebDAV: {filename}")
            saved = True
            modified = False
            messagebox.showinfo("Success", "File updated on WebDAV.")
        else:
            messagebox.showerror("WebDAV Error", f"Failed to save file. HTTP Status: {response.status}")

    except Exception as e:
        messagebox.showerror("WebDAV Error", f"Failed to save file:\n{e}")


# --- Helper Methods & Callbacks ---
def QuitApp():
    top.destroy()


def font_size():
    global fontsize, fontname
    font_spec = askfont(root)
    if font_spec:
        fontname = font_spec['family']
        fontsize = font_spec['size']
        if 9 < fontsize < 100:
            textbox.configure(font=(fontname, fontsize))


def date_time():
    dt_str = time.strftime("%d/%m/%Y %H:%M:%S %w")
    weeknumber = int(dt_str[20])
    weekday = weekdays[weeknumber - 1]
    timestamp = weekday + " " + time.strftime("%d/%m/%Y %H:%M:%S")
    textbox.insert(INSERT, timestamp + '\n')


def just_time():
    timestamp = time.strftime("%H:%M:%S")
    textbox.insert(INSERT, timestamp + '\n')


def new_file():
    global filename, current_remote_path, txtfilename
    if modified:
        response = messagebox.askquestion("Save", 'Save current work first?')
        if response == 'yes':
            Save()
    filename = ''
    txtfilename = ''
    current_remote_path = ''
    textbox.delete(1.0, END)
    top.title("TinyJot")
    textbox.focus_set()


def open_file():
    global filename, txtfilename, current_remote_path
    data = [('Text', '*.txt')]
    txtfilename = askopenfilename(filetypes=data)
    if txtfilename:
        textbox.delete(1.0, END)
        with open(txtfilename, 'r', encoding='utf-8', errors='ignore') as txtfile:
            text = txtfile.read()

        if key != '':
            text = decrypt(text)

        textbox.insert(INSERT, text)
        filename = os.path.basename(txtfilename)
        current_remote_path = ''
        top.title("TinyJot - " + filename)
        textbox.focus_set()


def Save():
    global txtfilename, saved, modified
    if current_remote_path:
        webdav_save_same_name()
        return

    text = textbox.get(1.0, END).rstrip("\n")
    if key != '':
        text = encrypt(text)

    if not txtfilename:
        Save_to_file()
    else:
        with open(txtfilename, 'w', encoding='utf-8') as txtfilesave:
            txtfilesave.write(text)
        filename_base = os.path.basename(txtfilename)
        top.title("TinyJot - " + filename_base)
        textbox.focus_set()
        saved = True
        modified = False


def Save_to_file():
    global txtfilename, saved, modified, filename
    data = [('Text', '*.txt')]
    txtfilename = asksaveasfilename(filetypes=data, defaultextension=data)
    text = textbox.get(1.0, END).rstrip("\n")
    if key != '':
        text = encrypt(text)

    if txtfilename:
        with open(txtfilename, 'w', encoding='utf-8') as txtfilesave:
            txtfilesave.write(text)
        filename = os.path.basename(txtfilename)
        top.title("TinyJot - " + filename)
        textbox.focus_set()
        saved = True
        modified = False


def text_modified(event):
    global modified, saved
    if not modified:
        title = top.title()
        if not title.endswith("*"):
            top.title(title + "*")
        modified = True
        saved = False


def encrypt_pw():
    global key
    pwd = simpledialog.askstring("Password", "Enter password:", show='*')
    if pwd:
        key = ""
        for char in pwd:
            code = ord(char)
            if 64 < code < 91:
                key += str(code - 64)
            elif 96 < code < 123:
                key += str(code - 96)
            elif char.isdigit():
                key += char
    else:
        key = ''


def encrypt(text):
    """Encodes text to Base64 and shifts character codes based on a numeric key."""
    if not key:
        return text

    ciphertext = ""
    keyindex = 0
    keylength = len(key)

    text_b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")

    for char in text_b64:
        shift = int(key[keyindex])
        newcharcode = (ord(char) + shift) % 128
        ciphertext += chr(newcharcode)
        keyindex = (keyindex + 1) % keylength

    return ciphertext


def decrypt(ciphertext):
    """Reverses the character code shift and decodes the Base64 string back to original text."""
    if not key:
        return ciphertext

    try:
        b64_chars = []
        keyindex = 0
        keylength = len(key)

        for char in ciphertext:
            shift = int(key[keyindex])
            original_code = (ord(char) - shift) % 128
            b64_chars.append(chr(original_code))
            keyindex = (keyindex + 1) % keylength

        b64_string = "".join(b64_chars)
        decoded_bytes = base64.b64decode(b64_string.encode("ascii"))
        return decoded_bytes.decode("utf-8", errors="ignore")

    except Exception as e:
        print(f"Decryption error: {e}")
        return ciphertext

def callback(url):
    webbrowser.open_new_tab(url)

def aboutbox():
    global aboutbox
    #print ('about')
    aboutbox=tk.Toplevel(top)
    aboutbox.geometry("500x240")
    aboutbox.resizable(0,0)
    aboutbox.title("About")
    about_label=Label(aboutbox)
    logo=b'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'
    logoimg=tk.PhotoImage(data=logo)
    about_label.place(x=35,y=40,height=102,width=430)
    about_label.configure(image=logoimg)
    about_label.image=logoimg
    about_label.bind("<Button-1>", lambda e: callback("https://symbolform.com/"))

    url_title=Label(aboutbox)
    url_title.place(x=35,y=10,height=40,width=430)
    url_title.configure(text="TinyJot 1.4.2", font=("Arial",15), anchor='center')

    url_label=Label(aboutbox)
    url_label.place(x=35,y=152,height=15,width=430)
    url_label.configure(text="https://symbolform.com/", anchor='center')
    url_label.bind("<Button-1>", lambda e: callback("https://symbolform.com/"))

    url_label2=Label(aboutbox)
    url_label2.place(x=35,y=172,height=30,width=430)
    url_label2.configure(text="https://symbolform.com//tinyjot/", anchor='center')
    url_label2.bind("<Button-1>", lambda e: callback("https://symbolform.com//tinyjot/"))

    close_button=Button(aboutbox)
    close_button.place(x=220,y=200,height=30,width=40)
    close_button.configure(text="Close")
    close_button.bind("<Button-1>", close_aboutbox)

def close_aboutbox(event):
    aboutbox.destroy()

    
# --- Application Initialization ---
if __name__ == "__main__":
    read_config()
    create_main_window()
    create_textbox()
    create_menu()

    if len(sys.argv) > 1:
        txtfilename = " ".join(sys.argv[1:])
        if os.path.isfile(txtfilename):
            with open(txtfilename, 'r', encoding='utf-8', errors='ignore') as f:
                textbox.insert(INSERT, f.read())
            filename = os.path.basename(txtfilename)
            top.title("TinyJot - " + filename)

    root.mainloop()
