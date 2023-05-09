"""TinyJot 1.0.0 - A very basic notepad.
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


txtfilename=''

#create main window
def create_main_window():
        global top
        global root
        img=b'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'
        root= tk.Tk()
        top= root
        top.geometry("600x450+468+138")
        top.title("TinyJot")
        favicon=tk.PhotoImage(data=img) 
        root.wm_iconphoto(True, favicon)

#Textbox
def create_textbox():
        global textbox
        textbox = Text(top)
        textbox.place(relx=0.033, rely=0.022, relheight=0.878, relwidth=0.933)
        scroll_1=Scrollbar (top)
        scroll_1.pack(side=RIGHT, fill=Y)
        textbox.configure(yscrollcommand=scroll_1.set)
        scroll_1.configure(command=textbox.yview)
        textbox.bind("<Key>", text_modified)

#menu
def create_menu():
    menubar=tk.Menu(top, tearoff=0)
    top.configure(menu=menubar)
    sub_menu=tk.Menu(top, tearoff=0)
    edit_menu=tk.Menu(top,tearoff=0)
    menubar.add_cascade(menu=sub_menu,compound="left", label="File")
    sub_menu.add_command(compound="left",label="New", command=new_file)
    sub_menu.add_command(compound="left",label="Open", command=open_file)
    sub_menu.add_command(compound="left",label="Save", command=Save)
    sub_menu.add_command(compound="left",label="Save As", command=Save_to_file)
    sub_menu.add_command(compound="left",label="Quit", command=QuitApp)
    menubar.add_cascade(menu=edit_menu,compound="left", label="Edit")
    edit_menu.add_command(compound="left",label="Copy", command=copy_code)
    edit_menu.add_command(compound="left",label="Paste", command=paste_code)

#Quit
def QuitApp():
    top.destroy()

#Copy Code
def copy_code():
    textbox.tag_add(SEL, "1.0", END)
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


#Open file
def open_file():
    global txtfile
    global txtfilename
    data=[('Text', '*.txt')]
    txtfilename=askopenfilename(filetypes=data)
    if str(txtfilename)!='':
        textbox.delete(1.0,END)
        txtfile=open(txtfilename,'rb')
        text=txtfile.read()
        textbox.insert(INSERT,text)
    filename=os.path.basename(txtfilename).split('/')[-1]
    top.title("TinyJot - "+filename)

#Save
def Save():
    global txtfilename
    text=textbox.get(1.0,END)
    if str(txtfilename)!='':
        txtfilesave=open(txtfilename,'w')
        txtfilesave.write(text)
        txtfilesave.close()
        filename=os.path.basename(txtfilename).split('/')[-1]
        top.title("TinyJot - "+filename)


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

#text modifies
def text_modified(event):
    global txtfilename
    filename=os.path.basename(txtfilename).split('/')[-1]
    top.title("TinyJot - "+filename+"*")


def main():
        create_main_window()
        create_textbox()
        create_menu()
        create_context_menu()
        
main()
root.mainloop()
