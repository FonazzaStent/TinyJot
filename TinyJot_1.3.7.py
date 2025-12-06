"""TinyJot 1.3.7 - A WebDAV enabled notepad.
Copyright (C) 2023-2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>."""

import base64
import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import simpledialog
from tkinter import font
#import io
from webdav3.client import Client
import time
import stat
from tkinter import messagebox
import webbrowser
from tkfontchooser import askfont

try:
    import pyi_splash
    pyi_splash.close()
except:
    True

password=''
FTPerror=False
configflag='open'
#read config file
filename=''
key=''
ciphertext=''
WebDAVerror=False
browsepath='/'
weekdays=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
#temporary
WebDAV_selected=1

def read_config():
    global txtfilename
    global server
    global port
    global username

    global fontname
    global fontsize
    txtfilename=''
    parameters=[]
    if os.path.isfile('config.ini'):
        configfile=open("config.ini",'r')
    else:
        parameterstring='ftp.host.com\nname@email.com\nTimes\n12'
        configfile=open("config.ini",'w')
        configfile.write(parameterstring)
        configfile.close()
        configfile=open("config.ini",'r')
    for n in range (0,4):
        try:
            line=configfile.readline()
            line=line.rstrip('\n')
        except:
            line=''
        parameters.append(line)
    configfile.close()
    server=parameters[0]
    username=parameters[1]
    fontname=parameters[2]
    fontsize=int(parameters[3])

    
#create main window
def create_main_window():
        global top
        global root
        img=b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAAXNSR0IB2cksfwAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAATtQTFRFaRLG////QkJCq83gQkJCq83gQkJCxuT0yOb1QkJCq83ge42YbnyEYWtxQkJCUlhbz+v6lKWtg4+WR0lKcXp/W2BjSkxMQkJCQ4bJRojJRojKR4nKSEpLSYrKS0xNTIzLTIzMVVxfWZXOXWJlXZjPYJrPY5zQY53VZnF4Z6DWbKTYbaPSc4OMdH6CdKfUfrHfgJSgg5mlhLLXhLLYhbPXhpyohrTYh5SaiLjiirfZi6KwjLjZjrnaj7rZkau5lL3blrHAlr/bl8Dcmqqym7jIm8LcnMPcnq+4n8Xdn8nrocbeorO8osfeo8zspMjepcnfpc3tp8rfqM/uqbvFq83gq9Lvr9TxsNXxscbQtdnzttrzuM7ZuNv0ut31u971v9biv+D3w+P4xuX5yOf6y+n7zer8z+z80e791vH/ZZ/c0wAAAAF0Uk5TAEDm2GYAAAAJcEhZcwAADdcAAA3XAUIom3gAAAAHdElNRQfpCh0JOyQaPEdvAAAA8ElEQVQ4y62SMQvCMBCFy7vBxaK0CNXBQdHNrg6KLkWclA6CoCAO2vv/v8A0vWgSK6XgBwfh8sh74S4IKoDvcmgSnBGq5qC66KmaYmNdM98QcQddZoAoxI66yIjaCBaam1Kqfpblqg62AAIzk4UlWHJJhJ+CWpwXHonHgVzBMxVmwtETsOGTwLMYKVK+j4aCb6EzKMHPDI0WxVowYXNq+U2+Clvhy+IkrIS2Fk2z6I8NwPsY2QvDxiJW2zQrD0dn3MxmWDH2lFbDcgWCtnYX5tKzwXyCsd0IAy95kniNt0WhKVu5huozcP9cu7QW9HfBCykxbF/WiDKeAAAAAElFTkSuQmCC'
        root= tk.Tk()
        top= root
        top.geometry("600x450")
        top.title("TinyJot")
        favicon=tk.PhotoImage(data=img) 
        root.wm_iconphoto(True, favicon)
        root.protocol("WM_DELETE_WINDOW", QuitApp)

