import sys
from _thread import *
import time

import grpc
import texteditor_pb2
import texteditor_pb2_grpc
import helpers
import constants
import server
import csv

class BackupTextEditorServicer():
    def __init__(self, backup_id, primary_id, stub):
        self.backup_id = backup_id
        self.primary_id = primary_id
        # set of (unique) filenames
        self.filenames = set()

        # Establish response stream to receive edited files from the primary
        edited_downloads_stream = stub.BackupEdits(texteditor_pb2.KeepAliveRequest(backup_id=self.backup_id))
        # Concurrently update state in a thread
        start_new_thread(self.download_edits, (edited_downloads_stream,))

        # Establish bidirectional stream to send and receive keep-alive messages from primary server.
        # requestStream and responseStream are generators of texteditor_pb2.KeepAlive objects.
        requestStream = self.send_backup_heartbeats()
        responseStream = stub.Heartbeats(requestStream)
        self.keepalive_listen(responseStream)

    def download_edits(self, edited_downloads_stream):
        """Download edited files from the primary to this backup"""
        while True:
            download = next(edited_downloads_stream)
            if not helpers.filenameExists(download.filename, self.filenames):
                self.filenames.add(download.filename)
            try:
                with open("./usertextfiles/" + download.filename, "wb") as f:
                    f.write(download.contents)
            except:
                print("Error downloading file from server to backup")

    # Listens for messages from primary server's KeepAlive response stream
    def keepalive_listen(self, responseStream):
        primary_id = -1
        backup_ids = []
        while True:
            try:
                responseKeepAlive = next(responseStream)
                backup_ids = responseKeepAlive.backup_ids
                print("Received heartbeat from primary at server_id", responseKeepAlive.primary_id)
                time.sleep(constants.HEARTBEAT_INTERVAL)
            except Exception:
                print("Error in heartbeat from primary.")
                # Failstop by setting lower backup_id as new primary
                print("backup_ids:", backup_ids)
                if len(backup_ids) > 0:
                    new_primary_id = min(backup_ids)
                    if new_primary_id == self.backup_id:
                        server.serve(new_primary_id)
                        sys.exit()
                    else:
                        serve(self.backup_id, new_primary_id)
                else:
                    print("backup_ids empty")
                return

    # sends keepalive messages to primary server
    def send_backup_heartbeats(self):
        keep_alive_request = texteditor_pb2.KeepAliveRequest(backup_id=self.backup_id)
        while True:
            yield keep_alive_request
            time.sleep(constants.HEARTBEAT_INTERVAL)

def serve(backup_id, primary_id):
    # ip and port of the current primary
    primary_ip = constants.IP_PORT_DICT[primary_id][0]
    primary_port = constants.IP_PORT_DICT[primary_id][1]

    with grpc.insecure_channel('{}:{}'.format(primary_ip, primary_port)) as channel:
        stub = texteditor_pb2_grpc.TextEditorStub(channel)
        BackupTextEditorServicer(backup_id, primary_id, stub)
            
if __name__ == '__main__':
    # Checks for correct number of args
    if len(sys.argv) != 3:
        print("Correct usage: script, backup_id (0, 1, 2, 3), primary_id")
        exit()
    backup_id = int(sys.argv[1])
    primary_id = int(sys.argv[2])
    serve(backup_id, primary_id)