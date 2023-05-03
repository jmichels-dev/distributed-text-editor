import logging
import sys
from _thread import *
from tkinter import *
from tkinter import ttk
from tk_sandbox import EditorGUI
import ctypes
import threading

import grpc
import texteditor_pb2
import texteditor_pb2_grpc
import constants
import helpers        


# def update_file(filename, contents, edit):
#     print("Hello")
#     edit.update_file(filename, contents)



def run(server_id):
    # ip and port of the current primary
    primary_ip = constants.IP_PORT_DICT[server_id][0]
    primary_port = constants.IP_PORT_DICT[server_id][1]
    with grpc.insecure_channel('{}:{}'.format(primary_ip, primary_port)) as channel:
        stub = texteditor_pb2_grpc.TextEditorStub(channel)
        

        editor = EditorGUI(stub)


if __name__ == '__main__':
    logging.basicConfig()
    # Checks for correct number of args
    if len(sys.argv) != 2:
        print("Correct usage: script, primary_server_id")
        exit()
    server_id = int(sys.argv[1])
    run(server_id)
