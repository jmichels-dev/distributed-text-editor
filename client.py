import logging
import sys
from _thread import *
from tkinter import *
from tkinter import ttk
from tk_sandbox import EditorGUI
import ctypes
import time
import threading

import grpc
import texteditor_pb2
import texteditor_pb2_grpc

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
def listen_thread(stub, responseStream):
    while True:
        print("listening...")
        try:
            response = next(responseStream)
            print(response.filename)
            with open("./usertextfiles/" + response.filename, "wb") as f:
                while True:
                    f.write(response.contents)
        except:
            return

def run():
    ip = '10.250.226.222'
    #ip = '127.0.0.1'
    port = '8080'
    with grpc.insecure_channel('{}:{}'.format(ip, port)) as channel:
        stub = texteditor_pb2_grpc.TextEditorStub(channel)
        username = signinLoop(stub)
        print("Congratulations! You have connected to the collaborative file editing server.\n")

        responseStream = stub.Listen(texteditor_pb2.Username(name=username))
        start_new_thread(listen_thread, (stub, responseStream))

        editor = EditorGUI(stub)

        print("is this blocking?")
        # while True:
            # Establish response stream to receive messages from server.
            # responseStream is a generator of texteditor_pb2.??? objects.
            # Wait for input from command line


if __name__ == '__main__':
    logging.basicConfig()
    run()
