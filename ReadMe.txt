TinyJot 1.2.5

TinyJot is a basic notepad with FTP capabilities. It can open, edit and
save text files on a local drive, or open, edit and save a text logfile
on a remote FTP server.

For local files:

- File – Open (Alt-O), to open a text file
- File – New (Alt-N), to start a new text file
- File – Save (Alt-S), to save a file currently being edited
- File – Save As (Alt-A), to save a file with a new name
- File – Quit (Alt-Q), to quit the program
- Edit – Copy, to copy text
- Edit – Paste, to paste text

For remote FTP logfiles:

- File - FTP Open (Alt-T), to open a file hosted on the FTP server.
- File – FTP Save (Alt-W), to save editing window content to a remote
  File on the FTP server.
- File – FTP Save as (Alt-V), to save editing window content to a remote
  file with a different name on the FTP server.
- File – FTP Configure (Alt-C), to configure the FTP server settings.

Alt-F to open the command menu.

Every time you open a remote file, a timestamp will be automatically
added at the end of the text contained in the editing window. You can
start writing your next log entry below the timestamp.
The program will not store the FTP user password anywhere, so you will
have to type it every time you use the program.

The FTP configuration parameters are stored in the config.ini file. Do
not delete this file or the program will crash. You can also configure
the FTP server by editing the config.ini file, according to the following
specifications:

Row n.1: hostname (i.e. ftp.host.com)
Row n.2: port (most of the times 21)
Row n. 3:  FTP username (i.e. an email address or other username)

New in this version:
- Bugs fixed
