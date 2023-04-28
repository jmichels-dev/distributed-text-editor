# distributed-text-editor
Initial ideas:

Files will live on the server. Client will send a download request to the server to open a new/existing file.
The server will respond by sending the filename and contents of the file, at which point the client will create
a local copy of it on their computer. 

Changes that the client makes to a file will be sent to the server, which will then be propagated to all 
clients who are currently editing the same file.

After the client is finished, they will log out, and the local copy
of the file will be deleted.

How to get POS tkinter to work on POS macOS: 

https://stackoverflow.com/questions/58400564/tcl-tk-tkinter-not-installing-via-homebrew-pyenv-on-macos-mojave


What needs to get done:

1) Get working for single client (wip)
    i. Open new .txt file (done)
    ii. Open existing .txt file
    iii. List all files on server
    iv. Exit file, saving copy to server
        a) maybe snapshot feature? 
    v. Logout feature
        a) save file changes on server
        b) client gracefully exits

2) Get working for multiple clients
    i. real time updates between two clients working on same doc (operational transformation algo)

--------- IF TIME -----------

3) Implement server replication

4) GPT-3 api?
