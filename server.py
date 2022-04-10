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
    # dataStore['users'] = []
    # dataStore['threads'] = []
    pass

# Creates a new user (Upon detection of a new login)
def createNewUser(username, password, isActive):
    # newUser = {"username": poo, "password": pee, "isActive": True}
    # dataStore['users'].append(newUser)
    pass

# Checks if the given Username exists
def userIsNew():
    pass

def changeUserActive():
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

    while 1:
        print("Server waiting for clients...")
        message, clientAddr = serverSocket.recvfrom(2048)
        print("Client authenticating")
        while 1:
            # messagePass, clientAddr = serverSocket.recvfrom(2048)
            try:
                # analyse message
                alterMsg = (message.decode("utf-8")).upper()
                print(alterMsg)
                message, clientAddr = serverSocket.recvfrom(2048)
                if userIsNew(alterMsg) is True:
                    serverSocket.sendto("PASSWORD", clientAddr) # Wait for password next
                #   passMsg, clientAddr = serverSocket.recvfrom(2048)
                #   pass = (passMsg.decode("utf-8"))
                #   createNewUser(alterMsg, pass, True)
                elif "has exited" in message.decode("utf-8"):
                    # print(f"{user} exited")
                    print("Deez exited")
                    break

            # Upon "ctrl + c"
            except KeyboardInterrupt:
                print("\nKilling server...")
                dataStoreClear()
                serverSocket.close()
                break

