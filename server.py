# Python Version: 3.8.10
# Program written by z5361183
# 10/04/22
# Run; $ python3 server.py serverPort 
from socket import *
import sys
from datetime import datetime
import time

### Main Data Structure ###
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
        brokenLogin = allLinesF[i].split(" ") # "brokenLogin" is a list of strings
        user = brokenLogin[0]
        password = brokenLogin[1].rstrip() # removes trailing newline
        if (username == user):
            f.close()
            return True
    f.close()
    return False

# Checks credentials.txt if the user+pass combo exists
def checkUserPassCombo(username, password):
    f = open("credentials.txt", "r")
    allLinesF = f.readlines()
    numLinesF = len(allLinesF)
    for i in range(0, numLinesF):
        brokenLogin = allLinesF[i].split(" ")
        user = brokenLogin[0].rstrip()
        passW = brokenLogin[1].rstrip()
        if (username == user and password == passW):
            f.close()
            return True # combo is valid
    f.close()
    return False # combo invalid (password wrong, cause user already checked)

# Creates a new user data-struct (Upon detection of a new login), adds user deets to data store
# And adds user to credentials.txt IF it's new
def createNewUser(username, password, isActive, isNewUser):
    userStruct = {"username": username, "password": password, "isActive": isActive}
    dataStore['users'].append(userStruct)
    changeUserActive(username, True)
    if isNewUser == True: # user is not in credentials.txt yet
        f = open("credentials.txt", "a") # append new user deets to end of file
        strToAppend = "\n" + f"{username}" + f" {password}" # whitespace included before passW
        f.write(strToAppend)
        f.close()

# Make user online or offline
def changeUserActive(username, isActive):
    for users in dataStore['users']:
        if users["username"] == username:
            users["isActive"] == isActive
            return

# Breakdown Client's cmd-related msg to be suitable for processing
def breakCmdMsg(clientMsg):
    # break down per whitespace, and join index 2 to end, as one string
    brokenMsg = clientMsg.split(" ")
    lenBrokenMsg = len(brokenMsg)
    if lenBrokenMsg > 3:
        # join the 2nd+ indexes
        newMsg = ''
        for i in range(2, lenBrokenMsg):
            newMsg = newMsg + brokenMsg[i] + ' '
        # combine all needed
        retMsg = [str(brokenMsg[0]), str(brokenMsg[1]), str(newMsg.rstrip())]
        return retMsg
    # ELSE, its one or two inputs (e.g "XIT" or "DLT 3331")
    return brokenMsg


##################
#### MAIN Fnc ####
##################
if __name__ == "__main__":
    if (len(sys.argv) != 2):
        sys.exit("Execute program as such: $python3 server.py <server_port>")
    dataStoreClear()
    serverPort = int(sys.argv[1])
    serverSocket = socket(AF_INET, SOCK_DGRAM) 
    serverSocket.bind(('localhost', serverPort))
    # serverSocket.listen(1) # only for TCP ??

    while 1: # while loop 1 for Server's infinite loop
        try: 
            print("Server waiting for clients...")
            usernameMsg, clientAddr = serverSocket.recvfrom(2048)
            print("Client authenticating")
            checkForNewUserIter = 0
            i = 0
            userOnline = True
            while userOnline: # while loop 2 for authenticating
                # messagePass, clientAddr = serverSocket.recvfrom(2048)
                try:
                    if i == 0: # this is Just for the first loop
                        username = (usernameMsg.decode("utf-8")).strip()
                        i += 1
                    else: # this is for if the username prev entered is ticked as wrong, so on the 2nd input, wanna create a new user
                        username = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                    if usernameExists(username) is True:
                        checkForNewUserIter = 0 # reset the "check if new username is inputted" to 0
                        serverSocket.sendto("VALID USERNAME".encode("utf-8"), clientAddr) # Wait for password next
                        password = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                        # Check if username and password combo matches in credentials.txt
                        if checkUserPassCombo(username, password) is False:
                            serverSocket.sendto("INVALID PASSWORD".encode("utf-8"), clientAddr)
                            print("Invalid Password")
                            continue # loop back again, waiting for username
                        else:
                            # ADD USER to data store, and go to while loop 3
                            serverSocket.sendto("VALID PASSWORD".encode("utf-8"), clientAddr)
                            print("User+Pass combo is correct")
                            print(f"{username} successful login")
                            createNewUser(username, password, True, False)
                    elif usernameExists(username) is False: # else its a NEW user
                        if checkForNewUserIter == 0:
                            # respond to Client with "INVALID USERNAME"
                            serverSocket.sendto("INVALID USERNAME".encode("utf-8"), clientAddr)
                            print("Invalid username")
                            checkForNewUserIter += 1
                            continue # loop while 1 again
                        else: # if iterator != 0, then User's being prompted by Client a 2nd time, so create a new User now
                            # request Client for password and append both to credentials.txt file (createNewUser() will do that)
                            serverSocket.sendto("NEW USERS PASSWORD".encode("utf-8"), clientAddr)
                            print("Detected new user, waiting for new password")
                            password = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                            createNewUser(username, password, True, True)
                            print(f"{username} successful login")
                            # code goes to "checkForNewUserIter = 0", line X
                    # use "continue" if Client still hasn't authenticated
                    checkForNewUserIter = 0 # reset this for the next Client ??
                    while 1: # while loop 3 for normal COMMANDS (after logging in)
                        # request msg from Client, and break it down via its formatting ("<cmd> <arg1> <arg2")
                        cmdMsg = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                        cmdMsgBroken = breakCmdMsg(cmdMsg)
                        if cmdMsgBroken[0] == "XIT":
                            changeUserActive(username, False)
                            print(f"{username} exited")
                            userOnline = False # this'll break the 2nd while loop, making Server now wait for clients
                            break
                        elif cmdMsgBroken[0] == "CRT":
                            # CRT(cmdMsgBroken[1])
                            pass
                        elif cmdMsgBroken[0] == "MSG":
                            pass
                        elif cmdMsgBroken[0] == "DLT":
                            pass
                        elif cmdMsgBroken[0] == "EDT":
                            pass
                        elif cmdMsgBroken[0] == "LST":
                            pass
                        elif cmdMsgBroken[0] == "RDT":
                            pass
                        elif cmdMsgBroken[0] == "UPD":
                            pass
                        elif cmdMsgBroken[0] == "DWN":
                            pass
                        elif cmdMsgBroken[0] == "RMV":
                            pass
                        
                
                # Upon "ctrl + c"
                except KeyboardInterrupt:
                    killServer(serverSocket)
        except KeyboardInterrupt:
            killServer(serverSocket)

