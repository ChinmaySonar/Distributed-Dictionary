import socket
import os
from multiprocessing import Process
from time import sleep                    # to add delays for demonstration
import signal                             # for SIGCHILD (know when child terminates)
import math
import time
import random



def server_message_format(server_msg):
    server_msg = server_msg[1:-1]    
    l = len(server_msg)
    number = int(math.ceil(l/22.0))
    clients_list = []
    for i in range(number):
        address = server_msg[:20]
        address = address[1:-1]
        ip = address[1:10]
        port = int(address[13:])
        clients_list.append((ip,port))
        if i < (number-1):
            server_msg = server_msg[22:]
    return clients_list


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('Starting up on {} port {}'.format(*server_address))


sock.bind(server_address)

# Listen for incoming connections with backlog 1 (backlog is number of connections system will allow before denying the connections)
# TCP thing only handles one connection at a time, everytime we want to send messages across the network, we first build a conenction by socket 

sock.listen(5)


connected_clients = []           #list of currently connedcted clients in the network

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)      
        data = connection.recv(2000)
        data = data.split("  ")
        print('received {}'.format(data))
        #print("first 10 data:  ", data[:10])
        if data[0] == 'connecting':
            #print("I'm here")
            client_listen_add = data[1]
            #print("client_listen_add", client_listen_add)
            client_listen_address = server_message_format(client_listen_add)
            print('client_listen_address: ', client_listen_address)
            connected_clients.append(client_listen_address[0])
            print("Connected cliets: ", connected_clients)
            print('sending data back to the client')
            connection.sendall(str(connected_clients))
        elif data[:5] == 'close':
            connected_clients.remove(client_address) 


    finally:
        # Clean up the connection
        print("Closing current connection")
        connection.close()
