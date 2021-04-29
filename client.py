import socket
import os
import sys
from server_functions import send_file
from server_functions import recv_file
from server_functions import recv_listing

# define repetitive functions used throughout the program 
# shows correct input format to establish connection to server
# and valid input requests 
def usage():
    print("Correct usage: python3 client.py <host name> <port num> (<req keyword> <filename> or <req keyword>)")
    print("Port num: integer in range 1-65535")
    print("Valid Requests: get, put or list")
    print("If filename contains special characters put it in '' ")
    

# closes client connection to server
def close():
    cli_sock.close()
    print('\n' + "--------------------------------------")
    terminate = "You terminated connection to server"
    print(terminate + '\n')
   

# create client socket
cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if len(sys.argv) == 4:
    host_name = str(sys.argv[1])
    port_num = int(sys.argv[2])
    req_type = str(sys.argv[3])
    
elif len(sys.argv) == 5:
    host_name = str(sys.argv[1])
    port_num = int(sys.argv[2])
    req_type = str(sys.argv[3])
    file_name = str(sys.argv[4])
    
else:
    usage()
    close()
    


# connect client to server 
try:
    cli_sock.connect((host_name, port_num))
    print("Connected to server" + '\n')
    
# catch any immediate exception when trying to establish connection to server 
# close connecftion, print exception type and correct input format  
except Exception as e:
    print(e)
    usage()
    close()


while True:
    try:
        
        # if port number used to connect is out of range
        if type(port_num) != int or port_num not in range(1, 65535):
            usage()
        
        
        # processing 'put' or 'get' request  
        if len(sys.argv) == 5:
            
            # if input is 'put' (Upload) and file to upload does exist in client directory
            # send request type and filename of file to upload to server
            if (req_type == 'put' or req_type == "PUT") and os.path.isfile(file_name):
                cli_msg = str(req_type) + " " + str(file_name)
                cli_sock.sendall(cli_msg.encode("utf-8"))
            
            # if input is 'get' (Download) and file to downlaod doesnt already exist in client directory
            # send req type and filename of file to downlaod to server
            elif (req_type == 'get' or req_type == "GET") and not(os.path.isfile(file_name)):
                cli_msg = str(req_type) + " " + str(file_name)
                cli_sock.sendall(cli_msg.encode("utf-8"))
                
            else:
                
                # if input request type is invalid 
                # close connection and tell server to quit
                cli_sock.sendall("quit".encode("utf-8"))
                
                # show type of file error caused on CLIENT's side in each case
                # close connection to server
                if req_type == 'get' or req_type == "GET" : 
                    print("File: " + str(file_name) + " already exists in client directory" + '\n')
                elif req_type == 'put'or req_type == "PUT":
                    print("File: " + str(file_name) + " does not exists in client directory" + '\n')
                usage()
                close()
                break
            
            # receive server's response to initial request 
            inc_response = cli_sock.recv(4096).decode("utf-8")
        
            # if incoming response is CMDOK proceed with download or upload functions
            if inc_response == "CMDOK":
                if req_type == "put" or req_type == "PUT" and os.path.isfile(file_name):
                    send_file(cli_sock, file_name)
                    print("Upload Complete")
                    cli_sock.shutdown(socket.SHUT_WR)
        
                elif req_type == 'get' or req_type == "GET":
                    recv_file(cli_sock, file_name)
                    print("Download Complete")
                    cli_sock.shutdown(socket.SHUT_WR)
            
                close()
                    
            # if incoming response was CMDNOTOK 
            # show type of file error caused on SERVER's side and close connection
            elif inc_response == "CMDNOTOK":
                if req_type == "put" or req_type == "PUT" :
                    print("<" + str(file_name) + "> Already exists in server directory" + '\n')
                elif req_type == "get" or req_type == "GET":
                    print("<" + str(file_name) + "> does not exist in server directory" + '\n')
                usage()
                cli_sock.shutdown(socket.SHUT_WR)
                close()

            
           
        # processing 'list' request
        elif len(sys.argv) == 4:
            cli_msg = str(req_type)
            cli_sock.send(cli_msg.encode("utf-8"))
            recv_listing(cli_sock)
            
            close()
        
        break
    
    # catch unexpected exceptions and print its type and error message
    # exit while loop and terminate connection
    except Exception as ex:
        print("Exception type: " + str(ex.__class__.__name__))
        print('\n')
        usage()
        print('\n' + str(req_type) + " unsuccessful")
        break
    
    
        
