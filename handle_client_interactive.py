
from TCP_client import*


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

def format_blockchain(bc_from_child):
    bc_elements = bc_from_child.split("  ")
    print("bc_elements: ", bc_elements)
    bc = []
    for i in bc_elements:
        elements = i.split(" ")
        bc.append((elements[0], elements[1], elements[2], elements[3])) # sender, receiver, amount, sender_local_time
    return bc

############# Actions #####################

# part for pipe communication between parent process

parent_conn, child_conn = Pipe()
child_process  = Process(target = communication, args=(child_conn,))


child_process.start()
time.sleep(15) # initial time to connect between parent and child

print("Balance = $10")


def print_menu(d):
    print "Menu:"
    for item, itemnum in sorted(d.items(), key=lambda x: x[1]):
        print "{}: {}".format(itemnum, item)


menu1 = {"Balance": 1, "Transfer": 2, "Send Message": 3, "Print blockchain": 4,"Disconnect": 5}
menu2 = {"My balance": 1, "Someone else's balance": 2}

# Print sent message to after sending the message -- as usual add 5 seconds delay for demonstration purposes

# part for continuous while loop to iterate over user input / communication pipe signals

def handle_client_interactive(parent_conn):
    # first character in query message to child conveys information to child about query type
    while True:
    	print("")
        print_menu(menu1)
        user_command = (raw_input("Your option: "))
        if user_command.isdigit() == False:
            print("Please enter a valid command")
            continue
        user_command = int(user_command)
        #(Transfer)        
        if user_command == 2: # transfer
            receiver_id = raw_input("Enter receiver id:") #input a single number -- receiver_id
            amount = raw_input("Enter amount:")
            query_string = "2 "+ receiver_id + " " + amount
            # send query through network and wait
            parent_conn.send(query_string)
            #print("Added to blockchain")
            while True:
                if parent_conn.poll():
                    response = parent_conn.recv() # format -- 0/1 + " " + balance_before + " " + balance_after
                    #print("Response from Child: ", response)
                    l = response.split(" ")
                    if int(l[0]) == -1:
                    	print("")
                    	print("trivial transaction :)")
                    elif int(l[0]) == -2:
                    	print("")
                    	print("Unrecognized ID")
                    elif int(response[0]) == 0:
                    	print("")
                        print("Transaction failed :(, not enough balance")
                        print("Balance: {}".format(l[1]))
                    else:
                    	print("")
                        print("Transaction Successful")
                        print("Balance before: {}, Balance after: {}".format(l[1],l[2]))
                    break
                else:
                    continue
                
            
        elif user_command == 1: #balance
            bal_client = int(raw_input("Enter client id:"))
            query_string = '1 '+ str(bal_client)
            parent_conn.send(query_string)
            
            while True:                
                if parent_conn.poll():
                    #print('I am here')
                    response = parent_conn.recv()
                    if response.strip() == '-1':
                        print("Unrecognized Client ID")
                        break
                    else:
                        print("Current balance: " + response)
                        break
                else:
                    continue
        elif user_command == 3: # send message 
            receiver = raw_input("Enter receiver id:")
            query_string = '3 '+ receiver
            parent_conn.send(query_string)
            print("Sent message request to {}".format(receiver))

        elif user_command == 4: # print blockchain
            query_string = str(4)
            parent_conn.send(query_string)
            while True:                
                if parent_conn.poll():
                    response = parent_conn.recv()
                    response = response.strip()
                    if response == '': # empty blockchain
                    	print("")
                        print("No events in blockchain yet")
                        break
                    else:
                        bc = format_blockchain(response)
                        for i in bc:
                            print("Sender local time: {}".format(i[0]))
                            print("Sender: {}".format(i[1]))
                            print("Receiver: {}".format(i[2]))
                            print("Amount: {}".format(i[3]))
                            print("")
                        break
                else:
                    continue
        
        elif user_command == 5:
            print("")
            print("Disconnecting the server")
            query_string = str(5)
            parent_conn.send(query_string)
            break        
        
        else:
       	    print("")
            print("Invalid command :(, please try again")
            continue

handle_client_interactive(parent_conn)

child_process.join()

