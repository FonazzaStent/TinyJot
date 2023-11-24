"""TinyJot 1.1.8 - An FTP-enabled notepad.
Copyright (C) 2023  Fonazza-Stent

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

import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import io
from ftplib import FTP
import time
import stat
from tkinter import messagebox


password=''
FTPerror=False
configflag='open'
#read config file

def read_config():
    global txtfilename
    global server
    global port
    global username
    global logfile
    global logdir
    txtfilename=''
    parameters=[]
    if os.path.isfile('config.ini'):
        configfile=open("config.ini",'r')
    else:
        parameterstring='ftp.host.com\n21\nname@email.com\nlog.txt\n/'
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
    logfile=parameters[3]
    logdir=parameters[4]

#create main window
def create_main_window():
        global top
        global root
        img=b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABhGlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9bpVJbHOxQxCFDdbKLiuhWqlgEC6Wt0KqDyaVf0KQhSXFxFFwLDn4sVh1cnHV1cBUEwQ8QVxcnRRcp8X9JoUWMB8f9eHfvcfcO8LZqTDH64oCimnommRDyhVXB/4pBRBDAHEIiM7RUdjEH1/F1Dw9f72I8y/3cnyMkFw0GeATiONN0k3iDeGbT1DjvE4dZRZSJz4kndLog8SPXJYffOJdt9vLMsJ7LzBOHiYVyD0s9zCq6QjxNHJUVlfK9eYdlzluclVqDde7JXxgsqitZrtMcRRJLSCENARIaqKIGEzFaVVIMZGg/4eIfsf1pcknkqoKRYwF1KBBtP/gf/O7WKE1NOknBBND/YlkfY4B/F2g3Lev72LLaJ4DvGbhSu/56C5j9JL3Z1aJHwNA2cHHd1aQ94HIHiDxpoi7ako+mt1QC3s/omwrA8C0QWHN66+zj9AHIUVfLN8DBITBepux1l3cP9Pb275lOfz/a3nLQoKjLugAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB+cLGAsGCHE8D64AAAAZdEVYdENvbW1lbnQAQ3JlYXRlZCB3aXRoIEdJTVBXgQ4XAAADU0lEQVRYw8VXv0srQRD+9jxPDUZzjSiKPwpRjhQiCinUQjBYWJpKK/8CiysFrbRLYyHYigpqY6OoaKUmxBSGEBIjBIkQUniYC/G8EO/2FQ+XRJO8BE7fBwc7u8POx+w3wxyhlFL8R3CVDiil2NraYvbd3R0SiQSzi8/C4TCi0Sizt7e32ToSiSAUClUkwFcjEA6HmZ3L5dDU1MTsYjKapqGxsZHZyWSSrRVFAc/ztWcgFothYWEBx8fH6OzsxPr6OgghUFUVj4+PIITg8PCQZYEQAkVRkEgkQAjBzs4Okskk9vf3QQhBLpdDKpWCJEnY3d2FYRiVCeTzeSwtLWFvb4/tEUIAAIIg4FMu5WRTSUqEEFBKEY1Gsbi4CL/fX/kJMpkMfD4fs9/f38FxXNkAhmEwcl/P2tvbS/yKkUqlahPh/f09ZmZmEAwGAQCFQgFvb28AgGAwiLm5Odze3jKin4F8Ph/m5+dxfX0NAMhms4xoJbExpNNpCuBHv4ODg+KQtKw8V1ZW0NzcbHnN39zc1FaGsiyjra3N0uCEEGxubtbeiP57J/wt8LU4vb6+4urqiqmZEILp6emScvtRAi8vL9B1HePj4wAAVVXh9XqxvLzM+sRXCIKAlpYWawh8tujieh4aGsLp6WlF/3g8jrW1NesIuN1uTE5O1pzajY0N657gK05OTuBwONDa2opQKAS3243Ly0tMTEygt7f356tA0zSMjIxAkiR0dXWB53kMDg7i4eHhd8owm80inU6XaCIQCGB0dPTnCRiGgY6ODvT398M0TXAcB9M04XK5IIoi6p3w6tIApRSUUszOzsI0TRBCMDU1BUIIRFGEaZp/L+V5awlwHIezs7OSUetfyOfz1hEYGBiALMvf9lVVxfn5OTweT9lGZGkGHA7Ht/2npyc8Pz9DEATYbDZrW3Emk2HTUDkUCgVEIhF4PB54vV64XK6KvqIoYmxsrD4CNpsNw8PDFS/9+PiA3+9HLBaDJElVfYvH+ZoJCIKAnp6equmTZRmKoqCvr6/63Gd1K/6E3W6H3W63biBpaGioq4Tqhaqq33oE+fpzurq6ing8DqfTaWlwXddxdHSEi4uLkqf9RkDXdQQCAWiaZvlQ6nQ60d3dXT0Dv40/vEGOjum+NckAAAAASUVORK5CYII='
        root= tk.Tk()
        top= root
        top.geometry("600x450+468+138")
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
    configwin=tk.Toplevel(top)
    configwin.geometry("493x250")
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
    logfile_label=Label(configwin)
    logfile_label.place(x=50,y=135,height=21,width=34)
    logfile_label.configure(text="File")
    y = tk.StringVar()
    y.set(logfile)
    logfile_entry=Entry(configwin,textvariable=y)
    logfile_entry.place(x=90,y=135,height=20,width=384)
    logdir_label=Label(configwin)
    logdir_label.place(x=50,y=165,height=21,width=34)
    logdir_label.configure(text="Path")
    z = tk.StringVar()
    z.set(logdir)
    logdir_entry=Entry(configwin,textvariable=z)
    logdir_entry.place(x=90,y=165,height=20,width=384)    
    pw_button=Button(configwin)
    pw_button.place(x=210,y=200, height=24,width=47)
    pw_button.configure(text="Save")
    pw_button.bind("<Button-1>",get_config)
    cancel_button=Button(configwin)
    cancel_button.place(x=290,y=200, height=24,width=47)
    cancel_button.configure(text="Cancel")
    cancel_button.bind("<Button-1>",config_cancel)
    pw_entry.focus_set()

def get_config(event):
    global password
    global configflag
    password=pw_entry.get()
    server=host_entry.get()
    port=port_entry.get()
    username=user_entry.get()
    logfile=logfile_entry.get()
    logdir=logdir_entry.get()
    configfile=open("config.ini",'w')
    configfile.writelines(server+"\n")
    configfile.writelines(port+"\n")
    configfile.writelines(username+"\n")
    configfile.writelines(logfile+"\n")
    configfile.writelines(logdir+"\n")
    configfile.close()
    configwin.destroy()
    read_config()
    if configflag=='open':
        ftp_open()
    if configflag=='browse':
        try:
            browsewin.destroy()
            browse()
        except:
            browse()


def config_cancel(event):
    configwin.destroy()

#Textbox
def create_textbox():
        global textbox
        textbox = Text(top)
        textbox.place(relx=0.033, rely=0.022, relheight=0.878, relwidth=0.933)
        scroll_1=Scrollbar (top)
        scroll_1.pack(side=RIGHT, fill=Y)
        textbox.configure(yscrollcommand=scroll_1.set,wrap=WORD)
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
    sub_menu.add_command(compound="left",label="Save As", command=Save_to_file,accelerator="Alt+A")
    sub_menu.add_command(compound="left",label="FTP Open", command=ftp_open_config,accelerator="Alt+T")
    sub_menu.add_command(compound="left",label="FTP Save", command=ftp_save,accelerator="Alt+V")
    sub_menu.add_command(compound="left",label="FTP Browse", command=browse_config,accelerator="Alt+B")
    sub_menu.add_command(compound="left",label="Quit", command=QuitApp,accelerator="Alt+Q")
    menubar.add_cascade(menu=edit_menu,compound="left", label="Edit")
    edit_menu.add_command(compound="left",label="Copy", command=copy_code)
    edit_menu.add_command(compound="left",label="Paste", command=paste_code)
    menubar.bind_all("<Alt-f>",menubar.invoke(1))
    top.bind_all("<Alt-n>",new_hotkey)
    top.bind_all("<Alt-o>",open_hotkey)
    top.bind_all("<Alt-s>",save_hotkey)
    top.bind_all("<Alt-a>",Save_to_file_hotkey)
    top.bind_all("<Alt-t>",ftp_open_hotkey)
    top.bind_all("<Alt-v>",ftp_save_hotkey)
    top.bind_all("<Alt-b>",browse_hotkey)
    top.bind_all("<Alt-q>",QuitApp_hotkey)

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

def configure_hotkey(event):
    configure()

def QuitApp_hotkey(event):
    QuitApp()



#FTP
def ftp_login():
    global ftp
    global FTPerror
    ftp = FTP()
    try:
        ftp.connect(server,int(port))
        ftp.login(username,password)
        ftp.cwd(logdir)
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
        ftp.cwd(logdir)
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

#CopyContextMenu
def create_context_menu():
    global menu
    menu = Menu(root, tearoff = 0)
    menu.add_command(label="Copy", command=copy_text)
    menu.add_command(label="Paste", command=paste_text)
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

#New file
def new_file():
    global txtfilename
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
        txtfile=open(txtfilename,'r', encoding="utf-8")
        text=txtfile.read()
        textbox.insert(INSERT,text)
    filename=os.path.basename(txtfilename).split('/')[-1]
    top.title("TinyJot - "+filename)
    textbox.focus_set()

#Save
def Save():
    global txtfilename
    text=textbox.get(1.0,END)
    if str(txtfilename)!='':
        txtfilesave=open(txtfilename,'w', encoding="utf-8")
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
    try:
        ftp_login()
        timestamp=time.strftime("%d/%m/%Y %H:%M:%S")
        filename=logfile
        
        try:
            tempfile=open("tempfile",'wb')
            ftp.retrbinary('RETR %s' % filename, tempfile.write)
            tempfile.close()
        except:
            tempfile=open("tempfile",'wb')
            tempfile.close()
            tempfile=open("tempfile",'r',encoding="utf-8")
            ftp.storbinary("STOR " + filename, tempfile)
            tempfile.close()
        tempfile=open("tempfile",'r')
        text=tempfile.read()
        tempfile.close()
        os.remove("tempfile")
        textbox.delete(1.0,END)
        textbox.insert(INSERT,text)
        textbox.insert(INSERT,'\n')
        textbox.insert(INSERT,timestamp+'\n')
        top.title("TinyJot - FTP: "+logfile)
        textbox.focus_set()
        ftp.quit()
        FTPerror=False
    except Exception as e:
        messagebox.showerror("FTP error", "Could not connect to the FTP server.")

    
#FTP Save
def ftp_save():
    global FTPerror
    try:
        ftp_login()
        text=textbox.get(1.0,END)
        tempfile=open("tempfile",'w')
        tempfile.write(text)
        tempfile.close()
        tempfile=open("tempfile",'rb')
        filename=logfile
        ftp.storbinary('STOR '+filename,tempfile)
        tempfile.close()
        os.remove("tempfile")
        top.title("TinyJot - FTP: "+logfile)
        textbox.focus_set()
        ftp.quit()
        FTPerror=False
    except Exception as e:
        messagebox.showerror("FTP error", "Could not connect to FTP server.")

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
        browsewin.bind("<<ListboxSelect>>",chdirs)
        #browsewin.protocol("WM_DELETE_WINDOW", QuitFTP)
        browsedir()
    else:
        True


    
def browsedir():
    dirlist=[]
    try:
        dirlist=ftp.nlst()
    except:
        messagebox.showerror("FTP error", "Could not connect to FTP server.")
    browselist.delete(0,END)
    browselist.insert(0,'..')
    for item in dirlist:
        browselist.insert(0,item)
        
def chdirs(event):
    fname=browselist.get(browselist.curselection())
    fname='/'+fname
    try:
        size=ftp.size(fname)
    except:
        ftp.cwd(fname)
        browsedir()

def QuitFTP():
    ftp.quit()

#text modified
def text_modified(event):
    global txtfilename
    filename=os.path.basename(txtfilename).split('/')[-1]
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
			txtfile=open(txtfilename,'r',encoding="utf-8")
			text=txtfile.read()
			textbox.insert(INSERT,text)
		filename=os.path.basename(txtfilename).split('/')[-1]
		top.title("TinyJot - "+filename)
		textbox.focus_set()
	except:
		True


def main():
        read_config()
        create_main_window()
        create_textbox()
        create_menu()
        create_context_menu()
        startup()
        
main()
root.mainloop()
