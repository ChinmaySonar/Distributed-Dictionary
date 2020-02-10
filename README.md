# Distributed-Dictionary
Aim: Implement efficient protocol for distributed log problem.

Motivation: Given several copies of same dataset placed in different physical locations; maintain consistency with read-write operations. Eg. Bank account data

Original Paper: "Efficient Solutions to Replicated Log and Dictionary Problems" -- https://sites.cs.ucsb.edu/~agrawal/spring2011/ugrad/p233-wuu.pdf

No external dependecies.

To run in terminal: (each instruction in new terminal window)
  1. python network_server.py # will create a network server to keep track of clients in the system
  2. python handle_client_interactive # one per client; this will allow client to put transaction requests interactively

handle_client_interactive.py will creat a new process to take care of communication in the network to maintain consistency.