#configure
def configure():
    global configwin
    global pw_entry
    global user_entry
    global port_entry
    global host_entry
    global file_entry
    global logfile_entry
    global logdir_entry
    global WebDAV_menu
    configwin=tk.Toplevel(top)
    configwin.geometry("493x140")
    configwin.resizable(0,0)
    configwin.title("Configure WebDAV")
    host_label=Label(configwin)
    host_label.place(x=20,y=19,height=19,width=64)
    host_label.configure(text="Hostname")
    v = tk.StringVar()
    v.set(server)
    host_entry=Entry(configwin,textvariable=v)
    host_entry.place(x=90,y=19,height=20,width=384)
  
    user_label=Label(configwin)
    user_label.place(x=20,y=47,height=19,width=64)
    user_label.configure(text="Username")
    x = tk.StringVar()
    x.set(username)
    user_entry=Entry(configwin,textvariable=x)
    user_entry.place(x=90,y=47,height=20,width=384)
    #user_entry.bind("<Return>",get_config)
    pw_label=Label(configwin)
    pw_label.place(x=25,y=75,height=21,width=54)
    pw_label.configure(text="Password")
    j = tk.StringVar()
    j.set(password)
    pw_entry=Entry(configwin,show="*",textvariable=j)
    pw_entry.place(x=90,y=75,height=20,width=384)
    pw_entry.bind("<Return>",get_config)
    
    pw_button=Button(configwin)
    pw_button.place(x=210,y=105, height=24,width=47)
    pw_button.configure(text="Save")
    pw_button.bind("<Button-1>",get_config)
    cancel_button=Button(configwin)
    cancel_button.place(x=290,y=105, height=24,width=47)
    cancel_button.configure(text="Cancel")
    cancel_button.bind("<Button-1>",config_cancel)
    pw_entry.focus_set()
    config_context_menu()

def get_config(event):
    global password
    global configflag
    global fontname
    global fontsize
    password=pw_entry.get()
    server=host_entry.get()
    username=user_entry.get()
    configfile=open("config.ini",'w')
    configfile.writelines(server+"\n")
    configfile.writelines(username+"\n")
    configfile.writelines(fontname+"\n")
    configfile.writelines(str(fontsize)+"\n")
    configfile.close()
    configwin.destroy()
    read_config()

def config_cancel(event):
    configwin.destroy()

def config_context_menu():
    global menu
    menu = Menu(configwin, tearoff = 0)
    menu.add_command(label="Paste", command=config_paste_text)
    configwin.bind("<Button-3>", trigger_config_context_menu)

def trigger_config_context_menu(event): 
    try: 
        menu.tk_popup(event.x_root, event.y_root)
    finally: 
        menu.grab_release()
        
def config_paste_text():
        pw_entry.event_generate(("<<Paste>>"))

#Textbox
def create_textbox():
        global textbox
        textbox = Text(top)
        textbox.place(relx=00, rely=00, relheight=1, relwidth=0.97)
        scroll_1=Scrollbar (top)
        scroll_1.pack(side=RIGHT, fill=Y)
        textbox.configure(yscrollcommand=scroll_1.set,wrap=WORD,undo=True,maxundo=50)
        textbox.configure(font=(fontname, fontsize))
        scroll_1.configure(command=textbox.yview)
        textbox.bind("<Key>", text_modified)

