from concurrent import futures
import logging
import os

import grpc
import sys
import texteditor_pb2
import texteditor_pb2_grpc
import helpers


class TextEditorServicer(texteditor_pb2_grpc.TextEditorServicer):

    def __init__(self):
        # set of (unique) filenames
        self.filenames = set()
        for filename in os.listdir("./usertextfiles/"):
            f = os.path.join("./usertextfiles/", filename)
            # checking if it is a file
            if os.path.isfile(f):
                self.filenames.add(filename)

    def SaveToServer(self, download, context):
        """Send saved file to primary server and overwrite any existing file with same name"""
        if not helpers.filenameExists(download.filename, self.filenames):
            self.filenames.add(download.filename)
        try:
            with open("./usertextfiles/" + download.filename, "wb") as f:
                while True:
                    f.write(download.contents)
                    return texteditor_pb2.FileResponse(errorFlag=False, filename=download.filename)
        except:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("File not found")
            return texteditor_pb2.FileResponse(errorFlag=True, filename=download.filename)
    
    def DeleteFromServer(self, file_response, context):
        """Delete file from primary server"""
        if not helpers.filenameExists(file_response.filename, self.filenames):
            print("Trying to delete a file that doesn't exist!")
            return texteditor_pb2.FileResponse(errorFlag=True, filename=file_response.filename)
        try:
            os.remove("./usertextfiles/" + file_response.filename)
            self.filenames.remove(file_response.filename)
            return texteditor_pb2.FileResponse(errorFlag=False, filename=file_response.filename)
        except:
            print("os remove exception!")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("File not found")
            return texteditor_pb2.FileResponse(errorFlag=True, filename=file_response.filename)

    def OpenExistingFile(self, download, context):
        print(download.filename)
        # return error if file does not exist
        try:
            with open("./usertextfiles/" + download.filename + ".txt", "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    yield texteditor_pb2.FileContents(contents=chunk)
        except IOError:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("File not found")
            return

    ## Replication RPCs
    def Heartbeats(self, backupStream, context):
        """Send latest state from primary to backups as a keepalive message"""
        print("Before new connection, existing backup servers:", self.backup_servers)
        this_backup_id = -1

        while True:
            try:
                # Recieve heartbeat from backup
                requestKeepAlive = next(backupStream)
                this_backup_id = requestKeepAlive.backup_id
                print("Received heartbeat from backup at server_id", this_backup_id)
                self.backup_servers.add(this_backup_id)
                if this_backup_id not in self.newOps:
                    self.newOps[this_backup_id] = []
                print("Operation repl queue:", self.newOps)

                # Send heartbeat to backup
                yield chat_pb2.KeepAliveResponse(primary_id=self.server_id, backup_ids=list(self.backup_servers))
                time.sleep(constants.HEARTBEAT_INTERVAL)
            except Exception:
                print("Error in heartbeat from backup.")
                self.backup_servers.remove(this_backup_id)
                self.newOps.pop(this_backup_id)
                print("Remaining backup servers:", self.backup_servers)
                break

    def BackupOps(self, this_backup_id, context):
        while True:
            if this_backup_id.backup_id in self.newOps and len(self.newOps[this_backup_id.backup_id]) > 0:
                yield chat_pb2.Operation(opLst=self.newOps[this_backup_id.backup_id].pop(0))

    ## Non-RPC server-side snapshots
    def Snapshot(self):
        with open('snapshot_' + str(server_id) + '.csv', 'w', newline = '') as testfile:
            rowwriter = csv.writer(testfile, delimiter=" ", quotechar="|", quoting=csv.QUOTE_MINIMAL)
            for key in self.clientDict:
                rowwriter.writerow([key] + self.clientDict[key])
    
    def OpenNewFile(self, download, context):
        if helpers.filenameExists(download.filename, self.filenames):
            return texteditor_pb2.FileResponse(errorFlag=True, filename=download.filename)
        self.filenames.add(download.filename)
        open("./usertextfiles/" + download.filename + ".txt", "w")
        return texteditor_pb2.FileResponse(errorFlag=False, filename=download.filename)


#     def SignInExisting(self, username, context):
#         eFlag, msg = helpers_grpc.signInExisting(username.name, self.clientDict)
#         return texteditor_pb2.Unreads(errorFlag=eFlag, unreads=msg)
    
#     def AddUser(self, username, context):
#         eFlag, msg = helpers_grpc.addUser(username.name, self.clientDict)
#         return texteditor_pb2.Unreads(errorFlag=eFlag, unreads=msg)

#     def Send(self, sendRequest, context):
#         response = helpers_grpc.sendMsg(sendRequest.sender.name, sendRequest.recipient.name, 
#                                         sendRequest.sentMsg.msg, self.clientDict)
#         return texteditor_pb2.Payload(msg=response)

#     # usernameStream only comes from logged-in user
#     def Listen(self, username, context):
#         while True:
#             # If any messages are queued
#             if len(self.clientDict[username.name][1]) > 0:
#                 # Yield first message
#                 yield texteditor_pb2.Payload(msg=self.clientDict[username.name][1].pop(0))
#             # Stop stream if user logs out
#             if self.clientDict[username.name][0] == False:
#                 break

#     def List(self, wildcard, context):
#         payload = helpers_grpc.sendUserlist(wildcard.msg, self.clientDict)
#         return texteditor_pb2.Payload(msg=payload)

#     def Logout(self, username, context):
#         self.clientDict[username.name][0] = False
#         return texteditor_pb2.Payload(msg="Goodbye!\n")

#     def Delete(self, username, context):
#         self.clientDict.pop(username.name)
#         return texteditor_pb2.Payload(msg="Goodbye!\n")


def serve():
    # ip = '10.250.226.222'
    ip = '127.0.0.1'
    port = '8080'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    texteditor_pb2_grpc.add_TextEditorServicer_to_server(TextEditorServicer(), server)
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()