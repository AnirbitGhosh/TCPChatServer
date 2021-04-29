import socket
import sys
import os
from server_functions import send_file
from server_functions import recv_file
from server_functions import send_listing

# Define repetitive functions used throughout program
# show correct input format to execute server
def usage():
    print("Correct usage: python3 server.py <Port Num>")
    print("Port num: integer in range 1-65535"+'\n')


# closes client connection
def close():
    cli_sock.close()
    print("Client connection was closed" + '\n')


# error message in case of invalid input from client side
def client_error():
    out_msg = "Invalid input"
    cli_sock.sendall(out_msg.encode("utf-8"))
    print("Invalid client input" + '\n')

#message to show while waiting for new connections
def waiting_clients():
    print("Waiting for clients")
    print("-------------------------------------" + '\n')


# create socket
srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


if len(sys.argv) != 2:
    usage()
    
port_num = int(sys.argv[1])


# Register socket with OS
srv_sock.bind(("0.0.0.0", port_num))
print('\n'+ "<< 0.0.0.0 " + str(port_num) + " >> Server up and running")


# wait for incoming client connections 
srv_sock.listen(10)
waiting_clients()


while True: 
    try:
        # receive client connection and initiate socket 
        cli_sock, cli_addr = srv_sock.accept()
        print(cli_addr[0] + " Just connected" + '\n')
    
    
        # receive client request and split into request type
        # and the associated request parameter (if any)
        inc_msg = cli_sock.recv(4096).decode("utf-8")
        split_msg = inc_msg.split(" " , 1)
    
        print("Client says: " + inc_msg + '\n')
        
        
        # in case of an input exception on the client side recieve "QUIT"
        # and close connection
        if inc_msg == "quit" or inc_msg == "QUIT":
            close()
            print("File error on client side" + '\n')
            waiting_clients()
        
    
        #recognize type of client request  
        elif len(split_msg) == 2:
            cli_req = split_msg[0]
            cli_file = split_msg[1]
        
        
            # upload and download method handling
            # if request type is 'put' (Upload)
            # and file to be uploaded is not already on server directory
            # send "CMDOK" acknowledgement msg to client
            # execute function to receive file from client
            
            if (cli_req == "put" or cli_req == "PUT") and not(os.path.isfile(cli_file)):
                cli_sock.sendall("CMDOK".encode("utf-8"))
                recv_file(cli_sock, cli_file)
                print("\n" + "Download Request Complete")
            
            # if request type is 'get' (Download)
            # and file to download exists on server directory
            # send "CMDOK" acknowledgement msg to client
            # execute program to send file to client
            
            elif (cli_req == "get" or cli_req == "GET") and os.path.isfile(cli_file):
                cli_sock.send("CMDOK".encode("utf-8"))
                send_file(cli_sock, cli_file) 
                print("\n" + "Upload Request Complete")
                
         
            
        
            else:
                # if request type if invalid 
                # or file to upload already exists
                # or file to download does not exists on server
                # send "CMDNOTOK" error acknowledgement msg to client
               
                
                cli_sock.send("CMDNOTOK".encode("utf-8"))
                if not(os.path.isfile(cli_file)):
                    print(str(cli_file) +  " does not exist in server directory")
                elif os.path.isfile(cli_file):
                    print(str(cli_file) +  " already exists in server directory")
            
            # close socket and return to waiting for more client connections
            close()
            waiting_clients()
    
    
    
        # list requrest handling
        # if request type if "list"
        # send client directory listing from server
        # return to waiting for more client connections
        elif len(split_msg) == 1 and inc_msg == "list" or inc_msg == "LIST":
            send_listing(cli_sock)
            close()
            waiting_clients()
            
       
        # if req type doesnt match the three valid types 
        # close connection and show client input error
        # return to waiting for more client connections
        else:
           client_error()
           close()
           waiting_clients()


    # catch all unexpected exceptions and print its type
    except Exception as e:
        print("Exception type: " + str(e.__class__.__name__))
        
        # if connection to client over socket is interrupted
        # or there is a connection drop
        if isinstance(e, BrokenPipeError) or isinstance(e, ConnectionResetError):
            print(e, "<<<Client connection interrupted>>>")

        print('\n'+ "Request <" + str(cli_req) + "> unsuccessful" + '\n')
        waiting_clients()
        
        
    