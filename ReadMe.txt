TinyJot 1.3.1

TinyJot is a basic notepad with FTP and WebDAV capabilities. It can open,
 edit and save text files on a local drive, or open, edit and save a text
file on a remote FTP or WebDAV server.

For local files:

- File – Open (Alt-O), to open a text file
- File – New (Alt-N), to start a new text file
- File – Save (Alt-S), to save a file currently being edited
- File – Save As (Alt-A), to save a file with a new name
- File – Quit (Alt-Q), to quit the program
- Edit – Copy, to copy text
- Edit – Paste, to paste text

For remote files:

- File - remote Open (Alt-T), to open a file hosted on the remote server.
- File – remote Save (Alt-W), to save editing window content to a remote
  File on the remote server.
- File – remote Save as (Alt-V), to save editing window content to a
  file with a different name on the remote server.
- File – remote Configure (Alt-C), to configure the remote server
  settings.

Encrypt and decrypt files
- File - Encrypt/Decrypt, input a password to encrypt or decrypt
  files. First you input a password, then you open the encrypted file.
- To encrypt a file, first input a password, then save the file.
- Changing the password while editing, will save the file with the
  new password when saving.

Alt-F to open the command menu.

- Edit – Font to choose font and font size. Bold, italic, underlined are
  not allowed

The program will not store the remote user password anywhere, so you will
have to type it every time you use the program.

The remote configuration parameters are stored in the config.ini file. Do
not delete this file or the program will crash. You can also configure
the remote server and the font by editing the config.ini file, according
to the following specifications:

Row n.1: hostname (i.e. ftp.host.com)
Row n.2: port (most of the times 21, unused for WebDAV)
Row n. 3:  FTP or WebDAV username (i.e. an email address or other username)
Ron n. 4: font name
Row n. 5 font size

New in this version:
- Timestamp menu item added
