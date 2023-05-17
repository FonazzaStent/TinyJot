TinyJot 1.1.3
TinyJot is a basic notepad with FTP capabilities. It can open, edit and save text files on a local drive, or 
open, edit and save a text logfile on a remote FTP server.

For local files:

- File – Open (Alt-O), to open a text file
- File – New (Alt-N), to start a new text file
- File – Save (Alt-S), to save a file currently being edited
- File – Save As (Alt-A), to save a file with a new name
- File – Quit (Alt-Q), to quit the program
- Edit – Copy, to copy text
- Edit – Paste, to paste text

For remote FTP logfiles:

Edit the config.txt file with the FTP server parameters according to the following specifications:

- Row n. 1: hostname (i.e. ftp.host.com)
- Row n. 2: FTP username (i.e. your email or other username)
- Row n. 3: file name for the text logfile (i.e. log.txt)
- Row n. 4: path on the FTP server where the logfile is stored (i.e. /folder/subfolder, / for root)

Start the program. A window will appear and prompt you for a password. Input here the FTP user password.

- File - FTP Open (Alt-T), to open the remote logfile specified in the config.txt file (if it exists)
- File – FTP Save (Alt-V), to save editing window content to the remote logfile specified in the config.txt file
- File - FTP Password (Alt-P), to input FTP user password 

Every time you open a remote file, a timestamp will be automatically added at the end of the text contained
in the editing window. You can start writing your next log entry below the timestamp.
The program will not save the FTP user password anywhere, so you will have to type it every time you
use the program.
