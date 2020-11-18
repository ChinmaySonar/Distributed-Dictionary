import math

def server_message_format(server_msg):
    # decoding client list from received from network server
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

def format_blockchain(bc_from_child):
    # decode blochchain received from child process
    bc_elements = bc_from_child.split("  ")
    print("bc_elements: ", bc_elements)
    bc = []
    for i in bc_elements:
        elements = i.split(" ")
        bc.append((elements[0], elements[1], elements[2], elements[3])) # sender, receiver, amount, sender_local_time
    return bc


def print_menu(d):
    print("Menu:")
    for item, itemnum in sorted(d.items(), key=lambda x: x[1]):
        print("{}: {}".format(itemnum, item))

# def server_message_format(server_msg):
#     # decode server message to obtain clients list
#     server_msg = server_msg[1:-1]    
#     l = len(server_msg)
#     number = int(math.ceil(l/22.0))
#     clients_list = []
#     for i in range(number):
#         address = server_msg[:20]
#         address = address[1:-1]
#         ip = address[1:10]
#         port = int(address[13:])
#         clients_list.append((ip,port))
#         if i < (number-1):
#             server_msg = server_msg[22:]
#     return clients_list


def balance(client_id, local_bc):
    # compute balance for a given client from local blockchain
    bal = 10
    for i in local_bc:
        if i[1] == client_id:
            bal -= i[3]
        if i[2] == client_id:
            bal += i[3]
    return bal