
#from TCP_client import*
from helpers import*


menu1 = {"Balance": 1, "Transfer": 2, "Send Message": 3, "Print blockchain": 4,"Disconnect": 5}
menu2 = {"My balance": 1, "Someone else's balance": 2}


# code to continuously interact with client

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
        
        # transfer
        if user_command == 2:
            receiver_id = raw_input("Enter receiver id:") #input a single number -- receiver_id
            amount = raw_input("Enter amount:")
            query_string = "2 "+ receiver_id + " " + amount
            # send query through network and wait
            parent_conn.send(query_string)
            #print("Added to blockchain")
            while True:
                if parent_conn.poll():
                    response = parent_conn.recv() 
                    # response format: 0/1 + " " + balance_before + " " + balance_after
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
                
        # balance   
        elif user_command == 1:
            bal_client = int(raw_input("Enter client id:"))
            query_string = '1 '+ str(bal_client)
            parent_conn.send(query_string)
            
            while True:                
                if parent_conn.poll():
                    response = parent_conn.recv()
                    if response.strip() == '-1':
                        print("Unrecognized Client ID")
                        break
                    else:
                        print("Current balance: " + response)
                        break
                else:
                    continue
        # send message
        elif user_command == 3: 
            receiver = raw_input("Enter receiver id:")
            query_string = '3 '+ receiver
            parent_conn.send(query_string)
            print("Sent message request to {}".format(receiver))

        # print blockchain
        elif user_command == 4:
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
        
        # disconnect
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


# part for pipe communication between parent process

parent_conn, child_conn = Pipe()
child_process  = Process(target = communication, args=(child_conn,))


child_process.start()
time.sleep(15) # initial time to connect between parent and child

print("Balance = $10")

handle_client_interactive(parent_conn)

child_process.join()

