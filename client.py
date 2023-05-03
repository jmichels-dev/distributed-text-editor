import logging
import sys
from _thread import *
from tkinter import *
from tkinter import ttk
from tk_sandbox import EditorGUI
import ctypes
import time
import threading
import os

import grpc
import texteditor_pb2
import texteditor_pb2_grpc
import constants
import helpers        


def signinLoop(stub):
        print("Please enter screen name")
        username = input("Screen name: ")
        # Username error check
        if helpers.isValidUsername(username):
            # Remove whitespace
            username = username.strip().lower()
            unreadsOrError = stub.SignInExisting(texteditor_pb2.Username(name=username))
            eFlag, msg = unreadsOrError.errorFlag, unreadsOrError.unreads
        if eFlag:
            print(msg)
            return signinLoop(stub)
        else:
            print(msg)
            return username

# Listens for messages from server's Listen response stream. Closes when user logs out or deletes acct.
def listen_thread(stub, responseStream, editor):
    while True:
        print("listening...")
        try:
            response = next(responseStream)
            print(response.filename)
            with open("./usertextfiles/" + response.filename, "wb") as f:
                f.write(response.contents)
            editor.update_file(filename, response.contents.decode('utf-8'))
        except:
            return

# Listens for deletes from server
def delete_thread(stub, deleteStream):
    while True:
        # try:
        response = next(deleteStream)
        # print(response.filename)
        os.remove("./usertextfiles/" + response.filename)
        # except:
        #     print("Error deleting", response.filename)


def run(server_id):
    # ip and port of the current primary
    primary_ip = constants.IP_PORT_DICT[server_id][0]
    primary_port = constants.IP_PORT_DICT[server_id][1]
    with grpc.insecure_channel('{}:{}'.format(primary_ip, primary_port)) as channel:
        stub = texteditor_pb2_grpc.TextEditorStub(channel)
        username = signinLoop(stub)
        print("Congratulations! You have connected to the collaborative file editing server.\n")
        editor = EditorGUI(stub)
        responseStream = stub.Listen(texteditor_pb2.Username(name=username))
        deleteStream = stub.ListenForDeletes(texteditor_pb2.Username(name=username))
        start_new_thread(listen_thread, (stub, responseStream, editor))
        start_new_thread(delete_thread, (stub, deleteStream))


        # while True:
            # Establish response stream to receive messages from server.
            # responseStream is a generator of texteditor_pb2.??? objects.
            # Wait for input from command line


if __name__ == '__main__':
    logging.basicConfig()
    # Checks for correct number of args
    if len(sys.argv) != 2:
        print("Correct usage: script, primary_server_id")
        exit()
    server_id = int(sys.argv[1])
    run(server_id)