#menu
def create_menu():
    menubar=tk.Menu(top, tearoff=0)
    top.configure(menu=menubar)
    sub_menu=tk.Menu(top, tearoff=0)
    edit_menu=tk.Menu(top,tearoff=0)
    menubar.add_cascade(menu=sub_menu,compound="left", label="File")
    sub_menu.add_command(compound="left",label="New", command=new_file,accelerator="Alt+N")
    sub_menu.add_command(compound="left",label="Open", command=open_file,accelerator="Alt+O")
    sub_menu.add_command(compound="left",label="Save", command=Save,accelerator="Alt+S")
    sub_menu.add_command(compound="left",label="Save as", command=Save_to_file,accelerator="Alt+A")
    sub_menu.add_command(compound="left",label="WebDAV", command=webdav_open,accelerator="Alt+T")
    sub_menu.add_command(compound="left",label="WebDAV Save", command=webdav_save_same_name,accelerator="Alt+W")
    sub_menu.add_command(compound="left",label="WebDAV Configure", command=browse_config,accelerator="Alt+C")
    sub_menu.add_command(compound="left",label="Encrypt/Decrypt", command=encrypt_pw,accelerator="Alt+E")
    sub_menu.add_command(compound="left",label="Quit", command=QuitApp,accelerator="Alt+Q")
    menubar.add_cascade(menu=edit_menu,compound="left", label="Edit")
    edit_menu.add_command(compound="left",label="Undo", command=textbox.edit_undo,accelerator="Ctrl+Z")
    edit_menu.add_command(compound="left",label="Redo", command=textbox.edit_redo,accelerator="Ctrl+Y")
    edit_menu.add_command(compound="left",label="Copy", command=copy_code,accelerator="Ctrl+C")
    edit_menu.add_command(compound="left",label="Paste", command=paste_code,accelerator="Ctrl+V")
    edit_menu.add_command(compound="left",label="Cut", command=cut_code,accelerator="Ctrl+X")
    edit_menu.add_command(compound="left",label="Font", command=font_size)
    edit_menu.add_command(compound="left",label="Date and time", command=date_time,accelerator='Alt+D')
    edit_menu.add_command(compound="left",label="Time", command=just_time,accelerator='Alt+I')
    
    menubar.bind_all("<Alt-f>",menubar.invoke(1))
    top.bind_all("<Alt-n>",new_hotkey)
    top.bind_all("<Alt-o>",open_hotkey)
    top.bind_all("<Alt-s>",save_hotkey)
    top.bind_all("<Alt-a>",Save_to_file_hotkey)
    top.bind_all("<Alt-t>",webdav_open_hotkey)
    top.bind_all("<Alt-w>",webdav_save_same_name_hotkey)
    #top.bind_all("<Alt-v>",webdav_save_hotkey)
    top.bind_all("<Alt-c>",configure_hotkey)
    top.bind_all("<Alt-e>",encrypt_pw_hotkey)
    top.bind_all("<Alt-q>",QuitApp_hotkey)
    #textbox.bind_all("<Control-z>",undo_hotkey)
    #textbox.bind_all("<Control-Shift-z>",redo_hotkey)
    top.bind_all("<Alt-d>",date_time_hotkey)
    top.bind_all("<Alt-i>",just_time_hotkey)

    #About menu
    about=tk.Menu(top, tearoff=0)
    menubar.add_cascade(menu=about,compound="left", label="?")
    about.add_command(compound="left", label="Help", command=helpbox)
    about.add_command(compound="left", label="About", command=aboutbox)

#hotkeys
def browse_hotkey(event):
    browse()
    
def new_hotkey(event):
    new_file()

def open_hotkey(event):
    open_file()

def save_hotkey(event):
    Save()

def Save_to_file_hotkey(event):
    Save_to_file()

def configure_hotkey(event):
    configure()

def QuitApp_hotkey(event):
    QuitApp()

def WebDAV_select(event):
    global WebDAV_selected
    WebDAV_selected=WebDAV_menu.get()

def browse_config():
    global configflag
    configflag='browse'
    configure()

#Quit
def QuitApp():
    top.destroy()

#Copy Code
def copy_code():
    #textbox.tag_add(SEL, "1.0", END)
    textbox.event_generate(("<<Copy>>"))

#Paste Code
def paste_code():
    textbox.event_generate(("<<Paste>>"))

#Cut Code
def cut_code():
    textbox.event_generate(("<<Cut>>"))

def font_size():
    global fontsize
    global fontname
    fontsize=11
    font = askfont(root)
    fontname=font['family']
    fontsize=font['size']
    if fontsize>9 and fontsize<100:
        textbox.configure(font=(fontname, fontsize))

#CopyContextMenu
def create_context_menu():
    global menu
    menu = Menu(root, tearoff = 0)
    menu.add_command(label="Copy", command=copy_text)
    menu.add_command(label="Paste", command=paste_text)
    menu.add_command(label="Cut", command=cut_text)
    root.bind("<Button-3>", context_menu)

def context_menu(event): 
    try: 
        menu.tk_popup(event.x_root, event.y_root)
    finally: 
        menu.grab_release()
        
def copy_text():
        textbox.event_generate(("<<Copy>>"))

def paste_text():
        textbox.event_generate(("<<Paste>>"))

