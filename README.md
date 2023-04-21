# distributed-text-editor
Initial ideas:

Files will live on the server. Client will send a download request to the server to open a new/existing file.
The server will respond by sending the filename and contents of the file, at which point the client will create
a local copy of it on their computer. 

Changes that the client makes to a file will be sent to the server, which will then be propagated to all 
clients who are currently editing the same file.

After the client is finished, they will log out, and the local copy
of the file will be deleted.