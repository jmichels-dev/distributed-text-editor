"""Primary server default at IP_PORT_DICT[0], backup servers defaults at IP_PORT_DICT[1], 
IP_PORT_DICT[2], and IP_PORT_DICT[3]"""
IP0 = '10.250.64.41'
IP1 = '10.250.226.222'
IP_PORT_DICT = {0 : [IP0, '8080'], 1 : [IP0, '8081'], 2 : [IP1, '8080'], 3 : [IP1, '8081']}

SNAPSHOT_INTERVAL = 60 # seconds
HEARTBEAT_INTERVAL = 5