def cut_text():
        textbox.event_generate(("<<Cut>>"))

def undo():
    try:
        textbox.edit_undo
    except:
        True
        
def redo():
    try:
        textbox.edit_redo
    except:
        True

def undo_hotkey(event):
    undo()

def redo_hotkey(event):
    redo()

def date_time():
    date= time.strftime("%d/%m/%Y %H:%M:%S %w")
    weeknumber=int(date[20])
    weekday=weekdays[weeknumber-1]
    timestamp=time.strftime("%d/%m/%Y %H:%M:%S")
    timestamp=weekday+" "+timestamp
    textbox.insert(INSERT,timestamp+'\n')

def date_time_hotkey(event):
    date_time()

def just_time():
    timestamp=time.strftime("%H:%M:%S")
    textbox.insert(INSERT,timestamp+'\n')

def just_time_hotkey(event):
    just_time()

#New file
def new_file():
    global txtfilename
    response=messagebox.askquestion("Save",'Save first?')
    if response=='yes':
        Save()
    txtfilename=''
    textbox.delete(1.0,END)
    top.title("TinyJot")
    textbox.focus_set()


#Open file
def open_file():
    global txtfile
    global txtfilename
    data=[('Text', '*.txt')]
    txtfilename=askopenfilename(filetypes=data)
    if str(txtfilename)!='':
        textbox.delete(1.0,END)
        txtfile=open(txtfilename,'r')

        text=''
        eof=False
        while eof==False:
           try:
               char=txtfile.read(1)
           except:
               char="?"
           text=text+char
           if char=='':
               eof=True
        if key!='':
            ciphertext=decrypt(text)
            text=ciphertext

        #text=txtfile.read()
        textbox.insert(INSERT,text)
    filename=os.path.basename(txtfilename).split('/')[-1]
    top.title("TinyJot - "+filename)
    textbox.focus_set()

#Save
def Save():
    global txtfilename
    text=textbox.get(1.0,END)
    if key!='':
        ciphertext=encrypt(text)
        text=ciphertext
    if str(txtfilename)=='':
        Save_to_file()
    if str(txtfilename)!='':
        txtfilesave=open(txtfilename,'w')
        txtfilesave.write(text)
        txtfilesave.close()
        filename=os.path.basename(txtfilename).split('/')[-1]
        top.title("TinyJot - "+filename)
        textbox.focus_set()


#Save as
def Save_to_file():
    global txtfilename
    data=[('Text','*.txt')]
    txtfilename=asksaveasfilename(filetypes=data, defaultextension=data)
    text=textbox.get(1.0,END)
    if key!='':
        ciphertext=encrypt(text)
        text=ciphertext
    if str(txtfilename)!='':
          txtfilesave=open(txtfilename,'w')
          txtfilesave.write(text)
          txtfilesave.close()
    filename=os.path.basename(txtfilename).split('/')[-1]
    top.title("TinyJot - "+filename)
    textbox.focus_set()

def webdav_open():
    global webdav
    global browselist
    global browsewin
    global WedDAVerror
    
    WebDAVerror=False
    try:
        options = {
        'webdav_hostname' : server,
        'webdav_login':    username,
        'webdav_password': password,
        'webdav_override_methods': {
            'check': 'GET'
        },
        'disable_check': True}
        webdav=Client(options)
    except:
        WebDAVwerror=True
    if WebDAVerror==False:
        webdav_browse()

def webdav_open_hotkey(event):
    webdav_open()
    
