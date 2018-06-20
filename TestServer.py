# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:25:49 2015

@author: Michael Cao, Muller Group
"""

import socket
import sys
#import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 41234)

print ("Starting up on %s on %s port" %server_address)

sock.bind(server_address)
#Listen for incoming connections

sock.listen(1)

while True:
    # Wait for a connection
    print ('waiting for a connection')
    connection, client_address = sock.accept()
        
    try:
        print('connection from', client_address)
    
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(4096).decode()
            print("%s" %data)
            if data:
                #print('sending data back to the client', file = sys.stderr)
                #time.sleep(10)
                connection.sendall(data.encode())
                pass
            else:
                print('no more data from', client_address)
                break
                
    finally:
#         Clean up the connection
        connection.close()
