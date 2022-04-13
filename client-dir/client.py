# Python Version: 3.8.10
# Program written by z5361183
# 10/04/22
# Run: $ python3 client.py serverPort
from socket import *
import sys
import os
from datetime import datetime
import time

#####################
#### Helper Fncs ####
#####################
### List of Commands possible ###
listOfCmds = ["CRT", "MSG", "DLT", "EDT", "LST", "RDT", "UPD", "DWN", "RMV", "XIT"]

# Globally change currCmd value (for socket.timeout issues) (workaround of using pointers)
def currCmdEquals(string):
    global currCmd
    currCmd = string

# Break down user input into a format suitable for Command's processing
def breakCmdInput(userInput):
    # break down per whitespace, and join index 2 to end, as one string
    brokenInput = userInput.split(" ")
    lenBrokenInput = len(brokenInput)
    if lenBrokenInput > 3:
        # join the 2nd+ indexes
        newIn = ''
        for i in range(2, lenBrokenInput):
            newIn = newIn + brokenInput[i] + ' '
        # combine all needed
        retInput = [str(brokenInput[0]), str(brokenInput[1]), str(newIn.rstrip())]
        return retInput
    # ELSE, its just 1 or 2 or 3 inputs (e.g "XIT" or "DLT 3331" or "MSG 3331 hi!")
    return brokenInput

###################
#### CMDs Fncs ####
###################

# CMD 1: User wants to exit Forum
def XIT(clientSocket, serverPort, username):
    clientSocket.sendto(f"XIT {username}".encode("utf-8"), ('localhost', int(serverPort)))
    clientSocket.close()
    sys.exit(f'Adios, "{username}"')

