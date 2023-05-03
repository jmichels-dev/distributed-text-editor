from concurrent import futures
import logging
import os
import sys
import time

import grpc
import texteditor_pb2
import texteditor_pb2_grpc
import helpers
import constants


class TextEditorServicer(texteditor_pb2_grpc.TextEditorServicer):

    def __init__(self, server_id):
        self.server_id = server_id
        # set of (unique) filenames
        self.filenames = set()
        # {Screen name: [names files to be sent (updated) to this user]}
        self.clientDict = {}
        self.deleteDict = {}
        # Save current filenames
        for filename in os.listdir("./usertextfiles/"):
            f = os.path.join("./usertextfiles/", filename)
            # checking if it is a file
            if os.path.isfile(f):
                self.filenames.add(filename)
        # Commit file edits that have not yet been sent to backups. Key is id of backup, value is list of filenames and contents to be sent.
        self.backup_edits = {}
        self.backup_servers = set()

    def SaveToServer(self, download, context):
        """Send saved file to primary server and overwrite any existing file with same name"""
        if not helpers.filenameExists(download.filename, self.filenames):
            print("saving file: " + download.filename)
            self.filenames.add(download.filename)
        try:
            with open("./usertextfiles/" + download.filename, "wb") as f:
                f.write(download.contents)
                for key in self.backup_edits:
                    self.backup_edits[key].append(download)
                helpers.broadcastUpdate(download.filename, self.clientDict)
                return texteditor_pb2.FileResponse(errorFlag=False, filename=download.filename)
        except:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("File not found")
            return texteditor_pb2.FileResponse(errorFlag=True, filename=download.filename)
    
    def DeleteFromServer(self, file_response, context):
        print("deleting file: " + file_response.filename)
        """Delete file from primary server"""
        if not helpers.filenameExists(file_response.filename, self.filenames):
            print("Trying to delete a file that doesn't exist!")
            return texteditor_pb2.FileResponse(errorFlag=True, filename=file_response.filename)
        try:
            os.remove("./usertextfiles/" + file_response.filename)
            self.filenames.remove(file_response.filename)
            helpers.broadcastUpdate(download.filename, self.deleteDict)
            return texteditor_pb2.FileResponse(errorFlag=False, filename=file_response.filename)
        except:
            print("os remove exception!")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("File not found")
            return texteditor_pb2.FileResponse(errorFlag=True, filename=file_response.filename)

    ## Replication RPCs
    def Heartbeats(self, backupStream, context):
        """Send latest state from primary to backups as a keepalive message"""
        # print("Before new connection, existing backup servers:", self.backup_servers)
        this_backup_id = -1

        while True:
            try:
                # Recieve heartbeat from backup
                requestKeepAlive = next(backupStream)
                this_backup_id = requestKeepAlive.backup_id
                print("Received heartbeat from backup at server_id", this_backup_id)
                self.backup_servers.add(this_backup_id)
                if this_backup_id not in self.backup_edits:
                    self.backup_edits[this_backup_id] = []
                # Send heartbeat to backup
                yield texteditor_pb2.KeepAliveResponse(primary_id=self.server_id, backup_ids=list(self.backup_servers))
                time.sleep(constants.HEARTBEAT_INTERVAL)
            except Exception:
                print("Error in heartbeat from backup.")
                self.backup_servers.remove(this_backup_id)
                self.backup_edits.pop(this_backup_id)
                print("Remaining backup servers:", self.backup_servers)
                break

    def BackupEdits(self, this_backup_id, context):
        """Send edited files from primary to backups"""
        while True:
            if this_backup_id.backup_id in self.backup_edits and len(self.backup_edits[this_backup_id.backup_id]) > 0:
                yield self.backup_edits[this_backup_id.backup_id].pop(0)

    def SignInExisting(self, username, context):
        eFlag, msg = helpers.signInExisting(username.name, self.clientDict)
        return texteditor_pb2.Unreads(errorFlag=eFlag, unreads=msg)

    # usernameStream only comes from logged-in user
    def Listen(self, username, context):
        self.clientDict[username.name] = []
        while True:
            # If any files need to be updated
            if len(self.clientDict[username.name]) > 0:
                contents = ""
                with open("./usertextfiles/" + self.clientDict[username.name][0], "rb") as f:
                    contents = f.read()
                contents = contents.encode()
                # Yield first file update
                yield texteditor_pb2.Download(filename=self.clientDict[username.name].pop(0), contents=contents)
            # # Stop stream if user logs out
            # if self.clientDict[username.name][0] == False:
            #     break

    # usernameStream only comes from logged-in user
    def ListenForDeletes(self, username, context):
        self.deleteDict[username.name] = []
        while True:
            # If any files need to be deleted
            if len(self.deleteDict[username.name]) > 0:
                # Yield first file to delete
                contents = "".encode()
                yield texteditor_pb2.Download(filename=self.deleteDict[username.name].pop(0), contents=contents)
            # # Stop stream if user logs out
            # if self.clientDict[username.name][0] == False:
            #     break

#     def List(self, wildcard, context):
#         payload = helpers_grpc.sendUserlist(wildcard.msg, self.clientDict)
#         return texteditor_pb2.Payload(msg=payload)

#     def Logout(self, username, context):
#         self.clientDict[username.name][0] = False
#         return texteditor_pb2.Payload(msg="Goodbye!\n")

#     def Delete(self, username, context):
#         self.clientDict.pop(username.name)
#         return texteditor_pb2.Payload(msg="Goodbye!\n")


def serve(server_id):
    ip = constants.IP_PORT_DICT[server_id][0]
    port = constants.IP_PORT_DICT[server_id][1]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    texteditor_pb2_grpc.add_TextEditorServicer_to_server(TextEditorServicer(server_id), server)
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    if len(sys.argv) != 2:
        print("Correct usage: script, server_id")
        exit()
    server_id = int(sys.argv[1])
    serve(server_id)