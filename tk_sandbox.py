import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox

import grpc
import texteditor_pb2
import texteditor_pb2_grpc

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

    def open_file(self):
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir="./usertextfiles"
        )
        if not filepath:
            return

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


    """Old local versions of save"""
    # def save(self):
    #     """If new file, save as, otherwise save with existing title"""
    #     if self.new_file_flag:
    #         self.save_as()
    #         return
    #     else:
    #         title_arr = self.title.split(" - ")
    #         filepath = title_arr[1]
    #         if not filepath:
    #             return
    #         with open(filepath, mode="w", encoding="utf-8") as output_file:
    #             text = self.txt_edit.get("1.0", tk.END)
    #             output_file.write(text)
    #         self.window.title(f"Distributed Collaborative Text Editor - {filepath}")
    #         self.title = f"Distributed Collaborative Text Editor - {filepath}"
    #         messagebox.showinfo("File Saved", "Your file has been saved.")

    # def save_as(self):
    #     """Save the current file as a new file"""
    #     if self.new_file_flag:
    #         filepath = asksaveasfilename(
    #             defaultextension=".txt",
    #             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    #             initialdir="./usertextfiles"
    #         )
    #     # If existing file, autofill the last title
    #     else:
    #         title_arr = self.title.split(" - ")
    #         filepath = title_arr[1]
    #         filename = filepath.split("/")[-1]
    #         filepath = asksaveasfilename(
    #             defaultextension=".txt",
    #             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    #             initialfile=filename,
    #             initialdir="./usertextfiles"
    #         )
    #     if not filepath:
    #         return
    #     with open(filepath, mode="w", encoding="utf-8") as output_file:
    #         text = self.txt_edit.get("1.0", tk.END)
    #         output_file.write(text)
    #     self.window.title(f"Distributed Collaborative Text Editor - {filepath}")
    #     self.title = f"Distributed Collaborative Text Editor - {filepath}"
    #     self.new_file_flag = False
    #     self.btn_delete.config(state="normal")