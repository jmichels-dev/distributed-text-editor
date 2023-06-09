import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from _thread import *
import os

import grpc
import texteditor_pb2
import texteditor_pb2_grpc
import helpers

"""Starter code source: realpython.com/python-gui-tkinter/#building-a-text-editor-example-app"""

class EditorGUI():
    def __init__(self, stub):
        """Run text editor GUI and save key attributes"""
        self.stub = stub

        self.window = tk.Tk()
        self.window.title("Distributed Collaborative Text Editor - New File")
        self.title = "Distributed Collaborative Text Editor - New File"
        self.new_file_flag = True
        self.window.rowconfigure(0, minsize=800, weight=1)
        self.window.columnconfigure(1, minsize=800, weight=1)
        
        self.txt_edit = tk.Text(self.window, font=("Helvetica", 16))
        frm_buttons = tk.Frame(self.window, relief=tk.RAISED, bd=2)
        btn_new = tk.Button(frm_buttons, text="New File", command=self.new_file)
        btn_open = tk.Button(frm_buttons, text="Open...", command=self.open_file)
        btn_save = tk.Button(frm_buttons, text="Save", command=self.save)
        btn_saveas = tk.Button(frm_buttons, text="Save As...", command=self.save_as)
        self.btn_delete = tk.Button(frm_buttons, text="Delete", command=self.delete, state="disabled", disabledforeground="black")

        btn_new.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_open.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_save.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        btn_saveas.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.btn_delete.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        frm_buttons.grid(row=0, column=0, sticky="ns")
        self.txt_edit.grid(row=0, column=1, sticky="nsew")

        username = self.signinLoop(stub)
        print("Congratulations! You have connected to the collaborative file editing server.\n")

        responseStream = stub.Listen(texteditor_pb2.Username(name=username))
        deleteStream = stub.ListenForDeletes(texteditor_pb2.Username(name=username))
        start_new_thread(self.listen_thread, (stub, responseStream))
        start_new_thread(self.delete_thread, (stub, deleteStream))

        self.window.mainloop()

    def new_file(self):
        """Create a new file"""
        # If there is text in the current file, prompt the user to save first
        if self.txt_edit.get("1.0", tk.END).strip() != "":
            response = messagebox.askyesnocancel("Save File", "Do you want to save your changes before creating a new file?")
            if response == True:
                # save the current file
                self.save()

        self.txt_edit.delete("1.0", tk.END)
        self.window.title("Distributed Collaborative Text Editor - New File")
        self.title = "Distributed Collaborative Text Editor - New File"
        self.new_file_flag = True

    def update_file(self, filename, contents):
        """Update file with edits from a different client"""
        title_name = self.title.split("/")[-1]
        if title_name == filename:
            self.txt_edit.delete("1.0", tk.END)
            self.txt_edit.insert("1.0", contents)

    def open_file(self):
        """Open a file for editing"""
        filepath = askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir="./usertextfiles"
        )
        if not filepath:
            return

        # Prompt user to save non-empty files
        if self.txt_edit.get("1.0", tk.END).strip() != "":
            response = messagebox.askyesnocancel("Save File", "Do you want to save your changes before creating a new file?")
            if response == True:
                # save the current file
                self.save()
        self.txt_edit.delete("1.0", tk.END)
        with open(filepath, mode="r", encoding="utf-8") as input_file:
            text = input_file.read()
            self.txt_edit.insert(tk.END, text)
        self.window.title(f"Distributed Collaborative Text Editor - {filepath}")
        self.title = f"Distributed Collaborative Text Editor - {filepath}"
        self.new_file_flag = False
        self.btn_delete.config(state="normal")
    
    def delete(self):
        """Delete the current file"""
        title_arr = self.title.split(" - ")
        filepath = title_arr[1]
        filename = filepath.split("/")[-1]
        if not filepath:
            return
        response = messagebox.askyesnocancel("Delete file", "Do you want to delete this file?")
        if response == True:
            delete_response = self.stub.DeleteFromServer(texteditor_pb2.FileResponse(errorFlag=False, filename=filename))
            self.txt_edit.delete('1.0', tk.END)
            self.btn_delete.config(state="disabled")
            if not delete_response.errorFlag:
                messagebox.showinfo("File Deleted", "The file has been deleted.")
                self.window.title("Distributed Collaborative Text Editor - New File")
                self.title = "Distributed Collaborative Text Editor - New File"
                self.new_file_flag = True
            else:
                print("Error deleting file!")

    def save(self):
        """If new file, save as, otherwise save with existing title"""
        if self.new_file_flag:
            self.save_as()
            return
        else:
            title_arr = self.title.split(" - ")
            filepath = title_arr[1]
            if not filepath:
                return
            filename = filepath.split("/")[-1]
            text = self.txt_edit.get("1.0", tk.END)
            contents = text.encode()
            download_response = self.stub.SaveToServer(texteditor_pb2.Download(filename=filename, contents=contents))
            self.window.title(f"Distributed Collaborative Text Editor - {filepath}")
            self.title = f"Distributed Collaborative Text Editor - {filepath}"
            if download_response.errorFlag: 
                messagebox.showinfo("File Save Error", "Error saving " + download_response.filename + ".txt")

    def save_as(self):
        """Save the current file as a new file"""
        filepath = ""
        if self.new_file_flag:
            filepath = asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                initialdir="./usertextfiles"
            )
        # If existing file, autofill the last title
        else:
            title_arr = self.title.split(" - ")
            filepath = title_arr[1]
            filename = filepath.split("/")[-1]
            filepath = asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                initialfile=filename,
                initialdir="./usertextfiles"
            )
        if not filepath:
            return
        filename = filepath.split("/")[-1]
        text = self.txt_edit.get("1.0", tk.END)
        contents = text.encode()
        download_response = self.stub.SaveToServer(texteditor_pb2.Download(filename=filename, contents=contents))
        self.window.title(f"Distributed Collaborative Text Editor - {filepath}")
        self.title = f"Distributed Collaborative Text Editor - {filepath}"
        self.new_file_flag = False
        self.btn_delete.config(state="normal")
        if download_response.errorFlag:
            messagebox.showinfo("File Save Error", "Error saving " + download_response.filename + ".txt")

    # Listens for messages from server's Listen response stream. Closes when user logs out or deletes acct.
    def listen_thread(self, stub, responseStream):
        while True:
            print("listening...")
            try:
                response = next(responseStream)
                print(response.filename)
                if response.filename == ".DS_Store":
                    continue
                with open("./usertextfiles/" + response.filename, "wb") as f:
                    f.write(response.contents)
                self.update_file(response.filename, response.contents.decode())
            except:
                print("Listening error")
                return

    # Listens for deletes from server
    def delete_thread(self, stub, deleteStream):
        while True:
            try:
                response = next(deleteStream)
            # print(response.filename)
                os.remove("./usertextfiles/" + response.filename)
            except:
                print("Already deleted", response.filename)
        
    def signinLoop(self, stub):
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