def webdav_browse():
    global browselist
    global browsewin
    global WebDAVerror
    global filename_entry

    global webdav
    WebDAVerror=False
    try:
        options = {
        'webdav_hostname' : server,
        'webdav_login':    username,
        'webdav_password': password,
        'webdav_override_methods': {
            'check': 'GET'
        },
        'disable_check': True}
        webdav=Client(options)
    except:
        WebDAVwerror=True

    
    browsewin=tk.Toplevel(top)
    browsewin.geometry("530x588")
    browsewin.resizable(0,0)
    browsewin.title("Browse WebDAV")
    browselist=Listbox(browsewin)
    browselist.place(x=15,y=15,height=500,width=500)
    #browsewin.bind("<<ListboxSelect>>",list_select)
    browsewin.bind('<Double-Button>', chdirs_webdav)
    #browsewin.protocol("WM_DELETE_WINDOW", QuitWebDAV)

    open_button=Button(browsewin)
    open_button.place(x=20,y=554, height=24,width=40)
    open_button.configure(text="Open")
    open_button.bind("<Button-1>",chdirs_webdav)

    save_button=Button(browsewin)
    save_button.place(x=70,y=554, height=24,width=40)
    save_button.configure(text="Save")
    save_button.bind("<Button-1>",webdav_save_file)
 

    newfolder_button=Button(browsewin)
    newfolder_button.place(x=125,y=554, height=24,width=65)
    newfolder_button.configure(text="New folder")
    newfolder_button.bind("<Button-1>",webdav_new_folder)

    deletefile_button=Button(browsewin)
    deletefile_button.place(x=200,y=554, height=24,width=50)
    deletefile_button.configure(text="Delete")
    deletefile_button.bind("<Button-1>",delete_file)

    rename_button=Button(browsewin)
    rename_button.place(x=275,y=554, height=24,width=50)
    rename_button.configure(text="Rename")
    rename_button.bind("<Button-1>",rename_file_key)

    cancel_button=Button(browsewin)
    cancel_button.place(x=400,y=554, height=24,width=45)
    cancel_button.configure(text="Cancel")
    cancel_button.bind("<Button-1>",webdav_cancel)
    
    filename_entry=Entry(browsewin)
    filename_entry.place(x=20,y=520,height=24,width=500)
    filename_entry.focus_set()

    scroll_webdav=Scrollbar (browsewin)
    scroll_webdav.pack(side=RIGHT, fill=Y)
    scroll_webdav.configure(command=browselist.yview)


    webdav_browsedir()

def webdav_browsedir():
    global dirlist
    global file_types
    fileyes=True
    dirlist=[]
    file_types=[]
    try:
        dirlist=webdav.list(browsepath)
        dirlist_info=webdav.list(browsepath,get_info=True)
        if len(dirlist)>0:
            del dirlist[0]
    except Exception as e:
        messagebox.showerror("WebDAV error", "Could not connect to WebDAV server.")
        print (e)
    browselist.delete(0,END)
    browselist.insert(0,'..')
    
    index=len(dirlist)   
    for item in dirlist[::-1]:
        namelength=len(item)
        if dirlist_info[index]['isdir']==True:
            fileyes=False
        else:
            fileyes=True
            file_types.append(index)
        if fileyes==False:
            item='['+str(item)+']'
        browselist.insert(0,item)
        index=index-1
        #print (file_types)

def webdav_browse_save():
    global browselist
    global browsewin
    global filename_entry
    global WedDAVerror
    global webdav
    WebDAVerror=False
    try:
        options = {
        'webdav_hostname' : server,
        'webdav_login':    username,
        'webdav_password': password,
        'webdav_override_methods': {
            'check': 'GET'
        },
        'disable_check': True}
        webdav=Client(options)
    except:
        WebDAVwerror=True

    browsewin=tk.Toplevel(top)
    browsewin.geometry("530x588")
    browsewin.resizable(0,0)
    browsewin.title("Browse FTP")
    browselist=Listbox(browsewin)
    browselist.place(x=15,y=15,height=500,width=500)
    #browsewin.bind("<<ListboxSelect>>",list_select)
    browsewin.bind('<Double-Button>', chdirs)
    #browsewin.protocol("WM_DELETE_WINDOW", QuitFTP)

    ok_button=Button(browsewin)
    ok_button.place(x=20,y=554, height=24,width=40)
    ok_button.configure(text="Save")
    ok_button.bind("<Button-1>",webdav_save_file)
    cancel_button=Button(browsewin)
    cancel_button.place(x=70,y=554, height=24,width=45)
    cancel_button.configure(text="Cancel")
    cancel_button.bind("<Button-1>",webdav_cancel)
    newfolder_button=Button(browsewin)
    newfolder_button.place(x=125,y=554, height=24,width=65)
    newfolder_button.configure(text="New folder")
    newfolder_button.bind("<Button-1>",new_folder)

    deletefile_button=Button(browsewin)
    deletefile_button.place(x=200,y=554, height=24,width=70)
    deletefile_button.configure(text="Delete file")
    deletefile_button.bind("<Button-1>",delete_file)
    
    filename_entry=Entry(browsewin)
    filename_entry.place(x=20,y=520,height=24,width=510)
    filename_entry.focus_set()
    webdav_browsedir()


