# Python Version: 3.8.10
# Program written by z5361183
# 10/04/22
# Run; $ python3 server.py serverPort 
from socket import *
import sys
from datetime import datetime
import time


###########################
### Main Data Structure ###
###########################
dataStore = {
    'users': [],
    'threads': []
}

###################
### Helper Fncs ###
###################

# Wipes the whole data store clean (used when Server is killed)
def dataStoreClear():
    dataStore['users'] = []
    dataStore['threads'] = []

# Exits program, called for ctrl+C detection
def killServer(serverSocket):
    dataStoreClear()
    serverSocket.close()    
    sys.exit("\nKilling server...")

# Checks credentials.txt if the given Username exists
def usernameExists(username):
    f = open("credentials.txt", "r") # open for ONLY reading
    allLinesF = f.readlines()
    numLinesF = len(allLinesF)
    for i in range(0, numLinesF):
        # break up string into user and pass
        brokenLogin = allLinesF[i].split(" ") # this is a list
        user = brokenLogin[0]
        password = brokenLogin[1].rstrip() # removes trailing newline
        if (username == user):
            f.close()
            return True
    f.close()
    return False

# Creates a new user (Upon detection of a new login)
def createNewUser(username, password, isActive):
    # newUser = {"username": poo, "password": pee, "isActive": True}
    # dataStore['users'].append(newUser)
    # f = open("credentials.txt", "a") # append new user deets to end of file
    pass

def changeUserActive(username, isActive):
    pass

##################
#### MAIN Fnc ####
##################
if __name__ == "__main__":
    if (len(sys.argv) != 2):
        sys.exit("Execute program as such: $python3 server.py <server_port>")
    
    serverPort = int(sys.argv[1])

    serverSocket = socket(AF_INET, SOCK_DGRAM) 
    serverSocket.bind(('localhost', serverPort))
    # serverSocket.listen(1) # only for TCP ??

    while 1: # while loop 1 for Server's infinite loop
        try: 
            print("Server waiting for clients...")
            usernameMsg, clientAddr = serverSocket.recvfrom(2048)
            print("Client authenticating")
            checkNewUserIterator = 0
            while 1: # while loop 2 for authenticating
                # messagePass, clientAddr = serverSocket.recvfrom(2048)
                try:
                    username = (usernameMsg.decode("utf-8")).strip()
                    # message, clientAddr = serverSocket.recvfrom(2048) # only needed temp for letting server know user has Exited
                    if usernameExists(username) is True:
                        serverSocket.sendto("PASSWORD", clientAddr) # Wait for password next
                        passMsg, clientAddr = serverSocket.recvfrom(2048)
                        password = (passMsg.decode("utf-8")).strip()
                        createNewUser(username, password, True)
                    elif usernameExists(username) is False: # else its a NEW user
                        if checkNewUserIterator == 0:
                        # respond to Client with "NON-EXISTENT USERNAME"
                            serverSocket.sendto("PASSWORD", clientAddr)
                            checkNewUserIterator += 1
                            continue # loop while 1 again
                        else: # if iterator != 0, then User's being prompted by Client a 2nd time, so create a new User now
                            # request Client for password and append both to credentials.txt file
                            serverSocket.sendto("PASSWORD", clientAddr)
                            createNewUser(username, password, True)
                            print(f"{username} successful login")
                            # code goes to "checkNewUserIterator = 0"
                    elif "has exited" in usernameMsg.decode("utf-8"):
                        # print(f"{username} exited")
                        print("Deez exited")
                        # changeUserActive(username, False)
                        break
                    # use "continue" if Client still hasn't authenticated
                    checkNewUserIterator = 0 # reset this for the next Client ??
                    # while 1: # while loop 3 for normal COMMANDS (after logging in)
                    # request msg from Client, and break it down via its formatting
                    # if cmd_var == "XIT":
                    #     break # and break next loop
                    # break # if the 3rd loop is broken, itd be cause of XIT, so break the 2nd loop also
                
                # Upon "ctrl + c"
                except KeyboardInterrupt:
                    killServer(serverSocket)
        except KeyboardInterrupt:
            killServer(serverSocket)

