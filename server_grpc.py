from concurrent import futures
import logging

import grpc
import sys
import texteditor_pb2
import texteditor_pb2_grpc
import helpers


class TextEditorServicer(texteditor_pb2_grpc.TextEditorServicer):

    def __init__(self):
        # set of (unique) filenames
        self.filenames = set()
    
    def OpenNewFile(self, download, context):
        print(download.filename)
        if helpers.filenameExists(download.filename, self.filenames):
            return texteditor_pb2.FileResponse(errorFlag=True, filename=download.filename, content=None)
        self.filenames.add(download.filename)
        open("./usertextfiles/" + download.filename + ".txt", "w")
        return texteditor_pb2.FileResponse(errorFlag=False, filename=download.filename, content=None)


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
    ip = '10.250.226.222'
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