def chdirs_webdav(event):
    global browsepath
    #global filepath
    global filename
    filetype=False
    if browselist.get(browselist.curselection())=='..':
        updir=True
        updir_webdav()
    else:
        file_index=browselist.curselection()
        file_index=int(file_index[0])
        for item in file_types:
            #print (file_index,item)
            if file_index+1==item:
                filetype=True
                filepath=browsepath+(browselist.get(browselist.curselection()))
                filename=browselist.get(browselist.curselection())
                webdav_open_file(filepath)
                
        if filetype==False:
            browsepath=browsepath+dirlist[file_index]
            webdav_browsedir()

def chdirs_webdav_event(event):
    chdirs_webdav()

def updir_webdav():
    global browsepath
    browsepath=browsepath[:-1]
    browsepath='/'.join(browsepath.split("/")[:-1])
    browsepath=browsepath[:]+'/'
    webdav_browsedir()

def webdav_open_file(filepath):
    tempfile=open("tempfile",'wb')
    webdav.download_file(filepath, tempfile.name)
    tempfile.close()
    tempfile=open("tempfile",'r')
    top.title("TinyJot - WebDAV: "+filename)
    text=''
    eof=False
    while eof==False:
       try:
           char=tempfile.read(1)
       except:
           char="?"
       text=text+char
       if char=='':
           eof=True
    browsewin.destroy()
    if key!='':
        ciphertext=decrypt(text)
        text=ciphertext
    
    #text=tempfile.read()
    tempfile.close()
    os.remove("tempfile")
    textbox.delete(1.0,END)
    textbox.insert(INSERT,text)
    textbox.insert(INSERT,'\n')
    #textbox.insert(INSERT,timestamp+'\n')
    
    textbox.focus_set()

def webdav_save_file(event):
    global filename
    if filename_entry.get!='':
        filename=filename_entry.get()
    else:
        messagebox.showerror("WebDAV error", "Filename not specified")

    if filename!='':
        text=textbox.get(1.0,END)

    if key!='':
        ciphertext=encrypt(text)
        text=ciphertext

    tempfile=open("tempfile",'w')
    tempfile.write(text)
    tempfile.close()
    tempfile=open("tempfile",'rb')
    savepath=browsepath+filename
        #print (savepath)
    if filename[-4:]=='.txt':
        
        webdav.upload_file(savepath,"tempfile")
    else:
        webdav.upload_file(savepath+'.txt',"tempfile")
    tempfile.close()
    os.remove("tempfile")
    top.title("TinyJot - WebDAV: "+filename)
    textbox.focus_set()
    WebDAVerror=False
    browsewin.destroy()


def webdav_save_same_name():
    global filename
    if filename!='':
        text=textbox.get(1.0,END)
    else:
        webdav_browse()

    if key!='':
        ciphertext=encrypt(text)
        text=ciphertext
        
    tempfile=open("tempfile",'w')
    tempfile.write(text)
    tempfile.close()
    tempfile=open("tempfile",'rb')
    savepath=browsepath+filename
    try:
        if filename[-4:]=='.txt':
            webdav.upload_file(savepath,"tempfile")
        else:
            webdav.upload_file(savepath+'.txt',"tempfile")
        tempfile.close()
        os.remove("tempfile")
        top.title("TinyJot - WebDAV: "+filename)
    except Exception as e:
        print (e)
        tempfile.close()
    textbox.focus_set()

def webdav_save_same_name_hotkey(event):
    webdav_save_same_name()
 
def webdav_new_folder(event):
    global filename
    if filename_entry.get!='':
        filename=filename_entry.get()
    if filename!='':
        text=textbox.get(1.0,END)
        newdir=browsepath+filename
        webdav.mkdir(newdir)
        webdav_browsedir()

