import sys
from _thread import *
import time

import grpc
import chat_pb2
import chat_pb2_grpc
import helpers_grpc
import constants
import primary
import csv

class BackupTextEditorServicer():
    def __init__(self, id, primary_id, stub):
        self.id = id
        self.primary_id = primary_id
        self.stub = stub
        # set of (unique) filenames
        self.filenames = set()
        # Save current filenames
        for filename in os.listdir("./usertextfiles/"):
            f = os.path.join("./usertextfiles/", filename)
            # checking if it is a file
            if os.path.isfile(f):
                self.filenames.add(filename)

        # Establish response stream to receive edited files from the primary
        edited_downloads_stream = stub.BackupEdits(chat_pb2.KeepAliveRequest(backup_id=self.id))
        # Concurrently update state in a thread
        start_new_thread(download_edits, (edited_downloads_stream, self.id))

        # Establish bidirectional stream to send and receive keep-alive messages from primary server.
        # requestStream and responseStream are generators of chat_pb2.KeepAlive objects.
        requestStream = send_backup_heartbeats(self.id)
        responseStream = stub.Heartbeats(requestStream)
        keepalive_listen(responseStream, self.id)

    def download_edits(edited_downloads_stream, backup_id):
        """Download edited files from the primary to this backup"""
        while True:
            nextFile = next(edited_downloads_stream)
            with open('commit_log_' + str(server_id) + '.csv', 'a', newline = '') as commitlog:
                rowwriter = csv.writer(commitlog, delimiter=" ", quotechar="|", quoting=csv.QUOTE_MINIMAL)
                rowwriter.writerow(nextOp.opLst)

    # Listens for messages from primary server's KeepAlive response stream
    def keepalive_listen(responseStream, this_backup_id):
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
                    if new_primary_id == this_backup_id:
                        primary.serve(new_primary_id)
                        sys.exit()
                    else:
                        serve(this_backup_id, new_primary_id)
                else:
                    print("backup_ids empty")
                return

    # sends keepalive messages to primary server
    def send_backup_heartbeats(this_backup_id):
        keep_alive_request = chat_pb2.KeepAliveRequest(backup_id=this_backup_id)
        while True:
            yield keep_alive_request
            time.sleep(constants.HEARTBEAT_INTERVAL)

def serve(backup_id, primary_id):
    # ip and port of the current primary
    primary_ip = constants.IP_PORT_DICT[primary_id][0]
    primary_port = constants.IP_PORT_DICT[primary_id][1]

    with grpc.insecure_channel('{}:{}'.format(primary_ip, primary_port)) as channel:
        stub = chat_pb2_grpc.TextEditorStub(channel)
        BackupTextEditorServicer(backup_id, primary_id, stub)
            
if __name__ == '__main__':
    # Checks for correct number of args
    if len(sys.argv) != 3:
        print("Correct usage: script, backup_id (0, 1, 2, 3), primary_id")
        exit()
    backup_id = int(sys.argv[1])
    primary_id = int(sys.argv[2])
    serve(backup_id, primary_id)