# CMD 2: Server needs to create the thread with the given threadtitle and username
def CRT(clientSocket, serverPort, threadtitle, username, currCmd):
    # print(f"Before: {currCmd}")
    if ("CRT RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        clientSocket.sendto(f"CRT {threadtitle} {username}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING CRT RESPONSE")
    # print(f"After: {currCmd}")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    if "TITLE TAKEN" in resp:
        return False
    else:
        return True

# CMD 2:
def RMV():
    pass

# CMD 3:
def MSG(clientSocket, serverPort, threadtitle, msg, currCmd):
    if ("MSG RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        # skip the {username} for this one, so we dont need to change breakCmdInput()
        clientSocket.sendto(f"MSG {threadtitle} {msg}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING MSG RESPONSE")
    # print(f"After: {currCmd}")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    if "TITLE INVALID" in resp:
        return False
    else:
        return True

# let the OS pick a random Client Port -> "sock.bind(('localhost', 0))", selected port is in "sock.getsockname()"
##################
#### MAIN Fnc ####
##################
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Execute program as such: $python3 client.py <server_port>')
    global currCmd
    currCmd = ""
    serverPort = int(sys.argv[1])
    WAIT_TIME_NRML = 0.7 # wait time for non-image commands
    WAIT_TIME_IMG = 2 # wait time for image transfers

    clientSocket = socket(AF_INET, SOCK_DGRAM) # sock_dgram == UDP socket
    # Set the timeout time if packet is taking too long/lost
    clientSocket.settimeout(WAIT_TIME_NRML)
    currCmd = ""
    enterUser = True
    respStr = ""
    currUsername = "" # save curr User's username for CMDs section
    while 1: # while loop 1 for logging onto server
        # try-except block used for sockettimeout timer 
        try:
            if "ENTER USERNAME" in currCmd or enterUser is True:
                goToWhile2 = False
                username = str(input("Enter username: "))
                clientSocket.sendto(username.encode("utf-8"), ('localhost', serverPort))
                # Wait for Server to respond with either "WRONG/VALID USERNAME"
                currCmd = "ENTER USERNAME"
                response, serverAddress = clientSocket.recvfrom(2048)
                respStr = (response.decode("utf-8")).strip()
            # IF username doesn't exist, then prompt it again (i.e restart loop)
            if respStr == "WRONG USERNAME":
                print("Invalid username")
                enterUser = True
                continue
            # IF Server decides its gonna create this new user, then send Server a password from user
            elif respStr == "NEW USERS PASSWORD":
                if ("NEW USERS PASSWORD" in currCmd) is False: # prevent password re-prompt & go straight to waiting for response 
                    password = str(input("Enter new password: "))
                    clientSocket.sendto(password.encode("utf-8"), ('localhost', serverPort))
                    currCmd = "NEW USERS PASSWORD"
                currCmd = "NEW USERS PASSWORD"
                response = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
                if response == "NEW USER LOGGED IN":
                    enterUser = False
                    currUsername = username
                    goToWhile2 = True
                    break
            # IF given Username matches Server's files, then send Server the matching password
            elif respStr == "VALID USERNAME":
                if ("ENTER PASSWORD" in currCmd) is False: # prevent password re-prompt
                    password = str(input("Enter password: "))
                    clientSocket.sendto(password.encode("utf-8"), ('localhost', serverPort))
                    currCmd = "ENTER PASSWORD"
                enterUser = False
                currCmd = "ENTER PASSWORD"
                response = str(clientSocket.recvfrom(2048)[0], "utf-8")
                if response == "WRONG PASSWORD":
                    print("Wrong password")
                    enterUser = True
                    continue
                else: # if resp = "VALID PASSWORD"
                    enterUser = False
                    currUsername = username
                    goToWhile2 = True
                    break
        
        except Exception as e:
            # Upon socket.timeout()
            if (str(e).rstrip()) == "timed out":
                print("Server's packet timedout, retrying...")
                print(f"Last currCmd value: {currCmd}")
                continue
            else:
                print(f"e: {e}")
        # Upon "ctrl + c"
        except KeyboardInterrupt:
            print("\nKilling client...")
            goToWhile2 = False # just in case
            break

    # upon successful authentication, we can now enter forums
    if goToWhile2 is True:
        print("====================\nWelcome to the forum\n====================")
        while 1: 
            try:
                # This IF is for cases when timeout occurs and CMD input already occurred
                if ("CMD INPUTTED" in currCmd) is False:
                    cmdInput = str(input("Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT: "))
                    currCmdEquals("CMD INPUTTED")
                    # break down cmdInput into a list of args 
                    cmdList = breakCmdInput(cmdInput) # cmdList[0] is the cmd, [1] is 2nd, and [3] is final arg
                if (cmdList[0] in listOfCmds) is False:
                    print("Invalid command")
                    currCmdEquals("ENTER CMD")
                    continue
                # CRT
                elif cmdList[0] == "CRT":
                    # Include CRT-specific error checking !!
                    if len(cmdList) != 2: # should only be "CRT <title>"
                        print("Incorrect syntax for CRT")
                        currCmdEquals("ENTER CMD")
                        continue
                    else:
                        ret = CRT(clientSocket, serverPort, cmdList[1], currUsername, currCmd)
                        if ret == False:
                            print("Threadtitle taken, please try again...")
                            currCmdEquals("ENTER CMD")
                            continue
                        else:
                            print(f'Thread "{cmdList[1]}" created!')
                            currCmdEquals("ENTER CMD")
                            continue
                # MSG
                elif cmdList[0] == "MSG":
                    # Remove any whitespace included, mistakingly leads to extra args (for e.g. "MSG 3331 " instead of "MSG 3331")
                    for i in cmdList:
                        if i == '':
                            cmdList.remove(i)
                    if len(cmdList) != 3: # should only be "MSG <title> '<arg1>...<argX>'", everything after <title> is grouped as one string
                        print("Incorrect syntax for MSG")
                        currCmdEquals("ENTER CMD")
                        continue
                    else:
                        ret = MSG(clientSocket, serverPort, cmdList[1], cmdList[2], currCmd)
                        if ret == False:
                            print("Invalid threadtitle, please try again...")
                            currCmdEquals("ENTER CMD")
                            continue
                        else:
                            print(f'Message sent in thread "{cmdList[1]}"')
                            currCmdEquals("ENTER CMD")
                            continue
                # DLT
                elif cmdList[0] == "DLT":
                    pass
                # EDT
                elif cmdList[0] == "EDT":
                    pass
                # LST
                elif cmdList[0] == "LST":
                    pass
                # RDT
                elif cmdList[0] == "RDT":
                    pass
                # RMV
                elif cmdList[0] == "RMV":
                    pass
                # UPD
                elif cmdList[0] == "UPD":
                    # Tell Server to open TCP connection, then do file transfer
                    # once done, close TCP connection
                    pass
                # DWN
                elif cmdList[0] == "DWN":
                    # Tell Server to open TCP connection, then do file transfer
                    # once done, close TCP connection
                    pass
                # XIT
                elif cmdList[0] == "XIT":
                    if len(cmdList) != 1:
                        print("WRONG syntax for XIT")
                    else:
                        XIT(clientSocket, serverPort, username)
        
            except Exception as e:
                # Upon socket.timeout()
                if (str(e).rstrip()) == "timed out":
                    print("Server's packet timedout, retrying...")
                    # print(f"Last currCmd value: {currCmd}") # ONLY FOR DEBUGGING
                    continue
                else:
                    print(f"ERROR: {e}")
                    continue
            # Upon "ctrl + c"
            except KeyboardInterrupt:
                XIT(clientSocket, serverPort, username)

    clientSocket.close()
