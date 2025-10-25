# UDP client

import sys
import socket

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if len(sys.argv) != 4:
    print("Usage: client_udp <host server> <port> <message>")
    sys.exit(1)

host, port, message = sys.argv[1:4]

ClientSocket.sendto(str.encode(message), (host,int(port)))
