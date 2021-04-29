# upload function
# used by client during file upload
# used by server when sending file during client download
def send_file(socket, filename):
    import os
    import time
    try:
        
        # check file size of file to upload
        str_filename = str(filename)
        file_size = os.stat(str_filename).st_size
        
        # handling zero sized file
        # if file to upload is zero sized, send DONE 
        if file_size == 0:
            socket.sendall("DONE".encode("ascii"))
            print("Upload Successful" + '\n')
            
        else:
            
            # open file in binary read mode
            with open(str_filename, "rb") as file_to_send:
                
                data_to_send = file_to_send.read()
                
                # while there is more data to send in file
                # send data over socket and read next set of data from file
                while data_to_send:
                    print("Sending..." + '\n')
                    socket.sendall(data_to_send)
                    data_to_send = file_to_send.read()
                
                # close file when all data is sent
                # sleep for 1 second to let all file data be sent first and then
                # send 'DONE' acknowledgement msg to indicate end of sending data 
                file_to_send.close()
                time.sleep(1)
                send_ack = "DONE"
                socket.send(send_ack.encode("ascii"))
                
                # show upload successful on sender's side
                # and wait to receive any further acknowledgement msg from receiver
                print ("Upload successful")
                print(socket.recv(4096).decode("utf-8"))
                

    # If file to send is not in server directory catch exception caused
    # and send cause of exception to receiver    
    except FileNotFoundError as e:
        print(e)
        response = "File: " + str_filename + " not found in directory"
        socket.sendall(response.encode("utf-8"))
        print(response)



# download function
# used by client when downloading file from server
# used by server when receiving uploaded file from client    
def recv_file(socket, filename):
    str_filename = str(filename)
    try:
        
        # create new file in exclusive binary mode
        with open(str_filename, "xb") as file_to_write:
            
            while True:
                
                # loop and keep receiving file data from sender
                inc_data = socket.recv(4096)
                print("Receiving data..." + '\n')
                
                # if received data is "DONE" stop receiving
                # or if blank data is being received, stop receiving
                # else write received data to file created
                if inc_data == "DONE".encode("ascii"):
                    print("Dowload Successful")
                    break
                
                elif inc_data == "".encode("ascii"):
                    print("<<<Client connection interrupted>>>")
                    print("Download unsuccessful")
                    break
                
                else:
                    file_to_write.write(inc_data)
                    
               
            file_to_write.close()
          
            
    # created file is in exclusive mode, so catch exception if file with same 
    # name already exists in directory     
    except FileExistsError as e:
        print(e)
        response = "File: <<" + str_filename + ">> already exists in directory" 
        socket.sendall(response.encode("utf-8"))
        print(response)  
        


# function to send directory listing over socket
def send_listing(socket):
    import os
    
    # generate list of names of sub directories in server directory
    list_result =  os.listdir()
    
    # send list in string format to client
    out_result = str(list_result)
    socket.send(out_result.encode("utf-8"))
    print("Directory listing sent to client successfully" + '\n')



# function to receive directory listing over socket
def recv_listing(socket):
    
    # receive incoming string data from server
    inc_data = socket.recv(2048).decode("utf-8")
    
    # convert string back to a list of sub directories
    final_data = eval(inc_data)
    print("The list of files in the server directory are: ")
    for val in final_data:
        print(val)
        print('\n')        