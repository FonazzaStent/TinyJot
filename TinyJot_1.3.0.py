"""TinyJot 1.3.0 - An FTP and WebDav enabled notepad.
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
import io
from ftplib import FTP
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

#temporary
remote_selected=1

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
        parameterstring='ftp.host.com\n21\nname@email.com\nTimes\n12'
        configfile=open("config.ini",'w')
        configfile.write(parameterstring)
        configfile.close()
        configfile=open("config.ini",'r')
    for n in range (0,5):
        try:
            line=configfile.readline()
            line=line.rstrip('\n')
        except:
            line=''
        parameters.append(line)
    configfile.close()
    server=parameters[0]
    port=parameters[1]
    username=parameters[2]
    fontname=parameters[3]
    fontsize=int(parameters[4])

    
#create main window
def create_main_window():
        global top
        global root
        img=b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAKhJREFUOE9jZICCioYP/z+/7WCYOrmDMTu34j8+GqS2o0GAEaQVTIAAsiBMDBeN14BpV27+x2dAlo46I9VdgGLjtCs3GbJ01DEcgUscFAb/k0XNGUSzdzLAAgZJN8hweDhhUfsfbABIEcxfyGEAcgnIZhiAugw5DOAGwNQoMTAw3MfnAnS/UeoCsP9QvIBmA0YYIHsXlpAoCYPhkhKpl5kI5UJkeViqBQBbJ7ANHJY4MwAAAABJRU5ErkJggg=='
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
    global remote_menu
    configwin=tk.Toplevel(top)
    configwin.geometry("493x210")
    configwin.resizable(0,0)
    configwin.title("Configure FTP")
    host_label=Label(configwin)
    host_label.place(x=20,y=19,height=19,width=64)
    host_label.configure(text="Hostname")
    v = tk.StringVar()
    v.set(server)
    host_entry=Entry(configwin,textvariable=v)
    host_entry.place(x=90,y=19,height=20,width=384)
    port_label=Label(configwin)
    port_label.place(x=50,y=47,height=19,width=34)
    port_label.configure(text="Port")
    w = tk.StringVar()
    w.set(port)
    port_entry=Entry(configwin,textvariable=w)
    port_entry.place(x=90,y=47,height=20,width=84)    
    user_label=Label(configwin)
    user_label.place(x=20,y=75,height=19,width=64)
    user_label.configure(text="Username")
    x = tk.StringVar()
    x.set(username)
    user_entry=Entry(configwin,textvariable=x)
    user_entry.place(x=90,y=75,height=20,width=384)
    #user_entry.bind("<Return>",get_config)
    pw_label=Label(configwin)
    pw_label.place(x=25,y=105,height=21,width=54)
    pw_label.configure(text="Password")
    j = tk.StringVar()
    j.set(password)
    pw_entry=Entry(configwin,show="*",textvariable=j)
    pw_entry.place(x=90,y=105,height=20,width=384)
    pw_entry.bind("<Return>",get_config)
    remote_options=["FTP","WebDav"]
    remote_menu=ttk.Combobox(configwin)
    remote_menu.configure(state="readonly",values=remote_options)
    remote_menu.current(1)
    remote_menu.place(x=90,y=134,height=25,width=384)
    remote_menu.bind("<<ComboboxSelected>>", remote_select)
    
    pw_button=Button(configwin)
    pw_button.place(x=210,y=170, height=24,width=47)
    pw_button.configure(text="Save")
    pw_button.bind("<Button-1>",get_config)
    cancel_button=Button(configwin)
    cancel_button.place(x=290,y=170, height=24,width=47)
    cancel_button.configure(text="Cancel")
    cancel_button.bind("<Button-1>",config_cancel)
    pw_entry.focus_set()

def get_config(event):
    global password
    global configflag
    global fontname
    global fontsize
    password=pw_entry.get()
    server=host_entry.get()
    port=port_entry.get()
    username=user_entry.get()
    configfile=open("config.ini",'w')
    configfile.writelines(server+"\n")
    configfile.writelines(port+"\n")
    configfile.writelines(username+"\n")
    configfile.writelines(fontname+"\n")
    configfile.writelines(str(fontsize)+"\n")
    configfile.close()
    configwin.destroy()
    read_config()

def config_cancel(event):
    configwin.destroy()

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
    sub_menu.add_command(compound="left",label="Remote Open", command=ftp_open,accelerator="Alt+T")
    sub_menu.add_command(compound="left",label="Remote Save", command=ftp_save_same_name,accelerator="Alt+W")
    sub_menu.add_command(compound="left",label="Remote Save as", command=ftp_save,accelerator="Alt+V")
    sub_menu.add_command(compound="left",label="Remote Configure", command=browse_config,accelerator="Alt+C")
    sub_menu.add_command(compound="left",label="Encrypt/Decrypt", command=encrypt_pw,accelerator="Alt+E")
    sub_menu.add_command(compound="left",label="Quit", command=QuitApp,accelerator="Alt+Q")
    menubar.add_cascade(menu=edit_menu,compound="left", label="Edit")
    edit_menu.add_command(compound="left",label="Undo", command=textbox.edit_undo,accelerator="Ctrl+Z")
    edit_menu.add_command(compound="left",label="Redo", command=textbox.edit_redo,accelerator="Ctrl+Y")
    edit_menu.add_command(compound="left",label="Copy", command=copy_code,accelerator="Ctrl+C")
    edit_menu.add_command(compound="left",label="Paste", command=paste_code,accelerator="Ctrl+V")
    edit_menu.add_command(compound="left",label="Cut", command=cut_code,accelerator="Ctrl+X")
    edit_menu.add_command(compound="left",label="Font", command=font_size)    
    menubar.bind_all("<Alt-f>",menubar.invoke(1))
    top.bind_all("<Alt-n>",new_hotkey)
    top.bind_all("<Alt-o>",open_hotkey)
    top.bind_all("<Alt-s>",save_hotkey)
    top.bind_all("<Alt-a>",Save_to_file_hotkey)
    top.bind_all("<Alt-t>",ftp_open_hotkey)
    top.bind_all("<Alt-w>",ftp_save_same_name_hotkey)
    top.bind_all("<Alt-v>",ftp_save_hotkey)
    top.bind_all("<Alt-c>",configure_hotkey)
    top.bind_all("<Alt-e>",encrypt_pw_hotkey)
    top.bind_all("<Alt-q>",QuitApp_hotkey)
    #textbox.bind_all("<Control-z>",undo_hotkey)
    #textbox.bind_all("<Control-Shift-z>",redo_hotkey)

    #About menu
    about=tk.Menu(top, tearoff=0)
    menubar.add_cascade(menu=about,compound="left", label="?")
    about.add_command(compound="left", label="Help", command=helpbox)
    #about.add_command(compound="left", label="About", command=aboutbox)

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

def ftp_open_hotkey(event):
    ftp_open()

def ftp_save_hotkey(event):
    ftp_save()

def ftp_save_same_name_hotkey(event):
    ftp_save_same_name()

def configure_hotkey(event):
    configure()

def QuitApp_hotkey(event):
    QuitApp()

def remote_select(event):
    global remote_selected
    remote_selected=remote_menu.get()

#FTP
def ftp_login():
    global ftp
    global FTPerror
    ftp = FTP()
    try:
        ftp.connect(server,int(port))
        ftp.login(username,password)
        ftp.cwd('/')
        FTPerror=False
    except:
        messagebox.showerror("FTP error", "Could not connect to the FTP server.")
    textbox.focus_set()

def ftp_browse_login():
    global ftp
    global FTPerror
    ftp = FTP()
    try:
        ftp.connect(server,int(port))
        ftp.login(username,password)
        ftp.cwd('/')
        FTPerror=False
    except:
        messagebox.showerror("FTP error", "Could not connect to the FTP server.")
        FTPerror=True


#Quit
def QuitApp():
    okcancel= messagebox.askokcancel("Quit?","Do you want to quit the app?",default="ok")
    if okcancel== True:
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

#FTP Open

def ftp_open_config():
    global configflag
    configflag='open'
    configure()

def ftp_open():
    global FTPerror
    global timestamp
    timestamp=time.strftime("%d/%m/%Y %H:%M:%S")
    if remote_selected==0:
        browse()
    else:
        webdav_open()

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
    
def webdav_browse():
    global browselist
    global browsewin
    global WebDAVerror
    browsewin=tk.Toplevel(top)
    browsewin.geometry("530x570")
    browsewin.resizable(0,0)
    browsewin.title("Browse WebDAV")
    browselist=Listbox(browsewin)
    browselist.place(x=15,y=15,height=500,width=500)
    #browsewin.bind("<<ListboxSelect>>",list_select)
    browsewin.bind('<Double-Button>', chdirs)
    #browsewin.protocol("WM_DELETE_WINDOW", QuitWebDAV)

    ok_button=Button(browsewin)
    ok_button.place(x=20,y=520, height=24,width=40)
    ok_button.configure(text="Open")
    ok_button.bind("<Button-1>",chdirs)
    cancel_button=Button(browsewin)
    cancel_button.place(x=70,y=520, height=24,width=45)
    cancel_button.configure(text="Cancel")
    cancel_button.bind("<Button-1>",ftp_cancel)

    """newfolder_button=Button(browsewin)
    newfolder_button.place(x=125,y=520, height=24,width=65)
    newfolder_button.configure(text="New folder")
    newfolder_button.bind("<Button-1>",new_folder)"""

    deletefile_button=Button(browsewin)
    deletefile_button.place(x=125,y=520, height=24,width=50)
    deletefile_button.configure(text="Delete")
    deletefile_button.bind("<Button-1>",delete_file)
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
    ok_button.bind("<Button-1>",ftp_save_file_call)
    cancel_button=Button(browsewin)
    cancel_button.place(x=70,y=554, height=24,width=45)
    cancel_button.configure(text="Cancel")
    cancel_button.bind("<Button-1>",ftp_cancel)
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


def chdirs_webdav():
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
    textbox.insert(INSERT,timestamp+'\n')
    
    textbox.focus_set()

def webdav_save_file():
    global filename
    if filename_entry.get!='':
        filename=filename_entry.get()
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
        print (savepath)
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
    else:
        messagebox.showerror("WebDAV error", "Filename not specified")

def webdav_save_same_name():
    global filename
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
        if filename[-4:]=='.txt':
            webdav.upload_file(savepath,"tempfile")
        else:
            webdav.upload_file(savepath+'.txt',"tempfile")
        tempfile.close()
        os.remove("tempfile")
        top.title("TinyJot - WebDAV: "+filename)
        textbox.focus_set()
 
def webdav_new_folder():
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
        webdav.clean(delfname)
        webdav_browsedir()

    
def chdirs(event):
    global filename
    global filename_entry
    global fname
    if remote_selected==1:
        chdirs_webdav()
    else:
        fname=browselist.get(browselist.curselection())

        fnamelength=len(fname)
        fnametemp=''
        for n in range (0,fnamelength):
            if fname[n]!='[' and fname[n]!=']':
                fnametemp=fnametemp+fname[n]
        fname=fnametemp
        curdir= ftp.pwd()
        filename=fname
        fname=curdir+'/'+fname
        try:
            size=ftp.size(fname)
            ftp_open_file(event)

        except:
            ftp.cwd(fname)
            browsedir()

def ftp_open_file(event):
    global filename
    try:
        size=ftp.size(filename)
     
        tempfile=open("tempfile",'wb')
        ftp.retrbinary('RETR %s' % filename, tempfile.write)
        tempfile.close()
        tempfile=open("tempfile",'r')
        top.title("TinyJot - FTP: "+filename)
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
        
        #text=tempfile.read()
        tempfile.close()
        os.remove("tempfile")

        if key!='':
            ciphertext=decrypt(text)
            text=ciphertext
        textbox.delete(1.0,END)
        textbox.insert(INSERT,text)
        textbox.insert(INSERT,'\n')
        textbox.insert(INSERT,timestamp+'\n')
        
        textbox.focus_set()
        ftp.quit()
        FTPerror=False
    except:
        #filenamelen=len(filename)
        #for n in range (0,filenamelen)
        if filename!='..':
            filename=filename[1:-1]
        ftp.cwd(filename)
        browsedir()

    
#FTP Save
def ftp_save():
    global FTPerror
    global timestamp
    global filename
    if remote_selected==0:
        browse_save()
    else:
        webdav_browse_save()

def ftp_save_file_call(event):
    ftp_save_file()

def ftp_save_file():
    global filename
    global key
    if remote_selected==0:
        if filename_entry.get!='':
            filename=filename_entry.get()
        if key!='':
            ciphertext=encrypt(text)
            text=ciphertext
        if filename!='':
            text=textbox.get(1.0,END)
            tempfile=open("tempfile",'w')
            tempfile.write(text)
            tempfile.close()
            tempfile=open("tempfile",'rb')
            if filename[-4:]=='.txt':
                ftp.storbinary('STOR '+filename,tempfile)
            else:
                ftp.storbinary('STOR '+filename+'.txt',tempfile)
            tempfile.close()
            os.remove("tempfile")
            top.title("TinyJot - FTP: "+filename)
            textbox.focus_set()
            ftp.quit()
            FTPerror=False
            browsewin.destroy()
        else:
            messagebox.showerror("FTP error", "Filename not specified")
    else:
        webdav_save_file()

def ftp_save_same_name():
    global filename
    if remote_selected==0:
        
        ftp_browse_login()
        if filename!='':
            text=textbox.get(1.0,END)
            tempfile=open("tempfile",'w')
            tempfile.write(text)
            tempfile.close()
            tempfile=open("tempfile",'rb')
            if filename[-4:]=='.txt':
                ftp.storbinary('STOR '+filename,tempfile)
            else:
                ftp.storbinary('STOR '+filename+'.txt',tempfile)
            tempfile.close()
            os.remove("tempfile")
            top.title("TinyJot - FTP: "+filename)
            textbox.focus_set()
            ftp.quit()
            FTPerror=False
    else:
        webdav_save_same_name()

def ftp_cancel(event):
    browsewin.destroy()

#FTP Browse

def browse_config():
    global configflag
    configflag='browse'
    configure()

def browse():
    global browselist
    global browsewin
    global FTPerror
    ftp_browse_login()
    if FTPerror==False:
        browsewin=tk.Toplevel(top)
        browsewin.geometry("530x570")
        browsewin.resizable(0,0)
        browsewin.title("Browse FTP")
        browselist=Listbox(browsewin)
        browselist.place(x=15,y=15,height=500,width=500)
        #browsewin.bind("<<ListboxSelect>>",list_select)
        browsewin.bind('<Double-Button>', chdirs)
        #browsewin.protocol("WM_DELETE_WINDOW", QuitFTP)

        ok_button=Button(browsewin)
        ok_button.place(x=20,y=520, height=24,width=40)
        ok_button.configure(text="Open")
        ok_button.bind("<Button-1>",chdirs)
        cancel_button=Button(browsewin)
        cancel_button.place(x=70,y=520, height=24,width=45)
        cancel_button.configure(text="Cancel")
        cancel_button.bind("<Button-1>",ftp_cancel)

        """newfolder_button=Button(browsewin)
        newfolder_button.place(x=125,y=520, height=24,width=65)
        newfolder_button.configure(text="New folder")
        newfolder_button.bind("<Button-1>",new_folder)"""

        deletefile_button=Button(browsewin)
        deletefile_button.place(x=125,y=520, height=24,width=50)
        deletefile_button.configure(text="Delete")
        deletefile_button.bind("<Button-1>",delete_file)

        browsedir()
    else:
        True

def browse_save():
    global browselist
    global browsewin
    global FTPerror
    global filename_entry
    ftp_browse_login()
    if FTPerror==False:
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
        ok_button.bind("<Button-1>",ftp_save_file_call)
        cancel_button=Button(browsewin)
        cancel_button.place(x=70,y=554, height=24,width=45)
        cancel_button.configure(text="Cancel")
        cancel_button.bind("<Button-1>",ftp_cancel)
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
        browsedir()
    else:
        True
    
def browsedir():
    fileyes=False
    dirlist=[]
    try:
        dirlist=ftp.nlst()
    except:
        messagebox.showerror("FTP error", "Could not connect to FTP server.")
    browselist.delete(0,END)
    browselist.insert(0,'..')
    for item in dirlist:
        namelength=len(item)
        for n in range (0,namelength):
            if item[n]=='.':
                fileyes=True
        if fileyes==False:
            item='['+str(item)+']'
        browselist.insert(0,item)
        fileyes=False
        

def list_select(event):
    global filename
    filename=browselist.get(browselist.curselection())


def new_folder(event):
    global filename_entry
    if remote_selected==0:
        dirname=filename_entry.get()

        if dirname != "":
            try:
                ftp.cwd(dirname)
            except:
                #cdTree("/".join(dirname.split("/")[:-1]))
                ftp.mkd(dirname)
                browsedir()
    else:
        webdav_new_folder()

def delete_file(event):
    if remote_selected==0:
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

def QuitFTP():
    ftp.quit()

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
    about_label.bind("<Button-1>", lambda e: callback("https://fonazzastent.com/"))

    url_title=Label(aboutbox)
    url_title.place(x=35,y=10,height=40,width=430)
    url_title.configure(text="TinyJot 1.2.6", font=("Arial",15), anchor='center')

    url_label=Label(aboutbox)
    url_label.place(x=35,y=152,height=15,width=430)
    url_label.configure(text="https://fonazzastent.com/", anchor='center')
    url_label.bind("<Button-1>", lambda e: callback("https://fonazzastent.com/"))

    url_label2=Label(aboutbox)
    url_label2.place(x=35,y=172,height=30,width=430)
    url_label2.configure(text="https://fonazzastent.com/ftp-enabled-notepad/", anchor='center')
    url_label2.bind("<Button-1>", lambda e: callback("https://fonazzastent.com/ftp-enabled-notepad/"))

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
    readme="TinyJot 1.3.0\n\
SymbolForm\n\
\n\
TinyJot is a basic notepad with FTP and WebDAV capabilities. It can open, edit and \
save text files on a local drive, or open, edit and save a text logfile \
on a remote FTP or WebDAV server.\n\
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
For remote files:\n\
\n\
- File - Remote Open (Alt-T), to open a file hosted on the remote server.\n\
- File – Remote Save (Alt-W), to save editing window content to a remote \
  File on the remote server.\n\
- File – Remote Save as (Alt-V), to save editing window content to a remote \
  file with a different name on the remote server.\n\
- File – Remote Configure (Alt-C), to configure the remote server settings.\n\
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
Every time you open a remote file, a timestamp will be automatically \
added at the end of the text contained in the editing window. You can \
start writing your next log entry below the timestamp.\n\
The program will not store the remote user password anywhere, so you will \
have to type it every time you use the program.\n\
\n\
The remote configuration parameters are stored in the config.ini file. Do \
not delete this file or the program will crash. You can also configure \
the remote server by editing the config.ini file, according to the following \
specifications:\n\
\n\
Row n.1: hostname (i.e. ftp.host.com)\n\
Row n.2: port (most of the times 21, unused for WebDAV)\n\
Row n. 3:  FTP or WebDav username (i.e. an email address or other username)\n\
Ron n. 4: font name\n\
Row n. 5 font size\n\
\n\
New in this version:\n\
- WebDAV support"
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
