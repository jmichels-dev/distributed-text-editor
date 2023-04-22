import logging
import sys
from _thread import *
import time

import grpc
import texteditor_pb2
import texteditor_pb2_grpc

# import helpers_grpc

# Parse input from command line and do the correct action. Loops until logout or delete.
def commandLoop(stub):
    command = sys.stdin.readline().strip()
    # User wants to send a message
    if command == 'O' or command == 'o':
        new_filename = ""
        while True:
            new_filename = input("Enter a name for the new file. \n Filename: ")
            # Insert check if filename is valid here?
            break
        # Send sender username, recipient username, and message to the server & store confirmation response
        senderResponse = stub.OpenNewFile(texteditor_pb2.Download(filename=new_filename))
        print(senderResponse.msg)
        print("Command:")
    # # User wants to list users
    # if command == 'L' or command == 'l':
    #     wildcard = input("Optional text wildcard: ")
    #     if wildcard == "":
    #         wildcard = "*"
    #     listResponse = stub.List(texteditor_pb2.Payload(msg=wildcard))
    #     print("Fetching users... \n")
    #     print(listResponse.msg)
    #     print("Command:")
    # # User wants to log out
    # if command == 'O' or command == 'o':
    #     logoutResponse = stub.Logout(texteditor_pb2.Username(name=username))
    #     print("Logging out...")
    #     time.sleep(0.2)
    #     print(logoutResponse.msg)
    #     time.sleep(0.2)
    #     return
    commandLoop(stub)

# Listens for messages from server's Listen response stream. Closes when user logs out or deletes acct.
def listen_thread(username, stub, responseStream):
    while True:
        try:
            response = next(responseStream)
            print(response.msg)
        except:
            return

def run():
    ip = '10.250.226.222'
    port = '8080'
    with grpc.insecure_channel('{}:{}'.format(ip, port)) as channel:
        stub = texteditor_pb2_grpc.TextEditorStub(channel)
        print("Congratulations! You have connected to the chat server.\n")

        while True:
            # Now, the user is logged in. Notify the user of possible functions
            print("If any messages arrive while you are logged in, they will be immediately displayed.\n")
            print("Use the following commands to interact with the chat app: \n")
            print(" -----------------------------------------------")
            print("|L: List all files that exist on this server.   |")
            print("|O: Open a new file.                            |")
            print("|E: Open an existing file.                      |")
            print(" ----------------------------------------------- \n")
            print("Command: ")
            # Establish response stream to receive messages from server.
            # responseStream is a generator of chat_pb2.Payload objects.
            # Wait for input from command line
            commandLoop(stub)


if __name__ == '__main__':
    logging.basicConfig()
    run()
