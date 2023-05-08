# distributed-text-editor
In /grpc: A 3-fault tolerant distributed collaborative text editor and file sharing system using gRPC

Sections:
1. Setup (pull from github, required libraries, etc.)
2. Startup
4. Operation - gRPC

-----------------------------------------------------------------------------------------------------------------------------------------------
Overview.

A program which allows multiple users to edit the same document at the same time from a Tkinter GUI, similar to Google Docs. It is distributed because a scalable number of clients can connect to a 3-fault tolerant system of servers which holds all of the documents with persistent storage. 

-----------------------------------------------------------------------------------------------------------------------------------------------
1. Setup

The files for this application are stored in a public GitHub repo, which can be accessed at https://github.com/jmichels-dev/distributed-text-editor.
To get the files from this repository to your local machine, run the following command in the terminal when in the desired location for the files 
to be downloaded to:

    git clone https://github.com/jmichels-dev/distributed-text-editor

Now, you should have all of the files necessary to run the application.

gRPC install and setup instructions can be found in the gRPC documentation Python Quick Start guide: 
https://grpc.io/docs/languages/python/quickstart/. This will require installation of grpcio and grpcio-tools using pip or anaconda.

-----------------------------------------------------------------------------------------------------------------------------------------------
2. Startup

We first want to start up the server. To do this, edit the IP addresses in constants.py to match your machine(s). The constants use the following conventions: the four servers in the system use ids 0, 1, 2, 3, respectively. To start the primary server (at id 0), run:

    python server.py 0

If you are running the application on just one machine, use IP address 127.0.0.1 (localhost). Otherwise, look up your IPv4 (on Mac, Settings -> Network -> Advanced -> TCP/IP, listed as IPv4), start the server using this address, and give this address to each client that wishes to connect to the system. Only use this system with trusted machines because file editing can change the contents of files on other clients' machines. As for the port number, 8080, 8081, and 8082 are usually available. 

To start backup servers, specify the id of the backup server as the first argument and the primary server id as the second argument, e.g.

    python backups.py 1 0
    python backups.py 2 0
    python backups.py 3 0

Now that the servers are running, clients can begin to connect to the primary. The argument should match the primary server:

    python client.py 0
    
Congratulations! At this point, the client should connect to the server and recieve a welcome message. After inputing a username, the GUI will open and you will be able to edit, save, and delete files in the usertextfiles folder, which is shared by all clients. Replication ensures persistent state and system fault tolerance, but when the primary server fails, clients still need to terminate and connect to the new primary server. An extension of this project could implement a GUI which abstracts client reconnections so the user experience is uninterrupted.
