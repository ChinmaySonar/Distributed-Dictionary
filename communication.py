import socket
import os
from multiprocessing import Process, Pipe
from time import sleep                    # to add delays for demonstration
import signal 
#from handle_client_interactive import *
import time
import math
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


def balance(client_id, local_bc):
    bal = 10
    for i in local_bc:
        if i[1] == client_id:
            bal -= i[3]
        if i[2] == client_id:
            bal += i[3]
    return bal

############# different version for now ##################

def communication(child_conn):
    # Create a TCP/IP socket for listening
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    my_listen_address = None
    while True:
        port = random.randint(10001,65000)
        try:
            #print "trying to bind to", data_man_port
            sock_listen.bind(("localhost", port))
            my_listen_address = ("localhost", port)
            print("my_address: {}".format(my_listen_address))
            break
        except socket.error as err:
            if err.errno == 98:  # address already in use
                port = random.randint(10001, 65000)
                continue
            else:
                raise
    
    # this sock is sock_connect which'll be one time use per send communication
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ("localhost", 10000)
    print('connecting to {} port {}'.format(*server_address))

    # Registering connection with co-ordinate server 
    sock.connect(server_address)
    
    sock.sendall("connecting  {}".format(str([my_listen_address])))    
    #sock.sendall(str(my_listen_address))    

    data = sock.recv(2000)    #data contains information about all the connected servers
    
    #print("Data from coordinator: ", data)    
    #child_conn.send(data)
    
    client_list = server_message_format(data) # this is for information of child
    print("Current clients in the network: ", client_list)

    client_list_dict = {} #id, listen_address dict()
    for i in range(len(client_list)):
        client_list_dict[i] = client_list[i]
    #print("client_list_dict: ", client_list_dict)
        
    my_id = len(client_list)-1 # this will get affected things are deleted from the network 
    print("My id: ", my_id)

    print('START closing socket with co-ordinate')
    sock.close()

    #local copy of blockchain (make it objects and class later)
    local_bc = [] # format: (local_clock time, sender, receiver, amount)
     
    #local 2D time table
    local_table = []    

    #while loop between listening to parent and taking messages from other clients for Lamport
    local_clock = 0

    ########### new to network connection -- notify everyone else ############
    print("Notifying all others that I'm in network too")
    for i in range(len(client_list)):
        if client_list[i] == my_listen_address:
            init = [0]*len(client_list)
            local_table.append(init)
            #print("Local table: ", local_table)
            continue # break should also work
        else:
            print("Notifying: {}", i)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(client_list[i])
            sock.sendall("4  {}  {}".format(my_id, [my_listen_address])) 
            sock.close()
        init = [0]*len(client_list)
        local_table.append(init)
        #print("Local table: ", local_table)
        

    
    while True:
        try:
            sock_listen.settimeout(0.2) # timeout for listening
            sock_listen.listen(1) # try values other than one here
            connection, client_address = sock_listen.accept()
        except socket.timeout:
            pass
            if child_conn.poll():
                request = child_conn.recv()
                
                
                print("Local clock: ", local_clock)
                if request[0] == '5': #quit request
                    for i in client_list:
                        if i == my_listen_address:
                            continue
                        else: # sending request message to everyone
                            time.sleep(1)
                            print("Sending quit message to {}", i)
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect(i)
                            sock.sendall("5  {}  {}".format(my_id, [my_listen_address]))
                            sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(server_address)
                    sock.send("close")
                    sock.close()
                    break
                    
                
                
                if request[0] == '1': # balance
                    request = request.strip()
                    request_for = int(request[-1])
                    if request_for not in client_list_dict:
                        child_conn.send('-1')
                    else:
                        bal = balance(request_for, local_bc)
                        child_conn.send(str(bal))

                if request[0] == '2': # transfer
                    local_clock += 1  # doesn't matter if we only increment clock on successful transfer or not
                    request_list = request.strip().split(' ')
                    receiver = int(request_list[1])
                    if receiver == my_id:
                    	child_conn.send('-1 0 0')
                    	continue
                    if receiver not in client_list_dict:
                    	child_conn.send('-2 0 0')
                    	continue
                    amount = int(request_list[2])
                    avail_bal = balance(my_id, local_bc)
                    if avail_bal < amount:
                        reply = '0 {} {}'.format(avail_bal, avail_bal)
                        child_conn.send(reply)
                    else:
                        local_bc.append((local_clock, my_id, receiver, amount))
                        reply = '1 {} {}'.format(avail_bal, avail_bal-amount)                        
                        child_conn.send(reply)
                    local_table[my_id][my_id] = local_clock # updating the local table my entry
                    

                if request[0] == '3': # send message
                    request_list = request.strip().split(' ') 
                    receiver = int(request_list[1])
                    print("local_table: ", local_table)
                    print("local_bc: ", local_bc)
                    message = '1    '
                    for i in local_table:
                        for j in i:
                            message += str(j)+' ' #single space between two elements of same row
                        message += ' ' #double space between the rows
                    message += '  ' # 4 spaces between table and bc
                    for i in local_bc:
                        if local_table[receiver][i[1]] < i[0]: # don't have some information about sender
                            message += '{} {} {} {}'.format(i[0],i[1],i[2],i[3])
                            message += '  ' #gap of two between this and next entry
                    ##### create a socket and send the message
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(client_list_dict[receiver])
                    sock.sendall(message)
                    sock.close()
                        

                if request[0] == '4': # print bc
                    query_string = ''
                    for i in local_bc:
                        query_string += str(i[0]) + ' ' + str(i[1]) + ' ' + str(i[2]) + ' ' + str(i[3])
                        query_string += '  '
                    child_conn.send(query_string)

             
            continue        
        else:
            #connection established
            
            try:
                network_message = connection.recv(2000)
                
                if network_message[0] == '1': # incoming
                    print("Network message:", network_message)
                    message_list = network_message.strip().split("    ")
                    local_table_list = message_list[1]
                    local_table_list = local_table_list.split("  ") # list of rows
                    if len(message_list) == 2: # no new bc events received
                        for i in range(len(local_table_list)):
                            current_row = map(int, local_table_list[i].strip().split(" "))
                            for j in range(len(client_list)):
                                local_table[i][j] = max(local_table[i][j], current_row[j]) # updated my local table
                        print("local_table", local_table)
                        print("local_bc", local_bc)
                        connection.close()
                    else:
                        bc_table_list = message_list[2]
                        bc_table_list = bc_table_list.split("  ") # list of blockchain events
                        bc_received = []
                        for i in bc_table_list:
                            a,b,c,d = i.strip().split(" ")
                            bc_received.append((int(a), int(b), int(c), int(d)))
                        for i in bc_received:
                            if local_table[my_id][i[1]] < i[0]: # I don't know this info about the sender
                                local_bc.append(i)
                                local_table[my_id][i[1]] = i[0]
                        for i in range(len(local_table_list)):
                            current_row = map(int, local_table_list[i].strip().split(" "))
                            for j in range(len(client_list)):
                                local_table[i][j] = max(local_table[i][j], current_row[j]) # updated my local table
                        print("local_table", local_table)
                        print("local_bc", local_bc)
                        connection.close()

                elif network_message[0] == '4': #new client
                    message_list = network_message.split("  ")
                    str_to_list = server_message_format(message_list[2]) # listen address
                    client_id = int(message_list[1]) # client id
                    client_list.append(str_to_list[0])
                    client_list_dict[client_id] = str_to_list[0]
                    
                    connection.close()
                    init = [0]*len(client_list)
                    local_table.append(init)                    
                    for i in range(len(client_list)-1):
                        local_table[i].append(0)

                elif network_message[0] == '5': # going out of network
                    message_list = network_message.split("  ")
                    str_to_list = server_message_format(message_list[2])
                    print("removing id: {}, listen address: {} from users in the networks".format(int(message_list[1]), str_to_list[0]))
                    client_list.remove(str_to_list[0]) # need to update the dictionary too
                    del client_list_dict[int(message_list[1])]
                    connection.close()
            finally:
                pass
   

    # de-registrering from server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    try:

        #send
        message_close = 'close'

        sock.sendall(message_close)

    finally:
        print('CLOSING socket with co-ordinate')
        sock.close() 
    sock_listen.close() # closing listen socket manually
    return True
