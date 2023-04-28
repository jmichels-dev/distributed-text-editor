import logging
import sys
from _thread import *
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import ctypes
import time

import grpc
import texteditor_pb2
import texteditor_pb2_grpc

import helpers

filetypes = [("Text Files", "*.txt")]

# Parse input from command line and do the correct action. Loops until logout or delete.
def commandLoop(stub):
    command = sys.stdin.readline().strip()
    # User wants to open new .txt file
    if command == 'O' or command == 'o':
        new_filename = ""
        while True:
            new_filename = input("Enter a name for the new file. \n Filename: ")
            # Insert check if filename is valid here?
            break
        # Send sender username, recipient username, and message to the server & store confirmation response
        fileResponse = stub.OpenNewFile(texteditor_pb2.Download(filename=new_filename))
        print(fileResponse.errorFlag)
        if fileResponse.errorFlag:
            print("Error: Filename already exists.")
        else:
            launchGUI(fileResponse.filename)

    # User wants to open existing.txt file
    if command == 'E' or command == 'e':
        existing_filename = ""
        while True:
            existing_filename = input("Enter existing file name. (omit file type) \n Filename: ")
            # Insert check if filename is valid here?
            break
        # Send sender username, recipient username, and message to the server & store confirmation response
        fileResponse = stub.OpenExistingFile(texteditor_pb2.Download(filename=existing_filename))
        # if fileResponse.errorFlag:
        #     print("Error: Filename already exists.")
        # else:
        with open(existing_filename + ".txt", "wb") as f:
            for response in fileResponse:
                f.write(response.contents)
        launchGUI(fileResponse.filename)

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

def launchGUI(filename):
    appName = "Distributed Text Editor"
    
    window = tk.Tk()
    window.title(appName + " - " + filename)
    window.geometry('500x400')
    window.grid_columnconfigure(0, weight=1)

    txt = scrolledtext.ScrolledText(window, height=999)
    txt.grid(row=1,sticky=tk.N+tk.S+tk.E+tk.W)
    #txt.bind("<KeyPress>", textchange(window, appName, ))

    menu = tk.Menu(window)
    fileDropdown = tk.Menu(menu, tearoff=False)
    fileDropdown.add_command(label="Open", command=lambda: fileDropdownHandler("open", filename, window, appName, txt))
    fileDropdown.add_separator()
    fileDropdown.add_command(label="Save", command=lambda: fileDropdownHandler("save", filename, window, appName, txt))
    fileDropdown.add_command(label="Save as", command=lambda: fileDropdownHandler("saveAs", filename, window, appName, txt))
    menu.add_cascade(label="File", menu=fileDropdown)

    window.config(menu=menu)

    window.mainloop()

# prolly will get rid of this
def textchange(window, appName, event, filename):
    window.title(appName + " -*" + filename)

def fileDropdownHandler(action, filename, window, appName, txt):
    if action == "open":
        file = filedialog.askopenfilename(filetypes=filetypes)
        window.title(appName + " - " + filename)
        currentFilePath = file
        with open(file, 'r') as f:
            txt.delete(1.0, tk.END)
            txt.insert(tk.INSERT,f.read())
    elif action == "save" or action == "saveAs":
        if currentFilePath == "New File" or action == "saveAs":
            currentFilePath = filedialog.asksaveasfilename(filetypes=filetypes)
        with open(currentFilePath, "w") as f:
            f.write(txt.get("1.0", "end"))
        window.title(appName + " - " + currentFilePath)
        

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
