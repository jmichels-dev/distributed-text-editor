import logging
import sys
from _thread import *
from tkinter import *
from tkinter import ttk
from tk_sandbox import EditorGUI
import ctypes
import time

import grpc
import texteditor_pb2
import texteditor_pb2_grpc

import helpers        

# Listens for messages from server's Listen response stream. Closes when user logs out or deletes acct.
def listen_thread(username, stub, responseStream):
    while True:
        try:
            response = next(responseStream)
            print(response.msg)
        except:
            return

def run():
    # ip = '10.250.226.222'
    ip = '10.250.64.41'
    port = '8080'
    with grpc.insecure_channel('{}:{}'.format(ip, port)) as channel:
        stub = texteditor_pb2_grpc.TextEditorStub(channel)
        print("Congratulations! You have connected to the collaborative file editing server.\n")
        
        editor = EditorGUI(stub)

        print("is this blocking?")
        # while True:
            # Establish response stream to receive messages from server.
            # responseStream is a generator of texteditor_pb2.??? objects.
            # Wait for input from command line


if __name__ == '__main__':
    logging.basicConfig()
    run()