def webdav_delete_file():
    dirindex=browselist.curselection()
    dirfname=browselist.get(browselist.curselection())
    if dirindex!='' and dirfname!='..':
        fname=dirlist[dirindex[0]]
        delfname=browsepath+fname
        okdelete=messagebox.askokcancel("Delete?","Confirm delete?",default="ok")
        if okdelete==True:
            webdav.clean(delfname)
            webdav_browsedir()

    
def list_select(event):
    global filename
    filename=browselist.get(browselist.curselection())


def delete_file(event):
    if WebDAV_selected=='FTP':
        fname=browselist.get(browselist.curselection())
        fnamelength=len(fname)
        fnametemp=''
        fdir=False
        for n in range (0,fnamelength):
            if fname[n]!='[' and fname[n]!=']':
                fnametemp=fnametemp+fname[n]
        fname=fnametemp
        #print (filename)
        try:
            size=ftp.size(fname)
        except:
            fdir=True
        if fdir==True:
            okcancel= messagebox.askokcancel("Delete?","Do you want to delete the folder?",default="ok")
            if okcancel== True:
                ftp.rmd(fname)
        else:
            okcancel= messagebox.askokcancel("Delete?","Do you want to delete the file?",default="ok")
            if okcancel== True:
                ftp.delete(fname)
        #print (filename)
        browsedir()
    else:
        webdav_delete_file()

def rename_file():
    dirindex=browselist.curselection()
    dirfname=browselist.get(browselist.curselection())
    if dirindex!='' and dirfname!='..':
        fname=dirlist[dirindex[0]]
        renfname=browsepath+fname
        newname=filename_entry.get()
        newname=browsepath+newname
        
        renfname_info=webdav.list(renfname,get_info=True)

        if renfname_info[0]['isdir']==False:
            if newname[-4:]!='.txt':
                newname=newname+'.txt'
        #requests.request("MOVE", renfname, headers=newname, auth=HTTPBasicAuth(username, password))
        webdav.move(remote_path_from=renfname, remote_path_to=newname)
        webdav_browsedir()

def rename_file_key(event):
    rename_file()

def webdav_cancel(event):
    browsewin.destroy()

#text modified
def text_modified(event):
    global filename
    #filename=os.path.basename(txtfilename).split('/')[-1]
    top.title("TinyJot - "+filename+"*")

def startup():
	try:
		filename=str(" ".join(sys.argv[1:]))
		global txtfile
		global txtfilename
		data=[('Text', '*.txt')]
		txtfilename=filename
		if str(txtfilename)!='':
			textbox.delete(1.0,END)
			txtfile=open(txtfilename,'rb')
			text=txtfile.read()
			textbox.insert(INSERT,text)
		filename=os.path.basename(txtfilename).split('/')[-1]
		top.title("TinyJot - "+filename)
		textbox.focus_set()
	except:
		True

#Encrypt
def encrypt_pw():
    global key
    password = simpledialog.askstring("Password", "Enter password:", show='*')
    if password!='' and str(password)!='None':
        password_length= len(password)
        key=''
        for n in range (0,password_length):
            asciicode= ord(password[n])
            if (asciicode>64 and asciicode<91):
                numberstring=str(asciicode-64)
            if(asciicode>96 and asciicode<123):
                numberstring=str(asciicode-96)
            if password[n].isdigit()==True:
                numberstring=str(password[n])
            key=key+numberstring
    else:
        key=''

def encrypt_pw_hotkey(event):
    encrypt_pw()

def encrypt(text):
    ciphertext=''
    keyindex=0
    text = base64.b64encode(text.encode("utf-8"))
    text=str(text)
    text=text[2:-1]
    length=len(text)
    keylength=len(key)-1
    for n in range (0,length):
        char=ord(text[n])
        newcharcode=char+int(key[keyindex])
        if newcharcode>127:
            newcharcode=(newcharcode-128)
        newchar=chr(newcharcode)
        #print (newchar)
        keyindex=keyindex+1
        if keyindex>keylength:
            keyindex=0

        ciphertext=ciphertext+newchar
    return ciphertext

def decrypt(text):
    ciphertext=''
    keylength=len(key)-1

    keyindex=0
    length=len(text)


    for n in range (0,length):
        
        char=ord(text[n])
        newcharcode=char-int(key[keyindex])
        if newcharcode<0:
            newcharcode=(newcharcode+128)
        newchar=chr(newcharcode)
        keyindex=keyindex+1
        if keyindex>keylength:
            keyindex=0
        try:
            ciphertext=ciphertext+newchar
        except Exception as e:
            print (key[keyindex],newcharcode,newchar)
            print (txtimgstring[n],n)
            print (e)
    decoded_bytes = base64.b64decode(ciphertext)
    ciphertext = decoded_bytes.decode('utf-8')
    return ciphertext

     

#About
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
    url_title.configure(text="TinyJot 1.3.7", font=("Arial",15), anchor='center')

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

def callback(url):
    webbrowser.open_new_tab(url)

def helpbox():
    global helpbox
    helpbox=tk.Toplevel(top)
    helpbox.geometry("440x540")
    helpbox.resizable(0,0)
    helpbox.title("Help")
    
    textbox1 = Text(helpbox)
    textbox1.place(x=20, y=20, height=470, width=400)
    scroll_2=Scrollbar (helpbox)
    scroll_2.place(x=421, y=20, height=470, anchor='n')
    textbox1.configure(yscrollcommand=scroll_2.set, wrap=WORD)
    scroll_2.configure(command=textbox1.yview)
    textbox1.focus_set()
    readme="TinyJot 1.3.7\n\
SymbolForm\n\
\n\
TinyJot is a basic notepad with WebDAV capabilities. It can open, edit and \
save text files on a local drive, or open, edit and save a text logfile \
on a remote WebDAV server.\n\
\n\
For local files:\n\
\n\
- File – Open (Alt-O), to open a text file\n\
- File – New (Alt-N), to start a new text file\n\
- File – Save (Alt-S), to save a file currently being edited\n\
- File – Save As (Alt-A), to save a file with a new name\n\
- File – Quit (Alt-Q), to quit the program\n\
- Edit – Copy, to copy text\n\
- Edit – Paste, to paste text\n\
\n\
For WebDAV files:\n\
\n\
- File - WebDAV (Alt-T), to open a file hosted on the WebDAV server.\n\
- File – WebDAV Save (Alt-W), to save editing window content to a WebDAV \
  File on the WebDAV server.\n\
- File – WebDAV Save as (Alt-V), to save editing window content to a WebDAV \
  file with a different name on the WebDAV server.\n\
- File – WebDAV Configure (Alt-C), to configure the WebDAV server settings.\n\
\n\
Encrypt and decrypt files\n\
\n\
- File - Encrypt/Decrypt, input a password to encrypt or decrypt\
  files. First you input a password, then you open the encrypted file.\n\
- To encrypt a file, first input a password, then save the file.\n\
- Changing the password while editing, will save the file with the\
  new password when saving.\n\
\n\
Alt-F to open the command menu.\n\
\n\
- Edit – Font to choose font and font size. Bold, italic, underlined are \
  not allowed\n\
\n\
The program will not store the WebDAV user password anywhere, so you will \
have to type it every time you use the program.\n\
\n\
The WebDAV configuration parameters are stored in the config.ini file. Do \
not delete this file or the program will crash. You can also configure \
the WebDAV server by editing the config.ini file, according to the following \
specifications:\n\
\n\
Row n.1: hostname (i.e. ftp.host.com)\n\
Row n.2: port (most of the times 21, unused for WebDAV)\n\
Row n. 3:  FTP or WebDav username (i.e. an email address or other username)\n\
Ron n. 4: font name\n\
Row n. 5 font size\n\
\n\
New in this version:\n\
- Timestamp menu item added"
    textbox1.insert(INSERT,readme)
    textbox1.configure(state=DISABLED)
    close_button1=Button(helpbox)
    close_button1.place(x=200,y=500,height=30,width=40)
    close_button1.configure(text="Close")
    close_button1.bind("<Button-1>", close_helpbox)

def close_helpbox(event):
    helpbox.destroy()

def main():
        read_config()
        create_main_window()
        create_textbox()
        create_menu()
        create_context_menu()
        startup()
        
main()
root.mainloop()
